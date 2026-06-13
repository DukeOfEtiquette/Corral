---
schema_version: 1
id: COR-T-044
title: "Build the epic/phase file structure per ADR-037 (Phase A: trees, YAML files, bottom-up linkage)"
status: done
labels: []
priority: P2
created: 2026-06-12
updated: 2026-06-12
---

## Description

Phase A of the ADR-037 work-item storage cascade: build the new epic/phase file structure and the bottom-up linkage, **without** touching the dashboard ETL or the STATUS.md roadmap block. Phase B (the `etl.py` rewrite, the roadmap-block removal, and the dashboard render verification) is the sibling task COR-T-045 and runs second so the dashboard never breaks. Routes through the dispatched-worker flow.

This is a **faithful re-representation** of the current roadmap, not a re-curation of it. The epic membership encoded in the `roadmap:` block of `ai-infrastructure/project-manager/STATUS.md` is preserved exactly; deciding where un-epic'd tasks belong, or adding epics, is roadmap-content work explicitly out of scope.

In scope:

1. **New trees.** Create `ai-infrastructure/project-manager/epics/` and `ai-infrastructure/database/epics/` (each with a `.next-epic-id` counter), and `ai-infrastructure/project-manager/phases/`. No status subdivision (status is a derived rollup, ADR-037 decision 7).

2. **Phase files (0-8).** One pure-YAML file per phase in `phases/`, from the current roadmap entries (title, deliverables -> a concise `description`, `order` = phase number, `legacy: true` only for phase 0).

3. **Epic files (the 6 epics that currently have tasks).** One pure-YAML file per epic, department-prefixed IDs, decoupled from phase: `COR-E-001..005` for the five Phase-1 coordinator epics (E1.1-E1.5) and `DB-E-001` for the Phase-2 Database epic (E2.1). Each carries `id`, `title`, `dept`, `phase`, a concise `description`, and the governing `adrs` list from the roadmap entry. Epics do NOT list their tasks (linkage is bottom-up).

4. **Bottom-up linkage.** Stamp an `epic: <new-id>` frontmatter field on exactly the task files named in those 6 epics' roadmap task-lists (across the coordinator and database `tasks/` trees, including `done/`), and a `phase: <n>` field on each of the 6 epic files. Tasks not named in any current roadmap epic (COR-T-028, COR-T-041, COR-T-042, COR-T-043, COR-T-044, COR-T-045) are left untouched (they remain standalone, matching the current roadmap).

5. **Provisional epics deferred.** Do NOT materialize the zero-task provisional epics (Phase 2's Backend API E2.2, all of Phases 3-8). They are filed lazily when their work/department begins (ADR-021/031 lazy creation, the >=2-task convention). No `backend-api/epics/` tree is created in this phase.

6. **`tasks/README.md`.** Add an epics/phases convention to the file (file format, the `epics/`/`phases/` trees and `.next-epic-id`, the `epic:`/`phase:` linkage fields, the ID scheme) and refresh the Vocabulary section, cross-referencing ADR-037 and ADR-038.

Out of scope: `ai-infrastructure/project-manager/dashboard/etl.py` (COR-T-045); removing or editing the `roadmap:` block in STATUS.md (COR-T-045 removes it; Phase A leaves it so the dashboard keeps reading it); the provisional epics; any re-assignment of tasks to epics. The pinned epic/phase mapping, IDs, and YAML schema are carried in the kickoff.

References: `./decisions/ADR-037-work-item-storage-representation.md`, `./decisions/ADR-038-phase-as-first-class-view.md`, `./decisions/ADR-036-work-item-taxonomy.md`, `./decisions/ADR-031-per-department-task-trees.md`, `./STATUS.md` (the `roadmap:` block is the decomposition source), `./tasks/README.md`.

## Activity log

- 2026-06-12: Created in backlog. Triaged from the ADR-037 / ADR-038 resolution.
- 2026-06-12: Split into a two-phase dispatch (decided with the user): COR-T-044 is Phase A (build the structure, dashboard untouched); Phase B (etl rewrite + roadmap-block removal + render verification) filed as COR-T-045. Provisional zero-task epics deferred (decided with the user): only the 6 epics with tasks are materialized. Picked up; moved to in-progress. Next: draft+check the kickoff and dispatch the executor.
- 2026-06-12: Done. Kickoff drafted+checked (PASS), prelaunch PASS, executor dispatched (Sonnet). Delivered the epics/ + phases/ trees (6 epic files, 9 phase files), 40 task `epic:` linkage stamps, and the tasks/README convention, with the STATUS roadmap block and dashboard ETL left intact for Phase B. Verified against disk: per-epic counts exact (40 tasks, the report's "36" was a prose miscount), un-epic'd tasks untouched, roadmap block byte-unchanged, etl.py untouched; added the omitted ADR-031 forward-pointer note during close. Deliverable + handoffs committed in 7c6c8f7. Phase B is COR-T-045.
