---
schema_version: 1
id: COR-T-040
title: "Dashboard roadmap: status-colored task/ADR reference badges"
status: done
labels: []
priority: P2
created: 2026-06-12
updated: 2026-06-12
epic: COR-E-004
---

## Description

Rework the project-manager dashboard ROADMAP panel so phase/milestone status is conveyed by structured, deterministically-resolved reference badges instead of hand-set status badges and prose parentheticals. This is the coordinator dashboard (`ai-infrastructure/project-manager/dashboard/`), so it routes through the project-manager orchestrator's dispatched-worker flow; the milestone-ref schema lives in `STATUS.md` frontmatter (orchestrator-direct carve-out) while the consuming code (`etl.py`, `RoadmapPanel.jsx`, `styles.css`) is the dispatched deliverable.

Motivation: reduce drift (the stated anti-drift principle) by pulling ADR references out of prose titles into structured frontmatter and coloring every task/ADR badge by its live status (task = directory it sits in; ADR = frontmatter `status`), both already collected deterministically by `etl.py`. Advances/retires the COR-03 drift surface (hand-set milestone status).

Pinned decisions (resolved with the user 2026-06-12):

- **Fork 1:** Remove phase-level status badges (DONE/CURRENT/UPCOMING) AND milestone-level status badges. Keep the phase card side color bar + CURRENT blue background.
- **Fork 2:** Milestone effective status is derived from its refs (rollup) when refs are present; falls back to the hand-set `status:` field only for ref-less milestones (escape hatch). The derived value still feeds `derive_current_phase` / `derive_next_step`.
- **Fork 3:** Large contiguous ranges (P0-2 `ADR-001..009`, P0-3 `COR-T-001..006`) render as a single range badge; etl expands the range, resolves each id, colors by rollup; a mixed-status range gets a distinct color so drift is visible. Singles and discrete 2-4 lists render as individual badges.
- **Fork 4:** Schema is structured `tasks: []` + `adrs: []` lists (bare IDs or `..` range tokens) per milestone. Unresolvable refs render as a loud "broken ref" badge, never silently dropped or mis-colored.
- **Status -> color:** done/accepted=green; in-progress=blue; blocked=red; backlog/planned/pending=slate/grey; range mixed=amber; unresolved=loud warning (dashed red, "?").

Staging:

1. (orchestrator-direct) Minimal STATUS.md schema seed so the executor has real data exercising every render case.
2. (dispatch) Dashboard code change: etl.py resolution + RoadmapPanel.jsx display + styles.css, incl. unresolved-ref guard.
3. (user) Visual verify via compose.
4. (orchestrator-direct) Full per-milestone ref backfill, using the live dashboard's unresolved badges as the checklist.
5. (orchestrator-direct, follow-on) ADR fixing the roadmap-ref schema + etl resolution as the convention; promotes COR-03.

Out of scope: stage-5 ADR (separate follow-on); changes to non-roadmap panels.

## Activity log

- 2026-06-12: Created and picked up (in-progress). Forks 1-4 + palette resolved with the user; routes through the dispatched-worker flow for the code deliverable, orchestrator-direct for the STATUS.md schema seed and backfill.
- 2026-06-12: Done. Stages 1-3 delivered and user-confirmed (visual verify of the live dashboard at :8420). Deliverable committed in cb6e620: etl.py ref-resolution + task-only effective-status, RoadmapPanel.jsx badge rendering (Fork 1 status-pill removal + single/range/unresolved ref badges), styles.css badge palette, STATUS.md milestone schema seed; plus two verification-surfaced styling fixes (Agent Fleet column alignment via table-layout:fixed; roadmap milestone row dividers) and a blank-page regression fix (React reserved-prop `ref` -> `badge`). A rollup-semantic correction (ADR refs informational; task refs drive done-ness) was applied after verify-against-disk caught P2-3/P2-4 falsely resolving done from accepted ADRs. Handoff pair plus the styling report committed in cb6e620 (ADR-024). Deferred follow-ons (not this task): stage-4 per-milestone ref backfill and a stage-5 ADR codifying the roadmap-ref schema + etl resolution (promotes COR-03).
