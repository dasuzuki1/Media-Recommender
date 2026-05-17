"""Seed the local SQLite DB with a public AniList user's anime list.

Usage:
    python scripts/seed_user.py <username> [--db path/to/anilist.db]

Example:
    python scripts/seed_user.py SaikoKurami

Pulls the user's public anime list via AniList's GraphQL API (no auth needed),
upserts the user into Users, any new anime into Anime, and the interactions
into UserAnime.

Note: the v1 SQLite schema is anime-only. Manga support would require schema
changes (either a media_type column or a parallel Manga table). The v2
DynamoDB schema in aws/ already supports both via the media_type discriminator.
"""

import argparse
import json
import os
import sqlite3
import sys

# Make `src.*` importable when running as a script
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.api.fetch_data import fetch_user_lists_by_username


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("username", help="AniList username (e.g. SaikoKurami)")
    parser.add_argument("--db", default="data/anilist.db", help="Path to SQLite DB")
    args = parser.parse_args()

    print(f"Fetching anime list for '{args.username}' from AniList...")
    viewer, entries = fetch_user_lists_by_username(args.username, media_type="ANIME")

    if not viewer:
        print(f"No public list found for user '{args.username}' (private or doesn't exist).")
        sys.exit(1)

    print(f"  user_id={viewer['id']}  name={viewer['name']}  entries={len(entries)}")

    db_path = os.path.abspath(args.db)
    print(f"Writing to {db_path}...")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Upsert user
    cur.execute(
        """
        INSERT INTO Users (user_id, username, avatar_url)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            username = excluded.username,
            avatar_url = excluded.avatar_url
        """,
        (viewer["id"], viewer["name"], viewer["avatar"]["large"]),
    )

    anime_new = 0
    interactions = 0
    for entry in entries:
        media = entry["media"]
        relations_json = json.dumps([])  # not fetched here; existing rows keep theirs via OR IGNORE

        # Insert anime if missing, otherwise leave the (possibly richer) existing row alone
        cur.execute("SELECT 1 FROM Anime WHERE anime_id = ?", (media["id"],))
        if cur.fetchone() is None:
            cur.execute(
                """
                INSERT INTO Anime (
                    anime_id, title_romaji, title_english, description, episodes,
                    average_score, favourites, cover_image_large, cover_image_medium,
                    url, relations, genres
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    media["id"],
                    (media.get("title") or {}).get("romaji") or "",
                    (media.get("title") or {}).get("english") or "",
                    media.get("description") or "",
                    media.get("episodes") or 0,
                    media.get("averageScore") or 0,
                    media.get("favourites") or 0,
                    (media.get("coverImage") or {}).get("large") or "",
                    (media.get("coverImage") or {}).get("medium") or "",
                    f"https://anilist.co/anime/{media['id']}",
                    relations_json,
                    ", ".join(media.get("genres") or []),
                ),
            )
            anime_new += 1

        # Upsert interaction
        cur.execute(
            """
            INSERT INTO UserAnime (user_id, anime_id, rating, favourites, status)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id, anime_id) DO UPDATE SET
                rating = COALESCE(EXCLUDED.rating, rating),
                favourites = EXCLUDED.favourites,
                status = EXCLUDED.status,
                last_updated = CURRENT_TIMESTAMP
            """,
            (
                viewer["id"],
                media["id"],
                entry.get("score") or 0,
                1 if media.get("isFavourite") else 0,
                entry.get("status") or "",
            ),
        )
        interactions += 1

    conn.commit()

    # Report final totals
    cur.execute("SELECT COUNT(*) FROM Users")
    users_total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM Anime")
    anime_total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM UserAnime")
    interactions_total = cur.fetchone()[0]
    conn.close()

    print()
    print(f"Done. Wrote {interactions} interactions, added {anime_new} new anime to catalog.")
    print(f"Totals in {args.db}:")
    print(f"  Users:       {users_total}")
    print(f"  Anime:       {anime_total}")
    print(f"  UserAnime:   {interactions_total}")


if __name__ == "__main__":
    main()
