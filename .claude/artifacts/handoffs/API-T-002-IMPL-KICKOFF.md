# API-T-002 - Auth, sessions, and admin-user bootstrap for the FastAPI api service (IMPLEMENTATION phase: stand up the api service and drive the phase-1 tests green)

## Target

This is **web-app** work (ADR-005), in the backend-api department. It is **TDD phase 2 (green)** per `./ai-infrastructure/project-manager/decisions/ADR-016-testing-strategy-test-designer-agent.md`. The four failing pytest files already exist under `./app/api/tests/` (authored in phase 1, committed at `20bb782`). Your job is to stand up the FastAPI `api` service under `./app/api/` so that suite passes green, and to add the two compose services that run it. You do not author tests; you make the existing tests pass.

The artifact in scope is the `api` service: the FastAPI app, the admin-seed entry point, the auth/session logic, the psycopg2 data access, the env settings, the requirements files, the Dockerfiles, and the two new compose services. The schema is already migrated (the `migrate` one-shot applied `./app/db/alembic/versions/0001_baseline_schema.py`); you connect to the already-migrated database, you do not touch it.

## Decisions resolved by the Orchestrator

Every decision below is pinned. Do not re-open any of them; do not weigh alternatives. Where a tradeoff was already settled (raw psycopg2 over an ORM, server-side sessions over JWT), the rationale is stated for context only, not for you to revisit.

- **This is phase 2 (green); the tests are the specification.** The four failing files under `./app/api/tests/` were authored blind to the implementation (phase 1, red). You MAY read them to learn the contract you must satisfy; you MUST NOT create, edit, or delete any file under `./app/api/tests/` (ADR-016 no-touch rule). If you become convinced a test itself is wrong, do NOT edit it: return `RETURN: ESCALATION` and the Orchestrator routes the correction to a fresh `test-designer` dispatch. Editing a test to make it pass inverts the TDD cycle. The four protected files are: `./app/api/tests/conftest.py`, `./app/api/tests/test_admin_seed.py`, `./app/api/tests/test_auth_login.py`, `./app/api/tests/test_sessions.py`.

- **Data layer: raw SQL via psycopg2-binary (sync), no ORM.** This matches the only DB library in the repo (`./app/db/requirements.txt` pins `psycopg2-binary==2.9.10`) and ADR-014's no-ORM stance (cited by number, no read required; the rationale is the no-ORM, hand-written-SQL posture). Do NOT introduce SQLAlchemy ORM, asyncpg, or psycopg3. This is settled, not a tradeoff to weigh.

- **Route handlers are sync `def`.** FastAPI runs sync handlers in its threadpool, so synchronous psycopg2 calls inside a `def` handler do not block the event loop. The phase-1 async httpx `ASGITransport` test client (`./app/api/tests/conftest.py:131-141`) works against sync handlers unchanged. Do not convert the data layer to async to "match" the async test client.

- **Import surface the tests require (must match exactly).** The tests import these two symbols; provide them at exactly these paths or the suite fails at collection:
  - `app.api.main:app` - the FastAPI application instance, named `app`, in `./app/api/main.py`. Imported by `./app/api/tests/conftest.py:55` as `from app.api.main import app as fastapi_app`.
  - `app.api.admin_seed.seed_admin` - a directly-callable function `seed_admin()` in `./app/api/admin_seed.py`. Imported by all three test modules as `from app.api.admin_seed import seed_admin`.
  - Provide an `./app/api/__init__.py` (and rely on the existing `./app/api/tests/` directory) so `import app.api...` resolves under pytest. The package root is the repo `./app/` directory on `sys.path` inside the test image (mirror how the db image is structured; see References).

- **Endpoints (exact paths; all under the ADR-010 `/api/v1` prefix).** The tests call exactly these:
  - `POST /api/v1/auth/login` (`./app/api/tests/test_auth_login.py:36`, `LOGIN_URL`).
  - `POST /api/v1/auth/logout` (`./app/api/tests/test_sessions.py:39`, `LOGOUT_URL`).
  - `GET /api/v1/me` (`./app/api/tests/test_sessions.py:37`, `ME_URL`).

- **Session cookie name is `session`.** `./app/api/tests/test_sessions.py:111` sets `client.cookies.set("session", "this-is-not-a-real-session-id")` and expects that bogus value to be treated as the (invalid) session cookie and yield 401. The cookie your login sets and your `GET /api/v1/me` reads MUST be named `session`. The cookie name is also a configurable setting (see CONFIG below), but its default and the value the tests exercise is `session`.

