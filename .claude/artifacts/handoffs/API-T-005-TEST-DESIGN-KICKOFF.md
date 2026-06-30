# API-T-005 - Optimize the api test harness: consolidate the per-test admin seeding (hoist the argon2id hash to session scope)

## Target

This is **web-app** domain-1 work (ADR-005): the artifact in scope is the api test harness under `./app/api/tests/`. You are dispatched as the `test-designer` only because ADR-016 makes test files test-designer-owned (an executor may not edit them). This task does NOT change any web-app source outside the tests directory.

**Read this framing before anything else.** This is NOT the two-phase TDD red/green flow and NOT the authoring of new failing tests. It is a **green-preserving refactor** of existing test-harness fixtures for speed. The api suite is currently green: the FastAPI app exists at `./app/api/main.py` (stood up by API-T-002), so the app-import in `./app/api/tests/conftest.py` resolves and the suite runs. The dominant per-test cost is the argon2id hash recomputed in the seeding fixtures; argon2id is deliberately expensive. Your job is to remove that redundant per-test hashing while keeping every test's behavior and assertions identical.

Note: several module docstrings under `./app/api/tests/` still narrate the original "red-by-construction / `app/api/` does not exist yet" phase-1 state (for example the header comment at the top of `./app/api/tests/conftest.py`). That narrative is stale (the app now exists and the suite is green); it is out of scope for this task and you do not rewrite it. Touch a docstring only where a fixture you are moving carries one.

The single acceptance gate is at the bottom under "Hard rules": the same suite stays green after the refactor, with the redundant per-test argon2id hashing eliminated.

## Decisions resolved by the Orchestrator

All pinned with the user on 2026-06-30. These are settled, including the two hashing-helper and fixture-parametrization mechanisms below. Do not re-open them, do not frame them as options, and do not substitute a different code shape: the mechanisms are prescribed.

- **Optimize by consolidating the seeding, not by reworking the reset.** The dominant per-test cost is the argon2id hash recomputed in the seeding fixtures. The autouse `TRUNCATE` runs on two effectively-empty tables and is an order of magnitude cheaper, so it is left untouched.

- **Hoist the argon2id hashing to session scope (pinned mechanism).** Each distinct constant test password is argon2-hashed at most ONCE per test session, instead of once per test. Add to `./app/api/tests/conftest.py` a **session-scoped fixture that returns a memoized argon2id hashing callable**. The callable hashes a given password string with argon2-cffi's `PasswordHasher` and caches the result keyed by the password string, so a repeat call with the same password returns the cached hash rather than recomputing. Realize the cache as either a module-level dict keyed by the password string or `functools.lru_cache` on the hashing function; both are the same pinned shape (memoize the argon2id hash by password). Do NOT introduce a different caching strategy. The seeding fixtures obtain their hashes by calling this session-scoped memoized helper.

- **Unify the two duplicated `seeded_admin` fixtures into one shared `conftest` fixture (pinned mechanism).** The near-identical local `seeded_admin` fixtures in `./app/api/tests/test_auth_login.py` and `./app/api/tests/test_sessions.py` become ONE shared fixture in `conftest.py`. The shared fixture reads the requesting test module's `ADMIN_EMAIL` and `ADMIN_PASSWORD` module-level constants via pytest's `request.module` introspection (`request.module.ADMIN_EMAIL` / `request.module.ADMIN_PASSWORD`). Do NOT use indirect parametrization, a fixture factory, or per-module wrapper fixtures. Each module keeps its own two module-level constants and defines NO local `seeded_admin` fixture after the refactor. The shared fixture computes the admin's argon2id hash via the session-scoped memoized helper above, seeds via `seed_admin()`, and returns the same `(email, password, user_id)` tuple the two local fixtures return today.

- **Route `admin_env` in `test_admin_seed.py` through the same memoized helper.** Its argon2id hash must come from the same session-scoped memoized hashing helper, removing its per-test hash recompute (today it computes the hash via the local `_make_test_hash` helper). Its existing assertions are preserved verbatim (the stored `password_hash` equals the env-supplied hash). The seed tests that call `seed_admin()` in their bodies, and the two fail-fast tests that set no hash, are unchanged.

- **Keep the per-test re-seed.** The re-seed is a cheap `INSERT` and is still required because the autouse `TRUNCATE` wipes `users` each test. That is correct and stays.

