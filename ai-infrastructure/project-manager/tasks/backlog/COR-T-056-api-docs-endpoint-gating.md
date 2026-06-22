---
schema_version: 1
id: COR-T-056
title: "Implement ADR-044 api docs/OpenAPI endpoint gating (explicit URLs, env-gated off for remote)"
status: backlog
labels: []
priority: P2
created: 2026-06-22
updated: 2026-06-22
---

## Description

Implement the policy accepted in `ai-infrastructure/project-manager/decisions/ADR-044-api-docs-openapi-endpoint-policy.md`: configure the FastAPI documentation endpoints explicitly instead of inheriting the framework default, and gate their exposure by environment. Web-app (domain-1) work against the `api` service. Standalone coordinator-filed task (no epic); the deliverable routes through the dispatched-worker flow when picked up.

Currently `app/api/main.py:37` constructs `app = FastAPI(lifespan=lifespan)` with no `docs_url`/`redoc_url`/`openapi_url` override, so Swagger (`/docs`), ReDoc (`/redoc`), and the schema (`/openapi.json`) are served at root, always on, undocumented (verified on disk 2026-06-22 at ADR-044 acceptance).

### Scope (per the accepted ADR-044 decision)

1. **Placement stays at root.** Do NOT relocate the docs under `/api/v1`. Keep `/docs`, `/redoc`, `/openapi.json` at the FastAPI default root paths.
2. **Single env-driven gate** controlling all three endpoints together. Enabled in local/dev (docs stay on with no `.env` change), disabled in remote deployment (all three off: `docs_url=None`, `redoc_url=None`, `openapi_url=None`). No behind-auth variant.
3. **Mechanism** (left to this task by ADR-044, consistent with ADR-010's implementation-phase carve-out): add an env-read accessor in `app/api/settings.py` mirroring the existing `get_cookie_secure()` boolean parse, defaulting to enabled; read it in `app/api/main.py` at app construction to pass the three URL kwargs conditionally.

### Acceptance tests

(a) With the gate enabled (default / local), `/docs`, `/redoc`, and `/openapi.json` are served.
(b) With the gate disabled (remote setting), all three return 404.
(c) The docs paths remain at root, not under `/api/v1`.
(d) The gate defaults to enabled so local/dev needs no `.env` change.

References:
- `ai-infrastructure/project-manager/decisions/ADR-044-api-docs-openapi-endpoint-policy.md` (the accepted policy this implements)
- `ai-infrastructure/project-manager/decisions/ADR-010-api-shape-and-mcp-data-path.md` (the `/api/v1` prefix; implementation-detail carve-out)
- `ai-infrastructure/project-manager/decisions/ADR-003-docker-compose-runtime.md` and `ai-infrastructure/project-manager/decisions/ADR-006-admin-bootstrap-env-hash.md` (remote deployment posture and the do-not-over-expose ethos)
- `app/api/main.py` (the FastAPI app construction at line 37), `app/api/settings.py` (the env-accessor pattern, e.g. `get_cookie_secure()`)
- `ai-infrastructure/project-manager/tasks/backlog/COR-T-055-service-endpoint-inventory.md` (records the api docs-endpoint value this task makes real)

## Activity log

- 2026-06-22: Created in backlog by the Project Manager Orchestrator at the ADR-044 acceptance close. Filed as the implementation follow-up that ADR-044 Consequence 1 anticipates. P2, standalone, web-app domain, unlabelled per ADR-031.
