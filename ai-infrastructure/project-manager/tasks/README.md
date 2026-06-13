# Tasks (bootstrap convention)

Canonical task policy for the markdown era, per ADR-008 and ADR-031. This convention is interim: at the dogfood milestone these tasks are imported into the app's own database through the MCP server, all trees are frozen read-only, and a fuller coordination doc supersedes this file.

## Per-workspace task trees (ADR-031)

Every workspace (the `project-manager` coordinator and every department) owns its own `tasks/` tree. A task's workspace is implied by the tree it lives in; there is no shared pool partitioned by label. At the dogfood milestone (ADR-008) each tree's tasks are imported into the app, and the `dept:<slug>` label is applied from the tree at that point. Do not hand-apply `dept:*` labels to task files in the markdown era.

Each workspace's tree follows the same layout and format below, but with its own:
- ID prefix (coordinator uses `COR-T`; departments use their own prefix, e.g. `DB-T`, `API-T`).
- `.next-task-id` counter (plain integer; never shared across workspaces).

## Vocabulary

The canonical work-item taxonomy for this project, per `./decisions/ADR-036-work-item-taxonomy.md` (the binding why and what). This section carries the operating how and cross-references ADR-036 for rationale. As of ADR-037, Phases and Epics are **first-class files** (pure YAML in `phases/` and `epics/` trees); see "Epics and phases" below for the storage convention.

| Term | What it is | Stored as |
|---|---|---|
| **Roadmap** | The time-ordered strategic view: epics arranged over phases, communicating direction and progress. A living artifact, not a unit of work. | Derived view (dashboard ETL reconstructs it from files) |
| **Phase** | A delivery band that groups epics. Sequential and gated. Completes when all its epics are done. | Pure YAML file in `ai-infrastructure/project-manager/phases/` (ADR-037, ADR-038) |
| **Epic** | A department-scoped deliverable capability composed of tasks. Completes when all its tasks are done. | Pure YAML file in the owning workspace's `epics/` tree (ADR-037) |
| **Task** | The atomic, indivisible unit of work. A leaf; completes on its own. | Markdown file in the owning workspace's `tasks/` tree (this convention) |
| **ADR** | A decision and governance record (the rationale). Not a unit of work; never "completes". Referenced by epics and tasks; not imported as a work item. | Markdown file in `./decisions/` (ADR-008) |

**Containment:** A Phase contains only Epics. An Epic contains only Tasks. A Task is a leaf; it contains nothing.

**Cardinality:** A Phase has at least 2 Epics; an Epic has at least 2 Tasks. These are project conventions describing intended shape, not schema constraints enforced by the database (ADR-025 permits looser). A forming epic may transiently hold fewer than 2 tasks while its siblings are filed.

**Standalones:** A standalone Epic belongs to no phase (but still follows the >= 2 Tasks convention). A standalone Task belongs to no epic. Both float at the top level alongside phases. Most one-off coordinator work items are standalone tasks.

**Epic scope:** An epic is department-scoped -- it has exactly one owning department, and all its tasks come from that department's task tree. Cross-department work is expressed as sibling epics under a shared phase, never as one epic reaching across departments.

**Status rollup:** A Task's status is its directory (`backlog`, `in-progress`, `blocked`, `done`). An Epic's status derives from its tasks: done when >= 1 task and all are done; planned when it has no tasks or all are in backlog; in-progress otherwise. A Phase is done when all its epics are done. ADR references never enter any rollup.

**ADRs drive no completion.** An accepted ADR never makes an epic or phase "done". Completion is a property of work (tasks); an ADR is a decision. See ADR-036 for the full rationale and the dogfood import mapping.

## Epics and phases (ADR-037, ADR-038)

Per `./decisions/ADR-037-work-item-storage-representation.md` (accepted 2026-06-12), Epics and Phases are first-class files, stored as pure YAML (`.yml`). This is a deliberate file-type split: Tasks and ADRs are prose-first markdown; Epics and Phases are structure-first YAML, tracking the leaf-versus-container distinction.

### Trees

- **`epics/` tree -- per workspace.** Each workspace that owns epics gains an `epics/` directory alongside its `tasks/` tree (ADR-031). The coordinator's tree is `ai-infrastructure/project-manager/epics/`; the database department's is `ai-infrastructure/database/epics/`. Each `epics/` tree carries its own `.next-epic-id` counter (a plain integer, never shared across workspaces). No `backlog/`, `in-progress/`, `blocked/`, or `done/` subdirectory: epic status is a derived rollup, not a directory.

- **`phases/` tree -- coordinator-owned.** Phases cross-cut all departments, so a single coordinator-owned tree holds all phase files: `ai-infrastructure/project-manager/phases/`. No counter file; phases are keyed by their number. Same no-status-directory rule.

### Epic file format

