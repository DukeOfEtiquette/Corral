# COR-T-002: Resolve ADR-012 - issue, label, and view schema

## Target

This is **web-app** domain work (ADR-005): the artifact is a decision record about the web app's data model. No application code, SQL, migration, or compose files exist yet and none are written by this task. Your job is to take `./decisions/ADR-012-issue-label-view-schema.md` from `pending` to `accepted` by filling its stubbed sections with the schema the Orchestrator has already pinned (below), then applying one downstream documentation touch-up and the STATUS deltas. The Decision section must be precise enough that a fresh author of ADR-010 (API shape) or ADR-013 (MCP surface) could bind to it without asking questions; it is a decision record, not a migration file.

## Decisions resolved by the Orchestrator

Every decision below is pinned. Encode it as written; do not re-deliberate, do not re-open as options.

- **Status is a first-class column, not a label family** (ADR-012 Option A, confirmed with the user 2026-06-05). Values: `backlog | in-progress | blocked | done`, matching the lifecycle in `./tasks/README.md` and the existing flow ADR-017 cites. Store it as `text` with a `CHECK` constraint, not a native Postgres enum: cheaper to migrate when the status set changes, equally indexable.

- **Views are stored in the database, not client config** (ADR-012 Option A, confirmed with the user 2026-06-05): shareable across users and addressable by the MCP server. A v1 view is `name + label filter only`. The view row carries no per-view column configuration. This aligns with ADR-017's recorded leaning (fixed global columns), but ADR-017 (still pending) owns the final column-mapping call. ADR-012 must not preempt ADR-017 beyond keeping the view row free of column config.

- **Priority is a first-class column, not a reserved label family** (user call 2026-06-05). Values: `P0 | P1 | P2 | P3`, `text` with a `CHECK` constraint. This matches the committed migration mapping in `./tasks/README.md` (priority maps to a priority column) and resolves a latent contradiction with ADR-018's leaning text, which had listed `priority:P0..P3` as a candidate reserved label family. Record the consequence: ADR-018's open question is narrowed - priority is not a label family; reserved families under ADR-018 cover `dept:*` and any future families, not priority.

- **Comments and a structured events table are two separate tables** (user call 2026-06-05).
  - `issue_comments`: `id`, `issue_id` FK to issues, `author_id` FK to users, `body` (markdown text), `created_at`.
  - `issue_events` (structured, app-generated activity): `id`, `issue_id` FK to issues, `actor_id` FK to users, `event_type`, a structured payload capturing old/new values (e.g. status change, label add/remove, assignee change), `created_at`.
  - Reconciliation with the ADR-008 import mapping (`./tasks/README.md`: activity-log lines map to issue comments): imported activity-log lines are unstructured dated text, so they land as comments; `issue_events` records structured events going forward only. State this reconciliation in Consequences so the import mapping stays valid as written.

- **Assignee is a nullable FK to a minimal users table** (user call 2026-06-05). ADR-012 defines only the minimal user reference it needs for FKs: `users` carries `id` plus a display-identity column. The full users/invites schema (auth fields, password hash, invite tokens) is owned by ADR-011 (pending). State this scope boundary explicitly in Consequences.

