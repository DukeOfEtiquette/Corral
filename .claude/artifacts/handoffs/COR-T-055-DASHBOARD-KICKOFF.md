# COR-T-055 Dispatch 2: wire the dashboard ETL to discover services.yml, add a services panel, add the port drift-guard check

## Target

This is AI-infrastructure work (ADR-005, domain 2): the project-manager dashboard is a domain-2 build tool, even though the services it inventories are mostly domain-1 web-app services. The task is Dispatch 2 of the two-dispatch COR-T-055 flow. Dispatch 1 already authored the per-workspace `services.yml` inventory files; they are on disk now and are this dispatch's INPUT data. Dispatch 2 (this kickoff) wires the dashboard to consume and render them and adds a declared-port-vs-compose drift-guard check. The artifacts in scope are the dashboard ETL (`ai-infrastructure/project-manager/dashboard/etl.py`), a new React services panel, and a small wiring edit to the landing view. The spec you execute against is ADR-045 (accepted); the warning-family lineage is ADR-041.

## Decisions resolved by the Orchestrator

- **Scope boundary: consume, do not author.** Dispatch 1 wrote the three `services.yml` files (`ai-infrastructure/backend-api/services.yml` declaring `api`; `ai-infrastructure/database/services.yml` declaring `postgres`; `ai-infrastructure/project-manager/services.yml` declaring `dashboard` running plus `mcp` and `frontend` planned). They are the input. Do NOT edit any `services.yml` file in this dispatch. Rationale: ADR-045 decision 6 splits authoring (done) from consumption (this task); the files are the fixed contract you read.

- **All three deliverables are pinned by accepted ADR-045** (decision 4 for ETL consumption and the rendered panel; decision 5 for the drift guard) and ADR-041 (the owned-but-advisory warning family the drift check joins). The implementation is standard ETL + React work mirroring existing code in the same files. No paradigm choice is open; mirror the named precedents.

