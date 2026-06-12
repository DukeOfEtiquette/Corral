---
schema_version: 1
adr: 33
title: "Remote deployment topology for the shared Corral instance"
status: "pending"
date: "2026-06-12"
related_adrs: [3, 6, 11, 20, 26]
supersedes: []
superseded_by: null
---

# ADR-033: Remote deployment topology for the shared Corral instance

> Pending: gates roadmap Phase 6. Frames the open questions; decided when Phase 6 (remote deployment and concurrency) is taken up. Do not decide implicitly before then.

## Context

The roadmap's end goal (`./END-GOAL.md`) is a reusable project-manager that tracks its own and other projects' work through a single shared Corral instance rather than per-project markdown trees. The first step toward that (roadmap Phase 6) is to take the app off the local `docker compose` workstation (the only run path today, ADR-003) and stand it up on a remote server that many agent sessions, across machines and projects, reach concurrently.

This is the first time Corral runs as a shared, network-reachable service rather than a single-developer local stack. It surfaces deployment, persistence, identity, and networking questions that the local-only posture never forced. Phase 6 also exercises ADR-020 (the multi-user concurrency model) under real concurrent load for the first time; this ADR owns where and how the service runs, ADR-020 owns how conflicting writes resolve.

Open dimensions:

- **Hosting target.** Where the stack runs (a user-managed VPS, a home server, a managed container host) and how `docker compose up` (ADR-003) maps onto it, or whether a different runtime is adopted for the remote.
- **Data persistence and backup.** How the Postgres volume persists across restarts and redeploys, and what the backup story is for a database that is now the single source of project truth.
- **Remote agent authentication.** How agents on other machines authenticate to the remote MCP seam. ADR-026 (accepted) already makes each agent a first-class machine user with a hashed per-agent key; this ADR decides how those keys reach remote agents and how the service is exposed for them to present one (the ADR-011 bearer path over the network).
- **Networking and transport security.** Public vs private network exposure, TLS termination, and DNS for a service that now carries bearer credentials over the wire.
- **Secrets and bootstrap on the remote.** How the ADR-006 `.env` admin-bootstrap and per-agent keys are provisioned on a remote host without writing secrets into tracked files.
- **Concurrent-session reach.** How multiple simultaneous sessions connect and whether anything beyond ADR-020's concurrency model is needed at the deployment layer (connection limits, pooling).

## Alternatives considered

{Pending. Hosting target, persistence/backup strategy, remote auth exposure, and transport security are the dimensions to enumerate options against when this ADR is taken up.}

## Decision

{Pending.}

## Consequences

{Pending.}
