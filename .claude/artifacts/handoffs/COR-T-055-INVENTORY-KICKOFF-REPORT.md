## Deliverables completed

- Created `ai-infrastructure/backend-api/services.yml` with the `api` service entry (id: api, domain: 1, status: running, port 8123, base_url http://localhost:8123, 5 endpoints: /api/v1, /healthz, /docs, /redoc, /openapi.json). Values confirmed against `app/docker-compose.yml` (port 8123:8123, runtime `api`), `app/api/main.py` (routes and no docs_url override), and ADR-044 (docs at root, local/dev on, remote off).
- Created `ai-infrastructure/database/services.yml` with the `postgres` service entry (id: postgres, domain: 1, status: running, port 5432, base_url null, endpoints empty). Port confirmed from DATABASE_URL references in `app/docker-compose.yml` (postgresql://...@postgres:5432/corral). No credentials, no connection string; only host and port recorded per ADR-006 and the kickoff hard rule.
- Created `ai-infrastructure/project-manager/services.yml` with three service entries: `dashboard` (running, port 8420, / and /data.json endpoints), `mcp` (planned, workspace: mcp-server), and `frontend` (planned, workspace: frontend-ui). Dashboard port confirmed from `ai-infrastructure/project-manager/dashboard/docker-compose.yml` (8420:8420) and `entrypoint.sh` (python -m http.server 8420 --directory /served). Planned-service ownership follows ADR-045 decision 2.
- All three files validated with `yaml.safe_load`; no parse errors.

## Decisions made

- `schema_version` sits at the file top level (not per-entry), as pinned by the kickoff's "Decisions resolved" section. ADR-045 left field placement "not finalised"; the kickoff resolved it as file-top-level before dispatch.
- `ports` is a YAML inline list `[8123]` / `[5432]` / `[8420]` per the pinned content. This is the ADR-045 `port(s)` field, rendered as a list to allow multiple ports.
- Postgres `base_url` is `null` (not the empty string). The YAML `null` keyword was used to match the kickoff pin and the ADR-045 no-HTTP-service intent.
- Dashboard serves `/` and `/data.json` only. These two endpoints are the only paths the entrypoint.sh static server exposes from `/served`; no other API-style endpoints exist at the dashboard layer.

## Surprises

- `app/docker-compose.yml` does not publish a host port for `postgres` directly (only the `api` has `ports: ["8123:8123"]`). The Postgres port 5432 is an internal container port, visible only in the DATABASE_URL environment variables. The pinned value `ports: [5432]` records the internal port; this is consistent with ADR-045's intent (record the service's native port) and the kickoff pin. No discrepancy requiring escalation.
- `app/api/main.py` line 37 confirms `app = FastAPI(lifespan=lifespan)` with no `docs_url`, `redoc_url`, or `openapi_url` override, consistent with ADR-044's context ("FastAPI's documented default with no override"). The docs endpoints are implicit-default today; ADR-044 records the decision to make them explicit and gated. This is recorded in the services.yml note fields.

## Follow-ups

- ADR-045 Dispatch 2 (a separate kickoff): wire the dashboard ETL discovery (extend `etl.py` to read `ai-infrastructure/*/services.yml` files), author the services panel in the dashboard frontend, and add the drift-guard check (declared port vs `app/docker-compose.yml`). This is the explicit Dispatch 2 scope; COR-T-055 is the parent task. (COR-T candidate: Dispatch 2 of COR-T-055, per the kickoff's "Dispatch scope" decision.)
- ADR-044 implementation task (mentioned in ADR-044 Consequences 1): implement the env-driven docs gate in `app/api/main.py` and `app/api/settings.py`. Out-of-scope for this dispatch; flagged as a follow-up. (COR-T candidate: triage to orchestrator.)
- ADR-045 Consequences 1 and 2 reference forward-pointer notes to be added to ADR-037 and ADR-031. These notes were not authored here (the ADR files are read-only per the kickoff's "Files out of scope" section). (COR-T candidate: triage to orchestrator.)

## Files touched

- `ai-infrastructure/backend-api/services.yml` (created)
- `ai-infrastructure/database/services.yml` (created)
- `ai-infrastructure/project-manager/services.yml` (created)
- `.claude/artifacts/handoffs/COR-T-055-INVENTORY-KICKOFF-REPORT.md` (this report, created)

## Build / verification status

- All three files validated via `python3 -c "import yaml; yaml.safe_load(open(f))"` for each path: clean parse, no errors.
- No credentials or connection strings present in any file (grep confirmed).
- No em dashes in any file (grep confirmed).
- The dashboard services panel and the ETL reader are intentionally untouched: Dispatch 1 only authors the data files; Dispatch 2 wires the consumer. No services panel renders yet; this is expected.
- No compose run was performed: this dispatch authors data files only, no code changes, no container artifacts to verify. User verification: inspect the three YAML files; optionally run `python3 -c "import yaml; yaml.safe_load(open('ai-infrastructure/backend-api/services.yml'))"` (and analogously for the other two) to confirm parsability.
