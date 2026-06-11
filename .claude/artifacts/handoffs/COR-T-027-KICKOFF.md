# Dashboard: remove the Org Chart panel; expand Roadmap to full channel width (COR-T-027)

## Target

This is an AI-infrastructure task (ADR-005): a presentational deliverable for the project-manager insight dashboard under `ai-infrastructure/project-manager/dashboard/`. You are removing the Org Chart UI panel from the landing view, expanding the Roadmap to full channel width, and stripping the now-dead ETL/data path that fed the panel. Because the org-chart data has exactly one consumer, this is a `data.json` contract change: the emitted `data.json` will no longer carry an `org_chart` field. The task follows COR-T-026, which moved the Department Roster above this row and added the `.org-chart-card` style hook you now remove.

## Decisions resolved by the Orchestrator

- **Scope is FULL removal**, confirmed with the user. Remove the Org Chart UI panel, strip the now-dead ETL path, and remove the `org_chart` field from the `data.json` contract. Rationale: `data.org_chart` has exactly one consumer (`OrgChartPanel` via `LandingView`, verified by grep); removing the panel orphans the entire ETL path, so the panel removal and the ETL/contract removal are one change, not two. This is a `data.json` contract change (unlike COR-T-026, which was UI-only).
- **Target landing-view layout, top to bottom:** `PulsePanel` (overview) -> `DepartmentsPanel` (roster) -> `RoadmapPanel` (full width) -> `ActivityPanel`. The roster stays above the Roadmap; Recent Activity stays below it; `ActivityPanel` stays last.
- **The `.two-col` grid is unwrapped, not repurposed.** In `LandingView.jsx` the `.two-col` div currently wraps only `RoadmapPanel` + `OrgChartPanel`, and `.two-col` is referenced nowhere else in `src/` except its own CSS rules (it is NOT used in `WorkspaceView`). With the Org Chart gone, `RoadmapPanel` renders directly with no wrapper, at full channel width, and the orphaned `.two-col` CSS rules are removed. Do not reuse `.two-col` to hold the Roadmap alone.
- **Surfaces to remove, confirmed by content** (line numbers below are as of filing; re-confirm each by content, do not trust the numbers blindly):
  - `src/views/LandingView.jsx`: the `OrgChartPanel` import (line ~4), the `<OrgChartPanel orgChart={data.org_chart} />` element (line ~25), and the `<div className="two-col">` wrapper (line ~23 and its closing `</div>` at ~26) so `RoadmapPanel` is no longer nested.
  - `src/panels/OrgChartPanel.jsx`: DELETE the file. It is orphaned once `LandingView` no longer imports it.
  - `src/styles.css`: remove `.org-chart-card` (line ~257, added by COR-T-026), `.org-chart` (lines ~259-266), the `/* Org chart */` section comment (line ~256), and the `.two-col` rules (the base rule at lines ~93-97 and the responsive single-column override at lines ~99-101).
  - `etl.py`: remove `build_org_chart` (def at lines ~168-199), its call site and the `# -- Org chart` comment (`org_chart = build_org_chart(departments)` at lines ~409-410), the `"org_chart": org_chart,` field in the assembled `data` dict (line ~516), and the `org_chart: ASCII string` line in the JSON-contract docstring (line ~36).

## Deliverables

1. `src/views/LandingView.jsx` renders panel order `PulsePanel -> DepartmentsPanel -> RoadmapPanel (full width) -> ActivityPanel`, with no `OrgChartPanel` import, no `OrgChartPanel` element, and no `.two-col` wrapper around `RoadmapPanel`.
2. `src/panels/OrgChartPanel.jsx` deleted.
3. `src/styles.css` with `.org-chart-card`, `.org-chart`, the `/* Org chart */` comment, and the `.two-col` rules (base and responsive) removed.
4. `etl.py` with `build_org_chart`, its call site, the `"org_chart"` emitted field, and the `org_chart` docstring line removed; the emitted `data.json` no longer carries an `org_chart` field.

## Files in scope

