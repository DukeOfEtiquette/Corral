---
schema_version: 1
adr: 11
title: "Auth and session mechanism"
status: "pending"
date: "2026-06-05"
related_adrs: [6, 7, 10]
supersedes: []
superseded_by: null
---

# ADR-011: Auth and session mechanism

> Pending: blocks the first development iteration (Phase 1). Frames the question; decision not yet taken.

## Context

The app needs login for invited users (ADR-007), an admin-only page (ADR-006), and authenticated API access for the browser client. The hash algorithm for the admin bootstrap credential is finalized here too (bcrypt vs argon2). MCP server authentication to the API (if Option A in ADR-010 is taken) also lands here.

## Alternatives considered

### Option A: Server-side sessions with HTTP-only cookies

Simple, revocable, well-suited to a same-origin web app behind compose.

### Option B: JWT bearer tokens

Stateless; easier for non-browser clients (including the MCP server), harder to revoke.

### Option C: Library-provided auth (e.g. fastapi-users) vs hand-rolled minimal

Orthogonal axis: how much is built vs adopted.

## Decision

{Pending.}

## Consequences

{Pending.}
