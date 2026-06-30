---
schema_version: 1
id: API-T-005
title: "Optimize the api test harness: reduce the redundant per-test admin re-seed + table reset"
status: in-progress
labels: []
priority: P3
created: 2026-06-15
updated: 2026-06-30
---

## Description

Follow-up surfaced by the API-T-002 implementation (committed `a40cf3d`). The api suite re-seeds the admin and resets the auth tables on every test: the autouse `reset_auth_tables` fixture TRUNCATEs `users` and `sessions` (RESTART IDENTITY CASCADE) after each test, and the tests that need a seeded admin call `seed_admin()` explicitly in their own fixtures (`test_auth_login.py`, `test_sessions.py`, `test_admin_seed.py`). This is correct (`seed_admin()` is idempotent and the pinned TRUNCATE-between-tests isolation is intentional) and currently fast, so this is a pure optimization, not a correctness fix. If/when the suite grows and the per-test seed + reset cost becomes significant, explore reducing the redundant work (for example consolidating the explicit `seed_admin()` calls into shared fixture setup, or narrowing/sharing the reset) while preserving the pinned between-test isolation.

Premise re-anchored 2026-06-30 (see observation API-01). The originally-filed framing (a "session-scoped app fixture" to avoid "per-test FastAPI lifespan seeds") was verified against disk and does not hold: `app/api/tests/conftest.py` imports the app once at module scope (`from app.api.main import app as fastapi_app`; `app = create_app()` runs once at import), the `client` fixture only wraps that one app in a fresh httpx `ASGITransport` per test, and plain `ASGITransport` does not run the FastAPI lifespan (no `LifespanManager` / `asgi-lifespan` in the suite), so the lifespan's `seed_admin()` does not fire per test. The real per-test cost is the explicit `seed_admin()` calls plus the autouse TRUNCATE described above, so a session-scoped app fixture would not address it; the optimization levers are the explicit seeds and the reset, not app/lifespan construction.

Pinned approach (resolved with the user 2026-06-30; this is the `decisions_resolved` for the eventual test-design kickoff). Optimize by consolidating the seeding, NOT by reworking the reset:
- (1) Hoist the argon2id hash to a session/module-scoped fixture so each module's admin hash is computed once instead of per test. This is the high-leverage move: argon2id hashing is deliberately expensive and is the dominant per-test cost, an order of magnitude above the autouse TRUNCATE (which runs on two effectively-empty tables). The hash is a pure function of a constant test password, so it never needs recomputing per test.
- (2) Unify the two near-identical `seeded_admin` fixtures (`test_auth_login.py`, `test_sessions.py`) into one shared `conftest` fixture parametrized by the module's email/password constants.
- (3) Keep the per-test re-seed (a cheap INSERT, still required because the autouse TRUNCATE wipes `users` each test) and keep `reset_auth_tables` autouse and blanket. Making the reset opt-in is rejected: the deliberate between-test isolation is what prevents order-dependence bugs.
- Optional secondary (not the headline): reuse one session-scoped connection for the reset instead of reconnecting per test. Narrowing/sharing the reset is explicitly NOT the primary lever.
- Transaction-rollback isolation stays rejected (the app commits on its own connections; the `conftest.py` docstring records why).
- First step at pickup: a quick measurement to confirm argon2 dominates in this environment before refactoring (the ordering above is reasoned from argon2id's cost profile, not an in-environment measurement).

IMPORTANT routing note: this edits the protected test-harness files under `app/api/tests/` (the autouse `reset_auth_tables` fixture in `conftest.py` and the per-test `seed_admin()` setup in the test modules). Per ADR-016 an implementation executor may not touch test files; changes to them are authored by a `test-designer` dispatch. So when picked up, this routes as a test-design change (a fresh `test-designer` dispatch), not a regular executor task. Standalone task: test-harness ergonomics, not part of API-E-001's capability. P3 (deferred until suite growth makes it worthwhile).

References:
- `app/api/tests/conftest.py` (the autouse `reset_auth_tables` TRUNCATE fixture and the module-scoped `client` fixture)
- `app/api/tests/test_auth_login.py`, `app/api/tests/test_sessions.py`, `app/api/tests/test_admin_seed.py` (the explicit per-test `seed_admin()` calls that are the real cost)
- `ai-infrastructure/project-manager/decisions/ADR-016-testing-strategy-test-designer-agent.md` (test files change via a test-designer dispatch, not an executor)

## Activity log

- 2026-06-15: Created in backlog by the Backend API Orchestrator. Surfaced as a follow-up in the API-T-002 implementation report (`a40cf3d`): per-test lifespan seeds are redundant (idempotent, currently fast). Pure optimization, deferred (P3). Routes through a `test-designer` dispatch because it edits protected test-harness files (ADR-016), not an executor. Standalone, unlabelled per ADR-031.
- 2026-06-30: Premise re-anchored to the verified cost source and the file renamed (slug `optimize-api-test-seed-reset`) by the Backend API Orchestrator. The originally-filed diagnosis (per-test FastAPI lifespan re-seed, fixed by a session-scoped app fixture) was verified against disk and does not hold: the app is module-scoped and the lifespan never fires through the test `client`. The real per-test cost is the explicit `seed_admin()` calls in the test modules plus the autouse `reset_auth_tables` TRUNCATE; the proposed remedy is moot and the scope is restated around those levers. No change to priority (P3), routing (test-designer dispatch), or standalone status. Logged as observation API-01.
- 2026-06-30: Open optimization-approach decision resolved with the user (Backend API Orchestrator). Pinned the seed-consolidation lever (hoist the argon2id hash to session/module scope + unify the duplicated `seeded_admin` fixtures), keeping the autouse blanket TRUNCATE; reset narrowing demoted to an optional secondary. Homework: read all five api test modules; argon2id hashing in the seeding fixtures is the dominant per-test cost (deliberately expensive), not the TRUNCATE. Decision recorded in the "Pinned approach" block above as the `decisions_resolved` for the eventual test-design kickoff. Still backlog/P3 (deferred until suite growth justifies the work).
- 2026-06-30: Picked up; moved to in-progress (Backend API Orchestrator). Routes as a single `test-designer` dispatch (ADR-016), NOT the two-phase TDD red/green flow: this is a green-preserving harness refactor (consolidate the seeding per the pinned approach), not the authoring of new failing tests. Decisions are already resolved (the "Pinned approach" block); drafting the test-design kickoff next.
