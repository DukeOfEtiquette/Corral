---
schema_version: 1
id: COR-T-009
title: "Resolve ADR-025: native epics"
status: in-progress
labels: [dept:backend-api]
priority: P2
created: 2026-06-07
updated: 2026-06-10
---

## Description

Take `./decisions/ADR-025-native-epics.md` from pending to accepted. Decide how native epics (parent issues grouping child issues) are modeled and exposed: pick among the three framed alternatives (distinct epics table + join, self-referential `parent_id` on issues, or a `type` column + parent relation), whether an issue may belong to more than one epic, the MCP tool additions (e.g. `epic_create`, child attach/detach, or an `epic` param on `issue_create`), and how epics render across multi-view boards (ADR-017 territory). Resolution amends the accepted ADR-012 schema via a *new* ADR (the ADR-024 precedent: accepted ADRs are amended by a later ADR, not edited), and adds the epic tools additively to the ADR-013 surface per ADR-019's versioning policy. Native epics replace the deliberately-dropped `issue_link` body-convention workaround.

## Activity log

- 2026-06-07: Created in backlog. Surfaced as a COR-T-004 Worker follow-up (ADR-025 queued pending with no tracker); triaged to backlog by the Orchestrator.
- 2026-06-10: Picked up; moved to in-progress. Orchestrator-direct ADR resolution (decisions/ carve-out, mirroring COR-T-008). Decisions pinned with the user: Option C model (issues.type column + nullable parent_id self-FK); at-most-one parent; epics not nested in v1; three additive MCP tools (epic_create, epic_attach, epic_detach); board treatment deferred to the Kanban phase (ADR-015/017).
