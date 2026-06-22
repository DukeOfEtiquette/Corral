# COR-T-055 Dispatch 1: author the per-workspace services.yml inventory files

## Target

This is AI-infrastructure work (ADR-005, domain 2): you are authoring the structured service/endpoint inventory data that the project-manager dashboard will later consume. COR-T-055 runs as a two-dispatch flow. This is Dispatch 1, and its entire scope is the three per-workspace `services.yml` inventory files defined below. Dispatch 2 is a separate, later kickoff that wires the dashboard ETL discovery, the services panel, and the drift-guard check. You do not touch any ETL or dashboard source code in this dispatch.

The format is fully pinned by accepted ADR-045 (`ai-infrastructure/project-manager/decisions/ADR-045-service-endpoint-inventory-structured.md`): pure YAML, one `services.yml` per workspace, mirroring the structured-YAML-as-first-class-files precedent in ADR-037. Every value below is verified and provided; your job is to confirm the cited sources, then echo the pinned content exactly, not to reconstruct values from scratch.

## Decisions resolved by the Orchestrator

- **Dispatch scope.** Dispatch 1 authors ONLY the three `services.yml` files. The dashboard ETL discovery, the services panel, and the drift-guard check are Dispatch 2 (a separate later kickoff). Do not touch any ETL or dashboard source code here. Rationale: COR-T-055 is split so the data lands before the consumer is wired.
- **File format (ADR-045).** Pure YAML, one `services.yml` per workspace. Each file is a top-level mapping with `schema_version: 1` and a `services:` list of one or more service entries. `schema_version` sits at the file top level, not per-entry. Rationale: this finalises the ADR-045 framed schema, which explicitly left field placement "not finalised".
- **Service entry keys.** Each service entry carries: `id`, `name`, `domain` (1 = web-app, 2 = ai-infra), `status` (`running` | `planned`), `runtime` (compose service name or process), `host`, `ports` (a YAML list), `base_url`, `workspace` (owning department/coordinator slug), `adrs` (list of governing ADR numbers), and `endpoints` (a list of `{path, kind}` mappings where `kind` is one of `api` / `docs` / `openapi` / `health` / `ui`; an endpoint may carry an optional `note` string). Rationale: pinned by ADR-045 as the inventory schema.
- **Postgres is not an HTTP service.** In `ai-infrastructure/database/services.yml`, `base_url` is `null` and `endpoints` is an empty list. Do NOT encode the compose connection string: it contains a password, and the secrets rule in `./CLAUDE.md` plus ADR-006 forbid credentials in any tracked file. Record only host and port. Rationale: credential-safety is a hard rule.
- **Planned-service ownership.** In the coordinator file (`ai-infrastructure/project-manager/services.yml`), the two planned services (`mcp`, `frontend`) carry a `workspace` field naming their TRUE owner (`mcp-server`, `frontend-ui`) even though they are declared in the coordinator file because their departments do not exist yet. This is intentional per ADR-045 decision 2 (decouples where-declared from owned-by), so the Dispatch-2 dashboard panel renders their real ownership.
- **No services panel yet.** Dispatch 1 does not wire the ETL, so the dashboard will not yet render a services panel. That is expected and is Dispatch 2's job.

## Deliverables

Create exactly three new files with the pinned content below. Confirm each verified value against its cited source (see References), then echo the content exactly. No other files are created or modified.

### File 1: `ai-infrastructure/backend-api/services.yml`

```yaml
schema_version: 1
services:
  - id: api
    name: Corral API
    domain: 1
    status: running
    runtime: api
    host: localhost
    ports: [8123]
    base_url: http://localhost:8123
    workspace: backend-api
    adrs: [10, 44]
    endpoints:
      - {path: /api/v1, kind: api}
      - {path: /healthz, kind: health}
      - {path: /docs, kind: docs, note: "enabled in local/dev, disabled in remote (ADR-044)"}
      - {path: /redoc, kind: docs, note: "enabled in local/dev, disabled in remote (ADR-044)"}
      - {path: /openapi.json, kind: openapi, note: "enabled in local/dev, disabled in remote (ADR-044)"}
```

### File 2: `ai-infrastructure/database/services.yml`

```yaml
schema_version: 1
services:
  - id: postgres
    name: Postgres
    domain: 1
    status: running
    runtime: postgres
    host: localhost
    ports: [5432]
    base_url: null
    workspace: database
    adrs: [2, 12]
    endpoints: []
```

Postgres is not an HTTP service: `base_url` is `null` and `endpoints` is empty. Record only host and port; never the compose connection string (it carries a password).

### File 3: `ai-infrastructure/project-manager/services.yml`

