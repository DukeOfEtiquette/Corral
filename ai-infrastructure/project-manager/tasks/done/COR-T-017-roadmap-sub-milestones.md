---
schema_version: 1
id: COR-T-017
title: "Add roadmap sub-milestones (P1-1/P1-2 granularity) to the project-manager dashboard"
status: done
labels: [dept:agent-development]
priority: P3
created: 2026-06-10
updated: 2026-06-10
epic: COR-E-004
---

## Description

Enhance the project-manager dashboard roadmap (built in COR-T-014) with sub-milestone granularity: numbered sub-items per phase (e.g. P1-1, P1-2) each with their own title and status, instead of today's single freeform `deliverables` string per phase. Surfaced by the user on 2026-06-10 while reviewing the shipped dashboard.

The deliverable spans three layers:

- Data: extend the `roadmap:` block in `./STATUS.md` frontmatter so each phase carries an optional `milestones:` list, each item `{ id (e.g. "P1-1"), title, status, optional task/ADR refs }`. The existing per-phase `deliverables` string can remain as a phase summary or be superseded by the milestones list (decide at pickup).
- ETL (`dashboard/etl.py`): carry `milestones` through into the `data.json` roadmap contract (and, if status is derived, compute per-milestone status from the linked tasks).
- UI (`dashboard/src/panels/RoadmapPanel.jsx` + `dashboard/src/styles.css`): render an expandable per-phase sub-list, each milestone with its own status pill and, if referenced, a link to its `COR-T` task or ADR (the per-workspace detail route already exists for linking).

Open decision to resolve at pickup (raised with the user 2026-06-10, not yet answered): milestone `status` is either AUTHORED in the STATUS `roadmap` block, or DERIVED from the linked `COR-T` task state (more dogfooding; auto-updates as tasks move between status directories). This choice drives whether the ETL computes status and whether each milestone must carry a task ref.

Routing: the ETL/UI work routes through the dispatched-worker flow; the STATUS `roadmap`-schema extension is orchestrator-direct (coordination surface). Builds directly on COR-T-014 (the dashboard and the structured `roadmap` block it introduced). Keep the pending-ADR decoupling intact (ADR-015/017/018 unaffected).

## Activity log

- 2026-06-10: Created in backlog. Surfaced by the user while reviewing the shipped COR-T-014 dashboard: the roadmap shows phase-level deliverables only, with no P1-1/P1-2 sub-milestone granularity. The authored-vs-derived milestone-status choice is an open decision to resolve at pickup.
- 2026-06-10: Picked up; moved to in-progress. Resolving the authored-vs-derived milestone-status decision with the user before drafting the kickoff.
- 2026-06-10: Executed via the dispatched-worker flow. Decisions pinned: milestone status AUTHORED (not derived); vocabulary done/in-progress/planned; deliverables kept as phase summary; task ref renders as a non-linking tag (no per-task/ADR detail route exists, verified against App.jsx). Orchestrator authored the STATUS roadmap milestones block; worker carried it through etl.py and rendered it in RoadmapPanel.jsx + styles.css. ETL output re-derived against disk; both checkers PASS; user confirmed the visual. Deliverable committed as 5545faa. Moved to done.
