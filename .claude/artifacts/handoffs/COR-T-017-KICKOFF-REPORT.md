## Deliverables completed

- [x] **ETL (etl.py)**: Roadmap loop (lines 280-292 pre-edit, now ~280-305) extended to parse the `milestones` list from each phase entry. Each milestone dict carries `id`, `title`, `status` (verbatim pass-through), and `task` (empty string when absent). Phases without a `milestones` key default to `[]`. JSON-contract docstring (line 29 area) updated to document the new field with its vocabulary.
- [x] **UI (RoadmapPanel.jsx)**: Added `MILESTONE_STATUS_LABELS` map (`done` / `in-progress` / `planned`). Under each phase's `roadmap-deliverables` paragraph, renders a `<ul className="roadmap-milestones">` sub-list when `item.milestones` is non-empty. Each row shows: `roadmap-milestone-id`, `roadmap-milestone-title`, `badge badge-milestone-{status}` pill, and (when `ms.task` is truthy) a `roadmap-milestone-task` plain-text tag. Guard: renders nothing extra when milestones array is absent or empty. No interactive state; no hyperlinks.
- [x] **CSS (styles.css)**: Added `.roadmap-milestones` list layout (border-left accent, flex column, padding), `.roadmap-milestone-item` row styles, `.roadmap-milestone-id`, `.roadmap-milestone-title`, `.roadmap-milestone-task` badge, and three pill classes: `.badge-milestone-done` (green), `.badge-milestone-in-progress` (blue), `.badge-milestone-planned` (muted). Colors mirror the `.badge-roadmap-*` idiom exactly.
- [x] **ETL verified via compose image**: Ran ETL inside the built `dashboard-dashboard` image; confirmed all 6 roadmap entries in `data.json` carry a `milestones` array with correct id/title/status/task values; phases with authored milestones (P0 through P5) all populated correctly; task refs present where authored (P1-1: COR-T-001, P1-4: COR-T-014, P1-6: COR-T-017).
- [x] **STATUS hygiene**: `last_updated` already 2026-06-10; one new `recent_updates` entry prepended.

## Decisions made

- Milestone `task` field stored as empty string `""` when absent in the authored YAML (rather than null/omitted). This keeps the JSON shape consistent: every milestone dict has all four keys. The JSX guards on truthiness (`ms.task &&`), so empty string produces no tag. Rationale: simpler downstream consumers; no kickoff constraint violated (kickoff said "omit or set to empty string when absent").
- CSS pill for `in-progress` uses a hyphen in the class name (`badge-milestone-in-progress`) to match the authored status string exactly. This is the natural CSS class for the value `in-progress` and aligns with how the JSX constructs the class name via template literal.

## Surprises

- The `docker-compose.yml` has only one service (`dashboard`), not a separate `etl` service. The ETL runs at container startup via the Dockerfile entrypoint. Verification used `docker run --entrypoint python3 ... /app/etl.py` directly against the built image, which is equivalent to the compose-managed run. The ETL path and output were confirmed correct.

## Follow-ups

- COR-T candidate: The `docker-compose.yml` has no standalone ETL-only service, making it slightly awkward to run the ETL in isolation (e.g. for data-freshness checks without restarting the full dashboard). A future task could add a separate `etl` service target or a `--profile` variant. Triage to orchestrator.
- COR-T candidate: The `roadmap-milestone-id` minimum width is hardcoded at `2.8rem` in CSS. Once phases go beyond single-digit sub-milestone IDs (e.g. P10-1) the width may need adjustment. Low priority; triage to orchestrator.

## Files touched

- `/home/adam/src/corral/ai-infrastructure/project-manager/dashboard/etl.py`
- `/home/adam/src/corral/ai-infrastructure/project-manager/dashboard/src/panels/RoadmapPanel.jsx`
- `/home/adam/src/corral/ai-infrastructure/project-manager/dashboard/src/styles.css`
- `/home/adam/src/corral/ai-infrastructure/project-manager/STATUS.md`
- `/home/adam/src/corral/.claude/artifacts/handoffs/COR-T-017-KICKOFF-REPORT.md` (this file)

## Build / verification status

- **ETL verified**: Ran `python3 /app/etl.py` inside the built `dashboard-dashboard` image (compose ADR-003 path). All 6 roadmap entries in `data.json` carry a `milestones` array with correct structure. Output: 34703 bytes, no errors.
- **Visual confirmation**: Not performed by this worker. To bring the dashboard up and confirm the rendered RoadmapPanel: run `docker compose up --build` from `./ai-infrastructure/project-manager/dashboard/` and open `http://localhost:8420`. On the landing view, the Roadmap panel should show each phase with its existing deliverables summary line, followed by a nested sub-list of milestones. Each milestone row shows its id (e.g. "P1-1"), title, a colored status pill (green for done, blue for in-progress, gray for planned), and a monospace task tag where a `task` ref was authored (e.g. "COR-T-014"). No collapse/expand toggle; the list is always visible. The `deliverables` paragraph above the sub-list must still be present.