Filename: `<id>-<kebab-slug>.yml` (for example `COR-E-001-orchestration-system.yml`).

```yaml
schema_version: 1
id: COR-E-001                                  # department-prefixed: <DEPT-PREFIX>-E-NNN
title: "Orchestration system: roles, dispatch loop, agents"
dept: project-manager                          # owning department slug
phase: 1                                       # phase number (bottom-up linkage to the phase file)
description: "Concise one-line summary."
adrs: [23, 24, 28]                             # governing ADR numbers, informational
```

- **ID scheme:** department-prefixed and decoupled from phase (for example `COR-E-001`, `DB-E-001`), mirroring the task ID scheme (`COR-T-001`, `DB-T-001`). This retires the phase-coupled `E<phase>.<seq>` ids the former STATUS.md roadmap block used.
- **`phase:` field:** names the phase by number (bottom-up linkage, mirroring `parent_id` on tasks). Absent for a standalone epic.
- **Epics do not list their tasks.** Linkage is bottom-up: a task names its epic via the `epic:` frontmatter field (see below). The top-down `tasks: []` list is gone.

### Phase file format

Filename: `phase-<n>.yml` (for example `phase-1.yml`).

```yaml
schema_version: 1
id: 1                         # the phase number; its identity, its order
title: "AI infrastructure"
description: "Concise one-line summary."
order: 1                      # equal to id; ADR-038's first-class ordering field
# legacy: true                # present ONLY on phase-0; omitted for all other phases
```

- **`order` field:** carries phase sequence explicitly so the app and dashboard read it from the data rather than reconstructing it (ADR-038).
- **`legacy: true`:** present only on `phase-0` (Bootstrap), which predates the task system and is exempt from epic/task decomposition per ADR-036.

### Bottom-up linkage fields

- **`epic:` on tasks:** a task that belongs to an epic carries `epic: <id>` in its YAML frontmatter (for example `epic: COR-E-001`). Standalone tasks carry no `epic:` field. This field is the only linkage mechanism; there is no top-down task list on the epic file.
- **`phase:` on epics:** an epic that belongs to a phase carries `phase: <n>` in its YAML frontmatter. Standalone epics carry no `phase:` field.

Both fields mirror the app's `parent_id` direction (child names its parent), making the markdown isomorphic to the app model end to end (ADR-037 consequence 2, ADR-038).

### Lazy creation

Per ADR-021 and ADR-031: create an `epics/` tree for a workspace only when that workspace's first epic is ready to file (the `>= 2`-task convention from ADR-036). Do not create placeholder trees.

## Layout

```
tasks/
├── .next-task-id      # next unallocated NNN, plain integer
├── backlog/
├── in-progress/
├── blocked/
└── done/
```

The containing directory is authoritative for a task's status. Transitions are a plain `mv` between directories plus a frontmatter `status` + `updated` bump and an activity-log line.

Lifecycle: `backlog -> in-progress -> blocked -> done` (blocked is a detour, not a required stop; `done` tasks stay forever).

## File format

Filename: `<PREFIX>-T-NNN-<kebab-slug>.md` (e.g. `COR-T-001-foo.md` for the coordinator, `DB-T-001-foo.md` for the database department). IDs are allocated from `.next-task-id` (read the integer, use it, write back the increment). IDs are never reused; slugs are unique within a tree.

```markdown
---
schema_version: 1
id: COR-T-001
title: "Short imperative title"
status: backlog            # backlog | in-progress | blocked | done
labels: []                 # dept:* labels NOT hand-applied in markdown era (ADR-031)
priority: P2               # P0 (urgent) .. P3 (someday)
created: 2026-06-05
updated: 2026-06-05
---

## Description

What needs doing and why; enough context for a fresh session to act.

## Activity log

- 2026-06-05: Created in backlog.
```

The activity log is append-only, one dated line per event (created, claimed, moved, blocked-because, done-because).

## Migration mapping (why the fields look like this)

Every field maps mechanically onto the anticipated issue schema (ADR-012), so the future importer is a reader, not an interpreter:

| Task field | Issue column |
|---|---|
| `id` | `external_ref` (preserved for idempotent import) |
| `title` | `title` |
| `status` | `status` |
| `labels` | issue labels |
| `priority` | `priority` |
| `## Description` body | issue body |
| `## Activity log` lines | issue comments |
| `created` / `updated` | timestamps |

At import (ADR-008) the importer derives each task's `dept:<slug>` label from the tree it lives in and applies it inside the app; the label is not pre-populated in the markdown file.

## Rules

- Do not invent parallel TODO systems (rule in `../CLAUDE.md`); if it is work, it is a task file.
- One task per file; split rather than nest.
- Tasks reference ADRs and files by repo-relative path so they survive session boundaries.
- IDs are never reused. A gap in the sequence (e.g. because a task was relocated to another workspace) is fine; do not backfill.
