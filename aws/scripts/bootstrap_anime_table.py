"""One-time ingest of the legacy SQLite Anime catalog into DynamoDB.

Usage:
    cd aws/infra && terraform output -raw anime_table  # confirm table name
    cd aws/scripts
    python bootstrap_anime_table.py \\
        --sqlite ../../data/anilist.db \\
        --table media-recommender-dev-anime \\
        --region us-east-1

Reads every row from the SQLite Anime table and writes it to DynamoDB using
batch_writer (25 items per request, automatic retry on unprocessed items).
"""

import argparse
import sqlite3
import sys
from decimal import Decimal

import boto3


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sqlite", required=True, help="Path to anilist.db")
    parser.add_argument("--table", required=True, help="DynamoDB Anime table name")
    parser.add_argument("--region", default="us-east-1")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    conn = sqlite3.connect(args.sqlite)
    conn.row_factory = sqlite3.Row
    cursor = conn.execute("""
        SELECT anime_id, title_romaji, title_english, description, episodes,
               average_score, favourites, cover_image_large, cover_image_medium,
               url, relations, genres
        FROM Anime
    """)

    table = boto3.resource("dynamodb", region_name=args.region).Table(args.table)

    total = 0
    if args.dry_run:
        for row in cursor:
            item = _row_to_item(row)
            if total < 3:
                print(item)
            total += 1
        print(f"[dry-run] would write {total} items")
        return

    with table.batch_writer() as batch:
        for row in cursor:
            batch.put_item(Item=_row_to_item(row))
            total += 1
            if total % 500 == 0:
                print(f"  wrote {total}...", flush=True)

    print(f"wrote {total} anime to {args.table}")


def _row_to_item(row: sqlite3.Row) -> dict:
    item = {
        "anime_id": int(row["anime_id"]),
        "title_romaji": row["title_romaji"] or "",
        "title_english": row["title_english"] or "",
        "description": row["description"] or "",
        "episodes": int(row["episodes"] or 0),
        "average_score": _to_decimal(row["average_score"]),
        "favourites": int(row["favourites"] or 0),
        "cover_image_large": row["cover_image_large"] or "",
        "cover_image_medium": row["cover_image_medium"] or "",
        "url": row["url"] or "",
        "relations": row["relations"] or "",
        "genres": row["genres"] or "",
    }
    # DynamoDB rejects empty strings
    return {k: v for k, v in item.items() if v != ""}


def _to_decimal(v) -> Decimal:
    if v is None:
        return Decimal(0)
    return Decimal(str(round(float(v), 4)))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)
