# API-T-006 (item 2) - lock the missing-admin-creds fail-fast with a test (COR-09 coverage backfill)

## Target

This is web-app work (domain 1 per ADR-005): a pytest authored into the `app/api/tests/` suite, directed by the backend-api department. The target artifact is the existing test module `./app/api/tests/test_admin_seed.py`, which you extend with two fail-fast regression-guard tests.

**Read this framing before you touch anything: this is NOT a standard red-by-construction TDD phase.** The behavior under test ALREADY EXISTS in the implementation. This dispatch is a regression-guard / coverage-backfill: the two tests you author LOCK existing behavior, and they are EXPECTED TO PASS (green) immediately against the current code. Green-on-authoring is the intended and correct outcome here. There is NO phase-2 implementation executor for this item. Do not author a failing/red test; do not stub, rename, or alter anything to force a red collection or a red run. The reason this routes to a test-designer (not an executor) is solely the ADR-016 no-touch rule: only a test-designer may write files under `./app/api/tests/`. That routing constraint, not a red-then-green cycle, is why you are here.

Why the gap exists (COR-09, `./ai-infrastructure/project-manager/OBSERVATIONS.md`): API-T-002's suite always injects `ADMIN_EMAIL` / `ADMIN_PASSWORD_HASH` through the conftest `admin_env` fixture (`monkeypatch.setenv`), so the missing-admin-creds fail-fast path was never exercised by a test until a real `docker compose up api` hit it. These two tests backfill that coverage.

## Decisions resolved by the Orchestrator

All design decisions below are pinned by the Orchestrator and verified against the code. You make NO design decisions in this dispatch; author the tests exactly as specified.

- **The fail-fast behavior you are locking (verified against the code).** `./app/api/settings.py` reads admin creds at call time and raises a clear `RuntimeError` when unset: `get_admin_email()` raises `RuntimeError("ADMIN_EMAIL is not set")` and `get_admin_password_hash()` raises `RuntimeError("ADMIN_PASSWORD_HASH is not set")`. `./app/api/admin_seed.py` `seed_admin()` calls `settings.get_admin_email()` FIRST, then `get_admin_password_hash()`, BEFORE any DB connection (`get_database_url()` / `psycopg2.connect`). So when an admin env var is unset, `seed_admin()` raises BEFORE connecting to Postgres. The FastAPI lifespan in `./app/api/main.py` calls `seed_admin()` on startup, which is the boot fail-fast that refuses to start the api without creds. This is the contract the two tests pin.

- **Append to the existing file; do not create a new module.** Author both tests by APPENDING to `./app/api/tests/test_admin_seed.py`, the cohesive home (it already covers `seed_admin()` behavior). Do not create a new test module. Mirror the existing file's style: it already defines the `ADMIN_EMAIL = "admin@example.test"` constant, the `_make_test_hash` helper, and the `admin_env` fixture; reuse them where they fit rather than re-deriving equivalents.

- **Test 1 (required): `seed_admin()` raises `RuntimeError` when `ADMIN_EMAIL` is unset.** Use the pytest built-in `monkeypatch` fixture to ensure BOTH `ADMIN_EMAIL` and `ADMIN_PASSWORD_HASH` are UNSET: `monkeypatch.delenv("ADMIN_EMAIL", raising=False)` and `monkeypatch.delenv("ADMIN_PASSWORD_HASH", raising=False)`. Then wrap a direct `seed_admin()` call in `pytest.raises(RuntimeError)` and assert the raised error message mentions `"ADMIN_EMAIL"` (the clear-error contract). This test MUST NOT use the conftest `admin_env` fixture; that fixture sets the env, which would defeat the test.

- **Test 2 (required): `seed_admin()` raises `RuntimeError` when `ADMIN_PASSWORD_HASH` is unset but `ADMIN_EMAIL` is set.** Use `monkeypatch.setenv("ADMIN_EMAIL", ...)` (a throwaway value) and `monkeypatch.delenv("ADMIN_PASSWORD_HASH", raising=False)`. Wrap `seed_admin()` in `pytest.raises(RuntimeError)` and assert the message mentions `"ADMIN_PASSWORD_HASH"`. This test pins the second-check fail-fast (email present, hash missing).

- **Neither test needs a live database.** `seed_admin()` raises on the missing-cred check BEFORE it calls `get_database_url()` or connects, so no DB is required for either assertion. The suite's autouse `reset_auth_tables` fixture still runs (it truncates via `DATABASE_URL`, which the `api-test` compose service supplies); that is expected and fine. Do NOT disable, alter, or work around any shared fixture in `./app/api/tests/conftest.py`.

