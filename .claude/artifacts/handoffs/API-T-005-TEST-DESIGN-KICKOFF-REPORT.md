# API-T-005 Test-Design Kickoff - Closing Report

Green-preserving refactor of the api test harness (consolidate the seeding, hoist the argon2id hash to session scope). Dispatched as `test-designer` because the files are test-designer-owned (ADR-016). Worktree: `/home/adam/src/corral-api-t-005` on branch `api-t-005-test-designer`, commit `ecd0bf7`, left on disk for the Orchestrator to integrate.

## Deliverables completed

- **`./app/api/tests/conftest.py` - session-scoped memoized hashing fixture + shared `seeded_admin`.** Done. Added `hash_password` (session-scoped fixture returning a callable that argon2id-hashes a password string and memoizes the result keyed by the password string via `functools.lru_cache`, conftest.py:147-165) and the shared `seeded_admin` fixture (reads `request.module.ADMIN_EMAIL` / `request.module.ADMIN_PASSWORD`, hashes via `hash_password`, seeds via `seed_admin()`, returns `(email, password, user_id)`, conftest.py:168-189). Added imports `functools`, `from argon2 import PasswordHasher`, `from app.api.admin_seed import seed_admin`.
- **`./app/api/tests/test_auth_login.py` - remove local `seeded_admin`, consume the shared one.** Done. Removed the local fixture (was lines 42-54) and the now-orphaned `from app.api.admin_seed import seed_admin` import. Kept `ADMIN_EMAIL` / `ADMIN_PASSWORD` constants, the `PasswordHasher` / `VerifyMismatchError` imports (still used by the three primitive unit tests), and every test body and assertion unchanged.
- **`./app/api/tests/test_sessions.py` - remove local `seeded_admin`, consume the shared one.** Done. Removed the local fixture (was lines 45-56) and the now-orphaned `from argon2 import PasswordHasher` and `from app.api.admin_seed import seed_admin` imports. Kept the distinct constants and all test bodies unchanged.
- **`./app/api/tests/test_admin_seed.py` - route `admin_env` through the memoized helper.** Done. `admin_env` now takes the `hash_password` fixture and obtains its hash via `hash_password("throwaway-test-password")` (the same throwaway password string `_make_test_hash` used by default), so the per-test recompute is gone. All assertions and the seed-call / fail-fast test bodies are unchanged.
- **Before/after timing + green confirmation via the `api-test` compose one-shot (ADR-003).** Done. Recorded under "Build / verification status".

## Decisions made

- **Cache mechanism: `functools.lru_cache`.** The kickoff pinned "either a module-level dict keyed by the password string or `functools.lru_cache` on the hashing function; both are the same pinned shape." I chose `lru_cache(maxsize=None)` on the inner hashing function as the cleaner of the two named options. The cache lives inside the session-scoped `hash_password` fixture (one `PasswordHasher` + one `lru_cache`-wrapped closure per session), which realizes "memoize the argon2id hash by password" with session lifetime; it is not a different caching strategy.
- **Left `_make_test_hash` in place in `test_admin_seed.py` (now uncalled).** Routing `admin_env` through `hash_password` removes the per-test recompute the kickoff targeted. I deliberately did not delete `_make_test_hash` or its `PasswordHasher` import: deleting it would orphan the import and require editing the module docstring's "(see _make_test_hash)" reference, and the kickoff scoped this file's change to "route `admin_env`'s argon2id hash through the shared memoized helper" and fenced off docstring edits. Keeping the helper holds the change to pure fixture plumbing and keeps the docstring reference valid. The now-dead helper is logged under Follow-ups.
- **Removed imports orphaned by the fixture removals.** In `test_auth_login.py` (`seed_admin`) and `test_sessions.py` (`PasswordHasher`, `seed_admin`) the removed local `seeded_admin` fixtures were the only consumers of those imports; removing the imports is part of removing the fixtures. `PasswordHasher` was retained in `test_auth_login.py` because the three out-of-scope primitive unit tests still use it.
- **Added a 3-line cross-reference comment** in `test_auth_login.py` and `test_sessions.py` where each local fixture was removed, pointing readers to the shared `conftest` fixture. This is an explanatory note tied to the change, not a docstring rewrite.

