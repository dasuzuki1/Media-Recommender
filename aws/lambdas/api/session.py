"""Stateless signed-cookie sessions. No server-side storage needed."""

import base64
import hashlib
import hmac
import json
import os
import time

COOKIE_NAME = "session"
MAX_AGE_SECONDS = 60 * 60 * 24 * 7  # 1 week


def encode(payload: dict) -> str:
    body = {**payload, "exp": int(time.time()) + MAX_AGE_SECONDS}
    raw = json.dumps(body, separators=(",", ":")).encode()
    b64 = base64.urlsafe_b64encode(raw).rstrip(b"=").decode()
    sig = _sign(b64)
    return f"{b64}.{sig}"


def decode(cookie_value: str) -> dict | None:
    try:
        b64, sig = cookie_value.split(".", 1)
    except ValueError:
        return None
    expected = _sign(b64)
    if not hmac.compare_digest(sig, expected):
        return None
    padded = b64 + "=" * (-len(b64) % 4)
    body = json.loads(base64.urlsafe_b64decode(padded.encode()))
    if body.get("exp", 0) < int(time.time()):
        return None
    return body


def cookie_header(cookie_value: str) -> str:
    return (
        f"{COOKIE_NAME}={cookie_value}; "
        f"Max-Age={MAX_AGE_SECONDS}; Path=/; HttpOnly; Secure; SameSite=Lax"
    )


def read_session_from_event(event: dict) -> dict | None:
    cookies = event.get("cookies") or []
    for c in cookies:
        if c.startswith(f"{COOKIE_NAME}="):
            return decode(c[len(COOKIE_NAME) + 1 :])
    return None


def _sign(payload_b64: str) -> str:
    secret = os.environ["SESSION_SECRET"].encode()
    mac = hmac.new(secret, payload_b64.encode(), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(mac).rstrip(b"=").decode()
