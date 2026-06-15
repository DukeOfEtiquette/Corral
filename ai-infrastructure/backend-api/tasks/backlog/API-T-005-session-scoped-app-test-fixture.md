---
schema_version: 1
id: API-T-005
title: "Optimize the api test harness: session-scoped app fixture to avoid per-test lifespan seeds"
status: backlog
labels: []
priority: P3
created: 2026-06-15
updated: 2026-06-15
---

## Description

Follow-up surfaced by the API-T-002 implementation (committed `a40cf3d`). The api test suite's `client` fixture builds the ASGI app per test, so the FastAPI lifespan (which calls `seed_admin()`) fires on every test; combined with the autouse `reset_auth_tables` TRUNCATE, the admin is re-seeded each test. This is correct (seed_admin is idempotent) and currently fast (19 tests in ~2.7s), so this is a pure optimization, not a correctness fix. If/when the suite grows and per-test app/lifespan startup cost becomes significant, explore a session-scoped app fixture (or otherwise decoupling lifespan startup from per-test client creation) while preserving the pinned TRUNCATE-between-tests isolation.

IMPORTANT routing note: this edits the protected test-harness files under `app/api/tests/` (the `client` and `reset_auth_tables` fixtures in `conftest.py`). Per ADR-016 an implementation executor may not touch test files; changes to them are authored by a `test-designer` dispatch. So when picked up, this routes as a test-design change (a fresh `test-designer` dispatch), not a regular executor task. Standalone task: test-harness ergonomics, not part of API-E-001's capability. P3 (deferred until suite growth makes it worthwhile).

References:
- `app/api/tests/conftest.py` (the `client` and autouse `reset_auth_tables` fixtures this would refactor)
- `ai-infrastructure/project-manager/decisions/ADR-016-testing-strategy-test-designer-agent.md` (test files change via a test-designer dispatch, not an executor)

## Activity log

- 2026-06-15: Created in backlog by the Backend API Orchestrator. Surfaced as a follow-up in the API-T-002 implementation report (`a40cf3d`): per-test lifespan seeds are redundant (idempotent, currently fast). Pure optimization, deferred (P3). Routes through a `test-designer` dispatch because it edits protected test-harness files (ADR-016), not an executor. Standalone, unlabelled per ADR-031.
