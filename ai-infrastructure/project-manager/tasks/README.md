# Tasks (bootstrap convention)

Canonical task policy for the markdown era, per ADR-008 and ADR-031. This convention is interim: at the dogfood milestone these tasks are imported into the app's own database through the MCP server, all trees are frozen read-only, and a fuller coordination doc supersedes this file.

## Per-workspace task trees (ADR-031)

Every workspace (the `project-manager` coordinator and every department) owns its own `tasks/` tree. A task's workspace is implied by the tree it lives in; there is no shared pool partitioned by label. At the dogfood milestone (ADR-008) each tree's tasks are imported into the app, and the `dept:<slug>` label is applied from the tree at that point. Do not hand-apply `dept:*` labels to task files in the markdown era.

Each workspace's tree follows the same layout and format below, but with its own:
- ID prefix (coordinator uses `COR-T`; departments use their own prefix, e.g. `DB-T`, `API-T`).
- `.next-task-id` counter (plain integer; never shared across workspaces).

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
