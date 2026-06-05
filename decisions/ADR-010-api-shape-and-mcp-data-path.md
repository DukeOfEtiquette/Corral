---
schema_version: 1
adr: 10
title: "API shape (REST vs GraphQL) and the MCP server's data path"
status: "pending"
date: "2026-06-05"
related_adrs: [2, 4, 12, 13]
supersedes: []
superseded_by: null
---

# ADR-010: API shape (REST vs GraphQL) and the MCP server's data path

> Pending: blocks the first development iteration (Phase 1). Frames the question; decision not yet taken.

## Context

Two coupled questions. First, what shape is the HTTP API the React client consumes: REST or GraphQL? Second, what does the MCP server (ADR-004) talk to: the HTTP API, or the database directly? The answer determines where house rules (ADR-013) are enforced and whether the MCP server can be built before or after the API.

## Alternatives considered

### Option A: REST API; MCP server calls the HTTP API

One enforcement seam: house rules live in the API layer and apply identically to the web client and the MCP tools. Cost: a network hop and API auth for the MCP server.

**Leaning selected:** single home for validation outweighs the hop.

### Option B: REST API; MCP server reads/writes the database directly

Faster and lets the MCP server ship before the API, but house rules must exist in two places or in a shared package that both must apply correctly.

### Option C: GraphQL API

Flexible queries for multi-view boards, but heavier tooling for a narrow resource model (issues, labels, views).

## Decision

{Pending.}

## Consequences

{Pending.}
