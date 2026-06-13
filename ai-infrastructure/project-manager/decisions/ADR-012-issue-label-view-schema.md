---
schema_version: 1
adr: 12
title: "Database schema for issues, labels, and kanban views"
status: "accepted"
date: "2026-06-05"
related_adrs: [1, 8, 10, 13, 17, 18, 20, 25, 26]
supersedes: []
superseded_by: null
---

# ADR-012: Database schema for issues, labels, and kanban views

## Context

The core entities: issues, labels, the issue-to-label relation, and kanban view definitions (a view = a label filter + a column set over the same issue database, per ADR-001). Open dimensions: is `status` a first-class column (enum) or a special label family; are views stored in the database or in client config; what fields does an issue carry (title, body, status, priority, assignee, external_ref for the ADR-008 import, timestamps); how are comments / activity log modeled.

## Alternatives considered

### Option A: Status as a first-class column; views stored in the database

Views in the DB makes them shareable across users and addressable by the MCP server. Status as a column makes transitions explicit and indexable.

**Selected.** Within this option, `status` is stored as `text` with a `CHECK` constraint rather than a native Postgres `ENUM`: CHECK constraints are cheaper to migrate when the status set changes (no `ALTER TYPE`, no table lock), and are equally indexable. Priority is also modeled as a first-class column for the same reasons (see Consequences for the ADR-018 implication). Views in the database satisfy ADR-004's requirement that the MCP server can read and act on board state; per-machine view config would be invisible to it.

### Option B: Status as a reserved label family

Closer to GitHub's model; one mechanism for everything, but invariants ("exactly one status label") must be enforced everywhere.

**Rejected.** Enforcing "exactly one status label" at every mutation point (API, MCP server, import path) is more error-prone than a column-level CHECK constraint. The uniformity benefit does not outweigh the enforcement burden for a narrow-scope tracker.

### Option C: Views defined in client config only

Lighter, but per-machine and invisible to the MCP server.

**Rejected.** The MCP server is a first-class read and write path for LLM agents (ADR-004). Views that exist only in client config are invisible to it, breaking the multi-board use case. Per ADR-001, views must be durable, shared, and addressable by both the client and the MCP server.

## Decision

Eight tables constitute the v1 schema. All `id` columns are `bigserial` primary keys. All timestamp columns are `timestamptz not null`. The DDL blocks below are illustrative; this ADR is a decision record, not a migration file.

### users (minimal reference)

Carries only the identity fields needed for FK integrity in this schema. The full auth schema (password hash, invite tokens, session management) is owned by ADR-011 (pending). See Consequences item 3.

```sql
users (
  id           bigserial primary key,
  display_name text not null
)
```

### issues

`id` doubles as the human-facing issue number (no separate sequential counter). `status` and `priority` use `text` with `CHECK` constraints rather than native Postgres enums.

```sql
issues (
  id           bigserial primary key,
  title        text not null,
  body         text,
  status       text not null
               check (status in ('backlog', 'in-progress', 'blocked', 'done')),
  priority     text not null
               check (priority in ('P0', 'P1', 'P2', 'P3')),
  assignee_id  bigint references users(id),
  external_ref text unique,
  created_at   timestamptz not null,
  updated_at   timestamptz not null
)
```

`external_ref` is nullable; the `UNIQUE` constraint applies only to non-null values (standard Postgres null semantics). It carries the `COR-T-NNN` task id for the idempotent dogfood import per ADR-008.

### labels

Label taxonomy, reserved families, and creation permissions are owned by ADR-018 (pending). This table defines only the storage shape.

```sql
labels (
  id          bigserial primary key,
  name        text unique not null,
  color       text,
  description text
)
```

### issue_labels

```sql
issue_labels (
  issue_id bigint not null references issues(id),
  label_id bigint not null references labels(id),
  primary key (issue_id, label_id)
)
```

### views

A v1 view is name plus a label filter. The row carries no per-view column configuration; ADR-017 (pending) owns the final column-mapping decision. See Consequences item 4.

```sql
views (
  id   bigserial primary key,
  name text unique not null
)
```

