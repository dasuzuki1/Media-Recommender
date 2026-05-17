"""Hybrid recommender: content-based (genre cosine) + item-item collaborative.

Content-based: each anime is represented as a one-hot genre vector. The user's
preference vector is the rating-weighted average of their rated anime's vectors.
Recommendation score = cosine similarity(user_vector, anime_vector).

Collaborative: for each anime A the user rated highly, find anime that *other*
users who liked A also liked. The collaborative score for candidate C is the
sum over the user's liked anime A of (co-occurrence weight A→C) × user_rating(A).

Final score = content_weight * content + (1 - content_weight) * collaborative.
"""

from collections import defaultdict

import numpy as np

from db import from_decimal


def build_genre_index(anime_rows: list[dict]) -> list[str]:
    """Return the sorted list of all genres seen across the catalog."""
    genres = set()
    for row in anime_rows:
        for g in _parse_genres(row.get("genres")):
            genres.add(g)
    return sorted(genres)


def build_anime_matrix(anime_rows: list[dict], genre_index: list[str]) -> tuple[np.ndarray, list[int]]:
    """Returns (matrix shape (n_anime, n_genres), ordered anime_ids)."""
    idx = {g: i for i, g in enumerate(genre_index)}
    ids = []
    rows = []
    for row in anime_rows:
        ids.append(int(row["anime_id"]))
        vec = np.zeros(len(genre_index), dtype=np.float32)
        for g in _parse_genres(row.get("genres")):
            if g in idx:
                vec[idx[g]] = 1.0
        rows.append(vec)
    return np.vstack(rows) if rows else np.empty((0, len(genre_index))), ids


def content_scores(
    user_rows: list[dict],
    anime_matrix: np.ndarray,
    anime_ids: list[int],
) -> np.ndarray:
    """Cosine similarity between the user's preference vector and every anime."""
    if anime_matrix.shape[0] == 0:
        return np.zeros(0, dtype=np.float32)

    id_to_idx = {aid: i for i, aid in enumerate(anime_ids)}

    weighted = np.zeros(anime_matrix.shape[1], dtype=np.float32)
    weight_sum = 0.0
    for row in user_rows:
        aid = int(row["anime_id"])
        rating = float(from_decimal(row.get("rating") or 0))
        if rating <= 0 or aid not in id_to_idx:
            continue
        weighted += rating * anime_matrix[id_to_idx[aid]]
        weight_sum += rating

    if weight_sum == 0:
        return np.zeros(len(anime_ids), dtype=np.float32)

    user_vec = weighted / weight_sum

    # Cosine similarity (vectorized)
    norms = np.linalg.norm(anime_matrix, axis=1)
    user_norm = np.linalg.norm(user_vec)
    if user_norm == 0:
        return np.zeros(len(anime_ids), dtype=np.float32)

    dots = anime_matrix @ user_vec
    denom = norms * user_norm
    with np.errstate(divide="ignore", invalid="ignore"):
        sims = np.where(denom > 0, dots / denom, 0.0)
    return sims.astype(np.float32)


def collaborative_scores(
    user_id: int,
    user_rows: list[dict],
    all_interactions: list[dict],
    anime_ids: list[int],
    min_rating_threshold: float = 6.0,
) -> np.ndarray:
    """Item-item collaborative filtering via co-rated counts.

    For each anime A the target user rated >= threshold, count how often other
    users who rated A highly also rated each other anime C highly. Candidate C's
    score is sum over A of (co-occurrence(A,C) * user_rating(A) / popularity(A)).
    """
    target_high = {
        int(r["anime_id"]): float(from_decimal(r.get("rating") or 0))
        for r in user_rows
        if float(from_decimal(r.get("rating") or 0)) >= min_rating_threshold
    }
    if not target_high:
        return np.zeros(len(anime_ids), dtype=np.float32)

    # Group interactions by user, filter to "liked" only
    user_likes: dict[int, set[int]] = defaultdict(set)
    for row in all_interactions:
        uid = int(row["user_id"])
        if uid == user_id:
            continue
        rating = float(from_decimal(row.get("rating") or 0))
        if rating >= min_rating_threshold:
            user_likes[uid].add(int(row["anime_id"]))

    # Co-occurrence: for each target-anime A, sum likes-of-C across users who also liked A
    scores: dict[int, float] = defaultdict(float)
    popularity: dict[int, int] = defaultdict(int)
    for liked in user_likes.values():
        for a in liked:
            popularity[a] += 1

    for anime_a, target_rating in target_high.items():
        pop_a = popularity.get(anime_a, 0)
        if pop_a == 0:
            continue
        for liked in user_likes.values():
            if anime_a not in liked:
                continue
            for c in liked:
                if c == anime_a or c in target_high:
                    continue
                scores[c] += target_rating / pop_a  # normalize by popularity of A

    out = np.zeros(len(anime_ids), dtype=np.float32)
    id_to_idx = {aid: i for i, aid in enumerate(anime_ids)}
    for aid, s in scores.items():
        if aid in id_to_idx:
            out[id_to_idx[aid]] = s
    return out


def blend_and_rank(
    anime_rows: list[dict],
    anime_ids: list[int],
    content: np.ndarray,
    collaborative: np.ndarray,
    seen_anime_ids: set[int],
    content_weight: float,
    top_n: int,
) -> list[dict]:
    """Normalize each signal to [0, 1], blend, exclude seen, return top-N rows."""
    c_norm = _minmax(content)
    cf_norm = _minmax(collaborative)
    final = content_weight * c_norm + (1 - content_weight) * cf_norm

    anime_by_id = {int(r["anime_id"]): r for r in anime_rows}

    ranked_idx = np.argsort(-final)
    out = []
    for i in ranked_idx:
        aid = anime_ids[i]
        if aid in seen_anime_ids:
            continue
        row = anime_by_id.get(aid, {})
        out.append({
            "anime_id": aid,
            "title_romaji": row.get("title_romaji"),
            "title_english": row.get("title_english"),
            "cover_image_large": row.get("cover_image_large"),
            "genres": row.get("genres"),
            "score": float(final[i]),
            "content_score": float(c_norm[i]),
            "collaborative_score": float(cf_norm[i]),
        })
        if len(out) >= top_n:
            break
    return out


def _minmax(arr: np.ndarray) -> np.ndarray:
    if arr.size == 0:
        return arr
    lo, hi = float(arr.min()), float(arr.max())
    if hi <= lo:
        return np.zeros_like(arr)
    return (arr - lo) / (hi - lo)


def _parse_genres(raw) -> list[str]:
    if not raw:
        return []
    if isinstance(raw, list):
        return [g for g in raw if g]
    # Comma-separated string (matches legacy SQLite schema)
    return [g.strip() for g in str(raw).split(",") if g.strip()]
