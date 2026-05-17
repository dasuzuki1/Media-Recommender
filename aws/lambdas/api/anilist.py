"""AniList OAuth + GraphQL helpers. Uses urllib to avoid bundling `requests`."""

import json
import urllib.parse
import urllib.request

GRAPHQL_URL = "https://graphql.anilist.co"
TOKEN_URL = "https://anilist.co/api/v2/oauth/token"
AUTHORIZE_URL = "https://anilist.co/api/v2/oauth/authorize"


def authorize_url(client_id: str, redirect_uri: str) -> str:
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
    }
    return f"{AUTHORIZE_URL}?{urllib.parse.urlencode(params)}"


def exchange_code(client_id: str, client_secret: str, redirect_uri: str, code: str) -> str:
    payload = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "code": code,
    }
    data = _post_json(TOKEN_URL, payload)
    return data["access_token"]


def fetch_viewer(access_token: str) -> dict:
    query = """
    query { Viewer { id name avatar { large } } }
    """
    data = _graphql(access_token, query, {})
    return data["Viewer"]


def fetch_user_anime_list(access_token: str, user_id: int) -> list[dict]:
    """Returns a flat list of {anime, score, status, isFavourite} dicts."""
    query = """
    query ($userId: Int) {
      MediaListCollection(userId: $userId, type: ANIME) {
        lists {
          name
          entries {
            score
            status
            media {
              id
              title { romaji english }
              genres
              episodes
              averageScore
              favourites
              coverImage { large }
              isFavourite
            }
          }
        }
      }
    }
    """
    data = _graphql(access_token, query, {"userId": user_id})
    flat = []
    for lst in data["MediaListCollection"]["lists"]:
        for entry in lst["entries"]:
            flat.append(entry)
    return flat


def _graphql(access_token: str, query: str, variables: dict) -> dict:
    payload = {"query": query, "variables": variables}
    headers = {"Authorization": f"Bearer {access_token}"}
    data = _post_json(GRAPHQL_URL, payload, headers=headers)
    if "errors" in data:
        raise RuntimeError(f"AniList GraphQL error: {data['errors']}")
    return data["data"]


def _post_json(url: str, payload: dict, headers: dict | None = None) -> dict:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            **(headers or {}),
        },
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())
