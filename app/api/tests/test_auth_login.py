"""Login and password verification (ADR-011).

Behaviour 2 of the four under test. The contract (ADR-011):
  - credentials are verified with argon2id (argon2-cffi);
  - on success the server establishes a server-side session (a `sessions` row
    is created for the user) and sets an HTTP-only, SameSite session cookie on
    the response;
  - a wrong password yields HTTP 401 and establishes no session (no `sessions`
    row, no cookie).

Cookie assertions, per the kickoff hard rules:
  - assert HttpOnly and SameSite are set;
  - do NOT assert the `Secure` flag (ADR-011 relaxes it for local HTTP dev; the
    ASGI transport is not HTTPS);
  - do NOT assert the raw cookie value equals the stored `sessions.session_id`
    (ADR-011 stores the session id hashed at rest).

Endpoint paths: the kickoff pins `GET /api/v1/me` (behaviour 3). Login and
logout reuse that `/api/v1` prefix at `POST /api/v1/auth/login` and
`POST /api/v1/auth/logout`; a path mismatch with the implementation is corrected
via a fresh test-designer dispatch (ADR-016), not an executor edit.

A targeted argon2id-verify unit test is included where it adds coverage the
integration path does not (verifying the hashing primitive itself).

Red-by-construction: `app/api/` does not exist, so the app-import in conftest
fails at collection. That is the intended phase-1 state.
"""

import pytest
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

LOGIN_URL = "/api/v1/auth/login"

ADMIN_EMAIL = "login-admin@example.test"
ADMIN_PASSWORD = "correct-horse-battery-staple"  # throwaway test password

# The `seeded_admin` fixture is now the shared one in conftest.py (API-T-005);
# it reads this module's ADMIN_EMAIL / ADMIN_PASSWORD via request.module
# introspection and hashes once per session through the memoized helper.


def _session_count(cur, user_id):
    cur.execute("SELECT count(*) FROM sessions WHERE user_id = %s", (user_id,))
    (count,) = cur.fetchone()
    return count


@pytest.mark.asyncio
async def test_login_success_creates_session_row(client, seeded_admin, cur):
    """Login with the correct password creates exactly one `sessions` row for
    the authenticated user.
    """
    email, password, user_id = seeded_admin
    assert _session_count(cur, user_id) == 0, "no session before login"

    resp = await client.post(LOGIN_URL, json={"email": email, "password": password})

    assert resp.status_code == 200
    assert _session_count(cur, user_id) == 1, "a session row is created on success"


@pytest.mark.asyncio
async def test_login_success_sets_httponly_samesite_cookie(client, seeded_admin):
    """Login success sets a session cookie that is HTTP-only and carries a
    SameSite attribute. The Secure flag is NOT asserted (HTTP transport,
    ADR-011 relaxation).
    """
    email, password, _ = seeded_admin

    resp = await client.post(LOGIN_URL, json={"email": email, "password": password})

    assert resp.status_code == 200
    set_cookie_headers = resp.headers.get_list("set-cookie")
    assert set_cookie_headers, "login must set a session cookie"
    cookie_header = "; ".join(set_cookie_headers).lower()
    assert "httponly" in cookie_header, "the session cookie must be HttpOnly"
    assert "samesite" in cookie_header, "the session cookie must set SameSite"


@pytest.mark.asyncio
async def test_login_success_sets_a_session_cookie_value(client, seeded_admin):
    """Login success places a non-empty cookie in the client jar (the opaque
    session identifier). Its raw value is NOT compared to the stored
    `sessions.session_id`, which is hashed at rest (ADR-011).
    """
    email, password, _ = seeded_admin

    resp = await client.post(LOGIN_URL, json={"email": email, "password": password})

    assert resp.status_code == 200
    assert len(client.cookies) >= 1, "a session cookie is issued to the client"
    assert any(v for v in client.cookies.values()), "the session cookie is non-empty"


@pytest.mark.asyncio
async def test_login_wrong_password_returns_401(client, seeded_admin):
    """A wrong password yields HTTP 401."""
    email, _, _ = seeded_admin

    resp = await client.post(
        LOGIN_URL, json={"email": email, "password": "wrong-password"}
    )

    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_wrong_password_creates_no_session_and_no_cookie(
    client, seeded_admin, cur
):
    """A wrong password establishes no session (no `sessions` row) and sets no
    session cookie.
    """
    email, _, user_id = seeded_admin

    resp = await client.post(
        LOGIN_URL, json={"email": email, "password": "wrong-password"}
    )

    assert resp.status_code == 401
    assert _session_count(cur, user_id) == 0, "no session row on a failed login"
    assert not resp.headers.get_list("set-cookie"), "no cookie on a failed login"
    assert len(client.cookies) == 0, "no session cookie placed in the client jar"


@pytest.mark.asyncio
async def test_login_unknown_email_returns_401_no_session(client, cur):
    """Login for an email with no user yields 401 and creates no session for
    anyone (no admin is seeded in this test).
    """
    resp = await client.post(
        LOGIN_URL,
        json={"email": "nobody@example.test", "password": "whatever"},
    )

    assert resp.status_code == 401
    cur.execute("SELECT count(*) FROM sessions")
    (count,) = cur.fetchone()
    assert count == 0, "a login for an unknown email must not create any session"


# -- Targeted unit coverage: argon2id verify primitive (ADR-011) ---------------
# This is the one place a unit test adds coverage the integration path does not:
# it pins the hashing primitive's contract directly (a correct password
# verifies; a wrong one raises). The integration tests above exercise the same
# primitive through the login route but assert HTTP/DB outcomes, not the
# primitive's own behaviour.


def test_argon2id_verify_accepts_correct_password():
    """argon2-cffi's PasswordHasher (argon2id) verifies the correct password."""
    ph = PasswordHasher()
    digest = ph.hash(ADMIN_PASSWORD)
    assert ph.verify(digest, ADMIN_PASSWORD) is True


def test_argon2id_verify_rejects_wrong_password():
    """argon2id verification raises VerifyMismatchError for a wrong password."""
    ph = PasswordHasher()
    digest = ph.hash(ADMIN_PASSWORD)
    with pytest.raises(VerifyMismatchError):
        ph.verify(digest, "not-the-password")


def test_argon2id_hash_is_argon2id_encoding():
    """The hash produced by the configured hasher is an argon2id encoded string,
    matching what ADR-011 pins and what the admin-seed env supplies.
    """
    digest = PasswordHasher().hash(ADMIN_PASSWORD)
    assert digest.startswith("$argon2id$")
