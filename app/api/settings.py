"""Application settings read from environment variables.

No heavy config framework: mirrors the db department's minimal approach.
All values are read from os.environ at call time so monkeypatch works in tests.
"""

import os


def get_database_url() -> str:
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set")
    return url


def get_admin_email() -> str:
    email = os.environ.get("ADMIN_EMAIL")
    if not email:
        raise RuntimeError("ADMIN_EMAIL is not set")
    return email


def get_admin_password_hash() -> str:
    h = os.environ.get("ADMIN_PASSWORD_HASH")
    if not h:
        raise RuntimeError("ADMIN_PASSWORD_HASH is not set")
    return h


def get_cookie_name() -> str:
    return os.environ.get("SESSION_COOKIE_NAME", "session")


def get_session_lifetime_seconds() -> int:
    return int(os.environ.get("SESSION_LIFETIME_SECONDS", str(60 * 60 * 24 * 7)))


def get_cookie_secure() -> bool:
    return os.environ.get("SESSION_COOKIE_SECURE", "false").lower() == "true"
