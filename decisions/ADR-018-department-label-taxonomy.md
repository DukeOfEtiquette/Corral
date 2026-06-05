---
schema_version: 1
adr: 18
title: "Department label taxonomy"
status: "pending"
date: "2026-06-05"
related_adrs: [1, 12, 13, 21]
supersedes: []
superseded_by: null
---

# ADR-018: Department label taxonomy

> Pending: can wait. Needed when multi-view filtering is built; interacts with ADR-021's department list.

## Context

The headline use case (ADR-001): one kanban board per department, filtered by a department label. Open: what a department label looks like (`dept:backend` namespaced vs flat names), whether other reserved label families exist (priority? type?), who can create labels (admin only vs any user vs MCP house rules per ADR-013), and label color/metadata. The departments decided in ADR-021 become the first `dept:*` labels at the dogfood milestone.

## Alternatives considered

### Option A: Namespaced families, rogue-style

`dept:*`, `priority:P0..P3`, free-form labels outside reserved families. Server enforces family invariants (e.g. at most one `dept:*`).

**Leaning selected:** matches the conventions the agent fleet already knows.

### Option B: Flat labels, no reserved families

Simplest schema; invariants become convention rather than enforcement, which ADR-004 argues against.

## Decision

{Pending.}

## Consequences

{Pending.}
