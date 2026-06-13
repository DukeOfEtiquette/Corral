---
schema_version: 1
id: COR-T-042
title: "ADR-036 vocabulary cascade: tasks/README Vocabulary section + milestone->epic doc sweep"
status: in-progress
labels: []
priority: P2
created: 2026-06-13
updated: 2026-06-13
---

## Description

The final ADR-036 follow-on: propagate the work-item taxonomy into the operating docs so fresh sessions follow it strictly. Two parts, both documentation deliverables (routes through the dispatched-worker flow):

1. **Add a "Vocabulary" section to `ai-infrastructure/project-manager/tasks/README.md`** (the canonical work convention for the markdown era). It carries the operating *how* of the taxonomy and points to ADR-036 for the *why*: define Roadmap, Phase, Epic, Task, ADR; the strict containment (Phase contains only Epics; Epic only Tasks; Task is a leaf); the `>= 2` cardinality conventions (and that they are conventions describing intended shape, not schema constraints); department-scoped epics (one owning department; cross-department work = sibling epics under a phase); standalones float at the top level; status rolls up task -> epic -> phase; ADRs are governing references that never drive completion.

2. **Sweep the work-container sense of "milestone" to "epic"** in exactly three live-doc spots (the only work-container uses; every other "milestone" in the docs is the dogfood-*event* sense and must be left untouched):
   - `docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md` line ~101 (Pending-ADR playbook step 6): "update 'Next step' and the roadmap milestone" -> "the roadmap epic".
   - `README.md` line ~52: "Live phase and milestone status" -> "Live phase and epic status".
   - `END-GOAL.md` line ~35: "the authoritative live status with sub-milestones" -> "...with epics".

Out of scope (do NOT touch): every "dogfood milestone" / "dogfood-milestone" occurrence (the event sense; correct as written) in README.md:61, docs/README.md:33, END-GOAL.md:25/29, the three `*-orchestrator.md` commands, create-department.md, tasks/README.md:3/7, KICKOFF-CHECKER-SPEC.md, KICKOFF-DRAFTER-SPEC.md, ORCHESTRATOR-ROLE.md:85; the done task file `DB-T-001` (historical record); and the dashboard `.roadmap-milestone-*` / `.badge-milestone-*` CSS class names (a separate dead-CSS cleanup, not a vocabulary change).

Source of truth for the Vocabulary content is ADR-036 (`ai-infrastructure/project-manager/decisions/ADR-036-work-item-taxonomy.md`).

## Activity log

- 2026-06-13: Created and picked up (in-progress). The last ADR-036 follow-on (after the STATUS restructure and the COR-T-041 dashboard reshape, both committed). Routes through the dispatched-worker flow (documentation deliverable). Milestone-occurrence survey done by the orchestrator: exactly 3 work-container spots to sweep, the rest are the event sense and stay.