- **Keep `reset_auth_tables` exactly as it is: autouse and blanket.** Do NOT make it opt-in. The deliberate between-test isolation prevents order-dependence bugs. The reset is left fully untouched by this task.

- **Transaction-rollback isolation stays rejected.** The app commits on its own connections; the `conftest.py` docstring records why. Do not introduce it.

- **Preserve every test's behavior and assertions verbatim.** The ONLY change is fixture plumbing: where and when the argon2 hash is computed, and where the `seeded_admin` fixture lives. No assertion text, no test logic, no endpoint, and no source under `./app/api/` outside the tests directory changes.

## Deliverables

- `./app/api/tests/conftest.py`: add the session-scoped memoized argon2id hashing fixture (the pinned mechanism above: a session-scoped fixture returning a callable that caches the argon2id hash keyed by the password string) and the shared `seeded_admin` fixture (the pinned `request.module`-introspection mechanism above; the unified body of the two duplicated module fixtures, computing its hash via the memoized helper, seeding via `seed_admin()`, and returning `(email, password, user_id)`).
- `./app/api/tests/test_auth_login.py`: remove its local `seeded_admin` fixture and consume the shared `conftest` fixture; keep its `ADMIN_EMAIL` / `ADMIN_PASSWORD` constants and ALL test bodies and assertions unchanged.
- `./app/api/tests/test_sessions.py`: same as above. Remove its local `seeded_admin`, consume the shared fixture, keep its distinct constants and tests unchanged.
- `./app/api/tests/test_admin_seed.py`: route `admin_env`'s argon2id hash through the shared session-scoped memoized helper; keep all assertions and the seed-call test bodies unchanged.
- Establish a baseline suite wall-clock timing BEFORE refactoring, then capture an after timing, both via the `api-test` compose one-shot (ADR-003). Confirm the suite is fully green after the refactor and that the redundant per-test hashing is gone. This is a P3 optimization: a modest measured improvement is fine. The hard gate is green-preserved plus redundant per-test hashing eliminated, NOT a specific speedup number. Record both timings and the green result in the report's "Build / verification status" section.

## Files in scope

- `./app/api/tests/conftest.py`
- `./app/api/tests/test_auth_login.py`
- `./app/api/tests/test_sessions.py`
- `./app/api/tests/test_admin_seed.py`

## Files out of scope

Do not modify these. The final `git diff` must show changes confined to `./app/api/tests/`.

- `./app/api/main.py` and ALL non-test source under `./app/api/`. This task changes the test harness only.
- The three argon2id PRIMITIVE unit tests in `./app/api/tests/test_auth_login.py`: `test_argon2id_verify_accepts_correct_password`, `test_argon2id_verify_rejects_wrong_password`, and `test_argon2id_hash_is_argon2id_encoding`. They deliberately exercise the hashing primitive directly; leave their per-call hashing intact.
- `./app/api/tests/test_docs_gating.py` and `./app/api/tests/test_healthz.py`. They do not seed an admin; they only pay the unchanged autouse `TRUNCATE`.
- The autouse and blanket nature of `reset_auth_tables`, and the rejected transaction-rollback isolation. Both stay as they are.
- The two fail-fast tests in `./app/api/tests/test_admin_seed.py` (`test_seed_raises_when_admin_email_unset`, `test_seed_raises_when_admin_password_hash_unset`). They deliberately set no hash; leave them unchanged.

## References

Read these in order; the first five are the working surface, the rest are the contract the fixtures encode.

