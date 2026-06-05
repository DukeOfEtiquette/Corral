---
schema_version: 1
adr: 12
title: "Database schema for issues, labels, and kanban views"
status: "pending"
date: "2026-06-05"
related_adrs: [1, 8, 10, 13, 17, 18, 20]
supersedes: []
superseded_by: null
---

# ADR-012: Database schema for issues, labels, and kanban views

> Pending: blocks the first development iteration (Phase 1). Frames the question; decision not yet taken. Both the API (ADR-010) and the MCP tool surface (ADR-013) bind to this schema.

## Context

The core entities: issues, labels, the issue-to-label relation, and kanban view definitions (a view = a label filter + a column set over the same issue database, per ADR-001). Open dimensions: is `status` a first-class column (enum) or a special label family; are views stored in the database or in client config; what fields does an issue carry (title, body, status, priority, assignee, external_ref for the ADR-008 import, timestamps); how are comments / activity log modeled.

## Alternatives considered

### Option A: Status as a first-class enum column; views stored in the database

Views in the DB makes them shareable across users and addressable by the MCP server. Status as a column makes transitions explicit and indexable.

**Leaning selected.**

### Option B: Status as a reserved label family

Closer to GitHub's model; one mechanism for everything, but invariants ("exactly one status label") must be enforced everywhere.

### Option C: Views defined in client config only

Lighter, but per-machine and invisible to the MCP server.

## Decision

{Pending.}

## Consequences

{Pending.}
