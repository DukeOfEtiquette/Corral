---
schema_version: 1
adr: 25
title: "Native epics"
status: "accepted"
date: "2026-06-10"
related_adrs: [1, 12, 13, 17, 18, 19, 24]
supersedes: []
superseded_by: null
---

# ADR-025: Native epics

## Context

Corral wants native epics (parent issues that group child issues), unlike the GitHub Issues workflow it replaces, where epics were faked with the `task_link` body-convention (a markdown checklist under `## Tracked work`). That workaround is deliberately not ported (see ADR-013). This ADR frames how native epics are modeled and exposed.

It depends on the accepted schema (ADR-012, which has no parent/child relation today) and the accepted v1 MCP surface (ADR-013, which omits epic tools); resolving it will amend ADR-012's schema via a new ADR (the ADR-024 precedent: an accepted ADR is amended by a later ADR, not edited in place) and add epic tools additively to the ADR-013 surface (policy per ADR-019).

Open dimensions to resolve: the MCP tool additions (for example, `epic_create`, child attach/detach, or an `epic` param on `issue_create`); how epics render across multi-view boards (ADR-017 territory); whether an issue may belong to more than one epic; and the migration that introduces the relation.

## Alternatives considered

### Option A: Epic as a distinct entity/table with a child-membership join

A separate `epics` table (id, title, body, status, etc.) with an `epic_issues` join table linking epics to child issues. Schema amendment: two new tables. Board/UI treatment: epics appear as a separate entity type; a child issue card can show its parent epic name.

### Option B: Self-referential parent relation on `issues`

A nullable `parent_id` (or `epic_id`) column on `issues` that points to another row in the same table. Schema amendment: one new nullable FK column on `issues`. Board/UI treatment: issues with no parent are top-level; issues with a parent are nested. An issue marked as an epic by convention (e.g. a `type:epic` label) groups its children.

### Option C: Issue `type` field plus a parent relation

An explicit `type` column on `issues` (values: `task`, `epic`) combined with a nullable `parent_id` FK. Schema amendment: one new `type` column (with CHECK constraint) and one nullable FK column on `issues`. Board/UI treatment: epics have a distinct rendering on the board; child tasks are rolled up under their parent epic.

## Decision

**Option C selected: an explicit `type` column on `issues` plus a nullable self-referential `parent_id` FK.** This is the most consistent with the accepted ADR-012 schema philosophy, which models first-class attributes as `text` columns with `CHECK` constraints (status, priority both done this way) and explicitly rejected convention-enforced-everywhere invariants (ADR-012 Option B rejected status-as-label for that reason). Option C makes epic-ness queryable and schema-enforced rather than a soft label convention (Option B), and keeps the surface to a single table with one new column and one new FK rather than a separate entity and join table (Option A).

### Schema amendment (amends ADR-012 via this later ADR, per the ADR-024 precedent)

Two columns are added to the `issues` table. The DDL is illustrative, consistent with ADR-012's framing (a decision record, not a migration file):

```sql
alter table issues
  add column type text not null default 'task'
      check (type in ('task', 'epic')),
  add column parent_id bigint references issues(id);
```

Invariants, enforced in the HTTP API layer (ADR-010's single enforcement seam, consistent with ADR-013):

- **At-most-one parent.** `parent_id` is a single nullable FK, so a child issue belongs to at most one epic (0 or 1). This mirrors the at-most-one cardinality ADR-018 pinned for the `dept:*` family. Many-to-many epic membership (Option A's join) is deliberately not supported in v1.
- **Children are tasks, parents are epics.** A `parent_id` may point only to a row with `type = 'epic'`; only a row with `type = 'task'` may carry a non-null `parent_id`.
- **Epics are not nested in v1.** A row with `type = 'epic'` must have `parent_id` null. Epic-of-epic hierarchies are out of scope; a flat one-level parent-child relation covers the headline use case and precludes nothing (nesting can be added later).
- **`type` backfills to `'task'`.** The `default 'task'` backfills every existing row on migration, so the column is non-null from the first migration with no data fixup.

### MCP surface additions (additive to the ADR-013 nine-tool surface)

Three new tools are added to the ADR-013 surface, additively (no existing tool changes name, parameters, or semantics; consistent with the additive approach ADR-013 Consequence #4 already names, with the formal versioning policy remaining ADR-019's to decide):

| Tool | Purpose |
|---|---|
| `epic_create` | Create an issue with `type = 'epic'` (and `parent_id` null); `priority` required per the ADR-013 `issue_create` house rule |
| `epic_attach` | Set a child task's `parent_id` to a given epic; refuses if the child is itself an epic, the target is not an epic, or the child is already attached (detach first) |
| `epic_detach` | Clear a child task's `parent_id` (back to top-level) |

The two read tools surface the relation in their response shape rather than as new tools: `issue_get` returns `type` and `parent_id` (and an epic's child list); `issue_list` returns `type` and `parent_id` and is filterable by them. These are additive response-field and filter extensions, not interface-breaking changes.

### Board rendering (deferred to the Kanban UI phase)

Epics are ordinary issues carrying their own `status`, so they flow through the same status columns as any issue; native epics introduce no new board column and no separate board or entity, leaving ADR-017's fixed-global-columns leaning intact. The concrete visual treatment of the parent-child relation (nesting child cards under their epic, a rollup affordance, an epic badge) is deferred to the Kanban UI phase (ADR-015, ADR-017), the same deferral ADR-018 applied to its label color palette. This ADR pins only that epics reuse the status-column model.

## Consequences

1. **ADR-012 schema amended by a later ADR.** Per the ADR-024 precedent (an accepted ADR is amended by a later ADR, not edited in place), this ADR adds `issues.type` and `issues.parent_id` to the ADR-012 schema. A forward-pointer note is added to ADR-012 directing readers here; ADR-012's DDL block stays as authored.

2. **ADR-013 surface grows additively.** ADR-013 Consequence #5 anticipated this ADR; it is now resolved. The epic tools (`epic_create`, `epic_attach`, `epic_detach`) are added additively, so the ADR-013 nine-tool table stays as authored and the three epic tools live here. A forward-pointer note is added to ADR-013 Consequence #5.

3. **`issue_link` stays dropped.** Native epics are the reason ADR-013 dropped ghtask's `task_link` body-convention workaround. With the parent-child relation now schema-native, the body-convention link tool remains unneeded, as ADR-013 intended.

4. **ADR-017 leaning preserved.** Because epics reuse the status-column model and add no new column, ADR-017's fixed-global-columns leaning (Option A) is not contradicted. ADR-017 remains pending and owns the final column decision; this ADR only adds the parent-child relation it will render.

5. **ADR-019 not preempted.** Adding epic tools additively is compatible with every ADR-019 alternative; this ADR does not decide the versioning policy. It adds tools in the additive manner ADR-013 Consequence #4 already names and leaves the formal policy to ADR-019.

6. **At-most-one matches the house style.** Single-parent cardinality echoes ADR-018's at-most-one `dept:*` decision, keeping the enforcement model uniform: a single nullable FK, validated API-side, rather than a join table whose multiplicity would have to be policed at every mutation point.

7. **ADR-036 work-item taxonomy (forward pointer).** The project's planning vocabulary is pinned in ADR-036 (accepted), which layers a roadmap taxonomy on this epic model: a roadmap Epic maps to a `type = epic` issue and a Task to a `type = task` issue with `parent_id` set to its epic, Phases become labels, and ADRs stay external references. ADR-036 adds the project-level taxonomy and cardinality conventions only; it does not change this schema. See `./ADR-036-work-item-taxonomy.md`.
