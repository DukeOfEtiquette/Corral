"""Auth and session logic (ADR-011).

- Login: verify argon2id password, create a sessions row (session_id stored
  hashed at rest), set an HTTP-only SameSite cookie.
- Session lookup: hash the incoming cookie value, look up the sessions row.
- Logout: delete the sessions row.

Cookie name is configurable via SESSION_COOKIE_NAME (default: "session").
Session id hashing uses SHA-256 (fast, sufficient for a MAC/opaque-token store
where the raw value is high-entropy; the hash is never used as a password hash).
"""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import psycopg2
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from app.api import settings
from app.api.db import get_conn

_ph = PasswordHasher()


def _hash_session_id(raw: str) -> str:
    """Hash an opaque session token with SHA-256 for at-rest storage."""
    return hashlib.sha256(raw.encode()).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a plaintext password against an argon2id hash.

    Returns True on match, False on mismatch or invalid hash.
    """
    try:
        return _ph.verify(password_hash, password)
    except VerifyMismatchError:
        return False
    except Exception:
        return False


def create_session(user_id: int) -> str:
    """Create a sessions row for user_id and return the raw opaque session id
    (to be placed in the cookie). The stored sessions.session_id is its hash.
    """
    raw_id = secrets.token_hex(32)
    hashed_id = _hash_session_id(raw_id)
    lifetime = settings.get_session_lifetime_seconds()
    expires_at = datetime.now(tz=timezone.utc) + timedelta(seconds=lifetime)

    conn = get_conn()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO sessions (session_id, user_id, expires_at, created_at)
                    VALUES (%s, %s, %s, now())
                    """,
                    (hashed_id, user_id, expires_at),
                )
    finally:
        conn.close()

    return raw_id


def lookup_session(raw_cookie: str):
    """Return the users row for a valid, unexpired session cookie, or None.

    Hashes the raw cookie value and looks up the sessions row. Returns the
    matching users row (as a dict with at least 'id', 'email') or None if the
    session is absent, expired, or the hash matches nothing.
    """
    hashed_id = _hash_session_id(raw_cookie)
    conn = get_conn()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT u.id, u.email, u.display_name
                    FROM sessions s
                    JOIN users u ON u.id = s.user_id
                    WHERE s.session_id = %s
                      AND s.expires_at > now()
                    """,
                    (hashed_id,),
                )
                row = cur.fetchone()
    finally:
        conn.close()

    if row is None:
        return None
    return {"id": row[0], "email": row[1], "display_name": row[2]}


def delete_session(raw_cookie: str) -> None:
    """Delete the sessions row corresponding to the raw cookie value (logout)."""
    hashed_id = _hash_session_id(raw_cookie)
    conn = get_conn()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM sessions WHERE session_id = %s",
                    (hashed_id,),
                )
    finally:
        conn.close()


def get_user_by_email(email: str):
    """Return (id, email, password_hash) for the user with this email, or None."""
    conn = get_conn()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, email, password_hash FROM users WHERE email = %s",
                    (email,),
                )
                row = cur.fetchone()
    finally:
        conn.close()

    if row is None:
        return None
    return {"id": row[0], "email": row[1], "password_hash": row[2]}
