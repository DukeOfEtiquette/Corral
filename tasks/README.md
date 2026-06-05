# Tasks (bootstrap convention)

Canonical task policy for the markdown era, per ADR-008. This convention is interim: at the dogfood milestone these tasks are imported into the app's own database through the MCP server, this tree is frozen read-only, and a fuller coordination doc supersedes this file.

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

Filename: `COR-T-NNN-<kebab-slug>.md`. IDs are allocated from `.next-task-id` (read the integer, use it, write back the increment). IDs are never reused; slugs are unique across the whole tree.

```markdown
---
schema_version: 1
id: COR-T-001
title: "Short imperative title"
status: backlog            # backlog | in-progress | blocked | done
labels: []                 # e.g. [dept:ai-infra]
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

## Rules

- Do not invent parallel TODO systems (rule in `../CLAUDE.md`); if it is work, it is a task file.
- One task per file; split rather than nest.
- Tasks reference ADRs and files by repo-relative path so they survive session boundaries.
