---
schema_version: 1
adr: 36
title: "Work-item taxonomy: roadmap, phase, epic, task, ADR"
status: "accepted"
date: "2026-06-13"
related_adrs: [1, 8, 12, 13, 21, 24, 25, 31]
supersedes: []
superseded_by: null
---

# ADR-036: Work-item taxonomy: roadmap, phase, epic, task, ADR

## Context

The dashboard roadmap work (COR-T-040) added deterministically-resolved task/ADR reference badges to the roadmap and derived each roadmap entry's status from its references. Building it surfaced that the project's planning vocabulary was informal and conflated. The terms `phase`, `milestone`, `task`, and `ADR` were used across `STATUS.md`, the dashboard, and the role docs without pinned definitions, relationships, or cardinality, and "milestone" overlapped with the Corral app's native `epic` (ADR-025) without anyone having decided whether they were the same thing.

Two forces make this worth pinning now rather than later:

1. **Strict followability.** Fresh agent sessions (and the human operator returning later) need one canonical answer to "what is a milestone / epic / task, and how do they relate," so planning artifacts are produced consistently rather than reinvented per session.
2. **The dogfood import (ADR-008).** At the dogfood milestone the markdown task tree imports into the Corral app through the MCP server, and the app's only native work hierarchy is ADR-025's `Epic -> Task` (a `type` column of `task | epic` plus a self-referential `parent_id`, flat, one level, no epic nesting). Whatever vocabulary the roadmap uses must map cleanly onto that model, or the import becomes an interpreter instead of a reader.