- `ai-infrastructure/project-manager/dashboard/src/views/LandingView.jsx`
- `ai-infrastructure/project-manager/dashboard/src/panels/OrgChartPanel.jsx` (delete)
- `ai-infrastructure/project-manager/dashboard/src/styles.css`
- `ai-infrastructure/project-manager/dashboard/etl.py`

## Files out of scope

- The `WorkspaceView` and all of its panels.
- `PulsePanel`, `DepartmentsPanel`, `RoadmapPanel`, `ActivityPanel`, `TaskCountsPanel` content and styling. Do not restyle them; only remove the Org Chart and unwrap the grid.
- The Roadmap's content and the Department Roster's content.
- Any other `etl.py` field or behaviour beyond the four `org_chart` surfaces named above.

## References

- `ai-infrastructure/project-manager/tasks/in-progress/COR-T-027-dashboard-remove-org-chart-full-width-roadmap.md` - the task file; its Description carries the full context and the filing-time surface inventory.
- `ai-infrastructure/project-manager/dashboard/src/views/LandingView.jsx` - the landing view you edit; the `.two-col` wrapper and the `OrgChartPanel` import/element live here.
- `ai-infrastructure/project-manager/dashboard/src/styles.css` - the stylesheet carrying the `.two-col`, `.org-chart-card`, and `.org-chart` rules to remove.
- `ai-infrastructure/project-manager/dashboard/etl.py` - the ETL script with `build_org_chart`, its call site, the emitted `org_chart` field, and the JSON-contract docstring.

## Related tasks and ADRs

- COR-T-026 - immediate predecessor; moved the Department Roster above this row and added the `.org-chart-card` hook (`styles.css` ~257) that this task now removes.
- COR-T-014 - built the dashboard and defined the `data.json` contract this task amends.
- ADR-008 - the dashboard reads markdown now and repoints to the app at the dogfood milestone; the `data.json` contract is interim, so amending it is low-risk.

## STATUS deltas

No task-specific phase, roadmap, or "Next step" change. Apply universal STATUS hygiene only (bump `last_updated`, append a `recent_updates` entry) per `docs/ai-orchestration/roles/WORKER-ROLE.md`. The `recent_updates` entry should note the `data.json` contract delta, specifically that the `org_chart` field was removed, in addition to naming the panel removal and COR-T-027.

## Hard rules

- Re-confirm each removal target by content before editing; the line numbers above are as of filing and may have drifted. Match surrounding indentation exactly when removing lines.
- Do not leave dangling references: after the edits, no `OrgChartPanel` import or element remains, and no `.org-chart`, `.org-chart-card`, or `.two-col` class reference remains anywhere in `src/`.
- Do not reuse `.two-col` for the lone Roadmap; `RoadmapPanel` renders directly in `<main className="main-content">` with no intermediate wrapper.
- Run policy is docker compose only (ADR-003). Verification below runs through the dashboard's compose stack; do not assume host-installed Node or Python.

## Verification expectations

The user performs the visual confirmation; you confirm the non-visual checks in your report. Specifically:

- Bring up the dashboard with `docker compose up` in `ai-infrastructure/project-manager/dashboard/`. The expected render (user-confirmed): no Org Chart, the Roadmap at full channel width directly below the Department Roster, and Recent Activity below the Roadmap, at both wide and narrow viewport widths.
- The freshly built `data.json` no longer contains an `org_chart` field.
- The Vite build has no unresolved import: the `OrgChartPanel` import is gone and `src/panels/OrgChartPanel.jsx` is deleted.
- No `.org-chart`, `.org-chart-card`, or `.two-col` class reference remains in `src/` (grep `src/` to confirm).

## Worker pointer

You are the dispatched `worker-agent` (ADR-028). Universal worker conventions (file-edit hygiene, stage-do-not-commit, the run policy, STATUS hygiene) live in `docs/ai-orchestration/roles/WORKER-ROLE.md`. Write your closing report to `.claude/artifacts/handoffs/COR-T-027-KICKOFF-REPORT.md` per `WORKER-ROLE.md`, section "Report shape" (dual-channel: print the six sections to chat and write the same content to the file).
