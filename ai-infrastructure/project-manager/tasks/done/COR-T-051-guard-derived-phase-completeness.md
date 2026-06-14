---
schema_version: 1
id: COR-T-051
title: "Guard derived phase-completeness: eager forming-epic recipe step + dashboard no-epic check"
status: done
labels: []
priority: P2
created: 2026-06-14
updated: 2026-06-14
---

## Description

Implements ADR-041 (accepted 2026-06-14, Option D), promoting OBSERVATIONS COR-08. The fully-derived roadmap (ADR-037) reads a phase as done when all its FILED epics are done, so a department with anticipated work but no epic file makes its phase read prematurely complete (surfaced when Phase 2 read done because the Backend API epic was unfiled; the instance was fixed in `530b671`). ADR-041 adds a two-layer guard. Read ADR-041 (`ai-infrastructure/project-manager/decisions/ADR-041-guard-derived-phase-completeness.md`) before scoping; it is the authority.

Three deliverables:

1. **Dashboard consistency check (owned-but-advisory).** In `ai-infrastructure/project-manager/dashboard/etl.py`, add a check that flags any existing department (an entry in `DEPARTMENTS_ROSTER` whose `exists` is true) that has zero epics in its `epics/` tree. Render it as an advisory warning, joining the existing warning family (`phase_warning`, `epic_warning`, `cross_dept_warning`) in `data.json` and surfaced on the dashboard (roster and/or the relevant phase). Warn-only: it must NOT change or suppress the derived phase/epic status (ADR-035 / ADR-039 owned-but-advisory model). Confirm against the current repo state that the check passes (every existing department now has at least one epic after `API-E-001` was filed).

2. **Create-department recipe step (amends ADR-030).** Add a step to the create-department recipe so a newly stamped department is given at least one forming epic for its active or next phase at creation time (the `epics/` tree + a forming epic YAML with `dept`/`phase`/`title`/`description`, zero tasks = `planned` per ADR-036). Update the recipe/skill and any scaffold template as needed. This refines the ADR-037 lazy-`epics/` pointer (see the ADR-030 forward-pointer dated 2026-06-14): the recipe now stamps the tree and a forming epic rather than leaving it entirely to first-use.

3. **Convention note.** Add the eager-forming-epic convention to the "Epics and phases" section of `ai-infrastructure/project-manager/tasks/README.md`: a department files at least one forming epic when it is stood up, so no active phase reads done while a member department is unrepresented.

Routes through the dispatched-worker flow (etl code + dashboard render + recipe/doc edits). The render side is a visual surface (the new warning), so expect a headless-render / user visual gate per COR-07 and the Dispatched-worker-flow visual-confirmation step. The orchestrator may split the etl/dashboard deliverable from the recipe/convention docs at kickoff time.

## Activity log

- 2026-06-14: Created in backlog. Implements ADR-041 (accepted 2026-06-14); promotes COR-08. Filed as the spawned implementation task at ADR-041 resolution. Unlabelled per ADR-031.
- 2026-06-14: Picked up (in-progress). Routing through the dispatched-worker flow. Orchestrator doing homework (etl departments assembly + DepartmentsPanel render, the create-department recipe location, the tasks/README "Epics and phases" section) before resolving anticipated decisions and drafting the kickoff. Visual surface (the new warning) means a render/visual gate per COR-07.
- 2026-06-14: Done (committed `aa5da58`). One dispatch. Drafter+checker reached PASS on iteration 2: iteration 1 FAILed R1 (the epic-count source was left as an open option for the worker); the orchestrator resolved it by pinning the direct epic-file count (collect_roadmap_from_files omits phase-less epics and would undercount). Prelaunch W1 PASS. Close W2 PASS with one accepted nit: the executor misfiled a verification note ("Render gate") under Follow-ups with no coordination anchor; accepted-with-rationale because the real follow-up (a CSS hover-selector cleanup) is anchored and no follow-up is lost. Independently verified against disk: the etl `no_epic_warning` is additive (null for all in the clean state; current_phase=2/next_step/blocked byte-for-byte unchanged), fires correctly via a reverted fixture (backend-api with API-E-001 removed), and headless-renders the warning styling with no table regression; the create-department `<phase>`/forming-epic step and the tasks/README convention amendment match the kickoff. Guards COR-08 / ADR-041 against recurrence.
