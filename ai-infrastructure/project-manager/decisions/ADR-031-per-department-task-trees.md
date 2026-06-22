---
schema_version: 1
adr: 31
title: "Per-department task trees: reverse ADR-027 Fork B's shared task pool"
status: "accepted"
date: "2026-06-11"
related_adrs: [1, 8, 18, 21, 27, 30]
supersedes: []
superseded_by: null
---

# ADR-031: Per-department task trees: reverse ADR-027 Fork B's shared task pool

## Context

ADR-027 Fork B chose a single shared task pool at `ai-infrastructure/project-manager/tasks/`, partitioned only by `dept:<slug>` label, and explicitly rejected "per-department task trees, the rogue default." Its rationale was to dogfood the product model (ADR-001: a single-pool, per-label-board issue tracker) from day one by using that same shape for the project's own markdown task management.

The first real department creation (COR-T-023, which stood up `database` and `backend-api`) surfaced the problem. With the departments live, their `/<slug>-orchestrator` smoke tests had to survey the coordinator's pool filtered by label and read the coordinator's `STATUS.md` to find their own work, because the departments had no task home of their own. The user identified this as an unintended divergence: the stated inspiration until the dogfood milestone is `~/rogue/ai-workspaces/`, where every workspace (including `project-manager` itself) owns a `tasks/` tree with its own ID prefix (`AT-T-`, `MAVDEV-T-`, `MATH-T-`, `PM-T-`). There is no shared pool in rogue.

Fork B conflated two distinct things: the **app's data model** (one pool, label-filtered boards, which is correct for the Corral web app) and the **markdown-era file layout** (which should mirror rogue until dogfooding). The dogfooding goal is better served by keeping the two separate: mirror rogue now, and let the single-pool/per-label-board model take over inside the app at import time, which is where ADR-001's headline feature actually lives and is validated.

## Alternatives considered

### Option A: Keep ADR-027 Fork B's single shared pool (rejected)

Retain one `tasks/` tree at the coordinator, partitioned by `dept:<slug>` label; departments stay task-tree-less.

**Rejected because:** it leaves every department without a home for its own work in the markdown era, forcing department orchestrators to survey the coordinator's pool and STATUS for their own tasks (observed directly in the COR-T-023 smoke tests). It diverges from the rogue inspiration the project follows until dogfooding, and it conflates the app's data model with the filesystem layout. The dogfooding rationale does not require it: ADR-001's single-pool model is validated inside the app after import, not by faking the shape in markdown.

### Option B: Per-department task trees, rogue-faithful (selected)

Every workspace (the `project-manager` coordinator and every department) owns its own `tasks/` tree (`backlog/`, `in-progress/`, `blocked/`, `done/`, plus a `.next-task-id` counter), exactly as rogue does. A task's department is implied by the tree it lives in, not by a label. The `dept:<slug>` label is applied at the dogfood import (ADR-008), when each tree's tasks import into the Corral app and the single-pool/per-label-board model (ADR-001) takes over inside the app.

**Selected because:** it mirrors the rogue inspiration, gives each department a real task home from creation, and preserves the ADR-001 dogfooding goal by relocating it to the app layer where it belongs. The trade-off accepted: more `tasks/` trees to scaffold and a dashboard ETL that reads many trees instead of one, in exchange for a structure that matches the inspiration and gives departments a real home.

### ID scheme (sub-decision under Option B)

**Per-department prefixes, coordinator keeps `COR-T` (selected).** Departments get rogue-style prefixes derived per department (`DB-T-NNN` for `database`, `API-T-NNN` for `backend-api`), each tree carrying its own `.next-task-id`. The existing `ai-infrastructure/project-manager/tasks/` tree stays as the coordinator's own tree with its established `COR-T-NNN` prefix unchanged; the settled `COR-T` history is not renamed.

**Rejected alternatives:** a single global `COR-T-NNN` counter distributed across per-department trees (the prefix would no longer identify the department, only the tree location would); and a full rogue-parity rename of the coordinator's tree to `PM-T-NNN` (cleaner symmetry, but it churns 20+ settled tasks and every cross-reference to `COR-T-NNN` across ADRs and STATUS for no functional gain).

## Decision

ADR-027 Fork B is reversed. Corral adopts per-department task trees, rogue-faithful:

1. **Every workspace owns a `tasks/` tree.** The `project-manager` coordinator and every department `ai-infrastructure/<dept>/` each own a `tasks/` directory with `backlog/`, `in-progress/`, `blocked/`, `done/`, and a `.next-task-id` counter, following the existing task convention (`ai-infrastructure/project-manager/tasks/README.md`) scoped to that workspace.

2. **Per-department ID prefixes; the coordinator keeps `COR-T`.** Each department allocates IDs with its own prefix (`<DEPT-PREFIX>-T-NNN`, for example `DB-T-001`, `API-T-001`) from its own `.next-task-id`. The coordinator's tree keeps `COR-T-NNN` and is not renamed.

