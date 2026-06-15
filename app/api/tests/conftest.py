"""Shared fixtures for the api auth + admin-seed suite (API-T-002).

These tests are authored BLIND to the api implementation (ADR-016 TDD phase 1,
red). The `app/api/` application does not exist yet, so the app-import below
fails at collection time, by design: red-by-construction is the intended state
of this phase, not a defect to paper over. A separate phase-2 executor stands up
`app/api/` (the FastAPI app, the auth / session / admin-seed logic, the
`GET /api/v1/me` route, and the compose one-shot `test` service for the api) and
drives this suite green. That executor may not touch these test files (ADR-016
no-touch rule); they are the specification the implementation must satisfy.

Every assertion is derived from the contract, not from any implementation:
  - ADR-011: server-side sessions plus an HTTP-only, SameSite cookie; argon2id
    password hashing; the `sessions` store; session teardown is a row delete.
  - ADR-006: the admin user is seeded on first boot from an env-supplied
    argon2id password hash (ADMIN_EMAIL / ADMIN_PASSWORD_HASH), never from source.
  - ADR-012 / the 0001 baseline migration: the real `users` and `sessions`
    columns the tests assert against.
  - ADR-016: API-level / integration through the FastAPI app over a REAL
    Postgres (no DB mocking); targeted units only where they add coverage.

Harness conventions, mirroring `app/db/tests/conftest.py`:
  - DATABASE_URL is supplied via the environment (ADR-006: connection strings
    via env only). The compose `test` service for the api supplies it, exactly
    as the db suite's `test` service does. A session-scoped fixture fails the
    run with a clear message when it is unset.

Two additions the db suite does not have, both pinned by the kickoff:
  - an httpx ASGITransport client over the FastAPI app (in-process, no network
    listener), and
  - an autouse TRUNCATE-between-tests reset on `users` and `sessions`.
    Transaction-rollback isolation is rejected for this suite: these are
    API-level tests exercising the real app over the app's own DB connections,
    so a test-owned transaction would not enclose the app's commits, and
    rollback would presuppose a DB-session-override hook that does not exist in
    the red phase. TRUNCATE is implementation-agnostic, which is what this phase
    requires.

Run path is compose only (ADR-003): the api `test` one-shot is the phase-2
executor's deliverable; these tests only assume DATABASE_URL is present.
"""

import os

import psycopg2
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

# The application under test. This import is EXPECTED to fail today: `app/api/`
# does not exist yet (ADR-016 phase 1, red-by-construction). The phase-2 executor
# creates `app/api/main.py` exposing the FastAPI application as `app`. The exact
# module path is the implementer's to satisfy; if it differs, the correction is
# routed to a fresh test-designer dispatch (ADR-016), not an executor edit.
from app.api.main import app as fastapi_app

# Tables the auth suite mutates; reset between tests (pinned TRUNCATE strategy).
_MUTATED_TABLES = ("sessions", "users")


@pytest.fixture(scope="session")
def db_url():
    """The Postgres connection string, supplied via the environment (ADR-006:
    secrets / connection strings via env only). The compose `test` service for
    the api sets DATABASE_URL identically to the db suite's `test` service.

    Mirrors `app/db/tests/conftest.py`'s `db_url` fixture: one run contract
    across both suites.
    """
    url = os.environ.get("DATABASE_URL")
    if not url:
        pytest.fail(
            "DATABASE_URL is not set; the compose `test` service must provide it"
        )
    return url


@pytest.fixture()
def conn(db_url):
    """A psycopg2 connection for tests that inspect or seed the database
    directly (autocommit on, so test-side writes and reads are immediately
    visible to the app, which uses its own connections). Closed at end of test.
    """
    connection = psycopg2.connect(db_url)
    connection.autocommit = True
    try:
        yield connection
    finally:
        connection.close()


@pytest.fixture()
def cur(conn):
    """A cursor over the per-test connection."""
    cursor = conn.cursor()
    try:
        yield cursor
    finally:
        cursor.close()


@pytest.fixture(autouse=True)
def reset_auth_tables(db_url):
    """Autouse TRUNCATE-between-tests reset (pinned isolation strategy).

    After each test, TRUNCATE the tables the auth tests mutate (`users` and
    `sessions`), restoring a clean slate. CASCADE covers the `sessions ->
    users` FK; RESTART IDENTITY resets the bigserial counters so id-based
    assertions do not drift across tests. Tests and fixtures re-establish any
    baseline they need (for example a seeded admin) explicitly; nothing relies
    on residue from a prior test.

    Transaction-rollback isolation is REJECTED for this suite (see module
    docstring): TRUNCATE is implementation-agnostic, which is the property the
    red phase requires.
    """
    yield
    connection = psycopg2.connect(db_url)
    connection.autocommit = True
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "TRUNCATE TABLE {} RESTART IDENTITY CASCADE".format(
                    ", ".join(_MUTATED_TABLES)
                )
            )
    finally:
        connection.close()


@pytest_asyncio.fixture()
async def client():
    """An httpx client bound to the FastAPI app via ASGITransport (in-process,
    no network listener), per ADR-016. New to the api conftest: the db suite has
    no application. The app is imported above (the import that fails today, by
    design). Each test gets a fresh client so cookie jars do not leak across
    tests.
    """
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac
