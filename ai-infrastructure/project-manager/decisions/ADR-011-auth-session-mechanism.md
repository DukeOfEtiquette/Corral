---
schema_version: 1
adr: 11
title: "Auth and session mechanism"
status: "accepted"
date: "2026-06-08"
related_adrs: [6, 7, 10, 12, 13, 20]
supersedes: []
superseded_by: null
---

# ADR-011: Auth and session mechanism

## Context

The app needs login for invited users (ADR-007), an admin-only page (ADR-006), and authenticated API access for the browser client. The hash algorithm for the admin bootstrap credential is finalized here too (bcrypt vs argon2). MCP server authentication to the API (if Option A in ADR-010 is taken) also lands here.

## Alternatives considered

### Option A: Server-side sessions with HTTP-only cookies

Simple, revocable, well-suited to a same-origin web app behind compose.

**Selected.** An opaque, high-entropy random session identifier is stored in an HTTP-only, SameSite cookie (Secure when served over HTTPS); session state is persisted server-side in a sessions store and is therefore directly revocable. The React client is same-origin behind the compose network, nothing requires statelessness, and instant revocation matters for an invite-only tool where admin control over active sessions is important. No token denylist, short-expiry-plus-refresh machinery, or cross-origin credential handling is needed.

### Option B: JWT bearer tokens

Stateless; easier for non-browser clients (including the MCP server), harder to revoke.

**Rejected.** Stateless tokens add revocation machinery (a denylist, or short expiry plus refresh cycle) that a single same-origin app does not need. The MCP server is an API client with its own service credential (see Decision below); browser-session convenience for non-browser clients is not a factor here. The added implementation complexity of token revocation is not justified.

### Option C: Library-provided auth (e.g. fastapi-users) vs hand-rolled minimal

Orthogonal axis: how much is built vs adopted.

**Resolved toward hand-rolled minimal.** Use trusted crypto and session primitives (argon2-cffi for password hashing; a server-side session store such as a sessions table keyed by the opaque cookie id, or Starlette session middleware backed server-side), but hand-write the small number of flows: admin seed, login, and invite redemption. No full auth framework (for example fastapi-users). The auth surface is deliberately narrow: invite-only with no self-registration (ADR-007), no password-reset email, no OAuth. A framework's main value-adds go unused while adding dependency weight and opinionated data models.

### Password hashing: argon2id vs bcrypt

ADR-006 deferred the hash algorithm choice (bcrypt or argon2; finalized here). Used for the admin bootstrap credential and for user passwords set at invite redemption.

**argon2id (via argon2-cffi) selected.** Greenfield project with no legacy hashes to honor; argon2id is the current OWASP first choice and is memory-hard. bcrypt is the rejected alternative: it has a 72-byte silent truncation limit, with no offsetting benefit in this context. The operator's local hash-generation step (ADR-006; README getting-started step 1) uses argon2id. This closes ADR-006's bcrypt-vs-argon2 open question.

### Invite-token mechanics

ADR-007 deferred token generation, expiry, and single-use enforcement to this ADR. Dimensions to pin: entropy source, email binding, single-use enforcement, expiry, storage, revocability, and redemption flow.

**Pinned properties (selected).** Tokens are: generated from a CSPRNG (high-entropy random), email-bound, single-use (consumed and invalidated on redemption), time-limited (an expiry is required), stored hashed at rest (never persisted in plaintext), and admin-revocable (mint, list, revoke on the ADR-006 admin page). Redemption verifies the token, then lets the invitee set a password (argon2id-hashed). Rejected alternatives: plaintext-token-at-rest and no-expiry. Exact token byte-length and expiry window are implementation-phase, consistent with ADR-010's altitude deferring endpoint specifics. This closes ADR-007's deferral of token generation, expiry, and single-use enforcement.

### MCP-to-API authentication: static service API key vs alternatives

ADR-010 Consequence #3 deferred the MCP server's service credential mechanism to this ADR. Candidates: static service API key, service-account-login (coupling MCP auth to the browser session model), or per-agent tokens.

**Static service API key selected; single shared service identity.** The MCP server authenticates to the REST API with a long random bearer secret held in the MCP server's gitignored `.env` (per the ADR-006 secret convention), verified by the API. One shared service identity for all agents. Minimal moving parts; matches the `.env` secret convention; fits the agent fleet that currently shares one seam (ADR-004). Service-account-login is the rejected alternative: it would couple MCP auth to the browser session model without benefit. Per-agent tokens are the rejected v1 alternative: premature before the MCP surface is built. Per-agent identity is explicitly deferred to a future pending ADR. This closes ADR-010 Consequence #3.

## Decision

Auth and session mechanism for the Corral web app is resolved across five dimensions:

