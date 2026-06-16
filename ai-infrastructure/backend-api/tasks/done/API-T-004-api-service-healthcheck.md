---
schema_version: 1
id: API-T-004
title: "Add a healthcheck to the api compose service (enable depends_on: service_healthy)"
status: done
labels: []
priority: P3
created: 2026-06-15
updated: 2026-06-16
epic: API-E-001
---

## Description

Follow-up surfaced by the API-T-002 implementation (committed `a40cf3d`). The `api` runtime service added to `app/docker-compose.yml` exposes port 8000 but has no healthcheck, so downstream services cannot gate on it via `depends_on: { api: { condition: service_healthy } }`. Add a healthcheck mirroring the `postgres` service's pattern (a `CMD-SHELL` probe), so future services (the `mcp` service in Phase 3, or a cross-service end-to-end test harness) can wait for the api to be ready.

Anticipated decision for the kickoff: the probe should hit a cheap, un-authenticated endpoint rather than an auth-gated route; that likely means adding a lightweight liveness route (e.g. `GET /healthz`) to `app/api/main.py`. Decide whether to add that route or probe an existing cheap path. Routes through the dispatched-worker flow (compose + possibly a one-line api route). Part of the API-E-001 (Backend API) epic: compose/infra polish supporting the api service alongside its auth-and-endpoints capability. P3.

References:
- `app/docker-compose.yml` (the `api` service to add the healthcheck to; the `postgres` service's healthcheck is the pattern to mirror)
- `app/api/main.py` (where a `/healthz` liveness route would live, if added)
- `ai-infrastructure/project-manager/decisions/ADR-003-docker-compose-runtime.md` (compose-only run path)

## Activity log

- 2026-06-15: Created in backlog by the Backend API Orchestrator. Surfaced as a follow-up in the API-T-002 implementation report (`a40cf3d`): the `api` service has no healthcheck, blocking `depends_on: service_healthy` for downstream services. P3, standalone. Unlabelled per ADR-031.
- 2026-06-16: Picked up by the Backend API Orchestrator; moved to in-progress. Resolving the healthcheck-probe-target decision before drafting the kickoff for the dispatched-worker flow.
- 2026-06-16: Linked to epic API-E-001 at the user's direction (previously filed standalone); reconciled the description's standalone language. Probe-target decision resolved: add a dedicated top-level `GET /healthz` liveness route (200, `{"status": "ok"}`, unauthenticated, no DB) and probe it. Dispatched as ADR-016 TDD two-phase (test-design then implementation).
- 2026-06-16: Done. Both TDD phases dispatched and verified against disk (suite green, 22 passed under the api-test one-shot; no protected test file touched). Deliverable + handoff pair committed in `91607d9`. Moved to done.