3. **The tree is the partition; the `dept:<slug>` label is applied at dogfood import.** In the markdown era a task's department is implied by the tree it lives in, not by a hand-applied `dept:<slug>` label. At the dogfood milestone (ADR-008), each tree's tasks import into the Corral app carrying their workspace's `dept:<slug>` label, at which point the single-pool/per-label-board model (ADR-001, ADR-018 taxonomy) takes over inside the app. ADR-018's `dept:*` taxonomy is unchanged; only the moment of application moves from "now, in markdown" to "at import, in the app."

4. **The department scaffold (ADR-030) gains a `tasks/` tree.** The `templates/department/` baseline and the `/create-department` recipe add the per-department `tasks/` tree (the four state directories plus `.next-task-id`) and a department task-ID-prefix token. The department orchestrator command surveys its own `tasks/` tree, not the coordinator pool filtered by label.

5. **The implementation cascade is a named follow-on task** (see Consequences), routed through the dispatched-worker flow. This ADR is the spec it executes against.

## Consequences

- **ADR-027 Fork B partial amendment.** Fork B (and its "Single shared `dept:`-labeled task pool" alternative section and the `tasks/` line in the Decision tree) is superseded by this ADR. ADR-027 remains `accepted` and is not edited beyond a forward-pointer note (ADR-024/029/030 precedent: amend by a later ADR, never edit an accepted decision in place). ADR-027's other forks (A, C, D-as-amended-by-030, E) are unaffected, except that Fork D's and Fork E's "no `tasks/`" / "shared `tasks/` pool" mentions are now read through this ADR.

- **ADR-030 scaffold contract amendment.** The scaffold's "A department has NO own `tasks/`" clause is reversed: the baseline now includes a `tasks/` tree and a department task-ID-prefix token. ADR-030 gains a forward-pointer note; the `templates/department/` baseline and `/create-department` command are updated to match (deliverables, dispatched worker).

- **ADR-021 board mapping clarified.** ADR-021's "each `dept:*` label gets its own filtered kanban board at the dogfood milestone" is unchanged in substance; this ADR clarifies that the `dept:<slug>` label is applied to a department's tasks at that import, derived from the workspace tree, rather than hand-applied in the markdown era. ADR-021 gains a forward-pointer note.

- **The two live departments get task trees; COR-T-024 relocates.** `ai-infrastructure/database/tasks/` and `ai-infrastructure/backend-api/tasks/` are created. `COR-T-024` (the Postgres schema task, database work that was mis-filed into the coordinator pool under Fork B) relocates and is renamed to `DB-T-001` in `ai-infrastructure/database/tasks/backlog/`. The coordinator's `.next-task-id` reverts accordingly (the ID it consumed for COR-T-024 is freed); `database/tasks/.next-task-id` starts after `DB-T-001`.

- **Dashboard ETL reads many trees.** `ai-infrastructure/project-manager/dashboard/etl.py` is updated to read every workspace's `tasks/` tree (coordinator plus each department) instead of a single shared pool. The dogfood repoint (ADR-008) is unchanged.

- **Task convention doc scoped per workspace.** `ai-infrastructure/project-manager/tasks/README.md` is reframed from "the single COR-T pool" to "the per-workspace task convention" (each workspace owns a tree with its own prefix and `.next-task-id`), and the `dept:*`-label-partitions-the-pool language is replaced with the tree-is-the-partition, label-at-import model.

- **Dogfooding preserved, relocated to the app layer.** ADR-001's single-pool/per-label-board model is validated inside the Corral app after import, not faked in the markdown filesystem. This is a stronger self-referential test than Fork B's, because it exercises the real product surface.

- **One named follow-on task for the Orchestrator to queue:** the implementation cascade (update `templates/department/` and `/create-department`; re-point the `database` and `backend-api` orchestrator commands; create the two department `tasks/` trees; relocate `COR-T-024` to `DB-T-001`; update `etl.py`; reframe `tasks/README.md`; and sweep the shared-pool language in `project-manager/CLAUDE.md`, the template `CLAUDE.md`, `STATUS.md`, and `README.md`). It is a coordinator/agent-development deliverable and routes through the dispatched-worker flow.

- **ADR-037 epics/ sibling tree (forward pointer).** ADR-037 (accepted) extends this per-workspace tree model: each workspace that owns epics gains an `epics/` tree alongside its `tasks/` tree (with its own `.next-epic-id`), and the coordinator additionally owns a `phases/` tree. The per-workspace, per-prefix structure this ADR established is unchanged; epics and phases are a sibling planning representation, not a change to `tasks/`. See `./ADR-037-work-item-storage-representation.md`.

- **ADR-045 services.yml sibling file (forward pointer).** ADR-045 (accepted) extends this per-workspace model once more: each workspace that runs or plans a service gains an optional `services.yml` alongside its `tasks/` (and, where present, `epics/`) tree, discovered generically by the dashboard ETL across all workspaces. No ID counter is added (services are not ID-allocated). The per-workspace structure this ADR established is unchanged; the service inventory is a sibling structured surface. See `./ADR-045-service-endpoint-inventory-structured.md`.
