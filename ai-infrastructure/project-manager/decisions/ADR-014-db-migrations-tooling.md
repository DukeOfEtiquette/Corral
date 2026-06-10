---
schema_version: 1
adr: 14
title: "Database migrations tooling"
status: "pending"
date: "2026-06-05"
related_adrs: [2, 12]
supersedes: []
superseded_by: null
---

# ADR-014: Database migrations tooling

> Pending: can wait. Needed before the second schema change, not the first boot.

## Context

Postgres (ADR-002) plus an evolving schema (ADR-012) means migrations. The tooling choice should fit the FastAPI ecosystem and run inside the compose topology (ADR-003), likely as a startup step or one-shot service.

## Alternatives considered

### Option A: Alembic

The standard for SQLAlchemy-based stacks; autogeneration support.

### Option B: Raw SQL migration files with a tiny runner

Maximum transparency, no magic; more hand maintenance.

### Option C: ORM-managed schema (e.g. SQLModel create_all) until v1 stabilizes

Fastest start; no real migration story, acceptable only while data is disposable.

## Decision

{Pending.}

## Consequences

{Pending.}
