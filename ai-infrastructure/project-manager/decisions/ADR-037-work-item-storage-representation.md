---
schema_version: 1
adr: 37
title: "Work-item storage representation: epics and phases as first-class files"
status: "accepted"
date: "2026-06-12"
related_adrs: [8, 12, 25, 27, 31, 36, 38]
supersedes: []
superseded_by: null
---

# ADR-037: Work-item storage representation: epics and phases as first-class files

> Accepted 2026-06-12. Decides how Phases and Epics are stored in the markdown era, a representation ADR-036 left unpinned. Resolved alongside ADR-038 (Phase as a first-class View), which the import targets defined here point at. The decomposition itself is a dispatched follow-on (COR-T-044), not performed by this ADR.

> **Forward pointer (2026-06-13):** ADR-039 extends this source-only derivation pattern (contract preserved, source moved) from the roadmap to the STATUS activity surface: `last_updated` and `recent_updates` become derived (git-by-path) and leave STATUS.md frontmatter, the same churn-coupling resolution applied one level further. See ADR-039. ADR-040 extends the same pattern one further hop, deriving the `STATUS.md` narrative body (`## Current phase` / `## Next step` / `## Blocked on`) so no hand-authored content remains in `STATUS.md`. See ADR-040.

> **Forward pointer (2026-06-22):** ADR-045 reuses this ADR's generic per-workspace YAML discovery (the `epics/` walk in `collect_roadmap_from_files`) for a new structured file family: a per-workspace `services.yml` service/endpoint inventory, discovered the same way and rendered as a dashboard panel per the ADR-039/040 derived-surface model. Same structured-data-as-files discipline, applied to a new surface. See ADR-045.

## Context

ADR-036 pinned the work-item taxonomy and semantics (the five terms, strict containment, the `>= 2` cardinality conventions, status rollup, the dogfood import mapping) but did not decide *how each term is stored* in the markdown era. Its consequence 6 simply assumed the representation already in place: Tasks and ADRs are one markdown file each, while Phases and Epics are nested structures inside the `roadmap:` block of `ai-infrastructure/project-manager/STATUS.md` frontmatter. That representation is therefore an inherited implementation choice, never a reasoned decision.

Three problems motivate revisiting it.

1. **Import asymmetry.** ADR-036's mapping makes an Epic the same kind of app object as a Task (both issues, distinguished by `type` and `parent_id`), yet stores a Task as a file and an Epic as a buried frontmatter node. The source representation is inverted from the model it converges on, forcing the importer to be an interpreter (two read mechanisms) rather than a reader.

2. **Inverted containment direction.** The `roadmap:` block is the single place recording which tasks an epic contains; a task file does not know its epic. This is the opposite of how tasks cite ADRs (bottom-up) and the opposite of the app's own `task.parent_id -> epic` storage.

3. **Churn coupling.** STATUS.md frontmatter mixes a slow-changing plan (the roadmap) with a fast-growing changelog (`recent_updates`, appended every session), burying the roadmap's git history under changelog noise.

ADR-038 resolves the deeper half of this (Phase is now a first-class View entity, not a bare label), so making Phase a file in markdown has a first-class import target. This ADR decides the markdown-side representation against that model. A design conversation (2026-06-12) selected the file-based model below.

## Alternatives considered

### Option A: Split the roadmap into its own file, keep it embedded

Move the `roadmap:` block out of STATUS.md into a single `roadmap.yml`, but keep Phases and Epics as nested structures within it.

Rejected: this fixes only the churn coupling. The import asymmetry and the inverted containment direction remain, because epics are still frontmatter nodes and membership is still stored top-down in one file.

### Option B: Epics and phases each become a first-class file, with bottom-up linkage and a derived roadmap (selected)

Each Epic and each Phase becomes its own file; membership is stored bottom-up on the child (a task names its epic, an epic names its phase, mirroring `parent_id`); the roadmap becomes a view the dashboard derives from the files.

Selected: it makes the markdown isomorphic to the app end to end (epic = file -> issue, task = file -> issue, the linkage field -> `parent_id` / `phase:*` label, phase = file -> View per ADR-038), so the importer is a single reader dispatching on kind. It also resolves all three problems at once. The cost (placeholder phases for not-yet-started bands carried as files) is accepted as temporary and front-loaded deliberately.

### Option C: Hybrid (epics as files, phases in one ordered manifest, top-down membership)

Epics become files but phases stay in a single ordered manifest, and membership stays top-down (an epic lists its tasks).

Rejected: it keeps the inverted containment edge (top-down lists) and a second mechanism for phase, so it does not achieve the isomorphism that is the point.

## Decision

**Option B selected.** Epics and Phases each become a first-class file, stored as follows.

1. **File format: pure YAML with a concise `description` field.** Epics and phases are link-heavy and prose-light (their job is to relate work, not to narrate it), so they are `.yml` files whose structured fields carry the linkage and whose single `description` field stays to a concise line or two. This is a deliberate file-type split within the work-item family: Tasks and ADRs stay prose-first markdown (`.md`); Epics and Phases are structure-first YAML (`.yml`). The split is conscious, tracking the leaf-versus-container distinction, not an inconsistency to reconcile.

