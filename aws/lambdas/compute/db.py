import os
import time
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key

_dynamodb = boto3.resource("dynamodb")

users_table = _dynamodb.Table(os.environ["USERS_TABLE"])
user_anime_table = _dynamodb.Table(os.environ["USER_ANIME_TABLE"])
anime_table = _dynamodb.Table(os.environ["ANIME_TABLE"])
recommendations_table = _dynamodb.Table(os.environ["RECOMMENDATIONS_TABLE"])

RECOMMENDATION_TTL_SECONDS = 60 * 60 * 25  # 25h (slightly > hourly schedule)


def scan_all_users() -> list[dict]:
    items = []
    kwargs = {}
    while True:
        resp = users_table.scan(**kwargs)
        items.extend(resp.get("Items", []))
        if "LastEvaluatedKey" not in resp:
            return items
        kwargs["ExclusiveStartKey"] = resp["LastEvaluatedKey"]


def scan_all_anime() -> list[dict]:
    items = []
    kwargs = {}
    while True:
        resp = anime_table.scan(**kwargs)
        items.extend(resp.get("Items", []))
        if "LastEvaluatedKey" not in resp:
            return items
        kwargs["ExclusiveStartKey"] = resp["LastEvaluatedKey"]


def scan_all_user_anime() -> list[dict]:
    """Used to build the collaborative co-occurrence matrix across all users."""
    items = []
    kwargs = {}
    while True:
        resp = user_anime_table.scan(**kwargs)
        items.extend(resp.get("Items", []))
        if "LastEvaluatedKey" not in resp:
            return items
        kwargs["ExclusiveStartKey"] = resp["LastEvaluatedKey"]


def query_user_anime(user_id: int) -> list[dict]:
    resp = user_anime_table.query(
        KeyConditionExpression=Key("user_id").eq(user_id)
    )
    return resp.get("Items", [])


def write_recommendations(user_id: int, ranked: list[dict]) -> None:
    """Replace all recommendations for a user with the new ranked list."""
    expires_at = int(time.time()) + RECOMMENDATION_TTL_SECONDS
    with recommendations_table.batch_writer() as batch:
        for rank, item in enumerate(ranked, start=1):
            batch.put_item(Item=_to_dynamo({
                "user_id": user_id,
                "rank": rank,
                "anime_id": item["anime_id"],
                "title_romaji": item.get("title_romaji"),
                "title_english": item.get("title_english"),
                "cover_image_large": item.get("cover_image_large"),
                "genres": item.get("genres"),
                "score": item["score"],
                "content_score": item["content_score"],
                "collaborative_score": item["collaborative_score"],
                "expires_at": expires_at,
            }))


def _to_dynamo(obj):
    if isinstance(obj, dict):
        return {k: _to_dynamo(v) for k, v in obj.items() if v not in (None, "")}
    if isinstance(obj, list):
        return [_to_dynamo(v) for v in obj]
    if isinstance(obj, float):
        return Decimal(str(round(obj, 6)))
    return obj


def from_decimal(v):
    if isinstance(v, Decimal):
        return float(v)
    return v