**Browser session model: server-side sessions with HTTP-only cookies (Option A).**
An opaque, high-entropy random session identifier stored in an HTTP-only, SameSite cookie (Secure when served over HTTPS). Session state is persisted server-side in a sessions store (a sessions table keyed by the opaque session id, or equivalent Starlette session middleware backed server-side). Sessions are directly revocable by the admin.

**Build approach: hand-rolled on vetted primitives (Option C, resolved toward minimal).**
No full auth framework. Auth flows (admin seed, login, invite redemption) are hand-written using trusted primitives: argon2-cffi for password hashing, and a server-side session store. The auth surface is narrow by design: invite-only, no self-registration, no password-reset email (ADR-007).

**Password hashing: argon2id via argon2-cffi.**
argon2id is used for the admin bootstrap credential (closing ADR-006's bcrypt-vs-argon2 open question) and for user passwords set at invite redemption. The operator's local hash-generation step (ADR-006; README getting-started step 1) uses argon2id.

**Invite-token mechanics (closing ADR-007's deferral).**
Tokens are CSPRNG-generated, email-bound, single-use (consumed and invalidated on redemption), time-limited (expiry required), stored hashed at rest, and admin-revocable (mint, list, revoke on the admin page). Redemption verifies the token and lets the invitee set a password (argon2id-hashed). Exact token byte-length and expiry window are implementation-phase.

**MCP-to-API authentication: static service API key, single shared service identity (closing ADR-010 Consequence #3).**
The MCP server holds a long random bearer secret in its gitignored `.env` (per ADR-006 secret convention) and presents it as a bearer token to the REST API. One shared service identity for all agents. Per-agent identity is deferred to a future pending ADR.

**Auth schema boundary (per ADR-012 Consequence #3).**
ADR-011 owns the auth extension to the ADR-012 schema: `users` gains `email` (unique; the identity anchor per ADR-007) and `password_hash`; plus an invites concept (email, token-hash, expiry, consumed marker, created-by) and a sessions concept (opaque session id, user, expiry), or an equivalently capable signed-session store. Exact DDL, column names, and types are implementation-phase (ADR-014 migration work). The `assignee_id` FK on `issues` (ADR-012) is the seam between the core schema and the auth identity.

**Named, not decided (implementation-phase or future-ADR).**
Exact session lifetime, cookie-attribute specifics (for example, toggling the Secure flag for local HTTP dev), token byte-length and expiry windows, and the concrete DDL are implementation-phase. MCP contract versioning (ADR-019) and the multi-user concurrency model (ADR-020) are not touched beyond the claim-lease non-preclusion note in Consequences.

## Consequences

1. **ADR-006 closed (hash algorithm).** argon2id is the resolved hash algorithm for the admin bootstrap credential and invite-redemption user passwords. ADR-006's bcrypt-vs-argon2 open question is answered.

2. **ADR-007 closed (invite-token mechanics).** Token generation (CSPRNG), expiry (required), single-use enforcement, storage (hashed at rest), and admin revocability are pinned. ADR-007's deferral of these properties is resolved.

3. **ADR-010 Consequence #3 closed (MCP-to-API service credential).** The MCP server uses a static long-random bearer key in its `.env`; the API verifies it. One shared service identity. The token shape and session model deferred in ADR-010 are resolved here.

4. **ADR-012 Consequence #3: auth schema boundary defined.** ADR-012 scoped `users` to `id` plus `display_name` and handed the auth schema to ADR-011. ADR-011 now owns: `users` gains `email` (unique) and `password_hash`; plus an invites concept and a sessions concept (or equivalent). The `assignee_id` FK on `issues` (ADR-012) is the seam between the core schema and the auth identity. Exact DDL is implementation-phase and ADR-014 migration work.

5. **Single-identity to claim-lease coupling (ADR-013 and ADR-020).** Because all agents share one MCP service identity, `issues.assignee_id` set via ADR-013's `issue_claim` resolves to that single service user; claim-as-lease cannot distinguish one agent from another. ADR-020 (pending) leans toward assignee-as-lease (its Option C) so agents avoid contention by convention; per-agent identity is the prerequisite for agent-vs-agent claim contention. This non-preclusion note records the coupling; the per-agent-identity ADR will carry this rationale when it is drafted.

6. **Per-agent MCP identity deferred.** Per-agent service credentials are premature before the MCP surface is built. A future pending ADR owns this decision. No per-agent-identity ADR is created by this task.

7. **Implementation-phase items named.** Exact session lifetime, cookie-attribute specifics (for example, toggling the Secure flag for local HTTP dev), token byte-length and expiry windows, and the concrete DDL and migration are deferred to the implementation phase and ADR-014 migration work. MCP contract versioning (ADR-019) and the multi-user concurrency model (ADR-020) remain pending and are not resolved here.