2. **Location and ownership.** Each workspace that owns epics (the `project-manager` coordinator and each department) gains an `epics/` tree alongside its `tasks/` tree (ADR-031), with its own `.next-epic-id` counter. Phases are cross-department bands (they group sibling epics from multiple departments, ADR-036), so they cannot live in any one department tree; the coordinator owns a single `phases/` tree under `ai-infrastructure/project-manager/`.

3. **Membership is bottom-up.** A Task gains an `epic:` frontmatter field naming its epic (absent for a standalone task). An Epic gains a `phase:` field naming its phase (absent for a standalone epic). These mirror the app's `parent_id` (task -> epic) and, per ADR-038, the `phase:*` label (epic -> phase). The top-down `tasks: []` / `epics: []` lists in the current roadmap block are removed.

4. **ID scheme: department-prefixed epics, numeric phases.** Epic IDs are department-prefixed and decoupled from phase (for example `COR-E-001`, `DB-E-001`), isomorphic with the task ID scheme (`COR-T-001`, `DB-T-001`) and stable when an epic is re-banded into another phase. This retires the phase-coupled `E<phase>.<seq>` ids (`E2.1`) the current roadmap uses. Phases are keyed by their number (files `phase-0` .. `phase-N`); the phase number is its order (ADR-038's first-class ordering).

5. **The roadmap becomes a derived view.** The dashboard ETL reconstructs the phase -> epic -> task roadmap from the files: walk the `epics/` trees, group epics by their `phase:` field, attach tasks by their `epic:` field, and roll status up per ADR-036. The roadmap is no longer authored as a block; it is computed, the same way task counts and epic status already are.

6. **The roadmap leaves STATUS.md.** With the roadmap derived from files, the `roadmap:` block is removed from STATUS.md frontmatter, resolving the churn coupling. STATUS.md keeps the current-phase narrative and the `recent_updates` changelog; the plan gets its own clean-diff home in the epic and phase files.

7. **Status stays derived; epic and phase files carry no status directory.** Unlike tasks (whose directory is their status, ADR-031), epic and phase files are definitions, not status-bearing objects: their status is the ADR-036 rollup, computed. A `phases/` and `epics/` tree has no `backlog/ in-progress/ blocked/ done/` subdivision. The hand-set status field survives only as the escape hatch for a not-yet-decomposed epic that has no tasks yet.

8. **Import targets (per ADR-038).** An epic file imports to a `type = epic` issue; a task's `epic:` field imports to that issue's `parent_id`; an epic's `phase:` field imports to a `phase:<n>` label on the epic issue; a phase file imports to a View plus its reserved `phase:<n>` label. The importer reads each from data already present in the files.

The decomposition (creating the trees, splitting the current roadmap block into epic and phase files, stamping `epic:`/`phase:` fields onto existing tasks and epics, rewriting the ETL reader, updating the `tasks/README.md` Vocabulary and layout, and removing the roadmap block from STATUS.md) is a single dispatched follow-on task, COR-T-044, the analog of ADR-036's restructure (COR-T-041). This ADR does not perform it.

## Consequences

1. **End-to-end import isomorphism.** Together with ADR-038, the markdown mirrors the app's model at every level (epic and task and phase each have a file and a direct app target), so the dogfood importer (ADR-008) is a single file-walker that dispatches on kind, not an interpreter.

2. **Containment direction matches the app.** Membership is stored bottom-up on the child (`epic:` on tasks, `phase:` on epics), the same direction as `parent_id`, removing the single-file roadmap bottleneck and making "what epic is this task in?" answerable from the task file.

3. **Churn coupling resolved.** The roadmap and the changelog no longer share a file; each has a clean, independent git history.

4. **Amends ADR-031.** Each workspace's tree gains an `epics/` sibling to `tasks/` (with its own `.next-epic-id`), and the coordinator additionally owns a `phases/` tree. A forward-pointer note is added to ADR-031. The per-workspace, per-prefix model is otherwise unchanged.

5. **A conscious file-type split.** The work-item family is no longer uniformly `.md`: leaves (tasks) and decisions (ADRs) are markdown; containers (epics, phases) are YAML. Accepted as tracking a real distinction (prose-first versus structure-first), not papered over.

6. **Cascade is dispatched, not done here.** The `tasks/README.md` Vocabulary and layout update, the `etl.py` reader rewrite, and the actual decomposition are COR-T-044, routed through the dispatched-worker flow. The dashboard data contract for the roadmap is expected to stay stable (the derivation changes its source, not its output shape), but confirming that is part of COR-T-044.

7. **Placeholder phases get heavier, temporarily.** Phases 3-8 (currently zero tasks) become files before their work begins. This is the accepted, front-loaded cost of paying the isomorphism early; it pays back as those phases fill in.
