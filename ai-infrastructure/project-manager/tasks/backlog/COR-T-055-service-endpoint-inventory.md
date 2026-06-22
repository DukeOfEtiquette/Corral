---
schema_version: 1
id: COR-T-055
title: "Author the service/endpoint inventory (structured, dashboard-consumed) and wire the dashboard to render it"
status: backlog
labels: []
priority: P2
created: 2026-06-22
updated: 2026-06-22
---

## Description

Author the project's service/endpoint inventory in the structured format decided by ADR-045, covering every running and planned server with its ports and endpoints (including docs/OpenAPI endpoints), and extend the dashboard to consume and render it. Standalone coordinator task (cross-cutting infra documentation that feeds the coordinator dashboard, COR-E-004). Surfaced 2026-06-22 when a "where are the servers and their docs endpoints documented?" question found there is no inventory anywhere.

**Gate cleared (2026-06-22): both governing ADRs are accepted.** `ai-infrastructure/project-manager/decisions/ADR-045-service-endpoint-inventory-structured.md` is accepted and pins the format, storage location, schema, ownership model, and dashboard-consumption mechanism this task implements (summarised in Scope below). `ai-infrastructure/project-manager/decisions/ADR-044-api-docs-openapi-endpoint-policy.md` is accepted and pins the api's docs-endpoint value: `/docs`, `/redoc`, `/openapi.json` at root, enabled in local/dev and disabled in remote (record this asserted value, not FastAPI's accidental default). This task is the authoring/wiring; the ADRs are the decision. Ready to pick up.

**Decided shape (per accepted ADR-045):**
- **Per-workspace ownership, generic discovery.** Each workspace owns a `services.yml` in its own tree (`ai-infrastructure/<workspace>/services.yml`); the ETL discovers them across all `ai-infrastructure/*/` workspaces, mirroring the existing `epics/` discovery in `collect_roadmap_from_files`. Adding a new department's service later requires no coordinator edit.
- **Coordinator holds planned-but-departmentless services.** mcp and frontend are declared in `ai-infrastructure/project-manager/services.yml` until their departments exist, then migrate; an explicit `workspace`/owner field renders their true ownership regardless of where declared.
- **Format:** pure YAML, one `services.yml` per workspace (not a per-service tree).
- **Schema per entry:** `schema_version`, `id`, `name`, `domain` (1/2), `status` (running/planned), `runtime`, `host`, `port(s)`, `base_url`, `endpoints` (list of `{path, kind}`, kind in api/docs/openapi/health/ui), `workspace`, `adrs`.
- **Drift guard built in this task (not deferred):** a declared-port-vs-`app/docker-compose.yml` consistency check joins the ADR-041 owned-but-advisory ETL warning family (warn-only, does not alter rendering).

### Scope (shape pinned by accepted ADR-045)

1. **Author the inventory** as per-workspace `services.yml` files in the ADR-045 schema, covering at least:
   - **api** (FastAPI, host 8123) -> `ai-infrastructure/backend-api/services.yml`: `/api/v1` route surface, `/healthz`, and the docs/OpenAPI endpoints per ADR-044 (`/docs`, `/redoc`, `/openapi.json` at root, enabled local / disabled remote).
   - **postgres** (5432) -> `ai-infrastructure/database/services.yml`.
   - **dashboard** (Vite/React + ETL, host 8420) -> `ai-infrastructure/project-manager/services.yml` (domain-2, coordinator-owned): currently documented only in a handoff report; this task gives it a standing structured entry.
   - **mcp** (FastMCP, Phase 3, planned) and **frontend** (React, Phase 4, planned): status planned, no built endpoints; declared in the coordinator `services.yml` until their departments exist (explicit `workspace` field records their true owner).
   Each entry carries the ADR-045 fields (id, name, domain 1/2, status running/planned, runtime/compose-service, host/port, base_url, endpoints with kinds, owning workspace, governing ADRs).