- **Issue field set** (Orchestrator pin, assembled from ADR-012's context): `id` (bigserial PK, doubles as the human-facing issue number), `title` (text, required), `body` (markdown text), `status`, `priority`, `assignee_id` (nullable FK to users), `external_ref`, `created_at`, `updated_at`.

- **`external_ref`**: nullable text, unique when present, carries the `COR-T-NNN` task id for the idempotent dogfood import per ADR-008 (Orchestrator pin).

- **Labels storage shape** (Orchestrator pin): a `labels` table (`id`, `name` unique, `color`, optional `description`) plus an `issue_labels` join table (`issue_id`, `label_id`, composite PK). Label taxonomy, reserved families, and creation permissions stay with ADR-018 (pending); ADR-012 defines only the storage shape.

- **Concurrency: ADR-012 stays silent on version columns and locking** (Orchestrator pin). ADR-020 (pending) owns the concurrency model. The schema must not preclude adding a version column later; note this non-preclusion in Consequences.

- **ADR depth** (Orchestrator pin): the Decision section spells out tables, columns, types, and constraints precisely enough for ADR-010 and ADR-013 to bind to, but it is a decision record, not a migration file. Create no SQL or DDL files anywhere in the repo. Fenced illustrative DDL inside the ADR body is acceptable.

- **Resolve mechanics** (per `./decisions/README.md`): edit ADR-012 in place. Fill the stubbed Decision and Consequences sections; expand "Alternatives considered" with honest selected/rejected reasoning for Options A, B, and C; flip frontmatter `status` to `"accepted"`; bump the frontmatter `date` to the work date (2026-06-05). The append-only rule forbids deleting the existing framing, but the pending blockquote callout under the H1 is a status marker, not decision content: remove or replace it since the ADR is no longer pending.

## Deliverables

- `./decisions/ADR-012-issue-label-view-schema.md` updated in place:
  - frontmatter `status: "accepted"`, `date` bumped to the work date;
  - "Alternatives considered" expanded with honest selected/rejected reasoning for Options A, B, and C;
  - Decision filled with the complete pinned schema: `issues`, `labels`, `issue_labels`, `views`, `issue_comments`, `issue_events`, and the minimal `users` reference;
  - Consequences filled, covering all five of these items:
    1. the ADR-018 priority narrowing (priority is a column, not a label family);
    2. the ADR-008 import-mapping reconciliation (activity-log lines land as comments; `issue_events` is forward-only);
    3. the ADR-011 users/invites scope boundary (ADR-012 defines only the minimal user reference);
    4. the ADR-017 view-shape alignment (no per-view column config; ADR-017 owns the final call);
    5. the ADR-020 non-preclusion note (schema must not preclude a future version column).

- `./docs/architecture/OVERVIEW.md` line 25 touch-up. The line currently reads: `- **postgres**: owns all tracker data: issues, labels, views, users, invites (schema pending, ADR-012).` The parenthetical attributes the users/invites schema to ADR-012, which is wrong under the pinned scope boundary. Reword so issues/labels/views cite ADR-012 and users/invites cite ADR-011. This is a one-line edit; make no other change to OVERVIEW.md.

- `./STATUS.md` per "STATUS deltas" below.

## Files in scope

- `./decisions/ADR-012-issue-label-view-schema.md` (the primary deliverable; edit in place).
- `./docs/architecture/OVERVIEW.md` (the single line 25 touch-up described above; no other change).
- `./STATUS.md` (the deltas below plus universal hygiene).

## Files out of scope

- Every other ADR. ADR-010, ADR-011, ADR-013, ADR-014, ADR-017, ADR-018, ADR-020, and ADR-021 remain pending and unedited. ADR-012's Consequences may reference them but must never edit them.
- The `./tasks/` tree, including `./tasks/backlog/COR-T-002-resolve-adr-012-schema.md`. Task transitions and activity-log lines are Orchestrator-only per `./docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md`.
- `./tasks/README.md`. The Orchestrator verified its migration mapping remains correct under the pinned decisions (priority maps to a column; activity-log lines map to comments); no edit is needed.
- Any application code, SQL files, migration files, or compose files. That is Phase 2 work.

## References

Read these in the order listed; the order encodes how context layers.

- `./decisions/ADR-012-issue-label-view-schema.md`: the target. Read first; it carries the Context and the three options (A/B/C) you will expand.
- `./decisions/README.md`: ADR conventions - frontmatter schema, status values, body convention, the append-only rule. Governs how you flip status and date.
- `./decisions/ADR-001-self-hosted-issue-tracker-scope.md`: the product boundary (multi-view kanban over one issue pool) the schema serves.
- `./decisions/ADR-008-bootstrap-tasks-dogfood-milestone.md` and `./tasks/README.md`: the migration mapping the field set must satisfy and the `external_ref` import contract. Read together; `./tasks/README.md` carries the field-to-column mapping table.
- `./decisions/ADR-017-board-column-status-mapping.md`: the pending neighbour whose fixed-global-columns leaning the no-column-config view shape aligns with. Acknowledge without resolving.
- `./decisions/ADR-018-department-label-taxonomy.md`: the pending neighbour narrowed by the priority-as-column decision. Acknowledge without resolving.
- `./decisions/ADR-020-multi-user-concurrency-model.md`: the pending neighbour the non-preclusion note refers to. Acknowledge without resolving.
- `./docs/architecture/OVERVIEW.md`: the runtime shape; also carries the line 25 touch-up in scope.

## Related tasks and ADRs

- COR-T-003 (`./tasks/backlog/COR-T-003-resolve-adr-010-api-shape.md`): ADR-010 binds the API to this schema; this task unblocks it.
- COR-T-004 (`./tasks/backlog/COR-T-004-resolve-adr-013-mcp-surface.md`): ADR-013 binds the MCP tool surface to this schema; this task unblocks it.
- COR-T-005 (`./tasks/backlog/COR-T-005-resolve-adr-011-auth.md`): ADR-011 owns the full users/invites schema; the assignee FK defined here is the seam between the two.
- COR-T-006 (`./tasks/backlog/COR-T-006-resolve-adr-021-departments.md`): ADR-021's department list becomes the first `dept:*` labels stored in the labels table defined here.
- ADR-001: the product boundary (multi-view kanban over one issue pool) the views table realises.
- ADR-008: `external_ref` and the import mapping are this schema's dogfood contract.
- ADR-017: pending; the no-column-config view shape aligns with its leaning without resolving it.
- ADR-018: pending; narrowed by the priority-as-column decision recorded here.
- ADR-020: pending; the schema must not preclude a future version column.

## STATUS deltas

Task-specific delta beyond universal hygiene:

- In `./STATUS.md`, under "Next step", remove COR-T-002 from the remaining-backlog list. The line currently reads "Work the remaining Phase 1 backlog: COR-T-002 (schema, ADR-012), COR-T-003 ...". Drop the COR-T-002 entry and leave the rest of the list intact.

Universal STATUS hygiene (bump `last_updated`, append a `recent_updates` entry) is handled per `./docs/ai-orchestration/roles/WORKER-ROLE.md`, section "Wrap-up STATUS hygiene"; do not enumerate it here.

## Hard rules

- **Append-only ADR discipline.** Per `./decisions/README.md`, do not delete the existing Context or the option framing. Expand the Alternatives reasoning; fill the Decision and Consequences stubs. The only existing content you remove is the pending blockquote status marker under the H1.
- **No SQL or DDL files.** Illustrative fenced DDL inside the ADR body is acceptable; a `.sql`, migration, or schema file anywhere in the repo is not.
- **Do not preempt the pending neighbours.** ADR-012 references ADR-011, ADR-017, ADR-018, and ADR-020 in its Consequences; it does not resolve any of them and does not edit their files.
- **One acceptance gate.** ADR-012 reads as an accepted ADR whose Decision section a fresh ADR-010 or ADR-013 author could bind to without asking questions: frontmatter `accepted` plus bumped date, all pinned decisions encoded, all five Consequences items present, the OVERVIEW.md line 25 fix applied, and the STATUS deltas applied. The closing report confirms these criteria.

## Worker pointer

The Worker session is `/corral-worker`. Universal worker conventions (report shape, universal STATUS hygiene, the writing rules and Agent Discipline in `./CLAUDE.md`, git boundaries, compose-only run policy) live in `./docs/ai-orchestration/roles/WORKER-ROLE.md`; reference them rather than re-deriving them. Write the closing report to `./.claude/artifacts/tmp/COR-T-002-KICKOFF-REPORT.md` per WORKER-ROLE.md, section "Report shape".
