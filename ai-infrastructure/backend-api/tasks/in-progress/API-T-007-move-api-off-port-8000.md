---
schema_version: 1
id: API-T-007
title: "Move the api service off port 8000 onto 8123 (host conflict with another local project)"
status: in-progress
labels: []
priority: P3
created: 2026-06-16
updated: 2026-06-16
epic: API-E-001
---

## Description

Another project on the developer's machine binds host port 8000 consistently, colliding with the api service's published port. Move the api off 8000 onto 8123, a full move (the container-internal listen port changes too, so 8000 appears nowhere in the api setup). Decided with the user: target port 8123, full move (not a host-only remap).

Three live edits across two files (the `8000` reference in the done API-T-004 task file is historical record and is left untouched):

1. `app/api/Dockerfile` (line 14): change the uvicorn CMD `--port 8000` to `--port 8123` (the container-internal listen port).
2. `app/docker-compose.yml` (the `api` service `ports`): change `"8000:8000"` to `"8123:8123"`.
3. `app/docker-compose.yml` (the `api` service `healthcheck`): change the probe URL `http://localhost:8000/healthz` to `http://localhost:8123/healthz`.

The `GET /healthz` route path itself does not change (it is a URL path, not a port); only the port the probe connects to changes. The api-test compose one-shot does not use the api service's port mapping, so the pytest suite is unaffected; verification is at runtime (the api service must still reach `healthy` and be reachable on host 8123). Routes through the dispatched-worker flow (config edit, single executor; no TDD two-phase: no new behavior, just a port reassignment).

References:
- `app/api/Dockerfile` (the uvicorn `--port` CMD)
- `app/docker-compose.yml` (the `api` service `ports` mapping and `healthcheck` probe URL added by API-T-004)
- `ai-infrastructure/project-manager/decisions/ADR-003-docker-compose-runtime.md` (compose-only run path)

## Activity log

- 2026-06-16: Created in backlog by the Backend API Orchestrator. Surfaced by the user: host port 8000 conflicts with another local project. Decided with the user: move to 8123, full move (container-internal port too). Linked to API-E-001 to match the API-T-004 precedent (api-service compose/infra polish under the epic). P3.
- 2026-06-16: Picked up; moved to in-progress. Decisions fully pinned (8123, full move); proceeding straight to the dispatched-worker flow (single executor, no TDD two-phase).
</content>
</invoke>
