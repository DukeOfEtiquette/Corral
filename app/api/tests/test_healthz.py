"""Failing test for the api GET /healthz liveness route (API-T-004, TDD phase 1, red).

Authored against the pinned contract, NOT against any implementation (ADR-016
two-phase TDD; this file is the specification the phase-2 executor satisfies, and
under the ADR-016 no-touch rule that executor may not edit it).

Pinned contract (from the API-T-004 test-design kickoff):
  - GET /healthz returns HTTP 200.
  - The JSON body is EXACTLY {"status": "ok"}.
  - The route requires NO authentication: 200 is returned with no session cookie
    present. "Unauthenticated liveness" is a load-bearing property of a probe
    target (the future docker-compose healthcheck, a phase-2 deliverable).
  - The route performs NO database access (pure process-liveness). The autouse
    `reset_auth_tables` TRUNCATE in conftest still runs, and the session-scoped
    `db_url` fixture still requires DATABASE_URL (supplied by the `api-test`
    compose service, ADR-003), even though /healthz itself touches no DB.

Top-level placement is pinned (ADR-010): /api/v1 is scoped to the API contract
surface; /healthz is an infrastructure liveness probe target, so it sits at the
ROOT, never under /api/v1. The assertions below hit "/healthz" only.

Red-by-construction: the FastAPI app already exists (app/api/main.py from
API-T-002), so the suite collects cleanly. These tests are RED because the
/healthz route does not exist yet and currently returns 404, so the status and
body assertions fail. Redness does NOT depend on a collection-time or import
error; the app import succeeds.

Run path is compose-only (ADR-003): these tests run under the existing
`api-test` one-shot service. The test designer runs nothing.
"""

import pytest

# The exact, pinned liveness body. /healthz returns this and nothing else.
_EXPECTED_BODY = {"status": "ok"}


@pytest.mark.asyncio
async def test_healthz_returns_200_and_ok_body(client):
    """GET /healthz returns HTTP 200 with the body exactly {"status": "ok"}.

    These are the two pinned minimum assertions: the status code and the exact
    JSON body. The route does not exist yet, so the response is 404 today and
    both assertions fail (red).
    """
    resp = await client.get("/healthz")

    assert resp.status_code == 200
    assert resp.json() == _EXPECTED_BODY


@pytest.mark.asyncio
async def test_healthz_is_unauthenticated(client):
    """GET /healthz returns 200 with NO session cookie present.

    Locks the unauthenticated-liveness contract: a healthcheck probe target must
    answer without a session. The `client` fixture yields a fresh httpx
    AsyncClient with an empty cookie jar each test, so this request carries no
    session cookie. The route is reachable and returns 200 regardless of auth
    state; it must never gate on a session.
    """
    # Sanity: the request carries no cookies (no prior login on this client).
    assert not client.cookies

    resp = await client.get("/healthz")

    assert resp.status_code == 200
    assert resp.json() == _EXPECTED_BODY


@pytest.mark.asyncio
async def test_healthz_is_top_level_not_under_api_v1(client):
    """/healthz lives at the ROOT, not under the /api/v1 prefix (ADR-010).

    The liveness probe target is deliberately top-level: /api/v1 is scoped to the
    API contract surface, while /healthz is an infrastructure probe. The pinned
    top-level route answers 200; the /api/v1/healthz path is NOT part of the
    contract and must not exist. This guards against an implementer accidentally
    mounting the route under the API prefix.
    """
    top_level = await client.get("/healthz")
    assert top_level.status_code == 200
    assert top_level.json() == _EXPECTED_BODY

    under_prefix = await client.get("/api/v1/healthz")
    assert under_prefix.status_code == 404
