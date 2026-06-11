---
schema_version: 1
adr: 2
title: "Tech stack: FastAPI + Postgres backend, React frontend, FastMCP server"
status: "accepted"
date: "2026-06-05"
related_adrs: [1, 3, 4, 10, 14, 15]
supersedes: []
superseded_by: null
---

# ADR-002: Tech stack: FastAPI + Postgres backend, React frontend, FastMCP server

## Context

ADR-001 commits to building a client+server web app with an MCP server as the LLM contract (ADR-004). A stack decision was needed before any code lands. The user already operates a Python FastMCP server (`ghtask` in `~/rogue`), so Python MCP experience exists and is current.

## Alternatives considered

### Option A: Python API + React frontend

FastAPI + Postgres for the backend, React for the kanban client, Python FastMCP for the MCP server.

**Selected because:** it matches the user's existing ghtask MCP experience, and the MCP server and HTTP API can share Python models and validation code. Trade-off accepted: two languages in the repo (Python + TypeScript/JavaScript).

### Option B: TypeScript full-stack

Node (Fastify/Express) + Postgres, React, TypeScript MCP SDK.

**Rejected because:** one language across the stack is appealing, but it diverges from the user's proven Python MCP tooling and patterns, which are the part of this system with the highest correctness stakes (the LLM guardrail).

### Option C: Defer the decision to a later design phase

**Rejected because:** the stack choice gates almost every pending ADR (API shape, migrations, frontend build); deferring would stall Phase 1.

## Decision

Backend: Python FastAPI with Postgres. Frontend: React. MCP server: Python FastMCP. All confirmed with the user on 2026-06-05.

## Consequences

- The MCP server (ADR-004, ADR-013) and the API can share a Python package for models and house-rules validation.
- Postgres becomes a compose service (ADR-003) and needs a migrations decision (ADR-014). **Resolved:** ADR-014 (accepted) selects Alembic with hand-written migrations; no ORM is adopted in v1, so the data-access-layer choice stays a backend-api decision. See `./ADR-014-db-migrations-tooling.md`.
- The React client needs a build/dev-server-in-Docker decision (ADR-015).
- Contributors need Python and JS toolchains, both containerized per ADR-003 so host installs stay optional.