## Surprises

- **None material.** The suite was already green before the refactor (30 passed), exactly as the kickoff framed it (the FastAPI app exists at `./app/api/main.py`; the stale "red-by-construction" module docstrings remain, untouched per the kickoff's out-of-scope instruction).
- The session-start `git status` snapshot showed HEAD at `9c50cda`, but local `master` was at `f68ac1c` when verified in-session; the worktree was branched from `f68ac1c` (current master HEAD). Not a conflict, just a stale snapshot.

## Follow-ups

- **`_make_test_hash` in `./app/api/tests/test_admin_seed.py` is now uncalled dead code** (lines 42-47), retained to keep this task's diff to pure fixture plumbing and avoid editing its module-docstring reference. A future test-design cleanup could remove the helper, its `from argon2 import PasswordHasher` import, and the "(see _make_test_hash)" docstring parenthetical together. **Triage: COR-T candidate (test-designer dispatch), Backend API Orchestrator.**
- **Import ordering in `conftest.py`:** `from app.api.admin_seed import seed_admin` was appended after the comment-attached `from app.api.main import app as fastapi_app` rather than in strict alphabetical order, to avoid churning the commented app-import block. No linter is in the compose run path (pytest only), so this is cosmetic. **Triage: triage to orchestrator (drop if no isort gate is ever added).**
- The stale "red-by-construction / `app/api/` does not exist yet" narrative in the test module docstrings remains (explicitly out of scope for this task per the kickoff). Noted here only so it is not lost; **triage to orchestrator** if a separate docstring-refresh task is ever warranted.

## Files touched

All under `./app/api/tests/` (diff confined as required), committed on branch `api-t-005-test-designer` as `ecd0bf7`:

- `./app/api/tests/conftest.py`
- `./app/api/tests/test_auth_login.py`
- `./app/api/tests/test_sessions.py`
- `./app/api/tests/test_admin_seed.py`
- `./.claude/artifacts/handoffs/API-T-005-TEST-DESIGN-KICKOFF-REPORT.md` (this report; dual-channel write, not committed - reports are committed at the Orchestrator's gate)

## Build / verification status

Run path: the `api-test` compose one-shot in `./app/docker-compose.yml` (ADR-003), built fresh before each run so the image picks up the edited test files.

- **Before (unrefactored, branched from master HEAD):** `30 passed in 10.61s` (pytest wall-clock); ~16s including postgres + migrate startup.
- **After (refactored):** `30 passed in 6.25s` (pytest wall-clock); ~12s including startup.
- **Green preserved:** all 30 tests pass, same test set, same assertions. No test was added, removed, or had its behavior changed.
- **Redundant per-test hashing eliminated (acceptance gate):** the three distinct seeding passwords (`correct-horse-battery-staple`, `session-throwaway-password`, `throwaway-test-password`) were argon2id-hashed 14 times across the seeding fixtures before the refactor (5 + 5 + 4 per-test recomputes); after the refactor each is hashed at most once per session via the `lru_cache`-backed `hash_password` helper (3 hashes total). The ~41% pytest wall-clock drop (10.61s -> 6.25s) corroborates the removal of ~11 redundant argon2id computations. The three argon2id primitive unit tests in `test_auth_login.py` deliberately hash directly and were left untouched (out of scope).
- **Diff scope verified:** `git diff --stat` shows changes confined to the four named files under `./app/api/tests/`; `reset_auth_tables`, the primitive unit tests, the fail-fast tests, and `test_docs_gating.py` / `test_healthz.py` are unchanged. Em-dash scan over `app/api/tests/` is clean.

The Orchestrator integrates the worktree (`/home/adam/src/corral-api-t-005`, branch `api-t-005-test-designer`, commit `ecd0bf7`) via `bin/git-integrate`.