2. **Wire the dashboard ETL** (`ai-infrastructure/project-manager/dashboard/etl.py`) to discover every `ai-infrastructure/*/services.yml` generically (same loop shape as the `epics/` discovery in `collect_roadmap_from_files`), aggregate into `data.json`, and **render a services panel** in the dashboard UI (a new panel under `dashboard/src/panels/`).
3. **Build the drift-guard check** (per accepted ADR-045): a declared-port-vs-`app/docker-compose.yml` consistency check in the ETL warning family (ADR-041 lineage, owned-but-advisory, warn-only).

Routes through the dispatched-worker flow when picked up. The inventory authoring is coordinator structured-data work; the ETL + UI wiring is dashboard work (COR-E-004 territory) and may be split into its own dispatch at kickoff. Standalone (no epic); relates to COR-E-004.

**Subsumes the open doc-gap:** this closes the "no service/ports/endpoints inventory" gap and finally captures the dashboard server in a standing surface. It does not replace `docs/architecture/OVERVIEW.md` (the domain-1 runtime-shape narrative stays); the inventory is the structured, machine-consumed companion.

### Acceptance tests

(a) The inventory exists as per-workspace `services.yml` files in the ADR-045 schema, covering api, postgres, dashboard, mcp, frontend, with each entry's `workspace` field naming its true owner.
(b) The dashboard ETL discovers every `ai-infrastructure/*/services.yml` generically and emits the aggregated inventory into `data.json` without error.
(c) The dashboard renders a services panel listing each service with its port(s) and endpoints (including the api docs endpoint per ADR-044).
(d) Planned services (mcp, frontend) appear with status planned and no asserted live endpoints.
(e) The drift-guard check fires an advisory warning when a declared port diverges from `app/docker-compose.yml`, and is silent when they match (verify both directions).

References:
- `ai-infrastructure/project-manager/decisions/ADR-045-service-endpoint-inventory-structured.md` (the gating decision: format, storage, schema, consumption)
- `ai-infrastructure/project-manager/decisions/ADR-044-api-docs-openapi-endpoint-policy.md` (governs the api docs-endpoint value the inventory records)
- `ai-infrastructure/project-manager/decisions/ADR-037-work-item-storage-representation.md` (the structured-YAML-as-first-class-files precedent to mirror)
- `ai-infrastructure/project-manager/decisions/ADR-039-status-derive-activity-surface.md` and `ai-infrastructure/project-manager/decisions/ADR-040-derive-full-status-narrative.md` (the derived dashboard-surface model)
- `ai-infrastructure/project-manager/dashboard/etl.py` (the ETL to extend; already discovers + yaml.safe_loads epic/phase files), `ai-infrastructure/project-manager/dashboard/src/` (the UI to add the panel to)
- `ai-infrastructure/project-manager/docs/architecture/OVERVIEW.md` (the domain-1 runtime-shape narrative this complements, not replaces)
- `app/docker-compose.yml` (api 8123, postgres 5432, service definitions), `app/api/main.py` (the FastAPI app and its default docs endpoints)

## Activity log

- 2026-06-22: Created in backlog by the Project Manager Orchestrator, at user direction. Surfaced by a "where are the servers and their docs endpoints documented?" question that found no inventory exists (OVERVIEW lists web-app services by role only, no ports/endpoints; the dashboard server is in no standing doc; the api serves Swagger by FastAPI default, undocumented). Filed P2, standalone, GATED on ADR-045 (structured-format decision) and informed by ADR-044 (api docs-endpoint policy). Unlabelled per ADR-031.
- 2026-06-22: Gate cleared. ADR-044 and ADR-045 both accepted by the Project Manager Orchestrator. Baked the pinned decisions into Scope and Acceptance tests (per-workspace `services.yml` + generic ETL discovery; coordinator holds planned mcp/frontend; YAML schema; drift-guard check built in this task per the ADR-041 lineage; api docs endpoint at root, local-on/remote-off per ADR-044). Task is execution-ready; routes through the dispatched-worker flow when picked up.
