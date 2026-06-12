---
schema_version: 1
adr: 19
title: "MCP contract versioning policy"
status: "pending"
date: "2026-06-05"
related_adrs: [4, 13]
supersedes: []
superseded_by: null
---

# ADR-019: MCP contract versioning policy

> Pending: can wait. Needed once external agent fleets depend on the tool surface.

## Context

Once the agent fleet in `~/rogue` (or any other consumer) depends on this MCP server, changes to tool names, parameters, or house rules can silently break running orchestrations. The contract needs an explicit evolution policy.

> Forward pointer (ADR-016, accepted 2026-06-12): ADR-016 defers the MCP contract tests (golden per-tool request/response fixtures) to Phase 3 / `mcp-server`, decided alongside this versioning policy because the fixtures pin exactly the surface this ADR governs. Resolving ADR-019 and authoring the MCP contract-test corpus are expected to land together.

## Alternatives considered

### Option A: Additive-only policy

New tools and optional parameters may be added; existing tools never change semantics or remove parameters. Breaking changes require a new tool name.

### Option B: Versioned tool schema

A declared contract version surfaced by a `server_info` tool; consumers pin a version; semver discipline on changes.

### Option C: No policy until there are two consumers

Defer; cheapest now, riskiest later.

## Decision

{Pending.}

## Consequences

{Pending.}