- `./app/api/tests/conftest.py`: the autouse `reset_auth_tables` `TRUNCATE` fixture (def at line 103), the module-scoped `client` fixture (def at line 132), and the `db_url` / `conn` / `cur` fixtures (defs at lines 62 / 79 / 93). The new session-scoped memoized hashing fixture and the shared `seeded_admin` fixture land here.
- `./app/api/tests/test_auth_login.py`: its local `seeded_admin` fixture (lines 43-54), its `ADMIN_EMAIL` / `ADMIN_PASSWORD` constants (lines 38-39), and the three primitive unit tests to leave intact (lines 165, 172, 180).
- `./app/api/tests/test_sessions.py`: its near-identical local `seeded_admin` fixture (lines 46-56) and its distinct `ADMIN_EMAIL` / `ADMIN_PASSWORD` constants (lines 41-42).
- `./app/api/tests/test_admin_seed.py`: the `admin_env` fixture (lines 51-59) and its `_make_test_hash` helper (line 42); the seed-call tests and the two fail-fast tests (`test_seed_raises_when_admin_email_unset` at line 140, `test_seed_raises_when_admin_password_hash_unset` at line 161) to leave unchanged.
- `./ai-infrastructure/backend-api/tasks/in-progress/API-T-005-optimize-api-test-seed-reset.md`: the "Pinned approach" block is the authoritative decisions source for this task.
- `./ai-infrastructure/project-manager/decisions/ADR-016-testing-strategy-test-designer-agent.md`: why this refactor routes as a test-designer dispatch (test files are test-designer-owned).
- `./ai-infrastructure/project-manager/decisions/ADR-006-admin-bootstrap-env-hash.md`: the admin-seed env contract (`ADMIN_EMAIL` / `ADMIN_PASSWORD_HASH`, argon2id hash from env), preserved unchanged.
- `./ai-infrastructure/project-manager/decisions/ADR-011-auth-session-mechanism.md`: the argon2id / session contract the fixtures encode, preserved unchanged.
- `./ai-infrastructure/project-manager/decisions/ADR-003-docker-compose-runtime.md`: compose is the only run path; the suite runs via the `api-test` one-shot service.
- `./app/docker-compose.yml`: the `api-test` one-shot service definition (the compose service that runs this suite with `DATABASE_URL` supplied).
- `./docs/ai-orchestration/roles/TEST-DESIGNER-ROLE.md`: your role doc (report shape, dual-channel write, universal conventions).

## Related tasks and ADRs

- API-T-002 (done): stood up the api auth and admin-seed implementation and these test fixtures; this refactor optimizes the fixtures it introduced.
- ADR-016: test files are test-designer-owned; this is why the refactor routes as a test-designer dispatch, not an executor.
- ADR-006 / ADR-011: the admin-seed and argon2id / session contract the fixtures encode; preserved unchanged.
- Observation API-01 (`./ai-infrastructure/backend-api/OBSERVATIONS.md`): records that this task's original premise drifted and was re-anchored on the real cost source (the argon2 hashing this refactor targets).

## Hard rules

- **Green-preserving, not red.** Do not author new failing tests. Do not change any test's observable behavior or any assertion text. The mechanical end state is: the same set of tests, the same assertions, passing exactly as before, with the redundant per-test argon2id hashing removed.
- **Behavior-preservation is the contract.** The only permitted change is fixture plumbing: where and when the argon2 hash is computed, and where the `seeded_admin` fixture lives. If achieving the refactor appears to require changing an assertion, an endpoint, a test body, or any source under `./app/api/` outside the tests directory, stop and escalate; do not proceed.
- **Use the pinned mechanisms.** The hashing helper is the session-scoped memoized callable keyed by the password string; the shared `seeded_admin` fixture reads its module's constants via `request.module` introspection. Do not substitute indirect parametrization, a fixture factory, per-module wrapper fixtures, or a different caching strategy.
- **Confine the diff.** The final `git diff` must touch only files under `./app/api/tests/`, and only the four named in "Files in scope". No change to `reset_auth_tables`, the primitive unit tests, the fail-fast tests, or `test_docs_gating.py` / `test_healthz.py`.
- **Run path is compose only (ADR-003).** Establish the before-baseline timing, refactor, then capture the after timing, all via the `api-test` one-shot service in `./app/docker-compose.yml`. Do not assume host-installed Python.
- **Single acceptance gate.** The task is complete when, via the `api-test` compose one-shot: (1) the full api suite is green after the refactor, and (2) each distinct constant test password is argon2-hashed at most once per session rather than once per test (the redundant per-test hashing is demonstrably gone). The before/after wall-clock timings are recorded as supporting evidence; a specific speedup number is NOT a gate. There are no intermediate checkpoints.

## Executor pointer

The dispatched agent for this task is the `test-designer` (ADR-016). Universal conventions, the pinned six-section report shape, and the dual-channel write rule live in `./docs/ai-orchestration/roles/TEST-DESIGNER-ROLE.md`; follow them rather than re-deriving them here. The closing report is written to `./.claude/artifacts/handoffs/API-T-005-TEST-DESIGN-KICKOFF-REPORT.md` per that role doc's "Report shape" section (dual-channel: print to chat and write the same content to file).