The coordinator file: the running dashboard plus the two planned services whose departments do not exist yet, declared here per ADR-045 decision 2.

```yaml
schema_version: 1
services:
  - id: dashboard
    name: Project-Manager Dashboard
    domain: 2
    status: running
    runtime: dashboard
    host: localhost
    ports: [8420]
    base_url: http://localhost:8420
    workspace: project-manager
    adrs: [27, 37, 39, 40]
    endpoints:
      - {path: /, kind: ui}
      - {path: /data.json, kind: api}
  - id: mcp
    name: Corral MCP Server (FastMCP)
    domain: 1
    status: planned
    runtime: mcp
    host: null
    ports: []
    base_url: null
    workspace: mcp-server
    adrs: [4, 10]
    endpoints: []
  - id: frontend
    name: Corral Kanban UI (React)
    domain: 1
    status: planned
    runtime: frontend
    host: null
    ports: []
    base_url: null
    workspace: frontend-ui
    adrs: [1]
    endpoints: []
```

The `workspace` field on the `mcp` and `frontend` entries names the true owner (`mcp-server`, `frontend-ui`), not the coordinator, even though they are declared in this coordinator file. This is intentional per ADR-045.

## Files in scope

- `ai-infrastructure/backend-api/services.yml` (create)
- `ai-infrastructure/database/services.yml` (create)
- `ai-infrastructure/project-manager/services.yml` (create)

## Files out of scope

- `ai-infrastructure/project-manager/dashboard/etl.py` (Dispatch 2 only; do not touch)
- `ai-infrastructure/project-manager/dashboard/src/` (Dispatch 2 only; do not touch)
- `app/docker-compose.yml`, `app/api/` (read-only references; do not modify)
- The ADR files (already accepted; do not edit)

## References

Read each reference to confirm the pinned values before echoing them; the values are provided so you verify, not reconstruct.

- `docs/ai-orchestration/roles/EXECUTOR-ROLE.md` (your role and the six-section closing report shape)
- `ai-infrastructure/project-manager/decisions/ADR-045-service-endpoint-inventory-structured.md` (the accepted schema, format, and ownership model this implements)
- `ai-infrastructure/project-manager/decisions/ADR-044-api-docs-openapi-endpoint-policy.md` (the api docs-endpoint values: `/docs`, `/redoc`, `/openapi.json` at root, local-on / remote-off)
- `app/docker-compose.yml` (api port 8123 + runtime service `api`; postgres port 5432 + runtime service `postgres`)
- `app/api/main.py` (the api endpoint paths: `/api/v1/...`, `/healthz`, and the FastAPI default `/docs` + `/redoc` + `/openapi.json`)
- `ai-infrastructure/project-manager/dashboard/docker-compose.yml` (dashboard port 8420 + runtime service `dashboard`)
- `ai-infrastructure/project-manager/dashboard/entrypoint.sh` (dashboard serves `/` (SPA) and `/data.json` via `python -m http.server 8420 --directory /served`)

## Related tasks and ADRs

- COR-T-055 - the parent task; this is its Dispatch 1.
- ADR-045 - the accepted decision defining the inventory format, schema, and per-workspace ownership.
- ADR-044 - governs the api docs-endpoint values recorded here.
- ADR-037 - the structured-YAML-as-first-class-files precedent the format mirrors.

## Hard rules

- **No credentials in any file.** Postgres `base_url` is `null`; record only host and port. Never write the compose connection string or any password into a `services.yml` (the secrets rule in `./CLAUDE.md` and ADR-006).
- **Echo the pinned content; do not reconstruct.** Confirm each verified value against its cited source, then write the content exactly as given above. If a source disagrees with a pinned value, do not silently adjust it: surface the discrepancy.
- **Stay within the three in-scope files.** Create only the three `services.yml` files. Do not touch any ETL, dashboard, or app source.
- **Verification expectations:** each of the three files is valid YAML and parses with `yaml.safe_load`; each matches the pinned schema (file-level `schema_version` plus a `services` list, each entry carrying the specified keys); no credentials or connection strings appear in any file (postgres `base_url` is `null`). Note in your closing report that the dashboard services panel and the ETL are intentionally untouched (that is Dispatch 2's job), so no panel renders yet.

## Executor pointer

You are the dispatched `executor` (ADR-028). Universal executor conventions (writing rules, run policy, git boundaries, the pinned six-section report shape) live in `docs/ai-orchestration/roles/EXECUTOR-ROLE.md`; follow them rather than expecting them restated here. Write your closing report to the path derived per EXECUTOR-ROLE.md, section "Report shape" (the kickoff basename with `-REPORT.md`, in the kickoff's own directory).
