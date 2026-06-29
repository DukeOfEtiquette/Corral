---
schema_version: 1
id: API-T-006
title: "api devex hardening: .env.example placement, missing-admin-creds fail-fast test, gen-admin-hash.sh helper"
status: in-progress
labels: []
priority: P3
created: 2026-06-15
updated: 2026-06-29
---

## Description

Devex / operability hardening for the `api` service, surfaced while bringing API-T-002 up locally (the auth-service close plus the first real `docker compose up api`). Three related items; standalone task (operability polish, not part of API-E-001's auth-and-endpoints capability). Routes through the dispatched-worker flow, with the per-item routing noted below.

1. **Reconcile `.env.example` placement with where compose reads `.env`.** The templates live at `app/api/.env.example` and `app/db/.env.example`, but `docker compose -f app/docker-compose.yml` interpolates `${ADMIN_EMAIL}` / `${ADMIN_PASSWORD_HASH}` from `app/.env` (the compose project directory) -- verified empirically. The documented template location does not match where the values are actually read. Fix: add an `app/.env.example` at the compose project dir (variable names only, per ADR-006) and/or clearly document that the runtime env file is `app/.env`; reconcile or relocate `app/api/.env.example` so operators are not misled. Executor (compose/docs).

2. **Lock the missing-admin-creds fail-fast with a test.** The api correctly refuses to boot when `ADMIN_EMAIL` (or `ADMIN_PASSWORD_HASH`) is unset (`settings.get_admin_email()` raises; the lifespan seed fails fast). API-T-002's suite never covered this -- its fixtures always inject the env via `monkeypatch.setenv`, so the path was uncovered until a real `up api` hit it (COR-09). Add a test that `seed_admin()` / startup raises a clear error when the admin env is absent. This edits the protected `app/api/tests/` suite, so it routes through a **`test-designer` dispatch (ADR-016)**, not an executor.

3. **Formalize the `gen-admin-hash.sh` helper.** `app/api/gen-admin-hash.sh` was written as an orchestrator-direct one-off (committed under this task): it writes `app/.env` from `--email` / `--password` flags, argon2id-hashes the password via the api image (no host Python), escapes `$` to `$$` so compose does not interpolate the hash, and warns when either credential is unset. Review and own it as a tracked deliverable: confirm the approach, decide whether it warrants a smoke test (it is shell, outside the pytest TDD flow), and consider documenting the reseed gotcha (`seed_admin` is idempotent, so re-running the script + restarting does NOT update an already-seeded admin -- a `down -v` reset is needed) in the helper or an api README.

Out of scope: the COR-09 boot-smoke promotion into `docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md` is coordinator / process work (a future coordinator decision), not this backend-api task.

References:
- `app/api/gen-admin-hash.sh` (the helper to formalize), `app/docker-compose.yml` (compose env interpolation), `app/api/.env.example` + `app/db/.env.example` (the misplaced templates)
- `app/api/settings.py` (`get_admin_email` fail-fast), `app/api/admin_seed.py` (idempotent seed), `app/api/tests/` (the protected suite the fail-fast test joins)
- `ai-infrastructure/project-manager/decisions/ADR-006-admin-bootstrap-env-hash.md`, `ai-infrastructure/project-manager/decisions/ADR-016-testing-strategy-test-designer-agent.md`, `ai-infrastructure/project-manager/decisions/ADR-003-docker-compose-runtime.md`
- `ai-infrastructure/project-manager/OBSERVATIONS.md` (COR-09, the runtime-gate observation this hardens against)

## Activity log

- 2026-06-15: Created in backlog by the Backend API Orchestrator. Surfaced bringing API-T-002 up locally: the `.env.example` placement mismatch, the uncovered missing-`ADMIN_EMAIL` fail-fast path (COR-09), and the `gen-admin-hash.sh` one-off helper needing proper ownership. Standalone, P3. The helper is committed under this task as an orchestrator-direct one-off ($$-escaped, docker-based hashing); this task tracks its formalization. Item 2 (the fail-fast test) routes through a test-designer dispatch (ADR-016). Unlabelled per ADR-031.
- 2026-06-29: Picked up by the Backend API Orchestrator; moved to in-progress in worktree `api-t-006-devex-hardening`. Decisions pinned with the user: (1) item 1 produces a SINGLE tracked `app/.env.example` at the compose project dir documenting every var the stack drives today (required: ADMIN_EMAIL, ADMIN_PASSWORD_HASH; optional w/ defaults: DATABASE_URL, API_HOST_PORT, API_DOCS_ENABLED, SESSION_COOKIE_NAME, SESSION_LIFETIME_SECONDS, SESSION_COOKIE_SECURE), deleting the scattered `app/api/.env.example` and `app/db/.env.example`; the unwired vars (API_DOCS_ENABLED, SESSION_*) get `${VAR:-default}` passthrough on the compose `api` service so `app/.env` genuinely drives them. Verified: nothing consumes any `.env.example` (no `env_file:` in compose; the only references are `.dockerignore` exclusions). (2) item 3: NO shell smoke test for `gen-admin-hash.sh`; document the reseed gotcha in the helper header (no new README, per the global docs-placement rule). Cross-dept follow-up to file: unify DATABASE_URL/postgres creds across the `migrate`/`test`/`postgres` compose services from `app/.env` (database department). Routing: items 1+3 via one `executor` dispatch; item 2 via one `test-designer` dispatch (ADR-016).
