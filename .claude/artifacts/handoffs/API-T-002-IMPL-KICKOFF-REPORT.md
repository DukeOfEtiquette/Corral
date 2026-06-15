# API-T-002 Implementation report (TDD phase 2, green)

## Deliverables completed

All deliverables listed in the kickoff are shipped. The four protected test files
pass green (19/19) via `docker compose -f app/docker-compose.yml run --rm api-test`.

- `./app/api/__init__.py` (new): makes `app.api` an importable package.
- `./app/api/settings.py` (new): minimal env-based config; reads DATABASE_URL,
  ADMIN_EMAIL, ADMIN_PASSWORD_HASH, SESSION_COOKIE_NAME, SESSION_LIFETIME_SECONDS,
  SESSION_COOKIE_SECURE from os.environ at call time (monkeypatch-compatible).
- `./app/api/db.py` (new): psycopg2 connection helper (`get_conn()`); no ORM.
- `./app/api/admin_seed.py` (new): exposes `seed_admin()` at the pinned path
  `app.api.admin_seed.seed_admin`; idempotent seed from ADMIN_EMAIL /
  ADMIN_PASSWORD_HASH, verbatim hash storage, display_name set to "Admin",
  kind='human'.
- `./app/api/auth.py` (new): argon2id password verification via argon2-cffi;
  session create/lookup/delete with SHA-256 hashing of the opaque token for
  at-rest storage; get_user_by_email helper.
- `./app/api/main.py` (new): FastAPI instance `app` at the pinned path
  `app.api.main:app`; lifespan handler calls seed_admin() on startup;
  POST /api/v1/auth/login, POST /api/v1/auth/logout, GET /api/v1/me routes.
- `./app/api/requirements.txt` (new): fastapi, uvicorn[standard],
  psycopg2-binary==2.9.10, argon2-cffi.
- `./app/api/requirements-test.txt` (new): pytest, httpx, psycopg2-binary==2.9.10,
  argon2-cffi, pytest-asyncio, anyio[trio].
- `./app/api/Dockerfile` (new): builds from python:3.12-slim; copies source into
  /app/app/api/; sets PYTHONPATH=/app; runs uvicorn.
- `./app/api/Dockerfile.test` (new): installs both requirements.txt and
  requirements-test.txt (app code imports fastapi at collection time); copies
  source into /app/app/api/; sets PYTHONPATH=/app; runs pytest over app/api/tests/.
- `./app/docker-compose.yml` (edited): added `api` and `api-test` services;
  existing services unchanged.
- `./app/api/.env.example` (new, optional): documents variable NAMES only, no values.

## Decisions made

- **Test image installs both requirements.txt and requirements-test.txt.** The
  conftest.py imports `from app.api.main import app as fastapi_app` at collection
  time, which pulls in fastapi. A test-only requirements file would fail at
  collection. Decision: Dockerfile.test installs both files, keeping runtime and
  test deps split by file but co-installed in the test image.

- **Session id hashing: SHA-256 (not argon2id).** ADR-011 requires the opaque
  session token to be stored hashed at rest; it does not pin the hash algorithm
  for the session id (only for passwords). SHA-256 is appropriate here because
  the raw token is a 32-byte CSPRNG value (secrets.token_hex(32)); the hash
  serves as an index key, not a password KDF. argon2id is reserved for password
  hashing as ADR-011 pins.

- **Module layout: settings.py, db.py, auth.py alongside main.py and admin_seed.py.**
  The kickoff leaves internal module breakdown to executor discretion. Three
  supporting modules (settings, db, auth) keep concerns separated without
  over-engineering.

- **SameSite value: "lax".** The tests assert `samesite` appears in the cookie
  header but do not pin the value. "lax" is the standard default for same-origin
  web apps, consistent with ADR-011.

- **api service ports: 8000:8000.** The kickoff does not specify a host port for
  the runtime service. 8000 is the uvicorn default and matches OVERVIEW.md.

## Surprises

- **Dockerfile.test requires runtime deps.** The first build attempt failed with
  `ModuleNotFoundError: No module named 'fastapi'` because the test image only
  had requirements-test.txt installed. The conftest.py imports the FastAPI app
  at module load time (collection), so the runtime packages must be present in
  the test image. Resolved by installing both requirements files in Dockerfile.test.
  Not a test defect; the correct fix is in the Dockerfile.

- **pytest-asyncio 1.4.0 strict mode is the default.** The installed version
  (1.4.0) defaults to STRICT mode, which requires `@pytest.mark.asyncio` on each
  async test (the test files already carry those marks) and does not require a
  pytest.ini asyncio_mode setting. All 19 tests collected and ran without
  configuration changes.

## Follow-ups

- The `api` runtime service in docker-compose.yml exposes port 8000 on the host.
  A future task (COR-T candidate) may want to add a healthcheck for the `api`
  service mirroring the postgres healthcheck pattern, so downstream services can
  depend on `api: service_healthy`. Out of scope for this task.

- The `reset_auth_tables` autouse fixture in conftest.py runs TRUNCATE after each
  test (yield-then-cleanup). If the lifespan seed_admin() call fires on each
  test-client creation (which it does via ASGITransport), the admin is re-seeded
  each test. This is the intended behaviour (seed_admin is idempotent), but a
  future COR-T candidate could explore a session-scoped app fixture to avoid
  repeated lifespan calls in tests, if startup cost becomes significant.

## Files touched

- `/home/adam/src/corral/app/api/__init__.py` (new)
- `/home/adam/src/corral/app/api/settings.py` (new)
- `/home/adam/src/corral/app/api/db.py` (new)
- `/home/adam/src/corral/app/api/admin_seed.py` (new)
- `/home/adam/src/corral/app/api/auth.py` (new)
- `/home/adam/src/corral/app/api/main.py` (new)
- `/home/adam/src/corral/app/api/requirements.txt` (new)
- `/home/adam/src/corral/app/api/requirements-test.txt` (new)
- `/home/adam/src/corral/app/api/Dockerfile` (new)
- `/home/adam/src/corral/app/api/Dockerfile.test` (new)
- `/home/adam/src/corral/app/api/.env.example` (new)
- `/home/adam/src/corral/app/docker-compose.yml` (edited: api and api-test services added)
- `/home/adam/src/corral/.claude/artifacts/handoffs/API-T-002-IMPL-KICKOFF-REPORT.md` (this report)

Test files confirmed unchanged: `git diff -- app/api/tests/` returns no output.

## Build / verification status

- **GREEN: 19/19 tests pass** via `docker compose -f app/docker-compose.yml run --rm api-test`.
- All four test files under `./app/api/tests/` pass: test_admin_seed.py (4 tests),
  test_auth_login.py (9 tests: 6 integration + 3 unit), test_sessions.py (6 tests).
- Test files confirmed unmodified from git before and after execution.
- No em dashes in any file created or edited (scanned before run).
- Compose-only run path used throughout; no host-installed Python assumed (ADR-003).
- The `api` runtime service and Dockerfile are created but not separately verified
  (uvicorn startup); the acceptance gate is the api-test one-shot, which passed.
