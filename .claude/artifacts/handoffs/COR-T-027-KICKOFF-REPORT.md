## Deliverables completed

All four deliverables from the kickoff were completed:

1. `src/views/LandingView.jsx` - updated to render PulsePanel -> DepartmentsPanel -> RoadmapPanel (full width) -> ActivityPanel. The `OrgChartPanel` import (line 4) removed, the `<div className="two-col">` wrapper (line 23) and its closing tag (line 26) removed, the `<OrgChartPanel orgChart={data.org_chart} />` element (line 25) removed. RoadmapPanel now renders directly in `<main className="main-content">` with no intermediate wrapper.

2. `src/panels/OrgChartPanel.jsx` - deleted. The file (10 lines, a thin card wrapping `<pre className="org-chart">`) is orphaned with no remaining consumers. Confirmed deleted; no longer present in `src/panels/`.

3. `src/styles.css` - removed the `.two-col` base rule (former lines 93-97) and its `@media (max-width: 768px)` responsive override (former lines 99-101), plus the `/* Org chart */` section comment (former line 256), the `.org-chart-card` rule (former line 257), and the `.org-chart` rule block (former lines 259-266). No remaining `.two-col`, `.org-chart-card`, or `.org-chart` references in `src/`.

4. `etl.py` - removed four surfaces:
   - The `org_chart: ASCII string` line from the JSON-contract docstring (former line 36).
   - The `build_org_chart` function definition (former lines 168-199).
   - The `# -- Org chart ---` comment and `org_chart = build_org_chart(departments)` call site (former lines 409-410).
   - The `"org_chart": org_chart,` field in the assembled `data` dict (former line 516).
   The emitted `data.json` no longer carries an `org_chart` field.

## Decisions made

No Worker-level decisions were required. All decisions were resolved by the Orchestrator in the kickoff:
- Scope confirmed as full removal (UI panel + ETL/data path).
- Target layout confirmed: PulsePanel -> DepartmentsPanel -> RoadmapPanel (full width) -> ActivityPanel.
- `.two-col` unwrapped rather than repurposed; RoadmapPanel renders directly.

## Surprises

None. All four removal surfaces matched the kickoff's content descriptions exactly after re-confirming by content. Line numbers had not drifted from the kickoff's filing-time approximations. The `OrgChartPanel.jsx` file was 10 lines as expected with no additional consumers.

## Follow-ups

- COR-T candidate: visual confirmation via `docker compose up` in `ai-infrastructure/project-manager/dashboard/` is a user-run step (ADR-003 run policy). The user should verify: no Org Chart rendered, Roadmap at full channel width directly below the Department Roster, Recent Activity below the Roadmap, at both wide and narrow viewport widths.
- COR-T candidate: a grep of `src/` confirms zero remaining `.org-chart`, `.org-chart-card`, or `.two-col` class references; however, the Vite build's unresolved-import check (no `OrgChartPanel` import unresolved after `src/panels/OrgChartPanel.jsx` deleted) is a compose-stack verification step for the user to run as part of the docker compose up confirmation above.

## Files touched

- `ai-infrastructure/project-manager/dashboard/src/views/LandingView.jsx` (edited)
- `ai-infrastructure/project-manager/dashboard/src/panels/OrgChartPanel.jsx` (deleted)
- `ai-infrastructure/project-manager/dashboard/src/styles.css` (edited)
- `ai-infrastructure/project-manager/dashboard/etl.py` (edited)
- `.claude/artifacts/handoffs/COR-T-027-KICKOFF-REPORT.md` (this report, written per dual-channel convention)
- `ai-infrastructure/project-manager/STATUS.md` (updated: last_updated bumped to 2026-06-11, recent_updates entry prepended noting the data.json contract delta)

## Build / verification status

Non-visual checks performed in-session:
- Grep of `src/` for `OrgChartPanel`, `.org-chart`, `.org-chart-card`, `.two-col`: zero hits. No dangling class or import references remain.
- Grep of `etl.py` for `org_chart` and `build_org_chart`: zero hits. All four ETL surfaces cleanly removed.
- `src/panels/OrgChartPanel.jsx` confirmed absent from the `src/panels/` directory listing.
- No em dashes in any file written (verified per repo writing rule).

User-run verification expected (ADR-003 docker compose only):
- `docker compose up` in `ai-infrastructure/project-manager/dashboard/`: expected render is no Org Chart, Roadmap at full channel width directly below the Department Roster, Recent Activity below the Roadmap, at both wide and narrow viewport widths.
- Confirm the freshly built `data.json` does not contain an `org_chart` field.
- Confirm the Vite build reports no unresolved import (OrgChartPanel import is gone; the file is deleted).
