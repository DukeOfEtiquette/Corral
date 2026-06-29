---
schema_version: 1
id: DB-T-006
title: "unify DATABASE_URL and postgres credentials across compose services from app/.env"
status: backlog
labels: []
priority: P3
created: 2026-06-29
updated: 2026-06-29
---

## Description

Surfaced during API-T-006 (item 1), cross-department triage. API-T-006 made the compose `api` service read `DATABASE_URL` from `app/.env` via `${DATABASE_URL:-<dev default>}`, but deliberately left the database-owned services untouched to stay in the backend-api lane. The `postgres`, `migrate`, `test`, `test-roundtrip`, and `api-test` services in `app/docker-compose.yml` still hardcode `DATABASE_URL: postgresql://corral:devpassword@postgres:5432/corral`, and the `postgres` service hardcodes `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB`. To complete the single-source-of-truth goal (so `app/.env` drives the whole stack), drive these from `app/.env` with the same `${VAR:-default}` dev-default pattern, keeping the postgres credentials and the assembled `DATABASE_URL` in sync (a desync between `POSTGRES_*` and `DATABASE_URL` would break connectivity).

Design choices to resolve at pickup: whether to drive a single `DATABASE_URL` or the constituent `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` and assemble the URL from them (the latter keeps the postgres service and the connection string in sync by construction); and whether the `test` / `api-test` services should be overridable at all or pinned to the compose-stack DB for test isolation (API-T-006 pinned `api-test` deliberately). Add any newly-driven vars to `app/.env.example` (the consolidated template) as optional overrides once wired.

References:
- `app/docker-compose.yml` (the `postgres` / `migrate` / `test` / `test-roundtrip` / `api-test` services with hardcoded DATABASE_URL and creds)
- `app/.env.example` (the consolidated template to extend with any newly-driven vars)
- `ai-infrastructure/backend-api/tasks/done/API-T-006-api-devex-hardening.md` (origin: the api-service env wiring that deferred the DB side)
- `ai-infrastructure/project-manager/decisions/ADR-006-admin-bootstrap-env-hash.md` (secrets via env only), `ai-infrastructure/project-manager/decisions/ADR-003-docker-compose-runtime.md` (compose run path)

## Activity log

- 2026-06-29: Filed in backlog (database department) by the Backend API Orchestrator as a cross-department triaged follow-up from API-T-006. API-T-006 wired only the `api` service's DATABASE_URL from app/.env to stay in the backend-api lane; unifying the database-owned compose services is database-department scope. Standalone, P3, unlabelled per ADR-031.
