# API-T-002 - Auth, sessions, and admin-user bootstrap for the FastAPI api service (TEST-DESIGN phase: author failing tests against the contract)

## Target

This is **web-app** work (ADR-005): the `api` service is the FastAPI application sketched in `ai-infrastructure/project-manager/docs/architecture/OVERVIEW.md` ("api: FastAPI. Serves the client, enforces auth (ADR-011), seeds the admin user from `.env` on first boot (ADR-006)"). This is **TDD phase 1 (red)** per ADR-016: you author FAILING tests against the human auth and admin-seed contract for that service, and nothing else. You are the dispatched `test-designer` (ADR-016). The artifact in scope is the test suite under `app/api/tests/` (four behaviours; see Deliverables). You write test files only; you write no implementation.

The application under test (`app/api/`) does not exist yet. Your tests, and the conftest client fixture that imports the FastAPI app, reference it and therefore fail at collection or run. **That red-by-construction state is the intended deliverable for this phase**, not a defect to work around: do not stub, mock away, or otherwise paper over the missing application to make collection succeed. A separate phase-2 `executor` dispatch (later) stands up the `app/api/` skeleton, the auth and admin-seed logic, the `GET /api/v1/me` route, and the compose one-shot `test` service for the api, and drives this suite green. That executor may not touch the tests you author here (ADR-016 no-touch rule); design them as the specification the implementation must satisfy.

## Decisions resolved by the Orchestrator

- **Phase and deliverable kind: TDD phase 1, red; test files only.** You author failing tests; you write no implementation, no compose entries, no Dockerfile. Red-by-construction (the `app/api/` application is absent) is the intended end state of this dispatch. Rationale: ADR-016 pins the two-phase flow (test design precedes implementation; a separate worker drives green and may not modify your tests).

- **Surface under test: the human auth + admin-seed API on the `api` service, exactly four behaviours.** Do not test anything outside these four:
  1. **Admin bootstrap (ADR-006):** on first boot an admin user is seeded from an env-supplied argon2id password hash. The admin is a `users` row with `kind='human'`, `email` set (from the env), `password_hash` set (from the env hash). Seeding is idempotent on reboot: re-running the seed against an already-seeded database creates no duplicate admin (the admin `users` row count for that email stays at one).
  2. **Login (ADR-011):** credentials are verified with argon2id. On success the server establishes a server-side session (a `sessions` row is created for the user) and sets an HTTP-only, SameSite session cookie on the response. A wrong password yields HTTP 401 and establishes no session (no `sessions` row, no cookie).
  3. **Session-protected access (ADR-011), tested against `GET /api/v1/me`:** this surface includes one minimal, auth-owned protected endpoint, a current-session probe at `GET /api/v1/me`. With a valid session cookie it returns the authenticated user; with no cookie, an invalid cookie, an expired session, or a deleted (post-logout) session it yields HTTP 401. This probe is auth-owned identity, NOT a resource endpoint; it is what lets the suite exercise session gating without depending on any issue / view / label / epic endpoint (API-T-001).
  4. **Logout (ADR-011):** session teardown deletes the `sessions` row (sessions are server-side and revocable per ADR-011). After logout the previously valid cookie no longer authenticates: a follow-up `GET /api/v1/me` with that same cookie yields 401.
  Rationale: these four behaviours are the human auth and admin-seed contract that ADR-011 and ADR-006 pin for the `api` service.