- **Deliverable 1, ETL discovery (`ai-infrastructure/project-manager/dashboard/etl.py`):**
  - Add a `collect_services(repo_root)` function that discovers every `ai-infrastructure/*/services.yml` file generically, mirroring the existing `collect_roadmap_from_files` epic-discovery loop (iterate the `repo_root / "ai-infrastructure"` subdirectories, look for a `services.yml`, `yaml.safe_load` it, extend a flat list with the file's `services:` entries). Rationale: ADR-045 decisions 2 and 4 pin generic per-workspace discovery, the same loop the ETL already runs for `epics/` trees.
  - Tolerant parsing: skip unreadable or malformed files and files lacking a `services:` list, consistent with the rest of the ETL (the `parse_frontmatter` / `collect_roadmap_from_files` tolerance pattern, which wraps reads in `try/except (OSError, yaml.YAMLError)` and `continue`s).
  - Each emitted service object passes through the source fields (`id`, `name`, `domain`, `status`, `runtime`, `host`, `ports`, `base_url`, `workspace`, `adrs`, `endpoints`) and adds a derived `warning` field (a string when the drift check fires, else `null`), matching how epics carry a derived `warning`.
  - Sort the aggregated list deterministically: running services before planned, then by `workspace`, then by `id`.
  - Emit the list as a new top-level `services` key in `data.json` (add it to the `data` dict assembled in `run_etl`, alongside `roadmap`, `departments`, `blocked`, etc.).
  - Update the module docstring: add a source bullet (the `services.yml` inventory, ADR-045) to the Sources list and a `services:` entry to the JSON-contract shape section.
  - Do NOT change `WATCH_PATTERNS`: it already matches `.*/ai-infrastructure/.*\.yml$`, so `services.yml` edits already trigger rebuilds. State this in the report rather than editing it.

- **Deliverable 2, drift-guard check (in `etl.py`, owned-but-advisory, ADR-041 lineage):**
  - Parse published host ports from `app/docker-compose.yml`: for each compose service that has a `ports:` list, extract the host-side port from each `"HOST:CONTAINER"` mapping (the value left of the colon; a bare port with no colon counts as both host and container).
  - For each service entry whose `runtime` matches a compose service that publishes a host port: if the entry's declared `ports` does not include that published host port, set the entry's `warning` to a message naming the declared value versus the compose value.
  - Services whose `runtime` is not a service in `app/docker-compose.yml`, OR whose matched compose service publishes no host port, get NO warning (`warning: null`). This is intentional and must be stated in the report: it means `api` (compose publishes `8123:8123`) IS checked; `postgres` (no published host port in `app/docker-compose.yml`, internal-only) is NOT; `dashboard` (defined in a different compose file, not `app/docker-compose.yml`) is NOT; planned services (`mcp`, `frontend`) are NOT. Rationale: this first-cut scope is exactly ADR-045 decision 5's "declared port vs `app/docker-compose.yml`"; broadening it is the deferred future-enhancement layer (ADR-045 consequence 8), not this task.
  - Warn-only: the check sets the advisory `warning` field; it never alters or suppresses any other derived value, consistent with the existing `phase_warning` / `epic_warning` / `no_epic_warning` family. Rationale: ADR-041 pins the owned-but-advisory, non-gating posture for this warning family.

- **Deliverable 3, services panel (React):**
  - Add `ai-infrastructure/project-manager/dashboard/src/panels/ServicesPanel.jsx`, a component taking a `services` prop, rendering a `.card` titled "Services" with a table, mirroring the structure of the existing `DepartmentsPanel.jsx` (the `.card` > `<h3>` > `.table-scroll` > `<table>` shape). Columns: Service (name + id), Domain (1/2), Status (running/planned), Host:Port, Endpoints (path list with kinds), Owner (the `workspace` field).
  - Planned services render in a muted/planned row style: reuse the existing `dept-planned` CSS class (defined in `src/styles.css`, `opacity: 0.6`). A service carrying a non-null `warning` renders with a warning row style and the `warning` text as the row's `title` tooltip, mirroring how `DepartmentsPanel` surfaces `no_epic_warning` via the `dept-no-epic` class plus a `title` attribute. Rationale: ADR-045 decision 4 pins rendering consistent with the ADR-039/040 derived-surface model; the warning surfacing mirrors the existing panel exactly.
  - Wire it into `ai-infrastructure/project-manager/dashboard/src/views/LandingView.jsx`: import `ServicesPanel` and render `<ServicesPanel services={data.services} />` within `main-content`. Placement near the other roster/roadmap panels is the implementer's discretion within `main-content`; this is a layout-ordering choice with no contract impact, not an anticipated decision.
  - Reuse existing CSS classes (`.card`, `.table-scroll`, the table classes) where possible. Add minimal new CSS to `src/styles.css` ONLY if a planned/warning row style does not already exist to reuse; `dept-planned`, `dept-no-epic`, and `dept-orphaned` already exist and should be reused before adding anything new.

- **Run path is docker compose only (ADR-003).** The dashboard service is built and served from `ai-infrastructure/project-manager/dashboard/docker-compose.yml`. For ETL/data-layer verification (not the UI), running the ETL script directly against the repo is acceptable because the ETL is a build tool, not an app service. The rendered panel is a visual surface that requires the Orchestrator's user-facing visual confirmation; do not assert the panel renders, state it renders pending that visual check (see Build / verification status expectations below).

## Deliverables

- `etl.py` extended: a `collect_services` discovery function, the drift-guard check, the new top-level `services` key in `data.json`, and the docstring update (Sources list bullet + JSON-contract `services:` entry).
- `ai-infrastructure/project-manager/dashboard/src/panels/ServicesPanel.jsx` created and wired into `LandingView.jsx` (import + `<ServicesPanel services={data.services} />` render within `main-content`).
- Minimal `ai-infrastructure/project-manager/dashboard/src/styles.css` additions ONLY if a planned/warning row style does not already exist to reuse.

## Files in scope

- `ai-infrastructure/project-manager/dashboard/etl.py` (modify)
- `ai-infrastructure/project-manager/dashboard/src/panels/ServicesPanel.jsx` (create)
- `ai-infrastructure/project-manager/dashboard/src/views/LandingView.jsx` (modify: import + render the panel)
- `ai-infrastructure/project-manager/dashboard/src/styles.css` (modify only if a new row style is needed)

## Files out of scope

- `ai-infrastructure/backend-api/services.yml`, `ai-infrastructure/database/services.yml`, `ai-infrastructure/project-manager/services.yml` (Dispatch 1 output; the input data, do not edit)
- `app/docker-compose.yml`, `app/api/` (read-only; the drift check reads compose but does not modify it)
- The ADR files (already accepted; do not edit. The ADR-037 and ADR-031 forward-pointer notes ADR-045 anticipates are ALREADY committed; do not re-add them)
- Other dashboard panels and the ETL's existing collectors (do not refactor unrelated code)

## References

- `docs/ai-orchestration/roles/EXECUTOR-ROLE.md` (the Executor role and the six-section closing report shape)
- `ai-infrastructure/project-manager/decisions/ADR-045-service-endpoint-inventory-structured.md` (the accepted decision: generic discovery, the schema, the drift guard built now; decisions 4 and 5 are the binding spec for this task)
- `ai-infrastructure/project-manager/decisions/ADR-041-guard-derived-phase-completeness.md` (the owned-but-advisory ETL warning family the drift check joins)
- `ai-infrastructure/project-manager/dashboard/etl.py` (the ETL to extend; `collect_roadmap_from_files` is the generic per-workspace discovery pattern to mirror; the existing `warning` fields and the `data` dict assembly in `run_etl` are the shape to match)
- `ai-infrastructure/project-manager/dashboard/src/panels/DepartmentsPanel.jsx` (the panel structure and warning-tooltip pattern to mirror; note the `dept-planned` / `dept-no-epic` row classes and the `title` attribute)
- `ai-infrastructure/project-manager/dashboard/src/views/LandingView.jsx` (where panels are imported and placed within `main-content`)
- `ai-infrastructure/project-manager/dashboard/src/App.jsx` (how `data.json` is fetched and passed to `LandingView`)
- `ai-infrastructure/project-manager/dashboard/src/styles.css` (existing `dept-planned`, `dept-no-epic`, `dept-orphaned` row classes to reuse)
- `app/docker-compose.yml` (the source of published host ports for the drift check; the `api` compose service publishes `8123:8123`)
- `ai-infrastructure/backend-api/services.yml`, `ai-infrastructure/database/services.yml`, `ai-infrastructure/project-manager/services.yml` (the input files the ETL will discover; read-only here)

## Related tasks and ADRs

- COR-T-055: the parent task; this is its Dispatch 2 (Dispatch 1 authored the `services.yml` files).
- ADR-045: the accepted decision defining generic discovery, the schema, and the drift guard built now.
- ADR-041: the owned-but-advisory ETL warning family the drift check joins.
- ADR-037: the generic per-workspace YAML discovery precedent (`collect_roadmap_from_files`) the services discovery mirrors.
- ADR-039 / ADR-040: the derived-dashboard-surface model the services panel is consistent with.

## Hard rules

- Do not edit any `services.yml` file. They are Dispatch 1 output and the fixed input contract. If your verification temporarily mutates one (see the spot-test below), revert it before close and confirm via `git status` that no `services.yml` file is modified at close.
- The drift check is warn-only and must never alter or suppress any other derived value (the `phase_warning` / `epic_warning` / `no_epic_warning` posture).
- Keep the first-cut drift scope exactly as pinned (declared port vs `app/docker-compose.yml`, host-side port only). Do not broaden it to other compose files or to route introspection; that is the deferred future layer (ADR-045 consequence 8).
- Reuse existing CSS row classes before adding new ones.
- Universal conventions (no em dashes in files, repo-root-relative paths, the compose-only run policy, git boundaries, the pinned six-section report shape) are covered by `EXECUTOR-ROLE.md` and `./CLAUDE.md`; follow them, they are not restated here.

## Verification expectations

- Run the ETL against the repo: set `REPO_ROOT` to the repo root and `SERVED_DIR` to a scratch directory (for example under `./.claude/artifacts/tmp/`), then run `python3 etl.py`. Confirm `data.json` gains a `services` key listing all five services (`api`, `postgres`, `dashboard`, `mcp`, `frontend`) with the source fields plus a `warning` field.
- Confirm `api` carries no drift warning (declared `8123` matches the compose `8123:8123`); confirm `postgres`, `dashboard`, `mcp`, and `frontend` carry no warning (out of the check's scope, by design).
- Spot-test the drift check: temporarily change the `api` declared port in `ai-infrastructure/backend-api/services.yml` to a wrong value, re-run the ETL, confirm the `api` `warning` fires naming declared-versus-compose, then REVERT the `services.yml` change (it is Dispatch 1 output and must end unchanged). Confirm via `git status` that no `services.yml` file is modified at close.
- Confirm the SPA builds without error if a build is run. The rendered services panel is a visual surface that requires the Orchestrator's user-facing visual confirmation (via `docker compose up` in `ai-infrastructure/project-manager/dashboard/`), so the closing report should state that the panel renders pending that user visual check rather than asserting it renders.
- No em dashes in any authored file; no credentials introduced.

## Executor pointer

The executor is the dispatched `executor` (ADR-028). Universal executor conventions live in `docs/ai-orchestration/roles/EXECUTOR-ROLE.md`. Write the closing report in the pinned six-section shape per `EXECUTOR-ROLE.md`, section "Report shape", to `./.claude/artifacts/handoffs/COR-T-055-DASHBOARD-KICKOFF-REPORT.md` (the derivable dual-channel path).
