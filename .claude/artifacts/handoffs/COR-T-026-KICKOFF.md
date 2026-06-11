# Dashboard layout: move roster below overview; trim org-chart whitespace

## Target

This is AI-infrastructure work (ADR-005): a presentational change to the project-manager insight dashboard, a coordinator/agent-development artifact under `./ai-infrastructure/project-manager/dashboard/`. The task is COR-T-026. Two presentational tweaks to the dashboard's landing view, surfaced by the COR-T-025 visual review: (1) reorder the landing panels so the department roster renders directly below the overview box, and (2) trim the trailing vertical whitespace below the org-chart card. The change is purely presentational: no change to `etl.py` or the `data.json` contract.

## Decisions resolved by the Orchestrator

- **Panel reorder (`LandingView.jsx`).** The landing view currently renders panels in this order inside `<main className="main-content">` (`./ai-infrastructure/project-manager/dashboard/src/views/LandingView.jsx`, lines 21-27): `PulsePanel`, then a `<div className="two-col">` holding `RoadmapPanel` + `OrgChartPanel`, then `DepartmentsPanel`, then `ActivityPanel`. Move `DepartmentsPanel` to render directly below `PulsePanel` and above the `.two-col` grid. The final order must be: `PulsePanel` -> `DepartmentsPanel` -> `.two-col` (`RoadmapPanel`, `OrgChartPanel`) -> `ActivityPanel`. `ActivityPanel` stays last. This is a pure JSX reorder; every panel's props are unchanged.
- **Org-chart whitespace fix (pinned mechanic).** The root cause is verified: `.two-col` (`./ai-infrastructure/project-manager/dashboard/src/styles.css`, lines 93-97) is a CSS grid with `grid-template-columns: 1fr 1fr` and the default `align-items: stretch`, so both grid items stretch to the height of the taller card (Roadmap), leaving the shorter org-chart card with a large dead area below its ASCII `<pre className="org-chart">` content. Implement exactly this fix, in two parts:
  1. In `./ai-infrastructure/project-manager/dashboard/src/panels/OrgChartPanel.jsx`, add the class `org-chart-card` to the card div, so its current `className="card"` (line 5) becomes `className="card org-chart-card"`.
  2. In `./ai-infrastructure/project-manager/dashboard/src/styles.css`, add the rule `.org-chart-card { align-self: start; }`.

  This aligns ONLY the org-chart grid item to the start of its row, so it sizes to its content; the Roadmap card is untouched. Do not modify `.two-col`'s `align-items`, do not change `grid-template-columns`, and do not touch the `@media (max-width: 768px)` collapse rule at `styles.css` lines 99-101. This is the complete and only mechanic; implement it as written.
- **Acceptance criteria (verification gates).** After the change: (a) no large empty area below the org-chart tree on wide viewports; (b) the side-by-side Roadmap/org-chart arrangement is preserved on wide viewports; (c) the single-column collapse at the `@media (max-width: 768px)` breakpoint still works; (d) no other panel's sizing or styling changes. These are the gates the closing report confirms; they are not implementation choices.

## Deliverables

- Reordered panels in `./ai-infrastructure/project-manager/dashboard/src/views/LandingView.jsx`: `DepartmentsPanel` (the roster) moved above the `.two-col` grid, final order `PulsePanel` -> `DepartmentsPanel` -> `.two-col` -> `ActivityPanel`, props unchanged.
- The `org-chart-card` class added to the card div in `./ai-infrastructure/project-manager/dashboard/src/panels/OrgChartPanel.jsx`, and the `.org-chart-card { align-self: start; }` rule added in `./ai-infrastructure/project-manager/dashboard/src/styles.css`, satisfying acceptance criteria (a) through (d) above.

## Files in scope

- `./ai-infrastructure/project-manager/dashboard/src/views/LandingView.jsx`
- `./ai-infrastructure/project-manager/dashboard/src/panels/OrgChartPanel.jsx`
- `./ai-infrastructure/project-manager/dashboard/src/styles.css`

## Files out of scope

- `./ai-infrastructure/project-manager/dashboard/etl.py` and the `data.json` contract: no change.
- `./ai-infrastructure/project-manager/dashboard/src/views/WorkspaceView.jsx`.
- The org-chart ASCII content itself (owned by `etl.py build_org_chart`).
- Styling of any other panel: `PulsePanel`, `RoadmapPanel`, `DepartmentsPanel`, `ActivityPanel`, `TaskCountsPanel`.

## References

- `./ai-infrastructure/project-manager/tasks/in-progress/COR-T-026-dashboard-layout-roster-and-org-chart.md`: the task spec, with the full description and the verification expectation. Read-only (the Worker never edits the tasks tree).
- `./ai-infrastructure/project-manager/dashboard/src/views/LandingView.jsx`: the current panel order (lines 21-27); the reorder target.
- `./ai-infrastructure/project-manager/dashboard/src/panels/OrgChartPanel.jsx`: the org-chart card markup (`<div className="card">` at line 5, `<pre className="org-chart">` at line 7); the card div gets the `org-chart-card` class.
- `./ai-infrastructure/project-manager/dashboard/src/styles.css`: the `.two-col` grid at lines 93-101 (including the `@media (max-width: 768px)` collapse) and the `.org-chart` rule at line 257; the new `.org-chart-card` rule is added here.

## Related tasks and ADRs

- COR-T-014: built the project-manager insight dashboard (greenfield ETL + React SPA); origin of these files.
- COR-T-017: added `RoadmapPanel` milestones (the tall card that drives the grid stretch behind the org-chart whitespace).
- COR-T-020: made the dashboard live (`--watch` auto-rebuild + browser soft-refresh); relevant to how changes are observed under `docker compose up`.
- COR-T-025: the visual review that surfaced both layout asks filed in this task.

## STATUS deltas

No task-specific STATUS deltas; universal hygiene only.

## Hard rules

- Presentational only: do not touch `etl.py` or the `data.json` contract, and do not alter the org-chart ASCII content. The dashboard's data layer is fixed for this task.
- The panel reorder is a pure JSX move: do not change any panel's props, and do not restyle, rename, or restructure the panels themselves.
- The org-chart fix is the two-part pinned mechanic above and nothing more: add the `org-chart-card` class to the card div and the `.org-chart-card { align-self: start; }` rule. Do not edit `.two-col`'s `align-items` or `grid-template-columns`, and do not regress the `@media (max-width: 768px)` single-column collapse. Confirm both wide-viewport and narrow-viewport behaviour before reporting completion.

## Worker pointer

The Worker is the dispatched `worker-agent` (ADR-028). Universal Worker conventions, including the compose-only run policy and the dual-channel closing report, live in `./docs/ai-orchestration/roles/WORKER-ROLE.md`. Verification runs under `docker compose up` in `./ai-infrastructure/project-manager/dashboard/` per ADR-003; confirm that the department roster renders directly under the overview box and above the Roadmap/org-chart, and that the org-chart card has no large empty area below its tree, at both wide and narrow viewport widths. The closing report is written to `./.claude/artifacts/handoffs/COR-T-026-KICKOFF-REPORT.md` per WORKER-ROLE.md, section "Report shape".
