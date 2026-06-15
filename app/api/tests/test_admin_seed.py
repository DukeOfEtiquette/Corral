"""Admin bootstrap from an env-supplied argon2id hash (ADR-006, ADR-011).

Behaviour 1 of the four under test. The contract (ADR-006): on first boot an
admin user is seeded from an env-supplied argon2id password hash. The admin is a
`users` row with:
  - kind = 'human'        (the admin is a human user, not a machine identity)
  - email set            (from ADMIN_EMAIL)
  - password_hash set    (from ADMIN_PASSWORD_HASH, the env-supplied argon2id hash)
Seeding is idempotent on reboot: re-running the seed against an already-seeded
database creates no duplicate admin (the admin `users` row count for that email
stays at one).

Schema asserted against (the real 0001 baseline DDL):
  users(id, display_name, kind, email, password_hash, created_at),
  CHECK (kind in ('human','machine')), UNIQUE (email), email nullable.

Secrets: the seed env var carries a THROWAWAY test password hash generated in
the harness (see _make_test_hash); no real credential or real hash is ever
written into a test or any tracked file (repo CLAUDE.md secret rule, ADR-006).

Red-by-construction: `app/api/` does not exist, so the seed entry point imported
below cannot be resolved and these tests fail at collection. That is the
intended phase-1 state.
"""

import os

import pytest
from argon2 import PasswordHasher

# The admin-seed entry point the phase-2 executor must provide. The seed runs
# "on first boot" (ADR-006); the implementation exposes a callable the app's
# startup invokes, which the test drives directly so the seed can be exercised
# without standing up a full lifespan. The exact import path is the
# implementer's to satisfy; a mismatch is corrected via a fresh test-designer
# dispatch (ADR-016), not an executor edit.
from app.api.admin_seed import seed_admin

ADMIN_EMAIL = "admin@example.test"


def _make_test_hash(password: str = "throwaway-test-password") -> str:
    """A throwaway argon2id hash generated in-harness. Never a real credential
    (ADR-006 / repo secret rule). argon2-cffi's PasswordHasher defaults to
    argon2id, which is the algorithm ADR-011 pins.
    """
    return PasswordHasher().hash(password)


@pytest.fixture()
def admin_env(monkeypatch):
    """Set ADMIN_EMAIL / ADMIN_PASSWORD_HASH in the environment for the seed,
    using a throwaway in-harness hash. Returns (email, password_hash) so tests
    can assert the seeded row matches the env-supplied values.
    """
    password_hash = _make_test_hash()
    monkeypatch.setenv("ADMIN_EMAIL", ADMIN_EMAIL)
    monkeypatch.setenv("ADMIN_PASSWORD_HASH", password_hash)
    return ADMIN_EMAIL, password_hash


def _admin_rows(cur, email):
    """Fetch (kind, email, password_hash) for every users row with this email."""
    cur.execute(
        "SELECT kind, email, password_hash FROM users WHERE email = %s",
        (email,),
    )
    return cur.fetchall()


def test_seed_creates_admin_human_row_from_env(admin_env, cur):
    """On first boot the admin is seeded as a `users` row with kind='human',
    email set (from ADMIN_EMAIL), and password_hash set (from the env hash).
    """
    email, password_hash = admin_env

    seed_admin()

    rows = _admin_rows(cur, email)
    assert len(rows) == 1, "exactly one admin row should be seeded for the email"
    kind, seeded_email, seeded_password_hash = rows[0]
    assert kind == "human", "the admin is a human user, not a machine identity"
    assert seeded_email == email, "email comes from ADMIN_EMAIL"
    assert seeded_password_hash == password_hash, (
        "password_hash is the env-supplied argon2id hash, stored verbatim"
    )


def test_seed_sets_password_hash_not_plaintext(admin_env, cur):
    """The stored password_hash is the argon2id hash from the env, an argon2id
    encoded string (prefix '$argon2id$'), never a plaintext password.
    """
    email, password_hash = admin_env

    seed_admin()

    cur.execute("SELECT password_hash FROM users WHERE email = %s", (email,))
    (stored,) = cur.fetchone()
    assert stored == password_hash
    assert stored.startswith("$argon2id$"), (
        "the seed stores the argon2id hash from the env (ADR-011), not plaintext"
    )


def test_reseed_is_idempotent_no_duplicate_admin(admin_env, cur):
    """Re-running the seed against an already-seeded database creates no
    duplicate admin: the admin row count for the email stays at one (ADR-006:
    seed if and only if absent).
    """
    email, _ = admin_env

    seed_admin()
    seed_admin()
    seed_admin()

    cur.execute("SELECT count(*) FROM users WHERE email = %s", (email,))
    (count,) = cur.fetchone()
    assert count == 1, "reseeding must not create a duplicate admin"


def test_reseed_does_not_overwrite_existing_admin(admin_env, cur):
    """Idempotent reseed leaves the existing admin row intact: its id does not
    change across a second seed (the seed is a no-op when the admin exists, not
    a delete-and-recreate).
    """
    email, _ = admin_env

    seed_admin()
    cur.execute("SELECT id FROM users WHERE email = %s", (email,))
    (first_id,) = cur.fetchone()

    seed_admin()
    cur.execute("SELECT id FROM users WHERE email = %s", (email,))
    rows = cur.fetchall()

    assert len(rows) == 1
    assert rows[0][0] == first_id, "reseed must not replace the existing admin row"
