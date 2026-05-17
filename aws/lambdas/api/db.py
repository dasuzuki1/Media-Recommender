import os
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key

_dynamodb = boto3.resource("dynamodb")

users_table = _dynamodb.Table(os.environ["USERS_TABLE"])
user_anime_table = _dynamodb.Table(os.environ["USER_ANIME_TABLE"])
anime_table = _dynamodb.Table(os.environ["ANIME_TABLE"])
recommendations_table = _dynamodb.Table(os.environ["RECOMMENDATIONS_TABLE"])


def put_user(user_id: int, username: str, avatar_url: str) -> None:
    users_table.put_item(
        Item={
            "user_id": user_id,
            "username": username,
            "avatar_url": avatar_url,
        }
    )


def get_user(user_id: int) -> dict | None:
    resp = users_table.get_item(Key={"user_id": user_id})
    return resp.get("Item")


def put_user_anime_batch(rows: list[dict]) -> int:
    """Bulk-write user-anime interactions. Returns number written."""
    with user_anime_table.batch_writer(overwrite_by_pkeys=["user_id", "anime_id"]) as batch:
        for row in rows:
            batch.put_item(Item=_clean_for_dynamo(row))
    return len(rows)


def get_recommendations(user_id: int, limit: int = 20) -> list[dict]:
    resp = recommendations_table.query(
        KeyConditionExpression=Key("user_id").eq(user_id),
        Limit=limit,
        ScanIndexForward=True,  # rank ascending (rank 1 = best)
    )
    return [_from_dynamo(item) for item in resp.get("Items", [])]


def _clean_for_dynamo(obj):
    """DynamoDB rejects floats and empty strings. Convert + sanitize."""
    if isinstance(obj, dict):
        return {k: _clean_for_dynamo(v) for k, v in obj.items() if v != ""}
    if isinstance(obj, list):
        return [_clean_for_dynamo(v) for v in obj]
    if isinstance(obj, float):
        return Decimal(str(obj))
    return obj


def _from_dynamo(obj):
    """Convert DynamoDB Decimals back to float/int for JSON serialization."""
    if isinstance(obj, dict):
        return {k: _from_dynamo(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_from_dynamo(v) for v in obj]
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    return obj
