"""API Lambda — handles all HTTP routes for the Media Recommender.

Routes (dispatched on event['rawPath']):
  GET  /login           → redirect to AniList OAuth
  GET  /callback        → exchange code, persist user, set session cookie
  POST /sync            → fetch user's AniList list, write UserAnime rows
  GET  /recommendations → return precomputed top-N from DynamoDB
  GET  /health          → liveness probe
"""

import json
import logging
import os

import anilist
import db
import session

log = logging.getLogger()
log.setLevel(logging.INFO)

CLIENT_ID = os.environ["ANILIST_CLIENT_ID"]
CLIENT_SECRET = os.environ["ANILIST_CLIENT_SECRET"]
REDIRECT_URI = os.environ["REDIRECT_URI"]
FRONTEND_ORIGIN = os.environ["FRONTEND_ORIGIN"]


def lambda_handler(event, context):
    method = event.get("requestContext", {}).get("http", {}).get("method", "GET")
    path = event.get("rawPath", "/")
    log.info("request method=%s path=%s", method, path)

    try:
        if path == "/health":
            return _json(200, {"status": "ok"})
        if path == "/login" and method == "GET":
            return _login()
        if path == "/callback" and method == "GET":
            return _callback(event)
        if path == "/sync" and method == "POST":
            return _sync(event)
        if path == "/recommendations" and method == "GET":
            return _recommendations(event)
        return _json(404, {"error": "not found", "path": path})
    except Exception:
        log.exception("unhandled error")
        return _json(500, {"error": "internal error"})


def _login():
    url = anilist.authorize_url(CLIENT_ID, REDIRECT_URI)
    return {"statusCode": 302, "headers": {"Location": url}, "body": ""}


def _callback(event):
    code = (event.get("queryStringParameters") or {}).get("code")
    if not code:
        return _json(400, {"error": "missing ?code"})

    access_token = anilist.exchange_code(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, code)
    viewer = anilist.fetch_viewer(access_token)
    user_id = int(viewer["id"])

    db.put_user(user_id, viewer["name"], viewer["avatar"]["large"])

    cookie = session.encode({"user_id": user_id, "access_token": access_token})
    return {
        "statusCode": 302,
        "headers": {"Location": f"{FRONTEND_ORIGIN}/"},
        "cookies": [session.cookie_header(cookie)],
        "body": "",
    }


def _sync(event):
    sess = session.read_session_from_event(event)
    if not sess:
        return _json(401, {"error": "not logged in"})

    user_id = sess["user_id"]
    access_token = sess["access_token"]

    entries = anilist.fetch_user_anime_list(access_token, user_id)

    rows = []
    for entry in entries:
        media = entry["media"]
        rows.append({
            "user_id": user_id,
            "anime_id": int(media["id"]),
            "rating": entry.get("score") or 0,
            "favourites": bool(media.get("isFavourite")),
            "status": entry.get("status") or "",
        })

    written = db.put_user_anime_batch(rows)
    return _json(200, {"synced": written})


def _recommendations(event):
    sess = session.read_session_from_event(event)
    if not sess:
        return _json(401, {"error": "not logged in"})

    recs = db.get_recommendations(sess["user_id"], limit=20)
    return _json(200, {"user_id": sess["user_id"], "recommendations": recs})


def _json(status: int, body: dict) -> dict:
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }
