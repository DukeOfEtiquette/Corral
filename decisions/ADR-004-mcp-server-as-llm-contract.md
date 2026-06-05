---
schema_version: 1
adr: 4
title: "An MCP server is the sole contract for LLM interaction with the tracker"
status: "accepted"
date: "2026-06-05"
related_adrs: [1, 2, 10, 13, 19]
supersedes: []
superseded_by: null
---

# ADR-004: An MCP server is the sole contract for LLM interaction with the tracker

## Context

In the workflow this project replaces, LLM agents interact with GitHub Issues exclusively through an MCP server (`ghtask` in `~/rogue`). That MCP layer is deliberate: it is a guardrail. Agents are restricted to a small, validated tool surface instead of full access to a CLI or API, and "house rules" (required labels, valid status transitions) are enforced server-side where the model cannot skip them. This pattern has worked well and is the reason agent task coordination has stayed disciplined.

## Alternatives considered

### Option A: Purpose-built MCP server as the only LLM seam

All LLM reads and writes against the issue tracker flow through a FastMCP server exposing a small validated tool surface. Agents never receive raw database access, raw HTTP API credentials, or a CLI.

**Selected because:** it preserves the proven guardrail pattern, keeps enforcement on the server side, and makes the agent contract explicit and versionable (ADR-19). Trade-off accepted: every new agent capability requires an MCP tool change rather than ad-hoc API use.

### Option B: Give agents the HTTP API directly

**Rejected because:** a general-purpose REST surface is wider than agents need, validation tends to drift toward the client, and prompt-level restrictions ("only call these endpoints") are not enforcement.

### Option C: Give agents database or CLI access

**Rejected because:** this is precisely the failure mode the existing setup was designed to prevent; no enforcement layer at all.

## Decision

A purpose-built MCP server is a first-class deliverable of this project and the sole sanctioned path for any LLM agent to read or mutate tracker data. House rules are enforced inside the server, never delegated to the calling model.

## Consequences

- The MCP tool surface and its house rules need their own design decision (ADR-013), and the contract needs a versioning policy once external agent fleets depend on it (ADR-019).
- Whether the MCP server calls the HTTP API or the database directly is a pending decision (ADR-010).
- Until the MCP server exists, the markdown task convention in `./tasks/` is the interim seam (ADR-008).
- Agent-facing capability gaps surface as MCP tool requests, which is intended: the contract stays explicit.
