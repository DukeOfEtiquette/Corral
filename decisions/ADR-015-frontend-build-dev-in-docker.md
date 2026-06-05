---
schema_version: 1
adr: 15
title: "Frontend build and dev workflow inside Docker"
status: "pending"
date: "2026-06-05"
related_adrs: [2, 3]
supersedes: []
superseded_by: null
---

# ADR-015: Frontend build and dev workflow inside Docker

> Pending: can wait. Needed at the kanban UI phase.

## Context

The React client (ADR-002) must respect the compose-only run policy (ADR-003). Open: how does the dev loop work in containers (HMR), how is the client served in "production" mode, and how does it reach the API inside the compose network.

## Alternatives considered

### Option A: Vite dev-server container for development; static build served by the API or a tiny web server for deployment

Two compose profiles (dev vs deploy); standard pattern.

### Option B: Always build static, no dev container

Simpler topology, painful iteration loop.

### Option C: Dev server on host, containers for everything else

**Likely rejected:** violates the compose-only policy and reintroduces host drift.

## Decision

{Pending.}

## Consequences

{Pending.}