- **Admin bootstrap contract (`seed_admin`).** `seed_admin()` reads `ADMIN_EMAIL` and `ADMIN_PASSWORD_HASH` from the environment and idempotently seeds the admin as a `users` row with:
  - `kind = 'human'`,
  - `email` from `ADMIN_EMAIL`,
  - `password_hash` set to the value of `ADMIN_PASSWORD_HASH` **verbatim** (the env var already holds an argon2id encoding; `seed_admin` stores it as-is and does NOT re-hash it). `./app/api/tests/test_admin_seed.py:84` asserts `seeded_password_hash == password_hash` (the exact env value), and `:100` asserts it starts with `$argon2id$`.
  - `display_name` set to a sensible admin display name (the real `users` table has `display_name TEXT NOT NULL` at `./app/db/alembic/versions/0001_baseline_schema.py:41`; the tests assert no specific value, but the column is NOT NULL so the seed MUST populate it).
  - Idempotent: re-running `seed_admin()` does not create a second `users` row for that email and does not change the existing row's `id` (`./app/api/tests/test_admin_seed.py:105-137`). Seed if and only if the admin row is absent.
  - Run `seed_admin()` at app startup via a FastAPI lifespan handler AND keep it directly callable (the tests call it directly; the running app calls it on boot).

- **Login behaviour.** `POST /api/v1/auth/login` takes a JSON body `{"email": <str>, "password": <str>}`. On a correct password (verified with argon2id via argon2-cffi against the stored `password_hash`): return HTTP 200, create exactly one `sessions` row for that user, and set the `session` cookie (HTTP-only, with a SameSite attribute) on the response. On a wrong password OR an unknown email: return HTTP 401, create no `sessions` row, and set no cookie. Verified by `./app/api/tests/test_auth_login.py` (success: `:64-107`; wrong password: `:111-138`; unknown email: `:142-154`).

- **`GET /api/v1/me` behaviour.** With a valid (unexpired, not-logged-out) `session` cookie: return HTTP 200 with a body in which the authenticated user's email is discoverable (`./app/api/tests/test_sessions.py:91` asserts `email in str(body)`; any JSON shape containing the email satisfies this). With an absent, invalid, expired, or post-logout cookie: return HTTP 401 (`:97-141`, `:162-182`).

- **Logout behaviour.** `POST /api/v1/auth/logout` deletes the caller's `sessions` row and returns HTTP 200 or 204 (`./app/api/tests/test_sessions.py:158` accepts either). After logout, the same cookie no longer authenticates: a follow-up `GET /api/v1/me` with it yields 401 (`:162-182`).

- **Session storage (ADR-011): `sessions.session_id` is hashed at rest.** Per `./ai-infrastructure/project-manager/decisions/ADR-011-auth-session-mechanism.md`, sessions are server-side and revocable; the opaque session identifier in the cookie is stored HASHED in `sessions.session_id`, never in plaintext. Generate a high-entropy opaque id for the cookie; store its hash in `sessions.session_id`; on each request, hash the incoming cookie value and look the row up by the hash. The tests cannot match the row from the raw cookie (by design): the expired-session test ages `expires_at` keyed on `user_id`, not on the cookie (`./app/api/tests/test_sessions.py:133-137`). An expired session (`expires_at` in the past) must not authenticate. The `sessions` columns you write are exactly: `session_id` (text, the hash), `user_id` (bigint FK), `expires_at` (timestamptz, not null), `created_at` (timestamptz, not null) per `./app/db/alembic/versions/0001_baseline_schema.py:202-210`.

- **Password hashing/verification: argon2id via argon2-cffi.** Use `argon2-cffi`'s `PasswordHasher` (which defaults to argon2id, the algorithm ADR-011 pins) to verify a submitted password against the stored `password_hash`. The admin seed stores the env-supplied hash verbatim; login verifies against it.

