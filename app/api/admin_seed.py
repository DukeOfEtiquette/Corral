"""Admin user bootstrap from env-supplied argon2id hash (ADR-006, ADR-011).

seed_admin() is directly callable (tests drive it without a running app) and is
also invoked by the FastAPI lifespan handler on startup. It is idempotent: it
seeds the admin if and only if no users row with ADMIN_EMAIL already exists.

The env-supplied ADMIN_PASSWORD_HASH is stored verbatim; it is an argon2id
encoding already (the operator generated it locally, ADR-006). seed_admin() does
NOT re-hash it.
"""

import psycopg2

from app.api import settings


def seed_admin() -> None:
    """Idempotently seed the admin user from ADMIN_EMAIL / ADMIN_PASSWORD_HASH.

    Inserts a users row with kind='human', email, password_hash (verbatim from
    the env), and a display_name. Does nothing if the email already exists.
    """
    email = settings.get_admin_email()
    password_hash = settings.get_admin_password_hash()

    url = settings.get_database_url()
    conn = psycopg2.connect(url)
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id FROM users WHERE email = %s",
                    (email,),
                )
                row = cur.fetchone()
                if row is not None:
                    return
                cur.execute(
                    """
                    INSERT INTO users (display_name, kind, email, password_hash, created_at)
                    VALUES (%s, %s, %s, %s, now())
                    """,
                    ("Admin", "human", email, password_hash),
                )
    finally:
        conn.close()
