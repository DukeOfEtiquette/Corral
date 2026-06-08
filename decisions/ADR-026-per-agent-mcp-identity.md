---
schema_version: 1
adr: 26
title: "Per-agent MCP identity"
status: "pending"
date: "2026-06-08"
related_adrs: [4, 10, 11, 12, 13, 20]
supersedes: []
superseded_by: null
---

# ADR-026: Per-agent MCP identity

> Pending: deferred from ADR-011. Frames whether and how each agent gets its own identity through the MCP seam; not needed until the MCP surface is built (Phase 3) and agent-vs-agent claim contention becomes real.

## Context

ADR-011 resolved MCP-to-API authentication as a single static service API key with one shared service identity for all agents. That was selected for v1 because the agent fleet currently shares one seam (ADR-004) and per-agent credentials are premature before the MCP surface exists (ADR-013).

The consequence (ADR-011, Consequences item 5): every agent action through the MCP server is attributed to that one service user. Because `issue_claim` sets `issues.assignee_id` (ADR-013, over the ADR-012 schema) to the single service identity, claim-as-lease cannot distinguish one agent from another, and the `issue_events` audit trail (ADR-012) cannot record which agent acted. ADR-020 (pending) leans toward assignee-as-lease for agents (its Option C); per-agent identity is the prerequisite for agent-vs-agent claim contention.

This ADR frames whether and how to give each agent its own identity. It depends on the accepted MCP-as-API-client data path (ADR-010) and the resolved single-seam auth (ADR-011); resolving it will likely extend ADR-011's service-credential model through a later ADR (the ADR-024 precedent: an accepted ADR is amended by a later ADR, not edited in place) and interacts with the ADR-020 concurrency decision.

Open dimensions to resolve: the credential model; where agent identities are provisioned, rotated, and revoked; how an agent identity maps onto the `users` table and `issues.assignee_id` (are agents first-class users?); whether claim-as-lease (ADR-020) keys on agent identity; and how per-agent attribution renders in `issue_events`.

## Alternatives considered

### Option A: Per-agent API keys

Each fleet agent holds its own bearer key in its environment; the API maps each key to a distinct identity. Finest-grained attribution. Cost: the most credential management (provisioning, rotation, and revocation per agent), and the API must store and index a key set.

### Option B: Single service key plus an asserted agent id

The MCP server keeps one service credential (the ADR-011 key) but each call carries an agent identifier (header or parameter) that the API trusts and records. Lighter credential management; the MCP server is the trust boundary, so attribution is only as trustworthy as the asserted id.

### Option C: Per-agent service-account users

Each agent is a real row in the `users` table with its own credential, authenticating like an invited user. Unifies the agent and human identity model and reuses ADR-011's session machinery; heaviest setup, and it conflates the human invite flow (ADR-007) with machine accounts.

## Decision

{Pending.}

## Consequences

{Pending.}
