"""Database connection helpers using raw psycopg2-binary (sync).

No ORM (ADR-014). Route handlers are sync def; psycopg2 calls are safe inside
FastAPI's threadpool for sync handlers.
"""

import psycopg2

from app.api import settings


def get_conn():
    """Open and return a psycopg2 connection using DATABASE_URL."""
    url = settings.get_database_url()
    conn = psycopg2.connect(url)
    conn.autocommit = False
    return conn
