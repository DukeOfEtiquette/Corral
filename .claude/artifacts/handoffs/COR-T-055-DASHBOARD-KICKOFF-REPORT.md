## Deliverables completed

- **ETL discovery (`etl.py`):** `collect_services(repo_root)` added. Generically iterates `ai-infrastructure/` subdirectories, loads `services.yml` from each, aggregates a flat list. Tolerant parsing: skips unreadable/malformed files and files without a `services:` list. Mirrors the `collect_roadmap_from_files` epic-discovery loop exactly (same directory walk, same `yaml.safe_load`, same `try/except (OSError, yaml.YAMLError)` + `continue` pattern).

- **ETL drift-guard check (in `etl.py`):** `parse_compose_host_ports(compose_path)` parses `app/docker-compose.yml` for host-side ports per service. `collect_services` applies the check: for each service entry whose `runtime` matches a compose service that publishes a host port, if the declared `ports` list does not include that published host port, `warning` is set to a message naming declared vs compose value. Services not matched in compose, or matched to a compose service with no host port, get `warning: null` by design.

- **Services key in `data.json`:** `collect_services(repo_root)` called in `run_etl`; result stored as `services` variable and emitted as top-level `"services"` key in the `data` dict. Verified: 5 services (`api`, `postgres`, `dashboard`, `mcp`, `frontend`), sorted running-first then workspace then id.

- **ETL docstring updated:** Added source bullet (i) for `services.yml` inventory (ADR-045) and `services:` entry to the JSON contract shape section.

- **`WATCH_PATTERNS` not changed:** The pattern `re.compile(r".*/ai-infrastructure/.*\.yml$")` already matches `services.yml` files, so `services.yml` edits already trigger rebuilds. Confirmed in `etl.py` lines 1607-1608 (original numbering). No edit needed; stated here per kickoff instruction.

- **`ServicesPanel.jsx` created:** `ai-infrastructure/project-manager/dashboard/src/panels/ServicesPanel.jsx`. Takes a `services` prop; renders a `.card` with `<h3>Services</h3>`, `.table-scroll`, and a `.dept-table` with columns: Service (name + id), Domain, Status, Host:Port, Endpoints, Owner. Mirrors `DepartmentsPanel.jsx` structure exactly (`.card` > `<h3>` > `.table-scroll` > `<table>`). Planned services use `dept-planned` class; warning-carrying services use `dept-no-epic` class with the `warning` text as `title` tooltip, mirroring `DepartmentsPanel`'s `dept-no-epic` + `title` pattern.

- **`LandingView.jsx` wired:** `ServicesPanel` imported and rendered as `<ServicesPanel services={data.services} />` inside `main-content`, placed before `AgentsPanel` and `RoadmapPanel` (near the roster panels, implementer's discretion per kickoff).

- **No new CSS added:** `dept-planned` and `dept-no-epic` are reused from `styles.css` (confirmed present at lines 365 and 374). No new classes were needed.

## Decisions made

- **Placement of `<ServicesPanel>` in `LandingView.jsx`:** Placed immediately after the roster row (before `AgentsPanel`), grouping it with the other roster/inventory panels. The kickoff explicitly delegated this as implementer's discretion with no contract impact.

- **Port normalization in `collect_services`:** The `ports` field emitted uses `[int(p) for p in declared_ports if ...]` to normalise to integers consistently. The `parse_compose_host_ports` function also emits integer sets. This ensures the drift-guard integer comparison is type-safe.

## Surprises

- **`ports` list in YAML can contain integers or strings:** The `services.yml` files store ports as bare YAML integers (e.g., `[8123]`), which `yaml.safe_load` returns as Python `int`. The port normalization in `collect_services` handles both `int` and stringifiable values via the `str(p).isdigit()` guard, matching the data as actually stored.

- **`app/docker-compose.yml` has no published host port for `postgres`:** Confirmed on read -- the `postgres` service has no `ports:` list at all. So `postgres` gets `warning: null` correctly (not in `compose_host_ports`). The `api` service publishes `"8123:8123"`, confirmed as a string entry in the `ports:` list.

## Follow-ups

- **Visual confirmation of the Services panel rendering:** The `ServicesPanel` renders pending the Orchestrator's user-facing visual check via `docker compose up` in `ai-infrastructure/project-manager/dashboard/`. The panel logic is verified at the ETL/data layer; the browser render requires the compose dashboard service. Triage to orchestrator for the close visual check.

- **Full Option C derivation (auto-derive ports from compose):** ADR-045 consequence 8 notes that auto-deriving ports and routes from compose plus FastAPI introspection is a future enhancement layer. The drift guard is the first step. Triage to orchestrator as a COR-T candidate when the API surface stabilizes.

- **Dashboard compose file services.yml:** The `dashboard` service is defined in `ai-infrastructure/project-manager/dashboard/docker-compose.yml`, not `app/docker-compose.yml`. The kickoff pinned this as out-of-scope for the first-cut drift guard (ADR-045 consequence 8). No warning fires for `dashboard`, which is correct. A future enhancement could extend the check to the dashboard compose file. Triage to orchestrator as a COR-T candidate.

## Files touched

- `ai-infrastructure/project-manager/dashboard/etl.py` (modified: docstring updated, `parse_compose_host_ports` and `collect_services` functions added, `collect_services` call in `run_etl`, `services` key added to `data` dict)
- `ai-infrastructure/project-manager/dashboard/src/panels/ServicesPanel.jsx` (created)
- `ai-infrastructure/project-manager/dashboard/src/views/LandingView.jsx` (modified: import added, `<ServicesPanel services={data.services} />` render added)
- `.claude/artifacts/handoffs/COR-T-055-DASHBOARD-KICKOFF-REPORT.md` (this report, dual-channel write)

No `services.yml` files were modified. Confirmed via `git status`: all three (`ai-infrastructure/backend-api/services.yml`, `ai-infrastructure/database/services.yml`, `ai-infrastructure/project-manager/services.yml`) appear as untracked (their pre-existing Dispatch 1 state), with zero modifications.

## Build / verification status

- **ETL verified:** Ran `python3 etl.py` with `REPO_ROOT` and `SERVED_DIR` set. `data.json` gained a `services` key listing all 5 services (`api`, `postgres`, `dashboard`, `mcp`, `frontend`) with source fields and `warning` field. All warnings are null on clean data (api port 8123 matches compose 8123:8123; postgres has no compose host port; dashboard not in `app/docker-compose.yml`; planned services not in compose).

- **Drift-guard spot-test verified:** Temporarily changed `ai-infrastructure/backend-api/services.yml` `ports: [8123]` to `ports: [9999]`, re-ran ETL, confirmed `api` `warning` fired: `"Port drift: service 'api' declares ports [9999] but compose publishes host port 8123 (ADR-045)."`. Reverted the change immediately. Confirmed via `git status` that no `services.yml` file is modified at close.

- **React panel and wiring:** `ServicesPanel.jsx` and the `LandingView.jsx` import/render are authored and in place. Visual render confirmation requires the Orchestrator's user-facing check via `docker compose up` in `ai-infrastructure/project-manager/dashboard/`; this report asserts the panel renders pending that visual check.

- **No em dashes** in any authored file (confirmed via grep).

- **SPA build:** Not run (compose-only run policy, ADR-003; build is user-run). The component uses only standard React JSX and reuses existing CSS classes; no build errors are anticipated, but user should confirm with a compose build run.