- **Scope boundary (hard): human session auth + admin seed only. Each deferral below carries its scope-of-impact so the boundary is self-justifying.** You must NOT author tests for any of these:
  - **Per-agent API-key / machine auth: deferred to Phase 3 (ADR-026).** ADR-026 gates per-agent identity to Phase 3, alongside the MCP server. This suite does not depend on it: the four behaviours under test are human session auth plus admin seed only, no machine-auth flow is exercised, and `agent_credentials` and `users.kind='machine'` rows are not touched by any of these tests.
  - **Invite-token redemption (ADR-011 invite mechanics): deferred to sibling task API-T-003.** This suite does not depend on it: none of the four behaviours touch the `invites` table or any redemption flow, and the admin user is seeded directly from env (ADR-006), not invited, so no invite has to exist for these tests.
  - **Issue / view / label / epic resource endpoints: deferred to API-T-001 (built onto this task's skeleton later).** This suite does not depend on them: the contract under test is identity establishment and verification only (admin seed, login, session-protected access via `GET /api/v1/me`, logout), and the session-gating test targets the auth-owned `GET /api/v1/me` probe rather than any resource endpoint, so no issue, label, view, or epic needs to exist for any of these tests.
  Rationale: the surface is deliberately narrow (the four behaviours above); ADR-026 and the sibling-task split fix the boundary, and each deferral's scope-of-impact statement is the concrete reason this suite is unaffected by skipping it.

- **Auth mechanism specifics are pinned by ADR-011; do not re-litigate them in test design.** Server-side sessions plus an HTTP-only, SameSite cookie (Secure under HTTPS; the flag may be relaxed for local HTTP dev, so do not assert `Secure` is set under the test harness's HTTP transport). Password hashing is argon2id via argon2-cffi. The auth is hand-rolled on vetted primitives, NOT a full framework like fastapi-users. Session state lives in the `sessions` table. Rationale: ADR-011 is the binding record for all of these auth dimensions; your tests assert the resolved behaviour, they do not explore alternatives.

- **Schema is already migrated (owned by the database department, DB-E-001); assert against the real columns.** The live DDL is in `app/db/alembic/versions/0001_baseline_schema.py`. Assert against exactly these columns:
  - `users(id, display_name, kind, email, password_hash, created_at)`, with `CHECK (kind in ('human','machine'))` and `UNIQUE (email)` (email is nullable in the DDL; the admin row sets it).
  - `sessions(session_id [PK], user_id [FK -> users.id], expires_at, created_at)`. The `session_id` column stores the opaque identifier HASHED at rest per ADR-011, so do not assert the raw cookie value equals the stored `session_id`.
  No migration work is in scope: the schema and migrations are owned by the database department, not backend-api. Do not author, edit, or assert ownership over any migration.

- **Test approach (ADR-016): API-level / integration through the FastAPI app, against a REAL Postgres.** Drive the four behaviours through the FastAPI app via an httpx `ASGITransport` client (in-process, no network listener), against a real Postgres reached through `DATABASE_URL` (the same env the db suite uses). Do NOT mock the database: mocking it would bypass the ADR-010 enforcement seam that ADR-016 requires tests to exercise. Add targeted unit tests only for genuinely non-trivial pure logic (for example, argon2id verify: a correct password verifies, a wrong one does not), and only where a unit test adds coverage the integration tests do not. Rationale: ADR-016 selects API-level-primary precisely so the enforced contract is verified at the HTTP layer, not against mocks.

- **Test-harness pattern to mirror: `app/db/tests/conftest.py`.** Follow its `DATABASE_URL`-from-env convention: a session-scoped fixture reads `os.environ.get("DATABASE_URL")` and fails the run with a clear message if it is unset, exactly as the db conftest's `db_url` fixture does (the compose `test` service supplies it per ADR-003/ADR-006). Your api conftest ADDS two things the db suite does not have, both described in the next two decisions: (a) an httpx `ASGITransport` client fixture over the FastAPI app, and (b) the pinned between-tests reset. Rationale: reusing the db suite's env-`DATABASE_URL` convention keeps one run contract across both suites; the two additions are exactly the deltas the auth surface requires.

- **ASGI client fixture (new, not in the db suite).** Add an httpx `ASGITransport` client fixture over the FastAPI app. The db suite has no application, so this fixture is new to the api conftest. It imports the app object from `app/api/` (the import that fails today, by design, because `app/api/` does not exist) and yields an `httpx` client bound to it via `ASGITransport`. Rationale: the four behaviours are exercised at the HTTP layer per ADR-016, and the ASGI transport runs the real app in-process without a network listener.

- **Between-tests isolation is PINNED to TRUNCATE; this is not a choice for you to make.** Add an autouse fixture that, after each test, TRUNCATEs the tables the auth tests mutate (`users` and `sessions`), restoring a clean slate. Tests and fixtures re-establish any baseline they need (for example, a seeded admin) explicitly within the test or its fixture, never by relying on residue from a prior test. Transaction-rollback isolation is REJECTED and you must NOT use it: these are API-level tests exercising the real FastAPI app over the app's own database connections, so a test-owned transaction would not enclose the app's commits, and rollback isolation would presuppose a DB-session-override hook in implementation code that does not exist yet in the red phase. TRUNCATE is implementation-agnostic, which is the property this phase requires. Whichever fixture mechanics you use, state must not leak across tests. Rationale: the orchestrator resolved this dimension with the user; encode the resolved TRUNCATE strategy, do not reconsider it.

- **Run path is compose-only (ADR-003); the api test service is NOT your job.** The tests assume `DATABASE_URL` is present in the environment, exactly as the db suite does; they do not configure how it is supplied. The compose run path mirrors the existing db one-shot, `docker compose run --rm test`; the api's own one-shot `test` service (its `app/docker-compose.yml` entry and any `app/api/Dockerfile`) is the phase-2 executor's deliverable. Do not add or edit any compose service or Dockerfile. Rationale: ADR-016 selects a one-shot compose `test` service for execution, and ADR-003 makes compose the only run path; standing it up belongs to the green phase.

- **Secrets: drive admin-seed through an env var with a throwaway test hash; never a real credential.** The admin password hash arrives via the gitignored `.env` in production (ADR-006 and the repo `CLAUDE.md` secret rule). In the admin-seed tests, set the seed env var (for example `ADMIN_EMAIL` / `ADMIN_PASSWORD_HASH`) WITHIN the test harness to a throwaway test password and its argon2id hash generated for the test; never write a real secret or a real password hash into any test or tracked file. Rationale: the repo secret rule and ADR-006 bar real credential material from tracked files; a test-generated throwaway hash exercises the seed path without violating it.

## Deliverables

A set of FAILING pytest test files covering the four behaviours above, plus the api test conftest, all under `app/api/tests/`. Concretely:

- `app/api/tests/conftest.py`: the shared fixtures: an httpx `ASGITransport` client fixture over the FastAPI app, the env-`DATABASE_URL` Postgres fixture (mirroring `app/db/tests/conftest.py`), and the pinned autouse TRUNCATE-between-tests reset on `users` and `sessions` described under Decisions resolved.
- `app/api/tests/test_admin_seed.py`: admin seeded from the env-supplied argon2id hash on boot as a `users` row with `kind='human'`, `email` and `password_hash` set; reseeding is idempotent (no duplicate admin for the same email).
- `app/api/tests/test_auth_login.py`: login success verifies the password with argon2id, creates a `sessions` row, and sets an HTTP-only SameSite cookie; wrong password yields 401 with no session and no cookie. Targeted argon2id-verify unit coverage belongs here if warranted.
- `app/api/tests/test_sessions.py`: session-protected access through `GET /api/v1/me` (valid session cookie returns the authenticated user; absent / invalid / expired / post-logout session each yields 401); logout deletes the `sessions` row and the same cookie no longer authenticates against `GET /api/v1/me` afterward.

Red-by-construction: because `app/api/` does not exist, the suite fails at collection or run. That is the expected outcome of this phase; report it as such (the closing report's verification section should record that the suite is red because the application is absent, which is the intended phase-1 state).

The exact test file names above may be adjusted if a different split reads better, but every file you author stays under `app/api/tests/` and the four behaviours all remain covered.

## Files in scope

You author ONLY these (names may be adjusted, but every file stays under `app/api/tests/`):

- `app/api/tests/conftest.py`
- `app/api/tests/test_admin_seed.py`
- `app/api/tests/test_auth_login.py`
- `app/api/tests/test_sessions.py`

## Files out of scope

Do NOT create or edit any of these:

- ALL implementation: any `app/api/` application source. This includes (non-exhaustively) `app/api/main.py`, the auth / session / admin-seed modules, the `GET /api/v1/me` route, routers, models, and settings, and the FastAPI app object itself. Your tests reference the app; they do not create it.
- `app/docker-compose.yml` (the api `test` / service entries) and any `app/api/Dockerfile*`. The compose one-shot `test` service for the api is the phase-2 executor's job.
- `app/db/**`. Reference-only: you mirror `app/db/tests/conftest.py`'s pattern, but you do not modify any database-department file (the schema and migrations are owned by the database department).
- Any ADR, any task file, and any other workspace file.

## References

Read these (the contract this suite tests is defined by them). All exist on disk; cite these exact paths.

- `ai-infrastructure/project-manager/decisions/ADR-011-auth-session-mechanism.md`: the auth and session mechanism: server-side sessions plus HTTP-only SameSite cookies, argon2id hashing, hand-rolled on vetted primitives, the `sessions` store. The binding record for the login / session / logout behaviours.
- `ai-infrastructure/project-manager/decisions/ADR-006-admin-bootstrap-env-hash.md`: admin user seeded from an env-supplied password hash on first boot, never from source; the secret convention for the seed credential.
- `ai-infrastructure/project-manager/decisions/ADR-012-issue-label-view-schema.md`: the `users`-table FK seam (minimal users) and the boundary handing the auth schema delta to ADR-011; context for which columns are auth-owned.
- `ai-infrastructure/project-manager/decisions/ADR-026-per-agent-mcp-identity.md`: the scope boundary in the other direction: per-agent / machine auth is Phase 3 and OUT of scope for this suite.
- `ai-infrastructure/project-manager/decisions/ADR-016-testing-strategy-test-designer-agent.md`: the TDD two-phase flow, API-level-primary backend strategy, the compose one-shot `test` service, and the test-ownership (no-touch) boundary.
- `ai-infrastructure/project-manager/decisions/ADR-003-docker-compose-runtime.md`: compose is the only supported run path; the env-supplied `DATABASE_URL` convention the suite assumes.
- `app/db/alembic/versions/0001_baseline_schema.py`: the REAL `users` and `sessions` DDL (column names, the `kind` CHECK, the `email` UNIQUE, the `sessions` FK to `users`) your tests assert against.
- `app/db/tests/conftest.py`: the harness pattern to mirror: the env-`DATABASE_URL` session fixture and per-test connection fixtures. Your api conftest follows this env convention and adds the ASGI client fixture plus the pinned TRUNCATE-between-tests reset.
- `app/docker-compose.yml`: the compose topology the api `test` service will join later (reference only): the existing `postgres` healthcheck, the db-side `migrate` and `test` one-shots, and the `DATABASE_URL` wiring. You do not edit this file.
- `ai-infrastructure/project-manager/docs/architecture/OVERVIEW.md`: the target runtime shape: the `api` service (FastAPI, enforces auth, seeds admin from `.env`).

## Related tasks and ADRs

- **API-T-002** (this task): the implementation / green phase is a later, separate `executor` dispatch that stands up `app/api/` and drives this suite green.
- **API-T-001**: the issue / view / label / epic endpoints, built onto the `api` skeleton this task establishes; depends on API-T-002. Out of scope here.
- **API-T-003**: invite-token redemption (sibling task); out of scope here.
- **API-E-001**: the owning epic (Phase 2).
- **ADR-011**: the auth / session mechanism contract (login, sessions, logout).
- **ADR-006**: the admin-seed-from-env-hash contract.
- **ADR-026**: the scope boundary: per-agent / machine auth is Phase 3, out of scope.
- **ADR-016**: the TDD two-phase flow and the API-level-primary test strategy this dispatch follows.

## Hard rules

These are task-specific. The universal conventions (the repo writing rules and Agent Discipline in `./CLAUDE.md`, the compose-only run policy in ADR-003, git boundaries, and the pinned six-section report shape) are covered by `EXECUTOR-ROLE.md` and the test-designer agent; honour them without re-derivation.

- **Author tests only; write no implementation.** Do not create the `app/api/` application, even a minimal stub, to make collection pass. The missing app is the point of phase 1.
- **Red is the expected end state.** Do not contort the tests to make the suite pass while the application is absent. The closing report records that the suite is red because `app/api/` does not exist yet, which is the intended phase-1 outcome.
- **Between-tests isolation is TRUNCATE, full stop.** Use the autouse TRUNCATE-between-tests reset on `users` and `sessions` pinned in Decisions resolved. Do not use transaction-rollback isolation; it is rejected for this suite (see the pinned decision for why). This is settled, not a tradeoff to weigh.
- **Test session gating through `GET /api/v1/me`, the auth-owned probe.** Exercise behaviours 3 and 4 against the `GET /api/v1/me` current-session endpoint, not against any issue / view / label / epic resource endpoint (those are API-T-001 and out of scope). `GET /api/v1/me` is the auth-owned identity surface that lets this suite test session gating without depending on the resource endpoints.
- **Assert against the real schema, not an idealized one.** Column names, the `kind` CHECK, the `email` UNIQUE, and the `sessions` FK come from `app/db/alembic/versions/0001_baseline_schema.py`. Do not invent columns the DDL does not have.
- **Do not assert the raw cookie equals the stored `session_id`.** Per ADR-011 the session identifier is stored hashed at rest; the cookie carries the opaque value and the table stores its hash. Assert session existence and the authenticate / no-longer-authenticate behaviour, not raw-value equality with the stored column.
- **Do not assert the `Secure` cookie flag under the test harness.** ADR-011 allows relaxing `Secure` for local HTTP dev; the ASGI transport is not HTTPS. Assert HTTP-only and SameSite, not `Secure`.
- **No real secrets.** Generate any test password hash within the harness as a throwaway; never write a real credential or a real argon2id hash into a test or any tracked file.
- **Stay out of `app/db/**` and `app/docker-compose.yml`.** Mirror the db conftest pattern by reading it; do not modify it or any other database-department or compose file.

## Executor pointer

You are the dispatched `test-designer` (ADR-016), the design half of the TDD pair. Universal conventions for a dispatched agent live in `docs/ai-orchestration/roles/EXECUTOR-ROLE.md` (the test-designer adopts the executor conventions for reporting and dispatch behaviour). Return the pinned six-section closing report with the first line `RETURN: COMPLETED`, and write the same content to the dual-channel report file at `.claude/artifacts/handoffs/API-T-002-TEST-DESIGN-KICKOFF-REPORT.md` per `EXECUTOR-ROLE.md`, section "Report shape".
