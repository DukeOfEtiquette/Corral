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

**GATED on ADR-045.** Do not start until `ai-infrastructure/project-manager/decisions/ADR-045-service-endpoint-inventory-structured.md` is accepted: that ADR decides the format, storage location, schema, and dashboard-consumption mechanism this task implements. This task is the authoring/wiring; ADR-045 is the decision. Also informed by `ai-infrastructure/project-manager/decisions/ADR-044-api-docs-openapi-endpoint-policy.md`: the api's docs-endpoint entry in the inventory must reflect whatever ADR-044 decides, not FastAPI's accidental default. If COR-T-055 is picked up while ADR-044 is still pending, record the api docs endpoint as "per ADR-044 (pending)" rather than asserting a value.

### Scope (final shape depends on ADR-045)

1. **Author the inventory** in the ADR-045 structured format, covering at least:
   - **api** (FastAPI, host 8123): `/api/v1` route surface, `/healthz`, and the docs/OpenAPI endpoints per ADR-044.
   - **postgres** (5432).
   - **dashboard** (Vite/React + ETL, host 8420): currently documented only in a handoff report; this task gives it a standing structured entry.
   - **mcp** (FastMCP, Phase 3, planned): status planned; no built endpoints yet.
   - **frontend** (React, Phase 4, planned): status planned.
   Each entry carries the fields ADR-045 settles (id, name, domain 1/2, status running/planned, runtime/compose-service, host/port, base_url, endpoints with kinds, owning workspace, governing ADRs).
2. **Wire the dashboard ETL** (`ai-infrastructure/project-manager/dashboard/etl.py`) to read the inventory files into `data.json`, mirroring how it already discovers and `yaml.safe_load`s epic/phase YAML (ADR-037/039/040), and **render a services panel** in the dashboard UI.
3. **(Decide at kickoff, per ADR-045)** whether to add a drift-guard consistency check (declared port vs `app/docker-compose.yml`) into the ADR-041 check lineage, or defer it.

Routes through the dispatched-worker flow when picked up. The inventory authoring is coordinator structured-data work; the ETL + UI wiring is dashboard work (COR-E-004 territory) and may be split into its own dispatch at kickoff. Standalone (no epic); relates to COR-E-004.

**Subsumes the open doc-gap:** this closes the "no service/ports/endpoints inventory" gap and finally captures the dashboard server in a standing surface. It does not replace `docs/architecture/OVERVIEW.md` (the domain-1 runtime-shape narrative stays); the inventory is the structured, machine-consumed companion.

### Acceptance tests (refine against the accepted ADR-045 schema)

(a) The inventory exists in the ADR-045-decided format and location, validating against its schema, and covers api, postgres, dashboard, mcp, frontend.
(b) The dashboard ETL parses the inventory without error and emits it into `data.json`.
(c) The dashboard renders a services panel listing each service with its port(s) and endpoints (including the api docs endpoint per ADR-044).
(d) Planned services (mcp, frontend) appear with status planned and no asserted live endpoints.

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