- **Secrets (ADR-006 / repo `./CLAUDE.md`).** Use only throwaway in-test values (for example an email like `"admin@example.test"`, already the module's `ADMIN_EMAIL` constant). Never write a real credential or a real password hash into the test or any tracked file.

## Deliverables

- `./app/api/tests/test_admin_seed.py` extended with Test 1 and Test 2 as pinned above. Each test derives its assertions from the fail-fast contract: a clear `RuntimeError` naming the missing variable. The suite is EXPECTED to be GREEN after authoring, because the behavior already exists in the implementation.

## Files in scope

- `./app/api/tests/test_admin_seed.py` (EDIT - append the two fail-fast tests).

## Files out of scope

- All non-test `./app/api/` source: `./app/api/settings.py`, `./app/api/admin_seed.py`, `./app/api/main.py`. The behavior already exists; do NOT modify it. This is a test-only dispatch.
- `./app/docker-compose.yml`, `./app/.env.example`, `./app/api/gen-admin-hash.sh`. API-T-006 items 1 and 3 are a SEPARATE executor dispatch running independently; do not touch them.
- The other test files in `./app/api/tests/`: `./app/api/tests/conftest.py`, `./app/api/tests/test_auth_login.py`, `./app/api/tests/test_sessions.py`, `./app/api/tests/test_docs_gating.py`, `./app/api/tests/test_healthz.py`. Only `./app/api/tests/test_admin_seed.py` is edited.

## References

- `./app/api/settings.py` - the `get_admin_email()` / `get_admin_password_hash()` `RuntimeError` fail-fast; the contract being locked.
- `./app/api/admin_seed.py` - `seed_admin()` call order: admin-cred checks run before any DB connect.
- `./app/api/main.py` - the FastAPI lifespan that calls `seed_admin()` on startup; why this is a boot fail-fast.
- `./app/api/tests/test_admin_seed.py` - the file to extend; mirror its existing style (`admin_env` fixture, `_make_test_hash`, the `ADMIN_EMAIL` constant).
- `./app/api/tests/conftest.py` - shared fixtures. `monkeypatch` is a pytest built-in; the autouse `reset_auth_tables` fixture truncates via `DATABASE_URL`.
- `./ai-infrastructure/project-manager/decisions/ADR-006-admin-bootstrap-env-hash.md` - admin bootstrap from an env-supplied hash; the fail-fast is the "refuse to boot without creds" guarantee.
- `./ai-infrastructure/project-manager/decisions/ADR-016-testing-strategy-test-designer-agent.md` - the test-designer / no-touch rule; API-level tests over a real Postgres. This is why a test-designer (not an executor) authors this file.
- `./ai-infrastructure/project-manager/decisions/ADR-003-docker-compose-runtime.md` - compose is the only supported run path.

## Related tasks and ADRs

- API-T-002 - built the auth / admin-seed service and its test suite; its fixtures always set the admin env, leaving this fail-fast path uncovered (the COR-09 gap this dispatch backfills).
- ADR-006 - admin bootstrap; the fail-fast is the refuse-to-boot-without-creds guarantee being locked.
- ADR-016 - test-designer dispatch and the `./app/api/tests/` no-touch rule (why this is a test-designer, not an executor).
- COR-09 (`./ai-infrastructure/project-manager/OBSERVATIONS.md`) - the runtime-gate observation: a path covered only once a real compose boot exercised it.

## Hard rules

- **This is a green-on-authoring coverage-backfill, not a red TDD phase.** The two tests are EXPECTED to PASS against the current, unmodified implementation. Do not force a red state; do not modify any source to make a test fail first.
- **Test 1 must not use the `admin_env` fixture.** That fixture sets the env and would defeat the missing-cred assertion. Delete both env vars via `monkeypatch.delenv(..., raising=False)`.
- **Do not modify shared fixtures or any source file outside `./app/api/tests/test_admin_seed.py`.** The autouse `reset_auth_tables` fixture running is expected; leave it alone.
- **Secrets:** throwaway in-test values only; never a real credential or hash (ADR-006 / `./CLAUDE.md`).

## Verification expectations

Per ADR-003, the run path is docker compose only. For this task specifically:

- Confirm the two new tests are present in `./app/api/tests/test_admin_seed.py` and collect under pytest.
- Run the api test suite via compose and confirm the new tests PASS (green-on-authoring, since the fail-fast behavior already exists). The whole suite should remain green:

  ```
  docker compose -f app/docker-compose.yml run --build --rm api-test
  ```

  The `api-test` service runs `pytest -v app/api/tests/`; `--build` ensures the newly-added test file is COPYed into the image.

- If docker is unavailable in this environment, say so explicitly (Agent Discipline, `./CLAUDE.md`) and fall back to confirming the test file is syntactically valid (for example `python3 -m py_compile app/api/tests/test_admin_seed.py`) and that the new tests collect logically. Do NOT claim a passing compose run you did not execute.
- Confirm no `./app/api/` source file outside the test suite changed: `git status` / `git diff` should show only `./app/api/tests/test_admin_seed.py` modified.

## Executor pointer

This kickoff is executed by the dispatched `test-designer` (ADR-016, the design half of the TDD pair; here applied to a coverage-backfill that is green-on-authoring). Universal conventions (the six-section report shape, the dual-channel report write, Agent Discipline, the compose-only run policy, git boundaries) live in `./docs/ai-orchestration/roles/EXECUTOR-ROLE.md` and the test-designer's own role doc; reference them rather than re-deriving. The closing report is written to `<kickoff-dir>/<KICKOFF-BASENAME>-REPORT.md` per `EXECUTOR-ROLE.md`, section "Report shape".
