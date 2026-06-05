---
schema_version: 1
adr: 17
title: "Kanban board column to status mapping"
status: "pending"
date: "2026-06-05"
related_adrs: [1, 12]
supersedes: []
superseded_by: null
---

# ADR-017: Kanban board column to status mapping

> Pending: can wait. Needed at the kanban UI phase.

## Context

The user's existing flow uses Backlog, In Progress, Blocked, Done. Open: are board columns a fixed global set mapping one-to-one onto issue statuses, or configurable per view (ADR-012)? Where does the mapping live, and what happens to issues whose status has no column in a given view?

## Alternatives considered

### Option A: Fixed global columns equal to the status set

One mental model everywhere; matches current usage; zero configuration.

**Leaning selected for v1.**

### Option B: Per-view column configuration

Each view picks which statuses it shows as columns (and their order). More flexible, more UI and schema surface.

## Decision

{Pending.}

## Consequences

{Pending.}
