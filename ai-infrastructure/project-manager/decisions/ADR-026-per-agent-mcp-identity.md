---
schema_version: 1
adr: 26
title: "Per-agent MCP identity"
status: "accepted"
date: "2026-06-10"
related_adrs: [4, 6, 7, 10, 11, 12, 13, 14, 20, 24]
supersedes: []
superseded_by: null
---

# ADR-026: Per-agent MCP identity

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

**Option A selected: per-agent API keys, with each agent a first-class machine identity in the `users` table and keys provisioned in deploy config.** This generalizes ADR-011's accepted mechanism (a single static service key, verified API-side, resolving to one shared identity) from one key to a keyed set of N keys mapping to N identities, reusing the same bearer-verified-API-side path rather than introducing a new auth paradigm. It extends ADR-011's service-credential model through this later ADR (the ADR-024 precedent: an accepted ADR is amended by a later ADR, not edited in place).

Option B (a single service key plus an asserted agent id) is rejected: it records attribution in the audit payload but leaves `issues.assignee_id` resolving to the one service user, so it cannot support per-agent claim-as-lease, which is the prerequisite ADR-020 named and the primary reason for this ADR. Option C (per-agent service-account users) is rejected: it conflates the human invite flow (ADR-007: email-bound, password-set, session-authenticated) with machine accounts, loading agents with auth machinery they do not use and undoing the human/machine separation ADR-011 chose deliberately.

### Credential model: per-agent API keys

Each fleet agent holds its own long random bearer secret in its environment. The REST API verifies the key and maps it to a distinct agent identity. Keys are stored hashed at rest, consistent with ADR-011's invite-token hashing and the service-key handling. The MCP server continues to present a bearer credential to the API per ADR-011; it now presents the acting agent's key rather than one shared key.

### Agents are first-class machine users

Each agent identity is a row in the `users` table, so the `issues.assignee_id` and `issue_events.actor_id` foreign keys (ADR-012) resolve to it. A machine-user row carries a `display_name` (the agent's identifier) and its hashed API key, but not the human-auth fields (`email`, `password_hash`, sessions): those stay owned by the human invite flow (ADR-007, ADR-011). A discriminator distinguishes machine identities from human users. The exact schema delta (a `kind`/`is_service` discriminator on `users` versus a separate `agent_credentials` table keyed to `user_id`, plus the key-storage columns) is implementation-phase, extending the ADR-011/ADR-012 schema through ADR-014 migration work. This ADR pins the model, not the DDL, mirroring ADR-011's altitude.

### Provisioning, rotation, revocation: deploy-config, operator-managed

Agent identities and their keys live in the deploy configuration (the gitignored `.env` per the ADR-006 secret convention), extending exactly how ADR-011 handles the machine service key (the service key is `.env`-held, in contrast to human invites and sessions, which ADR-011 makes admin-page-managed). The operator provisions an agent by adding its entry and key to the config; rotation and revocation are a config change plus a service restart. There is no self-registration, consistent with ADR-007's invite-only posture extended to machines. A runtime admin revocation surface (per-agent mint, list, revoke, as ADR-011 provides for invites) is not built in v1 and is not precluded; it can be added later if revoking a leaked key without a redeploy becomes a requirement.

### Claim-as-lease keys on agent identity (ADR-020 prerequisite supplied, not decided)

With per-agent identity, `issue_claim` (ADR-013) sets `issues.assignee_id` to the acting agent's machine-user row, so assignee-as-lease (ADR-020's Option C leaning) can finally distinguish one agent from another. This ADR supplies the identity prerequisite ADR-020 named; it does not decide ADR-020's concurrency model, which stays ADR-020's to resolve.

### Per-agent attribution in `issue_events`

Every MCP-mediated mutation records the acting agent's `actor_id` (ADR-012's `issue_events`), so the audit trail names which agent acted rather than collapsing to one shared service user. This is the direct resolution of ADR-011 Consequence #5.

### Gating and altitude

This ADR pins the model and direction now so that ADR-020 and the Phase 2/3 schema, auth, and MCP work can build against it; per-agent identity is not built before the MCP surface exists (Phase 3). Accepting it removes the "deferred to a future pending ADR" placeholder ADR-011 left. The exact DDL, the key-storage shape, the key-to-identity lookup, and the rotation tooling are implementation-phase (ADR-014).

## Consequences

1. **ADR-011 per-agent deferral closed.** ADR-011's Decision (MCP-to-API authentication) and Consequence #6 deferred per-agent identity to "a future pending ADR." This is that ADR. It extends ADR-011's single-shared-service-identity model to per-agent keys via a later ADR (the ADR-024 precedent: an accepted ADR is amended by a later ADR, not edited in place). Forward-pointer notes are added to ADR-011 Consequences #5 and #6.

2. **ADR-011 Consequence #5 coupling resolved.** The single-identity-to-claim-lease coupling ADR-011 recorded is removed: per-agent `assignee_id` now distinguishes agents, so both claim-as-lease and the `issue_events` audit trail can name the acting agent.

3. **ADR-012 `users`-table extension.** The `users` table now holds machine identities (agents) alongside human users, distinguished by a discriminator; `issues.assignee_id` and `issue_events.actor_id` resolve to either kind. The auth-field columns ADR-011 added (`email`, `password_hash`) stay human-only and are unset for machine rows. Exact DDL is implementation-phase (ADR-014). A forward-pointer note is added to ADR-012.

4. **ADR-020 prerequisite supplied, not resolved.** ADR-020's assignee-as-lease leaning (Option C) now has the per-agent identity it requires. This ADR does not resolve ADR-020; it removes the identity blocker so ADR-020 can decide the lease and concurrency model when taken up.

5. **ADR-013 `issue_claim` attribution sharpened; surface unchanged.** `issue_claim` and every other MCP mutation now attribute to the acting agent rather than the shared service user. The ADR-013 tool surface is unchanged: no new tool, no signature change, only the identity the API resolves the call to.

6. **Secret-handling consistency.** Per-agent keys follow the ADR-006 `.env` convention and ADR-011's hashed-at-rest storage; no key is written to a tracked file. The operator's deploy config now carries N agent keys in place of the one shared service key.

7. **Implementation-phase items named.** The `users` discriminator versus a separate credential table, key byte-length and hashing parameters, the key-to-identity lookup and index, and rotation tooling are implementation-phase (ADR-014). A runtime admin revocation surface is deferred and non-precluded.
