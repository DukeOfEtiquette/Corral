---
schema_version: 1
adr: 17
title: "Kanban board column to status mapping"
status: "pending"
date: "2026-06-05"
related_adrs: [1, 12, 25]
supersedes: []
superseded_by: null
---

# ADR-017: Kanban board column to status mapping

> Pending: can wait. Needed at the kanban UI phase.

## Context

The user's existing flow uses Backlog, In Progress, Blocked, Done. Open: are board columns a fixed global set mapping one-to-one onto issue statuses, or configurable per view (ADR-012)? Where does the mapping live, and what happens to issues whose status has no column in a given view?

ADR-025 (native epics, accepted) does not change this question: epics are ordinary issues carrying their own status, so they flow through the same status columns and introduce no new column. This ADR additionally owns how the parent-child relation renders within a column (nesting child cards under their epic, a rollup affordance, an epic badge); ADR-025 deferred that visual treatment here, to the Kanban UI phase.

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
