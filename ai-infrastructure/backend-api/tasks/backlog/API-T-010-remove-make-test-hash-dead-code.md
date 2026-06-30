---
schema_version: 1
id: API-T-010
title: "Remove the now-dead _make_test_hash helper from the api admin-seed test module"
status: backlog
labels: []
priority: P3
created: 2026-06-30
updated: 2026-06-30
---

## Description

Follow-up surfaced by the API-T-005 test-design dispatch (committed `ecd0bf7`). API-T-005 routed `app/api/tests/test_admin_seed.py`'s `admin_env` fixture through the shared session-scoped memoized `hash_password` helper in `conftest.py`, which left the module's local `_make_test_hash` helper (and its `from argon2 import PasswordHasher` import) uncalled. API-T-005 deliberately retained the dead helper to hold its diff to pure fixture plumbing and to avoid editing the module docstring's "(see `_make_test_hash`)" parenthetical, logging this cleanup as a follow-up instead.

Scope: remove the now-uncalled `_make_test_hash` helper, its `PasswordHasher` import (only if no other use remains in the module after removal), and the "(see `_make_test_hash`)" reference in the module docstring, together so nothing is orphaned. Pure dead-code removal: no test behavior or assertion changes, and the api suite stays green.

IMPORTANT routing note: this edits a protected test-harness file under `app/api/tests/`. Per ADR-016 an implementation executor may not touch test files; changes to them are authored by a `test-designer` dispatch. So when picked up, this routes as a test-design change (a fresh `test-designer` dispatch), not a regular executor task. Standalone task: test-harness ergonomics, not part of API-E-001's capability. P3.

References:
- `app/api/tests/test_admin_seed.py` (the module holding the dead `_make_test_hash` helper, its `PasswordHasher` import, and the docstring reference)
- `app/api/tests/conftest.py` (the shared `hash_password` helper that `admin_env` now uses instead, added by API-T-005)
- `ai-infrastructure/backend-api/tasks/done/API-T-005-optimize-api-test-seed-reset.md` (the task that produced this follow-up; deliverable commit `ecd0bf7`)
- `ai-infrastructure/project-manager/decisions/ADR-016-testing-strategy-test-designer-agent.md` (test files change via a test-designer dispatch, not an executor)
- `ai-infrastructure/project-manager/decisions/ADR-003-docker-compose-runtime.md` (compose-only run path: the `api-test` one-shot)

## Activity log

- 2026-06-30: Created in backlog by the Backend API Orchestrator. Triaged from the API-T-005 test-design report (`ecd0bf7`): the `_make_test_hash` helper in `test_admin_seed.py` became dead code once `admin_env` was routed through the shared `hash_password` fixture. Pure dead-code cleanup, P3, standalone. Routes through a `test-designer` dispatch (ADR-016), not an executor. Filed unlabelled per ADR-031.