### view_labels (view label filter)

The label filter for a view is stored in a join table, mirroring the `issue_labels` pattern. Match semantics are AND: an issue matches a view when it carries all of the view's filter labels. A view with no filter rows is the vacuous case and matches every issue.

```sql
view_labels (
  view_id  bigint not null references views(id),
  label_id bigint not null references labels(id),
  primary key (view_id, label_id)
)
```

### issue_comments

Stores both user-authored comments and imported activity-log lines from the markdown task convention. See Consequences item 2 for the import-mapping reconciliation.

```sql
issue_comments (
  id         bigserial primary key,
  issue_id   bigint not null references issues(id),
  author_id  bigint not null references users(id),
  body       text not null,
  created_at timestamptz not null
)
```

### issue_events

App-generated structured activity. `payload` is a `jsonb` object capturing old and new values; its shape varies by `event_type` (for example, `{"from": "backlog", "to": "in-progress"}` for a status change, or `{"label_id": 7}` for a label add or remove).

```sql
issue_events (
  id         bigserial primary key,
  issue_id   bigint not null references issues(id),
  actor_id   bigint not null references users(id),
  event_type text not null,
  payload    jsonb not null,
  created_at timestamptz not null
)
```

## Consequences

1. **ADR-018 priority narrowing.** Priority is a first-class column (`P0 | P1 | P2 | P3`), not a reserved label family. ADR-018's open question is narrowed: reserved label families under ADR-018 cover `dept:*` and any future families; the `priority:P0..P3` candidate from ADR-018's Option A leaning text is not a label family under this schema and is off the table.

2. **ADR-008 import-mapping reconciliation.** The migration mapping in `./tasks/README.md` maps activity-log lines to issue comments. That mapping remains valid as written: imported activity-log lines are unstructured dated text and land in `issue_comments`. `issue_events` records structured, app-generated events going forward only and plays no role in the import path.

3. **ADR-011 scope boundary.** ADR-012 defines only the minimal `users` table needed for FK integrity: `id` plus `display_name`. Auth fields (password hash, invite tokens, session management) are owned by ADR-011 (pending). The `assignee_id` FK on `issues` is the seam between this schema and ADR-011.

4. **ADR-017 view-shape alignment.** The `views` row carries no per-view column configuration, consistent with ADR-017's fixed-global-columns leaning. ADR-017 (pending) owns the final decision on whether columns are fixed globally or configurable per view; ADR-012 does not preempt that choice.

5. **ADR-020 non-preclusion.** The schema does not include a version column. ADR-020 (pending) owns the concurrency model. Adding a `version` column to `issues` (or other tables) in a future migration is not precluded by this schema.

6. **ADR-025 epic relation (forward pointer).** The `issues` table is amended by ADR-025 (accepted), which adds a `type` column (`task | epic`, CHECK-constrained) and a nullable self-referential `parent_id` FK for native epics. Per the ADR-024 precedent the amendment lives in that later ADR; the DDL block above stays as authored. See `./ADR-025-native-epics.md`.

7. **ADR-026 machine users (forward pointer).** The `users` table holds machine identities (fleet agents) alongside human users, per ADR-026 (accepted): an agent is a `users` row carrying `display_name` and a hashed API key but not the human-auth fields ADR-011 adds (`email`, `password_hash`), distinguished by a discriminator. `issues.assignee_id` and `issue_events.actor_id` resolve to either kind, so per-agent claim-as-lease and audit attribution work. Per the ADR-024 precedent the amendment lives in that later ADR; exact DDL is implementation-phase (ADR-014). See `./ADR-026-per-agent-mcp-identity.md`.

8. **ADR-038 phase Views (forward pointer).** ADR-038 (accepted) maps roadmap Phases onto the `views` model (a Phase is a View filtering on a reserved `phase:*` label) and adds a nullable ordering column to `views` for sequenced phase views; exact DDL is implementation-phase (ADR-014). Per the ADR-024 precedent the amendment lives in that later ADR; the `views` DDL block above stays as authored. See `./ADR-038-phase-as-first-class-view.md`.
