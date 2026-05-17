"""Scheduled batch recommender.

Triggered by EventBridge. For each user, computes a hybrid (content + collaborative)
recommendation list and writes the top-N to the Recommendations table. The API
Lambda then serves these via a single DynamoDB Query (~5-15ms).
"""

import logging
import os
import time

import db
from recommender import (
    blend_and_rank,
    build_anime_matrix,
    build_genre_index,
    collaborative_scores,
    content_scores,
)

log = logging.getLogger()
log.setLevel(logging.INFO)

TOP_N = int(os.environ.get("TOP_N", "20"))
CONTENT_WEIGHT = float(os.environ.get("CONTENT_WEIGHT", "0.6"))


def lambda_handler(event, context):
    started = time.time()

    users = db.scan_all_users()
    log.info("found %d users", len(users))
    if not users:
        return {"users_processed": 0}

    anime = db.scan_all_anime()
    log.info("loaded %d anime", len(anime))
    if not anime:
        log.warning("Anime catalog is empty — run aws/scripts/bootstrap_anime_table.py")
        return {"users_processed": 0, "reason": "empty_catalog"}

    all_interactions = db.scan_all_user_anime()
    log.info("loaded %d interactions across all users", len(all_interactions))

    genre_index = build_genre_index(anime)
    anime_matrix, anime_ids = build_anime_matrix(anime, genre_index)

    processed = 0
    for user in users:
        user_id = int(user["user_id"])
        user_rows = db.query_user_anime(user_id)
        if not user_rows:
            continue

        seen = {int(r["anime_id"]) for r in user_rows}
        content = content_scores(user_rows, anime_matrix, anime_ids)
        collab = collaborative_scores(
            user_id, user_rows, all_interactions, anime_ids
        )
        ranked = blend_and_rank(
            anime_rows=anime,
            anime_ids=anime_ids,
            content=content,
            collaborative=collab,
            seen_anime_ids=seen,
            content_weight=CONTENT_WEIGHT,
            top_n=TOP_N,
        )

        if ranked:
            db.write_recommendations(user_id, ranked)
            processed += 1

    elapsed = time.time() - started
    log.info("processed %d users in %.1fs", processed, elapsed)
    return {"users_processed": processed, "elapsed_seconds": elapsed}
