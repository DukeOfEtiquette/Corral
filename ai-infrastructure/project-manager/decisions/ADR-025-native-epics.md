---
schema_version: 1
adr: 25
title: "Native epics"
status: "pending"
date: "2026-06-07"
related_adrs: [1, 12, 13, 17]
supersedes: []
superseded_by: null
---

# ADR-025: Native epics

> Pending: can wait. Frames the native epics model; needed before epic tools and schema amendments are scoped.

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

{Pending.}

## Consequences

{Pending.}
