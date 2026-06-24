---
schema_version: 1
adr: 10
title: "API shape (REST vs GraphQL) and the MCP server's data path"
status: "accepted"
date: "2026-06-05"
related_adrs: [1, 2, 4, 6, 11, 12, 13, 14, 19]
supersedes: []
superseded_by: null
---

# ADR-010: API shape (REST vs GraphQL) and the MCP server's data path

## Context

Two coupled questions. First, what shape is the HTTP API the React client consumes: REST or GraphQL? Second, what does the MCP server (ADR-004) talk to: the HTTP API, or the database directly? The answer determines where house rules (ADR-013) are enforced and whether the MCP server can be built before or after the API.

## Alternatives considered

### Option A: REST API; MCP server calls the HTTP API

One enforcement seam: house rules live in the API layer and apply identically to the web client and the MCP tools. Cost: a network hop and API auth for the MCP server.

**Selected.** REST is FastAPI's native idiom and generates OpenAPI documentation automatically. The single enforcement seam means ADR-013's house rules live in the API layer and bind the web client and LLM agents identically, preserving ADR-004's guardrail intent. Accepted costs: a network hop inside the compose network, the MCP server requires service credentials (mechanism owned by ADR-011), and the API must exist before the MCP server can function.

### Option B: REST API; MCP server reads/writes the database directly

Faster and lets the MCP server ship before the API, but house rules must exist in two places or in a shared package that both must apply correctly.

**Rejected.** Dual enforcement paths (API layer and MCP server) would require the house rules defined in ADR-013 to be correctly applied in two independent code paths. ADR-004 requires enforcement on the server side where the model cannot skip it; a dual-path model creates the drift risk that ADR-004 was designed to prevent. Any enforcement bug in one path would silently bypass the guardrail.

### Option C: GraphQL API

Flexible queries for multi-view boards, but heavier tooling for a narrow resource model (issues, labels, views).

**Rejected.** The resource model is deliberately narrow (ADR-001, ADR-012): issues, labels, views, and their relations. GraphQL's flexibility and its associated tooling weight (schema definition, resolver structure, client query language) are not justified for a surface this small. FastAPI's native REST idiom with OpenAPI generation is the better fit.

## Decision

The HTTP API is REST, using FastAPI's native idiom with OpenAPI generation. All routes carry an `/api/v1` path prefix. The resource model maps 1:1 onto the accepted ADR-012 schema: issues, labels, views, issue_labels, view_labels, issue_comments, issue_events, and the minimal users reference. The full endpoint table (verbs, routes, payloads), error envelope format, and pagination conventions are implementation-phase decisions, not ADR content.

The MCP server (ADR-004, ADR-013) is an ordinary authenticated API client: it calls the HTTP API over the compose network and never touches Postgres directly. All data access, whether from the web client or from LLM agents, flows through the same API layer, enforcing a single seam for house rules.

## Consequences

1. **Build-order inversion.** Choosing the API data path means the MCP server cannot function before the API exists. The roadmap phases swap: Phase 2 becomes "API + DB core" (Postgres schema, FastAPI endpoints with house rules, auth/sessions, invite tokens, migrations per ADR-014, admin seeding per ADR-006; milestone: first moment the app can store an issue). Phase 3 becomes "MCP server" (FastMCP server as an authenticated API client per ADR-004 and this decision; milestone: the agent seam goes live). The README roadmap rows 2 and 3 were updated accordingly (COR-T-003).

2. **Single enforcement seam.** ADR-013's house rules live in the API layer only. The MCP server stays thin: it calls the API, which enforces the rules. The web client and LLM agents share the same enforcement path. No house-rule logic is duplicated in the MCP server.

3. **MCP-to-API service credentials.** The MCP server holds service credentials to authenticate to the API. The token shape and session model are deferred to ADR-011 (pending). **Forward pointer (COR-T-053, 2026-06-24):** ADR-011 has since been accepted (2026-06-08); read "ADR-011 (pending)" above as accepted. See `./ADR-011-auth-session-mechanism.md`.

4. **ADR-002 shared-package clarification.** ADR-002 anticipated a shared Python package for "models and house-rules validation." Under this decision, house-rules enforcement consolidates in the API layer and is not duplicated in the MCP server. The shared package carries models and types only; enforcement is not its responsibility. ADR-002 itself is not edited.

5. **`/api/v1` path prefix.** All REST routes carry this prefix. The full endpoint table, error envelope format, and pagination conventions are deferred to the API implementation phase. API path versioning is a separate concern from MCP contract versioning.

6. **ADR-019 independence.** MCP contract versioning (the stability policy for tool names, parameters, and house rules) is owned by ADR-019 (pending) and is independent of the `/api/v1` path prefix. The two versioning concerns are separate: one governs HTTP API routing, the other governs the MCP tool surface contract.
