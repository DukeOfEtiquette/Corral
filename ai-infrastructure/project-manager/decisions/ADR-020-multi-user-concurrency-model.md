---
schema_version: 1
adr: 20
title: "Multi-user concurrency model for issue mutations"
status: "pending"
date: "2026-06-05"
related_adrs: [12, 26]
supersedes: []
superseded_by: null
---

# ADR-020: Multi-user concurrency model for issue mutations

> Pending: can wait. Relevant once multiple humans and agents hit the same board.

## Context

Multiple users and multiple agents will eventually move and edit the same issues. Open: how conflicting writes are handled (two actors dragging the same card, simultaneous edits), and whether boards update live or on refresh.

## Alternatives considered

### Option A: Last-write-wins

Simplest; acceptable for small teams; silent lost updates possible.

### Option B: Optimistic concurrency with a version field

Mutations carry the version they read; stale writes are rejected with a refetch. Modest cost, removes silent loss.

### Option C: Claim/lease semantics for agents

Mirror ghtask's `task_claim` (assignee-as-lease) so agents avoid contention by convention; can combine with A or B for humans.

Per-agent identity, the prerequisite this option needs to distinguish one agent from another, is now resolved: ADR-026 (accepted) gives each agent a first-class machine-user identity, so `issues.assignee_id` set via `issue_claim` keys on the acting agent. This ADR still owns the lease and concurrency decision; ADR-026 only removed the identity blocker.

### Live updates (orthogonal)

Polling vs websockets/SSE for board freshness; can be decided separately or here.

## Decision

{Pending.}

## Consequences

{Pending.}
