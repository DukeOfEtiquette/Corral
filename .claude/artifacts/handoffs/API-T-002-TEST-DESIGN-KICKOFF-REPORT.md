# API-T-002 Test-Design report (TDD phase 1, red)

## Deliverables completed

All four in-scope test files authored under `./app/api/tests/`, covering the four behaviours the kickoff pins. The suite is red-by-construction (the `app/api/` application does not exist yet), which is the intended phase-1 outcome.

- `./app/api/tests/conftest.py` (shipped): the shared fixtures.
  - `db_url` session fixture reading `os.environ.get("DATABASE_URL")` and failing the run with a clear message when unset, mirroring `./app/db/tests/conftest.py:19-30`.
  - `client` httpx `ASGITransport` async fixture over the FastAPI app (the addition the db suite lacks), importing the app object from `./app/api/` (the import that fails today, by design): `conftest.py:62` (`from app.api.main import app as fastapi_app`).
  - `reset_auth_tables` autouse fixture: the pinned TRUNCATE-between-tests reset on `users` and `sessions` (`TRUNCATE ... RESTART IDENTITY CASCADE`); transaction-rollback isolation is not used.
- `./app/api/tests/test_admin_seed.py` (shipped): behaviour 1. Admin seeded from the env-supplied argon2id hash as a `users` row with `kind='human'`, `email` and `password_hash` set; password_hash is an argon2id encoding, not plaintext; reseeding is idempotent (count stays at one; the existing row id is unchanged).
- `./app/api/tests/test_auth_login.py` (shipped): behaviour 2. Login success verifies with argon2id, creates one `sessions` row, and sets an HTTP-only SameSite cookie; wrong password and unknown email each yield 401 with no session and no cookie. Includes the targeted argon2id-verify unit coverage (correct verifies, wrong raises `VerifyMismatchError`, hash is `$argon2id$`-encoded).
- `./app/api/tests/test_sessions.py` (shipped): behaviours 3 and 4. `GET /api/v1/me` returns the authenticated user with a valid cookie; absent / invalid / expired / post-logout cookie each yields 401; logout deletes the `sessions` row and the same cookie no longer authenticates.

## Decisions made

- **Login / logout endpoint paths: `POST /api/v1/auth/login` and `POST /api/v1/auth/logout`.** The kickoff pins only `GET /api/v1/me` (behaviour 3) by exact path; login and logout paths were not spelled out. I reused the pinned `/api/v1` prefix and a conventional `auth/` segment. Rationale: this is a path-naming choice within an already-pinned prefix, not an out-of-scope contract decision; ADR-016's sanctioned channel means a mismatch with the phase-2 implementation is corrected by a fresh test-designer dispatch, not an executor edit. Recorded in each file's module docstring so the implementer sees the expected paths.
- **App import shape: `from app.api.main import app as fastapi_app` and `from app.api.admin_seed import seed_admin`.** The kickoff says the conftest imports the app object from `app/api/` and that the seed runs "on first boot"; it does not pin module paths. I chose `app.api.main:app` (FastAPI convention) and a directly-callable `app.api.admin_seed.seed_admin()` so the seed can be exercised in tests without standing up a full app lifespan. Rationale: same as above; the exact path is the implementer's to satisfy, correctable via re-dispatch.
- **`GET /api/v1/me` success assertion: the authenticated user's email appears in the response body (`assert email in str(body)`).** The kickoff says the probe "returns the authenticated user" but does not pin the response schema. I asserted the identity is discoverable (email present) rather than pinning an exact JSON shape, keeping the test contract-faithful without over-constraining the implementation.
- **Expired-session test ages `expires_at` via the DB by `user_id`.** Because `sessions.session_id` is stored hashed at rest (ADR-011), the test cannot match the row from the raw cookie; it updates `expires_at` to the past keyed on `user_id`, then asserts the same cookie yields 401. This honours the "do not assert raw cookie equals stored session_id" hard rule.
- **`conn`/`cur` fixtures use `autocommit = True` (the db suite uses rollback).** The db suite's `conn` rolls back because its tests are read-only against the catalog; this suite seeds and inspects rows that the app must see over its own connections, so test-side writes must commit and the app's commits must be visible to the test. The db suite's rollback-`conn` would defeat both. Between-test cleanup is the pinned autouse TRUNCATE, not the connection lifecycle.

## Surprises

- The kickoff's `users` column list omits `display_name`, but the real 0001 baseline DDL has `display_name text NOT NULL` (`./app/db/alembic/versions/0001_baseline_schema.py:41`). The seed must therefore set `display_name` for the admin row to satisfy the NOT NULL constraint. The tests do not assert a specific `display_name` value (the kickoff does not pin one), so they neither over-constrain nor conflict with this; flagged here so the phase-2 executor knows the seed must populate it. Not a blocker.

## Follow-ups

- (none)

## Files touched

All test files (plus this report), all under sanctioned paths. No application source, migration, compose, or Dockerfile touched; `./app/db/**` and `./app/docker-compose.yml` confirmed clean via `git status`.

- `./app/api/tests/conftest.py` (new)
- `./app/api/tests/test_admin_seed.py` (new)
- `./app/api/tests/test_auth_login.py` (new)
- `./app/api/tests/test_sessions.py` (new)
- `./.claude/artifacts/handoffs/API-T-002-TEST-DESIGN-KICKOFF-REPORT.md` (this report; dual-channel)

No commits made (stage-not-commit; the Orchestrator owns the commit gate).

## Build / verification status

- **Suite status: RED, by construction. This is the intended phase-1 outcome.** The `app/api/` application does not exist, so `conftest.py`'s `from app.api.main import app as fastapi_app` (and the `from app.api.admin_seed import seed_admin` in the three test modules) cannot resolve; pytest fails at collection for the whole suite. No stub, mock, or app skeleton was created to paper over this, per the kickoff hard rule.
- **Verified in-session (read-only, no app import):** all four files pass `python3 -m py_compile` (syntax valid). A repo-wide em-dash / en-dash scan (U+2014 / U+2013) over `./app/api/tests/` returns no matches. `git status` confirms the only working-tree change I introduced is `./app/api/` and that `./app/db/**` and `./app/docker-compose.yml` are untouched. The transient `__pycache__` from the compile check was removed; `./app/api/` now holds exactly the four authored test files.
- **Not run (correctly):** the suite was NOT executed against Postgres. Execution is compose-only (ADR-003) through the api one-shot `test` service, which is the phase-2 executor's deliverable, not this dispatch's. When that service exists, the suite will run via `docker compose run --rm <api-test-service>` and move red-to-green as the executor implements the app.
- **What the phase-2 executor must satisfy** (so the suite goes green): a FastAPI app at `app.api.main:app`; a callable `app.api.admin_seed.seed_admin()` that seeds the admin idempotently from `ADMIN_EMAIL` / `ADMIN_PASSWORD_HASH` (setting `display_name`, `kind='human'`, `email`, `password_hash`); `POST /api/v1/auth/login`, `POST /api/v1/auth/logout`, and `GET /api/v1/me` with argon2id verification, server-side sessions in the `sessions` table, and an HTTP-only SameSite session cookie; and the api one-shot compose `test` service supplying `DATABASE_URL`. The executor may not modify these test files (ADR-016 no-touch rule).