- **Config: env-based via a small settings module reading `os.environ`.** No heavy config framework; mirror the db department's minimal approach. The settings the app reads:
  - `DATABASE_URL` - the Postgres connection string (the same value the `migrate` and `test` services use; see `./app/docker-compose.yml`).
  - `ADMIN_EMAIL`, `ADMIN_PASSWORD_HASH` - the admin bootstrap credentials, supplied via the gitignored `.env` (ADR-006). `ADMIN_PASSWORD_HASH` is an argon2id hash; never a plaintext password.
  - Session cookie settings: the cookie name (default `session`), the session lifetime (used to compute `expires_at`), and a Secure-flag toggle that may be OFF for local HTTP dev (ADR-011 relaxes Secure for local HTTP; the ASGI test transport is not HTTPS, and `./app/api/tests/test_auth_login.py:78-92` deliberately does NOT assert the Secure flag).
  - **No real secret or password hash goes into any tracked file** (repo `./CLAUDE.md` secrets rule + ADR-006). A committed `./app/api/.env.example` may document the variable NAMES only, with no values.

- **Dependencies (pinned; mirror the db department's split).** Create:
  - `./app/api/requirements.txt`: `fastapi`, `uvicorn[standard]`, `psycopg2-binary==2.9.10`, `argon2-cffi`.
  - `./app/api/requirements-test.txt`: `pytest`, `httpx`, `psycopg2-binary==2.9.10`, `argon2-cffi`.
  - The test image must also satisfy the test imports `pytest_asyncio`, `httpx.ASGITransport`, and `argon2` (`./app/api/tests/conftest.py:45-48`, `./app/api/tests/test_admin_seed.py:29`). Include the packages those imports require in `requirements-test.txt` (httpx and argon2-cffi are listed above; add `pytest-asyncio` so the `@pytest.mark.asyncio` tests run and the `pytest_asyncio.fixture` resolves). Keep `psycopg2-binary` pinned to `2.9.10` for repo consistency.

- **Compose (mirror the db department's one-shot pattern).** In `./app/docker-compose.yml`, ADD exactly two services and change nothing else:
  - A runtime `api` service: built from `./app/api` (a `Dockerfile` you create), running uvicorn serving `app.api.main:app`; environment carries `DATABASE_URL` plus the admin-seed env vars (`ADMIN_EMAIL`, `ADMIN_PASSWORD_HASH`); `depends_on` `postgres` (`condition: service_healthy`) and `migrate` (`condition: service_completed_successfully`).
  - An `api-test` one-shot service: built from `./app/api` (a `Dockerfile.test` you create, mirroring `./app/db/Dockerfile.test`); environment carries `DATABASE_URL`; `depends_on` `postgres` (`condition: service_healthy`) and `migrate` (`condition: service_completed_successfully`); its command runs `pytest` over `./app/api/tests/`. Match how the existing `test` service sets `DATABASE_URL` (`postgresql://corral:devpassword@postgres:5432/corral`, per `./app/docker-compose.yml:25-33`).
  - Do NOT alter the existing `postgres`, `migrate`, `test`, or `test-roundtrip` services except to add the two new ones. The schema is already migrated by the `migrate` one-shot; the `api` services depend on it.

- **Build context and module-path note.** The existing db services build from `./app/db` (context `./db`) and the test image copies `tests/` into the image (`./app/db/Dockerfile.test:11`). Your `api` build context is `./app/api`. Because the tests import `app.api.main` and `app.api.admin_seed`, the package path `app/api/` must be importable from the test image's working directory. Mirror the db Dockerfile pattern (install requirements, COPY source), and structure the build so `import app.api.*` resolves (for example, set the image working directory and `PYTHONPATH` so the `app` package root is on `sys.path`, or lay the copied files out under an `app/api/` path inside the image). The acceptance gate is the suite passing under `docker compose run --rm api-test`; structure the image so that command collects and runs the tests with the imports resolving.

- **Schema and migrations are OUT of scope.** The full v1 schema is already migrated (`./app/db/alembic/versions/0001_baseline_schema.py`); the `api` connects to the already-migrated DB. Do NOT add or edit migrations, and do NOT touch `./app/db/**`. Carry-forward finding from phase 1: the real `users` table has `display_name TEXT NOT NULL`, so `seed_admin()` MUST set `display_name` (the phase-1 report flags this at `./.claude/artifacts/handoffs/API-T-002-TEST-DESIGN-KICKOFF-REPORT.md:25`).

## Deliverables

- The FastAPI `api` service under `./app/api/`:
  - `./app/api/main.py` exposing the FastAPI instance as `app`, mounting the three routes under `/api/v1`, and seeding the admin on startup via a lifespan handler.
  - `./app/api/admin_seed.py` exposing a directly-callable `seed_admin()`.
  - `./app/api/__init__.py` so `app.api` is an importable package.
  - The auth/session logic, the psycopg2 db-connection access, and the env settings module, structured into whatever additional modules you choose under `./app/api/` (module breakdown is your discretion EXCEPT the two pinned import paths above).
- `./app/api/requirements.txt` and `./app/api/requirements-test.txt`.
- `./app/api/Dockerfile` and `./app/api/Dockerfile.test` (mirroring `./app/db/Dockerfile` and `./app/db/Dockerfile.test`).
- The `api` and `api-test` services added to `./app/docker-compose.yml` (those two services only).
- Optionally `./app/api/.env.example` documenting the env variable NAMES only (no values).

The completion condition: the four protected phase-1 test files pass green via the compose one-shot, with those test files unmodified.

## Files in scope

You create or edit these. The module breakdown within `./app/api/` is your discretion EXCEPT the two pinned import paths (`app.api.main:app`, `app.api.admin_seed.seed_admin`).

- `./app/api/main.py` (new; exposes `app`).
- `./app/api/admin_seed.py` (new; exposes `seed_admin`).
- `./app/api/__init__.py` (new; makes `./app/api/` an importable package).
- Additional auth / session / db-connection / settings modules under `./app/api/` (new; names and layout your discretion).
- `./app/api/requirements.txt`, `./app/api/requirements-test.txt` (new).
- `./app/api/Dockerfile`, `./app/api/Dockerfile.test` (new; mirror `./app/db/Dockerfile`, `./app/db/Dockerfile.test`).
- `./app/docker-compose.yml` (edit: ADD the `api` and `api-test` services only).
- `./app/api/.env.example` (optional; new; variable NAMES only).

## Files out of scope

Do NOT create, edit, or delete any of these.

- `./app/api/tests/conftest.py`
- `./app/api/tests/test_admin_seed.py`
- `./app/api/tests/test_auth_login.py`
- `./app/api/tests/test_sessions.py`

  These four are the protected phase-1 test files. They are read-only for you: read them to learn the contract, but modifying or adding any test file is forbidden (ADR-016; the close checker enforces this against your diff). If you believe a test is wrong, `RETURN: ESCALATION`; do not edit it.

- `./app/db/**` - the database department's schema, migrations, and db tests. Reference-only: mirror the Dockerfile and compose patterns, but do not modify anything under `./app/db/`.
- The existing `postgres`, `migrate`, `test`, and `test-roundtrip` services in `./app/docker-compose.yml` (you add two services; you do not change these four).
- Any ADR, any task file, any other workspace file.

## References

Read these in this order; they layer the contract from most-binding (the tests) outward to rationale.

- `./.claude/artifacts/handoffs/API-T-002-TEST-DESIGN-KICKOFF-REPORT.md` - the phase-1 report; its "What the phase-2 executor must satisfy" section (`:48`) enumerates the contract and lists the import paths, endpoints, and the `display_name` finding (`:25`).
- `./app/api/tests/conftest.py` - the shared fixtures: the `app.api.main:app` import (`:55`), the env-`DATABASE_URL` `db_url` fixture, the autouse TRUNCATE reset on `users`/`sessions`, and the httpx `ASGITransport` `client` fixture.
- `./app/api/tests/test_admin_seed.py` - behaviour 1: `seed_admin()` from env, idempotent, `kind='human'`, `password_hash` stored verbatim, argon2id-encoded.
- `./app/api/tests/test_auth_login.py` - behaviour 2: login success creates one session row and sets an HTTP-only SameSite cookie; wrong password / unknown email yield 401 with no session and no cookie; plus the argon2id-verify unit tests.
- `./app/api/tests/test_sessions.py` - behaviours 3 and 4: `GET /api/v1/me` with a valid cookie returns the user; absent / invalid / expired / post-logout cookie yields 401; logout deletes the `sessions` row. Note the cookie name `session` (`:111`) and the expiry-by-`user_id` ageing (`:133-137`).
- `./ai-infrastructure/project-manager/decisions/ADR-011-auth-session-mechanism.md` - auth/session mechanism: argon2id password hashing, server-side sessions, the hashed-at-rest session id, the Secure-flag relaxation for local HTTP dev.
- `./ai-infrastructure/project-manager/decisions/ADR-006-admin-bootstrap-env-hash.md` - admin seeded on first boot from the env-supplied hash; secrets via gitignored `.env` only; a committed `.env.example` documents names only.
- `./ai-infrastructure/project-manager/decisions/ADR-012-issue-label-view-schema.md` - the schema context and the `issues.assignee_id` -> `users.id` FK seam between the core schema and the auth identity.
- `./ai-infrastructure/project-manager/decisions/ADR-016-testing-strategy-test-designer-agent.md` - the TDD two-phase flow and the no-touch rule on test files.
- `./ai-infrastructure/project-manager/decisions/ADR-003-docker-compose-runtime.md` - compose is the only supported run path; do not assume host-installed Python.
- `./app/db/alembic/versions/0001_baseline_schema.py` - the real `users` (`:38-49`, note `display_name` NOT NULL at `:41`) and `sessions` (`:202-210`) DDL the app reads and writes.
- `./app/db/tests/conftest.py` - the env-`DATABASE_URL` convention the api conftest mirrors.
- `./app/db/Dockerfile` - the runtime image pattern to mirror for `./app/api/Dockerfile`.
- `./app/db/Dockerfile.test` - the test image pattern (install requirements-test, COPY `tests/`, CMD pytest) to mirror for `./app/api/Dockerfile.test`.
- `./app/db/requirements.txt`, `./app/db/requirements-test.txt` - the dependency-split pattern (and the `psycopg2-binary==2.9.10` pin) to mirror.
- `./app/docker-compose.yml` - the compose topology to extend with `api` and `api-test`; note the existing `test` service's `DATABASE_URL` (`:25-33`) and the `migrate` `service_completed_successfully` dependency pattern (`:44-45`).
- `./ai-infrastructure/project-manager/docs/architecture/OVERVIEW.md` - the target runtime shape: the `api` service serves the client, enforces auth (ADR-011), and seeds the admin on first boot (ADR-006).

ADR-014 (no ORM, hand-written migrations) and ADR-002 (FastAPI + Postgres stack) are the rationale for the pinned raw-psycopg2 data layer; they are cited by number and need no read.

## Related tasks and ADRs

- API-T-002 - this task; the phase-1 test-design dispatch is committed at `20bb782`. This kickoff is its phase-2 implementation.
- API-T-001 - the resource endpoints (issues / labels / views / epics) built ONTO this service skeleton; it depends on this task standing up the `api` service.
- API-E-001 - the owning epic (Phase 2).
- ADR-011 - the auth and session mechanism this implementation realizes.
- ADR-006 - the admin-bootstrap-from-env-hash contract `seed_admin` realizes.
- ADR-016 - the TDD two-phase flow and the test-file no-touch rule that governs this dispatch.
- ADR-026 - the per-agent MCP machine-user identity; the Phase-3 agent-auth boundary, out of scope here (this task is human-admin auth only).

## Hard rules

- **No-touch on test files.** Do not create, edit, or delete any file under `./app/api/tests/`. The close checker fails your close if any protected test path appears in your diff (ADR-016, rule W3). If a test seems wrong, `RETURN: ESCALATION`; do not edit it.
- **Stand up real behaviour, not stubs.** The tests run against a real Postgres over the app's own connections. Do not mock the DB, stub the routes, or hard-code responses to make assertions pass; the seed must really insert a row, login must really create a `sessions` row, logout must really delete it.
- **No secrets in tracked files.** No real password hash, no real credential, no `.env` contents in any file you create or edit. `./app/api/.env.example` (if you add it) documents variable NAMES only.
- **Do not touch the migrated schema or `./app/db/`.** You connect to the already-migrated database; you mirror the db department's Dockerfile/compose patterns by reading them, but you change nothing under `./app/db/`.
- **Acceptance gate (single).** All four files under `./app/api/tests/` pass GREEN via the compose one-shot, run as `docker compose -f app/docker-compose.yml run --rm api-test`, with those test files UNMODIFIED. Verify the test files are unchanged against git (`git diff -- app/api/tests/` shows no changes) before reporting completion. The run path is compose-only (ADR-003); do not assume a host-installed Python interpreter.

## Executor pointer

The executor is the dispatched `executor` (ADR-028). Universal executor conventions (the six-section report shape, the stage-don't-commit rule, the compose-only run policy, the repo writing rules, Agent Discipline, and the test-file no-touch rule) live in `./docs/ai-orchestration/roles/EXECUTOR-ROLE.md`; this kickoff does not restate them. The closing report is written to `./.claude/artifacts/handoffs/API-T-002-IMPL-KICKOFF-REPORT.md` per EXECUTOR-ROLE.md, section "Report shape" (dual-channel: print to chat and write to that file).
