---
schema_version: 1
adr: 3
title: "Docker Compose is the runtime: local-first but relocatable"
status: "accepted"
date: "2026-06-05"
related_adrs: [2, 6, 15]
supersedes: []
superseded_by: null
---

# ADR-003: Docker Compose is the runtime: local-first but relocatable

## Context

The app will initially run on the user's local machine, but a stated requirement is that it must later be shareable: runnable on other developer machines or on a centrally accessible server with no per-host setup drift.

## Alternatives considered

### Option A: Docker containers orchestrated by docker compose

Every service (database, API, frontend, MCP server) runs in a container; `docker compose up` / `docker compose down` is the entire lifecycle.

**Selected because:** it satisfies the stated requirement directly, makes the deployment identical across machines, and compose natively reads `.env` files, which ADR-006 relies on. Trade-off accepted: container build/dev-loop friction (addressed per-service, e.g. ADR-015 for the frontend).

### Option B: Bare-host installs with documented setup

**Rejected because:** host drift is exactly what the shareability requirement rules out; the user explicitly required containers.

### Option C: Kubernetes or similar heavier orchestration

**Rejected because:** wildly oversized for a small self-hosted tool; compose is sufficient for both local and small central-server deployments.

## Decision

The project must run inside Docker containers and be brought up and down with docker compose. This is a hard requirement, not a packaging convenience.

## Consequences

- A `docker-compose.yml` defining the service topology is a Phase 2+ deliverable; the anticipated services are sketched in `./docs/architecture/OVERVIEW.md`.
- Compose-native `.env` handling carries the admin bootstrap secret (ADR-006).
- Agents and humans never assume host-installed Python/Node; the supported run path is compose.
- Moving to a central server later is a compose-file concern, not an application rewrite.
