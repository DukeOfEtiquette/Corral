# API-T-006 (item 2) Test-Design Report - lock the missing-admin-creds fail-fast

## Deliverables completed

- DONE: `./app/api/tests/test_admin_seed.py` extended by appending the two pinned regression-guard tests (no new module created; appended to the cohesive existing home).
  - `test_seed_raises_when_admin_email_unset` (test_admin_seed.py:141): both `ADMIN_EMAIL` and `ADMIN_PASSWORD_HASH` removed via the pytest built-in `monkeypatch.delenv(..., raising=False)`; `seed_admin()` wrapped in `pytest.raises(RuntimeError)`; asserts the raised message contains `"ADMIN_EMAIL"`. Does NOT use the conftest `admin_env` fixture (pinned constraint), so the missing-cred path is genuinely exercised.
  - `test_seed_raises_when_admin_password_hash_unset` (test_admin_seed.py:164): `ADMIN_EMAIL` set to the throwaway module constant via `monkeypatch.setenv`, `ADMIN_PASSWORD_HASH` removed via `monkeypatch.delenv(..., raising=False)`; `seed_admin()` wrapped in `pytest.raises(RuntimeError)`; asserts the raised message contains `"ADMIN_PASSWORD_HASH"`. Pins the second-check fail-fast (email present, hash missing).
- Both tests are GREEN against the current, unmodified implementation, which is the intended outcome for this regression-guard / coverage-backfill dispatch (not a red-by-construction phase).

## Decisions made

(none) All design decisions were pinned by the Orchestrator in the kickoff and authored exactly as specified. No design latitude was exercised: the env-deletion approach, the `monkeypatch` built-in (not `admin_env`), the throwaway email value, the `pytest.raises(RuntimeError)` shape, and the substring assertions were all dictated. Tests append after the existing `test_reseed_does_not_overwrite_existing_admin` and mirror the module's existing docstring + structure style.

## Surprises

(none) Repo state matched the kickoff. The contract was verified against the code as pinned: `./app/api/settings.py:17-28` raises `RuntimeError("ADMIN_EMAIL is not set")` / `RuntimeError("ADMIN_PASSWORD_HASH is not set")`; `./app/api/admin_seed.py:23-27` calls `get_admin_email()` then `get_admin_password_hash()` BEFORE `get_database_url()` / `psycopg2.connect`, so a missing cred raises before any DB connection; `./app/api/main.py:31-34` invokes `seed_admin()` in the FastAPI lifespan (the boot fail-fast). The separate executor dispatch's staged changes (compose, `app/.env.example`, `app/api/.env.example` deletion, `app/api/gen-admin-hash.sh`) were present and left untouched.

## Follow-ups

(none)

## Files touched

- `./app/api/tests/test_admin_seed.py` (EDIT - appended the two fail-fast regression-guard tests; unstaged `M`).
- `./.claude/artifacts/handoffs/API-T-006-TEST-DESIGN-KICKOFF-REPORT.md` (this report; dual-channel write).

No non-test file was modified by this dispatch. The other `app/api/` diffs shown by `git status` (`app/api/.env.example` deletion, `app/api/gen-admin-hash.sh`) are the pre-existing STAGED changes from the separate item-1/3 executor dispatch, not this dispatch's work.

## Build / verification status

- Syntax: `python3 -m py_compile app/api/tests/test_admin_seed.py` passed.
- Em-dash scan: `grep -nP '[\x{2013}\x{2014}]'` over the test file found none (repo writing rule, `./CLAUDE.md`).
- Compose run (ADR-003, the only supported run path; docker was available in this environment): `docker compose -f app/docker-compose.yml run --build --rm api-test` => `30 passed in 3.58s`. Both new tests collected and PASSED:
  - `app/api/tests/test_admin_seed.py::test_seed_raises_when_admin_email_unset PASSED`
  - `app/api/tests/test_admin_seed.py::test_seed_raises_when_admin_password_hash_unset PASSED`
  - The whole api suite remained green (no regressions). Green-on-authoring is the intended outcome for this coverage-backfill; the fail-fast behavior already exists in the implementation.
- Scope confirmation: `git diff --stat HEAD -- app/api/` and `git status --short` confirm the only change this dispatch made is `app/api/tests/test_admin_seed.py`; no `app/api/` source outside the test suite was modified by this dispatch.
- Not done / not applicable: no STATUS file touched (ADR-040); no commit made (the Orchestrator owns the commit gate); the task file was not moved.
