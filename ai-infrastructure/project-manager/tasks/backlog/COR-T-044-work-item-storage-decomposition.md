---
schema_version: 1
id: COR-T-044
title: "Decompose the roadmap into epic/phase files per ADR-037 (epics/ + phases/ trees, bottom-up linkage, derived roadmap)"
status: backlog
labels: []
priority: P2
created: 2026-06-13
updated: 2026-06-13
---

## Description

Implement the markdown-side storage representation pinned in `./decisions/ADR-037-work-item-storage-representation.md` (accepted), targeting the app model in `./decisions/ADR-038-phase-as-first-class-view.md` (accepted). This is the rename-and-reshape cascade for ADR-037, the analog of the ADR-036 roadmap restructure (COR-T-041). It routes through the dispatched-worker flow; it is a coordinator deliverable, not orchestrator-direct.

The decisions are pinned in ADR-037; this task executes them. In scope:

1. **New trees.** Create an `epics/` tree in each workspace that owns epics (the `project-manager` coordinator and each department with epics: at minimum `project-manager`, `database`, `backend-api`), each with its own `.next-epic-id` counter. Create a coordinator-owned `phases/` tree under `ai-infrastructure/project-manager/`. Epic and phase trees carry NO `backlog/ in-progress/ blocked/ done/` status subdivision (status is a derived rollup per ADR-037 decision 7).

2. **Decompose the current roadmap.** Split the `roadmap:` block in `ai-infrastructure/project-manager/STATUS.md` frontmatter into one `.yml` file per phase (`phase-0` .. `phase-8`) in `phases/`, and one `.yml` file per epic (the current E1.1 .. E8.2 entries) in the owning workspace's `epics/` tree. Files are pure YAML with a concise `description` field. Epic IDs are re-minted department-prefixed and phase-decoupled (`COR-E-NNN`, `DB-E-NNN`, etc.), retiring the `E<phase>.<seq>` ids.

3. **Bottom-up linkage.** Stamp an `epic:` field on every existing task that belongs to an epic (across all workspace `tasks/` trees), and a `phase:` field on every epic that belongs to a phase. Remove the top-down `tasks: []` / `epics: []` lists.

4. **Remove the roadmap block from STATUS.md.** STATUS.md keeps the current-phase narrative and the `recent_updates` changelog; the roadmap is no longer authored there (churn coupling resolved per ADR-037 decision 6).

5. **Rewrite the dashboard ETL reader.** `ai-infrastructure/project-manager/dashboard/etl.py` currently reads the roadmap from STATUS frontmatter (`derive_current_phase`, `derive_roadmap_status`, `derive_epic_status`, `resolve_milestone_refs`, and the roadmap data contract). Rewrite it to reconstruct the roadmap from the files: walk the `epics/` trees, group epics by their `phase:` field, attach tasks by their `epic:` field, and roll status up per ADR-036. The roadmap data contract emitted to `data.json` should stay shape-stable (the derivation changes its source, not its output) so `RoadmapPanel.jsx` needs minimal or no change; confirm this and adjust the panel only if the contract must shift.

6. **Update `./tasks/README.md`.** Refresh the Vocabulary section and add an epics/phases convention (file format, the `epics/`/`phases/` trees, the `.next-epic-id` counter, the `epic:`/`phase:` linkage fields, the ID scheme) cross-referencing ADR-037 and ADR-038.

Out of scope: the ADR-038 app-schema realization (the `views` ordering column and `phase:*` family enforcement), which is deferred to the dogfood-import build (roadmap Phase 5/7) per ADR-038 consequence 8; any change to ADR-037/ADR-038 decisions themselves (they are accepted; if execution surfaces a problem, escalate rather than redecide). This task is a visual deliverable (it changes the dashboard roadmap render), so it carries a headless-render + user visual gate at close per COR-07.

References: `./decisions/ADR-037-work-item-storage-representation.md`, `./decisions/ADR-038-phase-as-first-class-view.md`, `./decisions/ADR-036-work-item-taxonomy.md`, `./decisions/ADR-031-per-department-task-trees.md` (the `epics/` tree amends it), `./tasks/README.md`, `ai-infrastructure/project-manager/dashboard/etl.py`.

## Activity log

- 2026-06-13: Created in backlog. Triaged from the ADR-037 / ADR-038 resolution (both accepted this session). The markdown decomposition cascade, analog of the ADR-036 restructure (COR-T-041). P2; routes through the dispatched-worker flow when picked up. Large and visual (touches the dashboard); may warrant splitting at kickoff time.
