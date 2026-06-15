"""Session-protected access and logout (ADR-011), via GET /api/v1/me.

Behaviours 3 and 4 of the four under test. The contract (ADR-011):

Behaviour 3, session-protected access, tested against the auth-owned probe
`GET /api/v1/me` (NOT any issue / view / label / epic resource endpoint, which
are API-T-001 and out of scope):
  - with a valid session cookie it returns the authenticated user;
  - with no cookie, an invalid cookie, an expired session, or a deleted
    (post-logout) session it yields HTTP 401.

Behaviour 4, logout: session teardown deletes the `sessions` row (sessions are
server-side and revocable, ADR-011). After logout the previously valid cookie no
longer authenticates: a follow-up `GET /api/v1/me` with that same cookie yields
401.

Session-id handling, per the kickoff hard rules: the cookie carries the opaque
value and `sessions.session_id` stores its hash, so these tests assert session
existence / row deletion and the authenticate vs no-longer-authenticate
behaviour, never raw-value equality with the stored column. Expiry is exercised
by ageing the live session row's `expires_at` into the past via the DB, since
the stored id is hashed and cannot be matched from the cookie.

Endpoint paths: `GET /api/v1/me` is pinned by the kickoff; logout reuses the
`/api/v1` prefix at `POST /api/v1/auth/logout` (as in test_auth_login). A path
mismatch is corrected via a fresh test-designer dispatch (ADR-016).

Red-by-construction: `app/api/` does not exist, so the app-import in conftest
fails at collection. That is the intended phase-1 state.
"""

import pytest
from argon2 import PasswordHasher

from app.api.admin_seed import seed_admin

ME_URL = "/api/v1/me"
LOGIN_URL = "/api/v1/auth/login"
LOGOUT_URL = "/api/v1/auth/logout"

ADMIN_EMAIL = "session-admin@example.test"
ADMIN_PASSWORD = "session-throwaway-password"  # throwaway test password


@pytest.fixture()
def seeded_admin(monkeypatch, cur):
    """Seed an admin with a known throwaway password (in-harness argon2id hash,
    never a real credential, ADR-006). Returns (email, password, user_id).
    """
    password_hash = PasswordHasher().hash(ADMIN_PASSWORD)
    monkeypatch.setenv("ADMIN_EMAIL", ADMIN_EMAIL)
    monkeypatch.setenv("ADMIN_PASSWORD_HASH", password_hash)
    seed_admin()
    cur.execute("SELECT id FROM users WHERE email = %s", (ADMIN_EMAIL,))
    (user_id,) = cur.fetchone()
    return ADMIN_EMAIL, ADMIN_PASSWORD, user_id


async def _login(client, email, password):
    """Log in; the issued session cookie is retained in the client's cookie jar
    for subsequent requests. Returns the login response.
    """
    resp = await client.post(LOGIN_URL, json={"email": email, "password": password})
    assert resp.status_code == 200, "fixture login should succeed"
    return resp


def _session_count(cur, user_id):
    cur.execute("SELECT count(*) FROM sessions WHERE user_id = %s", (user_id,))
    (count,) = cur.fetchone()
    return count


# -- Behaviour 3: session-protected access via GET /api/v1/me ------------------


@pytest.mark.asyncio
async def test_me_with_valid_session_returns_authenticated_user(
    client, seeded_admin
):
    """With a valid session cookie, GET /api/v1/me returns 200 and identifies
    the authenticated user (the seeded admin's email appears in the response).
    """
    email, password, _ = seeded_admin
    await _login(client, email, password)

    resp = await client.get(ME_URL)

    assert resp.status_code == 200
    body = resp.json()
    assert email in str(body), (
        "GET /api/v1/me returns the authenticated user's identity"
    )


@pytest.mark.asyncio
async def test_me_without_cookie_returns_401(client):
    """With no session cookie, GET /api/v1/me yields 401 (no admin seeded, no
    login performed).
    """
    resp = await client.get(ME_URL)
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_with_invalid_cookie_returns_401(client, seeded_admin):
    """With a bogus session cookie value (one that matches no session), GET
    /api/v1/me yields 401.
    """
    # An opaque value that no `sessions` row corresponds to.
    client.cookies.set("session", "this-is-not-a-real-session-id")

    resp = await client.get(ME_URL)

    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_with_expired_session_returns_401(client, seeded_admin, cur):
    """An expired session does not authenticate: after the live session row's
    `expires_at` is aged into the past, the same cookie yields 401 at
    GET /api/v1/me.
    """
    email, password, user_id = seeded_admin
    await _login(client, email, password)

    # Sanity: the session authenticates while unexpired.
    ok = await client.get(ME_URL)
    assert ok.status_code == 200, "session should authenticate before expiry"

    # Age the session into the past. The id is hashed at rest, so update by
    # user_id rather than by the raw cookie value (ADR-011).
    cur.execute(
        "UPDATE sessions SET expires_at = now() - interval '1 hour' "
        "WHERE user_id = %s",
        (user_id,),
    )

    resp = await client.get(ME_URL)

    assert resp.status_code == 401, "an expired session must not authenticate"


# -- Behaviour 4: logout deletes the session row; cookie stops working ---------


@pytest.mark.asyncio
async def test_logout_deletes_the_session_row(client, seeded_admin, cur):
    """Logout deletes the user's `sessions` row (server-side teardown,
    ADR-011).
    """
    email, password, user_id = seeded_admin
    await _login(client, email, password)
    assert _session_count(cur, user_id) == 1, "one session after login"

    resp = await client.post(LOGOUT_URL)

    assert resp.status_code in (200, 204)
    assert _session_count(cur, user_id) == 0, "logout deletes the session row"


@pytest.mark.asyncio
async def test_me_after_logout_with_same_cookie_returns_401(
    client, seeded_admin
):
    """After logout, the previously valid cookie no longer authenticates: a
    follow-up GET /api/v1/me with that same cookie yields 401.
    """
    email, password, _ = seeded_admin
    await _login(client, email, password)

    # The cookie authenticates before logout.
    before = await client.get(ME_URL)
    assert before.status_code == 200, "session authenticates before logout"

    await client.post(LOGOUT_URL)

    # The client jar still carries the same cookie; it must no longer work.
    after = await client.get(ME_URL)
    assert after.status_code == 401, (
        "the post-logout cookie must not authenticate"
    )
