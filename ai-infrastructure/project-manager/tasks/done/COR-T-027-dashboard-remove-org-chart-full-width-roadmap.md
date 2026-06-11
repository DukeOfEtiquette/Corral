---
schema_version: 1
id: COR-T-027
title: "Dashboard: remove the Org Chart panel; expand Roadmap to full channel width"
status: done
labels: []
priority: P2
created: 2026-06-11
updated: 2026-06-11
---

## Description

Presentational change to the project-manager insight dashboard (`ai-infrastructure/project-manager/dashboard/`), requested after the COR-T-026 visual review. Follows COR-T-026 (which moved the Department Roster above the Roadmap/Org-Chart row and trimmed the Org Chart's whitespace).

The Org Chart and the Roadmap currently share the `.two-col` grid as two equal-width columns on the landing view (`src/views/LandingView.jsx`). The Org Chart's information (the coordinator plus the AI-infrastructure and web-app department roster, with planned/created status) is already conveyed by the Department Roster panel (`DepartmentsPanel`), which now sits directly above this row. The org is flat enough that the spatial tree representation adds little over the roster. Remove the Org Chart entirely and give the Roadmap the full channel width.

Target landing-view layout, top to bottom: `PulsePanel` (overview) -> `DepartmentsPanel` (roster) -> `RoadmapPanel` (full width) -> `ActivityPanel`. The roster stays above the Roadmap; Recent Activity stays below it.

Known affected surfaces (verified at filing time):
- `src/views/LandingView.jsx` - remove the `OrgChartPanel` import and element; unwrap the `.two-col` grid so `RoadmapPanel` renders full width.
- `src/panels/OrgChartPanel.jsx` - the component becomes orphaned (used only in `LandingView`).
- `src/styles.css` - `.org-chart-card` (line 257), `.org-chart` (line 259), and `.two-col` (lines 93-101) all become orphaned (`.two-col` is used only by this row; confirmed not used in `WorkspaceView`).
- `etl.py` - `build_org_chart` (line 168), its call site (line 410), and the `org_chart` field in the emitted `data.json` (line 516) become orphaned once nothing consumes them.

Scoping decision to resolve at pickup: whether "remove completely" includes stripping the now-dead `etl.py build_org_chart` and the `org_chart` `data.json` field (and the JSON-contract docstring at `etl.py:36`), or only removes the UI panel and leaves the ETL field emitted-but-unconsumed. Lean: remove the dead ETL/data path too, since the field has no other consumer and the user emphasized "completely"; if so, this task touches the `data.json` contract (unlike COR-T-026) and that delta should be pinned in the kickoff. Routes through the `/project-manager-orchestrator` dispatched-worker flow when picked up.

Out of scope: the `WorkspaceView`; restyling unrelated panels (`PulsePanel`, `DepartmentsPanel`, `RoadmapPanel`, `ActivityPanel`, `TaskCountsPanel`); changing the Roadmap's content or the Department Roster's content.

Verification: `docker compose up` in `ai-infrastructure/project-manager/dashboard/` renders no Org Chart, the Roadmap at full channel width directly below the Department Roster, and Recent Activity below the Roadmap, at both wide and narrow viewport widths.

## Activity log

- 2026-06-11: Created in backlog. Filed during the COR-T-026 close review after the user, viewing the live render, decided the Org Chart is redundant with the now-above Department Roster for a flat org. Coordinator/agent-development presentational deliverable; routes through the dispatched-worker flow. Unlabelled per the ADR-031 convention (the coordinator tree is the partition; dept:* labels are applied at the dogfood import, not hand-applied in the markdown era).
- 2026-06-11: Picked up; moved to in-progress. Routing through the /project-manager-orchestrator dispatched-worker flow. One residual scoping decision to resolve with the user before drafting the kickoff: whether "remove completely" also strips the orphaned etl.py build_org_chart and the org_chart data.json field (touching the data.json contract), or removes only the UI panel.
- 2026-06-11: Executed via dispatched worker-agent and closed. Scoping decision resolved with the user: FULL removal (UI panel + dead ETL path + the org_chart data.json contract field). Kickoff drafter+checker loop PASSed on iteration 1 (0 findings); prelaunch W1 PASS, close W2 PASS. Deliverable verified against disk: OrgChartPanel.jsx deleted, LandingView.jsx reordered to PulsePanel -> DepartmentsPanel -> RoadmapPanel (full width) -> ActivityPanel with the .two-col wrapper unwrapped, styles.css .two-col/.org-chart/.org-chart-card rules removed, etl.py build_org_chart path stripped and data.json no longer emitting org_chart (grep-confirmed zero residual references). Visually confirmed by the user under docker compose up. Committed in af1f48c (deliverable + kickoff/report pair + STATUS hygiene). No follow-ups beyond the user-run verification already performed.
