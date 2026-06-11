---
schema_version: 1
id: COR-T-032
title: "Dashboard: split the department roster into side-by-side AI Roster and Web App Roster tables"
status: in-progress
labels: []
priority: P2
created: 2026-06-11
updated: 2026-06-11
---

## Description

Split the single full-width Department Roster on the dashboard landing view into two side-by-side tables that together occupy the same screen real estate the single table occupies now (the same two-column arrangement the Roadmap and the now-deleted Org Chart used before COR-T-027). Directed by the user.

- **Left table titled "AI Roster"**, showing only `ai-infrastructure`-domain departments (agent-development, test-design, docs-curation).
- **Right table titled "Web App Roster"**, showing only `web-app`-domain departments (backend-api, database, mcp-server, frontend-ui, devops).
- The underlying table is otherwise unchanged (Department, the four task-count columns, Total; the orphan-warning row behavior and `.dept-planned` dimming from COR-T-030/031 are preserved).
- **Drop the DOMAIN column.** It is redundant once each table is domain-specific.

This is a frontend-only change. The `departments` list in `data.json` already carries a `domain` field per entry; the split is a frontend partition (`data.departments.filter(d => d.domain === ...)`), so `etl.py` and the data.json contract are NOT touched (same pattern as COR-T-030/031: the field stays, the column goes).

Pinned design (resolved by the orchestrator from the user's spec; the request was fully specified):
- **Component:** parameterize `DepartmentsPanel` with a `title` prop (replacing the hardcoded "Department roster" `<h3>`), and render it twice from `LandingView`, once per domain-filtered list, wrapped in a new two-column grid. The domain partition happens in `LandingView`.
- **Layout:** a new grid wrapper (e.g. `.roster-row`) with `grid-template-columns: 1fr 1fr`, `gap: 1.25rem` (matching `.main-content`'s gap), `align-items: start` (so the shorter AI roster does not stretch to the taller Web App roster's height - the COR-T-026 org-chart-whitespace lesson), and a `@media (max-width: 768px)` collapse to a single column (the behavior the removed `.two-col` had). The grid occupies the same single vertical slot the current `DepartmentsPanel` occupies, between `PulsePanel` and `RoadmapPanel`.
- **DOMAIN column removal:** drop the `<th>Domain</th>` header and the domain `<td>` (the `domain-tag` span) from `DepartmentsPanel`; the table goes from 7 columns to 6 (Department, Backlog, In progress, Blocked, Done, Total).
- **Dead-CSS cleanup folded in:** removing the DOMAIN column orphans `.domain-tag`, `.domain-aiinfrastructure`, `.domain-webapp` (used only in that cell); remove those rules. Also remove `.badge-exists` and `.badge-missing`, left dead by COR-T-031 (verified: `.badge-planned` is still used by `WorkspaceView` and must stay).
- **Center-justify the five count columns (pinned):** Backlog, In progress, Blocked, Done, and Total are center-justified in BOTH the `<th>` header and the `<td>` cell; the Department column stays left-justified (header and cells). Current state is misaligned: count cells are right-aligned (`.count { text-align: right }`) and count headers are left-aligned (the `.dept-table th` default). Implementation: add `className="count"` to the five count `<th>` headers; change `.count` to `text-align: center` (keep `font-variant-numeric: tabular-nums`); add `.dept-table th.count { text-align: center; }` so the centered header overrides the `.dept-table th` left default (specificity 0,2,1 beats 0,1,1). Department header/cell carry no `.count` class and keep the left default.

Known affected surfaces: `src/views/LandingView.jsx` (partition + two-instance render + grid wrapper), `src/panels/DepartmentsPanel.jsx` (title prop, drop DOMAIN column), `src/styles.css` (new roster-grid rule + responsive collapse; remove the five dead rules named above).

Out of scope: `etl.py` and the data.json contract (the `domain` field stays emitted); the orphan-warning logic and `.dept-planned` dimming (preserve as-is); `WorkspaceView` and other panels; the Roadmap/Activity/Pulse panels.

Routes through the `/project-manager-orchestrator` dispatched-worker flow.

Verification: `docker compose up --build` in `ai-infrastructure/project-manager/dashboard/` renders two side-by-side roster cards titled "AI Roster" (3 departments) and "Web App Roster" (5 departments), together spanning the same width the single roster did, with no DOMAIN column, the count columns and orphan/planned row styling intact, tops aligned (no stretch whitespace), collapsing to stacked single-column on a narrow viewport. No dead `.domain-tag`/`.domain-*`/`.badge-exists`/`.badge-missing` references remain.

## Activity log

- 2026-06-11: Created and picked up (directed work; user instruction). Moved straight to in-progress; routing through the dispatched-worker flow. Decisions pinned by the orchestrator from a fully specified request (two domain-filtered tables, AI Roster / Web App Roster titles, drop DOMAIN column, two-col grid with align-items:start and narrow collapse, etl.py untouched, dead-CSS cleanup folded in). Unlabelled per ADR-031.