A design conversation (2026-06-12/13) resolved the model and the open cardinality questions with the operator. This ADR records the resulting taxonomy as binding. It also promotes observation COR-03 (hand-set milestone status as the dashboard's residual drift surface): once status rolls up from tasks, it is derived, not hand-maintained.

This ADR fixes project-level *taxonomy and roadmap semantics*. It does not change the database schema; ADR-025 remains the authority for the `issues.type` / `parent_id` model it builds on.

## Alternatives considered

### Option A: Keep "milestone" as a distinct work container alongside epic (status quo)

Leave the informal usage in place: phases contain milestones, milestones are bundles of work, epics are a separate app-only concept. Rejected: a milestone-as-work-bundle is functionally identical to ADR-025's epic, the app has no `milestone` type, and the duplication is precisely the source of the conflation and the COR-03 drift (two names, two status sources, for one concept).

### Option B: Keep "milestone" but redefine it as a best-practice checkpoint marker

In strict agile/PM vocabulary a "milestone" is a zero-duration checkpoint or event (for example "Beta launched", "Dogfood live"), not a container of work. We could retain the word for that meaning, distinct from epic. Considered and held in reserve: this is a legitimate and available meaning, but it adds a planning surface v1 does not need. "Phase N complete" already serves as the implicit checkpoint. The marker concept can be reintroduced later without contradicting this ADR; what this ADR forbids is "milestone" meaning "a bundle of tasks."

### Option C: Retire "milestone"; standardize on a four-term taxonomy mapped onto ADR-025 (selected)

Adopt `Phase`, `Epic`, `Task`, and `ADR` as the canonical terms (with `Roadmap` as the artifact that arranges them), with strict containment and cardinality, and retire "milestone" as a work container. This collapses the redundant concept onto the app's native `epic`, gives the import a one-to-one mapping, and makes status a derivation rather than a hand-set field.

## Decision

**Option C selected.** The canonical work-item taxonomy is the following.

### Terms

| Term | What it is | Completes when | App mapping at dogfood (ADR-008/ADR-025) |
|---|---|---|---|
| **Roadmap** | The time-ordered strategic view: epics arranged over phases, communicating direction and progress. A living artifact, not a unit of work. | n/a (a view) | a board view (the dashboard until import) |
| **Phase** | A delivery band that groups epics. Sequential and gated. | all its epics are done | a label (for example `phase:2`); not a work item |
| **Epic** | A department-scoped deliverable capability composed of tasks. | all its tasks are done | an issue with `type = epic` carrying its department's `dept:<slug>` label |
| **Task** | The atomic, indivisible unit of work. | on its own (it is a leaf) | an issue with `type = task`, `parent_id` -> its epic (or null) |
| **ADR** | A decision and governance record (the rationale). Not a unit of work; never "completes". | n/a | external (`decisions/`); referenced by issues, not imported as an issue |

### Containment and cardinality

- **Strict containment.** A Phase contains only Epics. An Epic contains only Tasks. A Task is a leaf.
- **Minimum cardinality.** A Phase has at least 2 Epics. An Epic has at least 2 Tasks. A grouping that would have a single child is not that grouping (a lone epic-under-a-phase is a standalone epic; a lone task-under-an-epic is a standalone task).
- **Standalones float at the top level.** A *standalone Epic* is an epic that belongs to no phase (it still has at least 2 tasks). A *standalone Task* is a task that belongs to no epic. Because phases contain only epics, a standalone task is never a phase member; it sits at the top level alongside phases and standalone epics. Most one-off coordinator work items (a rename, a single ADR resolution) are standalone tasks, and that is expected.
- **The minimums are conventions, not schema constraints.** ADR-025 permits an epic with zero children; these `>= 2` rules are a project modeling convention enforced by discipline and by a dashboard consistency check, not by the database. They describe the *intended shape*: a forming epic may transiently hold fewer than 2 tasks before its siblings are filed.

### Epic scope (department-scoped)

- **An epic is department-scoped: it has exactly one owning department, and all its tasks come from that department's task tree (ADR-031).** The coordinator (`project-manager`) counts as a department for this purpose; its `COR-T` epics are coordinator-scoped.
- **Cross-department work is expressed as sibling epics under a shared phase, never as one epic reaching across departments.** A phase is the cross-cutting band; a capability spanning, for example, database and backend-api is two department-scoped epics (one per department) grouped by the phase. Phase 2 (E2.1 Database + E2.2 Backend API) is the worked example.
- **Why single-owner.** Each department has its own orchestrator and task tree (ADR-027, ADR-031); a department-scoped epic has exactly one owner/driver, and at the dogfood import (ADR-008) it carries that department's single `dept:<slug>` label. A cross-department epic would have no single owner and no single import label.
- **Each epic records its owning department** (a `dept` field on the roadmap epic), which the dashboard renders as the epic's leading badge. Enforced as a convention by a dashboard consistency check that flags an epic whose tasks span more than one department tree (dormant while every epic is single-tree), the same convention-plus-check model as the cardinality minimums.

### Completion and status

- **Status rolls up.** A Task's status is its own: the directory it lives in, per ADR-031 (`backlog`, `in-progress`, `blocked`, `done`). An Epic's status is derived from its tasks: **done** when it has at least one task and all are done; **planned** when it has no tasks or all its tasks are still in backlog; **in-progress** otherwise (some tasks done, or any task in-progress or blocked). Partial progress reads as in-progress, not planned (one of two tasks done is in-progress). A Phase is **done** when all its epics are done (a `legacy` phase is done by fiat); otherwise it is the current or an upcoming band by its position. ADR references never enter any of these rollups.
- **ADRs drive no completion.** An ADR being accepted never makes an epic or phase "done". This is the principle behind COR-T-040's "tasks drive done-ness, ADRs are informational": completion is a property of *work* (tasks), and an ADR is a *decision*, not work.

### The role of ADRs

- An ADR is a decision and governance record, referenced by the epics and tasks it governs and never a parent of them. The reference is many-to-many: an epic or task may cite zero or more ADRs; an ADR may govern zero or more epics or tasks.
- **An ADR spawns work sized like any work.** Accepting an ADR does not create an epic or a task automatically; it may *imply* follow-on work, which is sized normally: a large body of work becomes an Epic (with its tasks), a small change becomes a Task (standalone or under an existing epic). The ADR is referenced by that work; it never becomes or contains it.
- **The act of deciding is itself a Task.** Authoring and accepting an ADR is usually done as a coordination Task (for example COR-T-008 produced ADR-018). So an ADR sits at the center of a reference hub: produced by a task, governing other epics and tasks, containing none of them.

### Dogfood mapping (ADR-008)

At import, Epics become `type = epic` issues, Tasks become `type = task` issues with `parent_id` set to their epic (or null for standalone tasks), Phases become labels, and ADRs remain external decision records that issues reference (by link or label). The markdown roadmap therefore imports onto the app's native model with no impedance.

## Consequences

1. **"Milestone" is retired as a work container.** Wherever the roadmap, the dashboard, or the docs used "milestone" to mean a bundle of work, it becomes "Epic". The marker meaning (Option B) is left available but unused in v1. ADR-008's title phrase "dogfooding is an explicit milestone" uses "milestone" in the generic event sense, not the retired work-container sense, and stays as authored; a forward-pointer note is added there.

2. **The existing roadmap is restructured, not merely renamed.** Most current roadmap entries are single-task (for example P2-1 -> DB-T-001, P1-1 -> COR-T-001) and so are not epics under the new cardinality. They are regrouped into department-aligned epics (for example Phase 2 -> a Database epic and a Backend API epic, with the current entries becoming their tasks) or recorded as top-level standalone tasks. This restructure is a planned follow-on and replaces the "stage-4 backfill" originally scoped under COR-T-040.

3. **COR-03 promoted.** Epic and phase status are derived from task rollup rather than hand-set, removing the residual hand-maintained drift surface that COR-03 logged. The hand-set status field survives only as the escape hatch for a not-yet-decomposed future epic that has no tasks yet.

4. **Cardinality is enforced by convention plus a check, not by schema.** The `>= 2` minimums are a modeling convention. A candidate dashboard consistency check flags an epic with fewer than 2 tasks or a phase with fewer than 2 epics; until built, the minimums are an authoring discipline.

5. **The dogfood import (ADR-008) gets a one-to-one mapping.** Because the taxonomy is defined against ADR-025's native model, the importer is a reader, not an interpreter: epics, tasks, the parent relation, and phase labels all have direct homes, and ADRs stay external by design.

6. **A canonical operating reference carries the how-to-follow.** This ADR is the binding *why and what*; a "Vocabulary" section in `../tasks/README.md` (the canonical work convention for the markdown era) carries the operating *how* and points back here. Propagating the taxonomy into `../tasks/README.md`, `STATUS.md`, the dashboard, and the role docs is the rename-and-reshape cascade, filed as a follow-on (the analog of the ADR-032 rename cascade, COR-T-036).

7. **This ADR does not touch the schema.** ADR-025 remains the authority for `issues.type` and `parent_id`. This ADR layers the project's planning taxonomy and roadmap semantics on top of that model; a forward-pointer note is added to ADR-025.
