---
schema_version: 1
id: DB-T-006
title: "unify DATABASE_URL and postgres credentials across compose services from app/.env"
status: done
labels: []
priority: P3
created: 2026-06-29
updated: 2026-06-30
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
- 2026-06-30: Picked up by the Database Orchestrator; moved to in-progress. Design choices resolved with the user: (1) drive constituent `POSTGRES_USER`/`POSTGRES_PASSWORD`/`POSTGRES_DB` from app/.env with dev defaults and assemble every `DATABASE_URL` in-string from those same vars (keeps postgres service and connection string in sync by construction); (2) `migrate` and `api` honor a top-level `${DATABASE_URL:-<assembled>}` external override, while `test`/`test-roundtrip`/`api-test` assemble from `POSTGRES_*` only with no external override (preserves API-T-006's test-isolation intent). Routing through the dispatched-worker flow next.
- 2026-06-30: Done. Executed via the dispatched-worker flow (kickoff `DB-T-006-KICKOFF.md`; executor report `DB-T-006-KICKOFF-REPORT.md`). `app/docker-compose.yml` and `app/.env.example` unified per both resolved decisions, committed in `f42c797` (deliverable) and `7ff51c7` (report), integrated to master in merge `0dc5e70`. Orchestrator independently re-derived all three `docker compose config` verification scenarios (default render, `POSTGRES_PASSWORD` sync-by-construction, external-`DATABASE_URL` isolation) against disk; all passed. kickoff-checker (R1-R8), prelaunch (W1), and close checker (W2) all PASS. Moved to done.
