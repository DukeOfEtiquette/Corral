---
schema_version: 1
id: COR-T-010
title: "Resolve ADR-026: per-agent MCP identity"
status: done
labels: [dept:backend-api]
priority: P3
created: 2026-06-08
updated: 2026-06-10
epic: COR-E-002
---

## Description

Take `./decisions/ADR-026-per-agent-mcp-identity.md` from pending to accepted. Decide the per-agent credential model (per-agent API keys, a single service key plus an asserted agent id, or per-agent service-account users), where agent identities are provisioned/rotated/revoked, how an agent identity maps onto the `users` table and `issues.assignee_id`, whether claim-as-lease (ADR-020) keys on it, and how per-agent attribution renders in `issue_events`. Deferred from COR-T-005/ADR-011, which pinned a single shared MCP service identity for v1. Gated on the MCP surface (Phase 3) being built and on ADR-020's concurrency model, since per-agent identity is premature before then; resolution extends ADR-011's service-credential model via a *new* ADR (the ADR-024 precedent: accepted ADRs are amended by a later ADR, not edited).

## Activity log

- 2026-06-08: Created in backlog. Surfaced as a COR-T-005 (ADR-011) Worker follow-up (single shared MCP service identity defers per-agent attribution); ADR-026 framed pending in the same change; triaged to backlog by the Orchestrator.
- 2026-06-10: Picked up; moved to in-progress. First task executed under the new "Pending-ADR resolution playbook" (ORCHESTRATOR-ROLE.md, via COR-T-019). Orchestrator-direct (decisions/ carve-out). Decisions pinned with the user: Option A (per-agent API keys; agents are first-class machine users in the `users` table with display_name + hashed key, no human-auth fields), keys provisioned in deploy config (`.env` per ADR-006, extending ADR-011's machine service-key handling); claim-as-lease prerequisite supplied to ADR-020 (not deciding ADR-020); per-agent actor_id attribution in issue_events; exact DDL deferred to implementation-phase (ADR-014).
- 2026-06-10: Done. ADR-026 set pending -> accepted (Option A; agents as machine users; deploy-config keys). Forward-pointer sweep over related_adrs (4/10/11/12/13/20): notes added to ADR-011 (Consequences 5/6 marked resolved), ADR-012 (new Consequence 7, machine users), ADR-013 (Consequence 3, assignee identity now per-agent), ADR-020 (Context, identity prerequisite supplied); related_adrs cross-links updated; ADR-011's historical "per-agent tokens" candidate text left as accurate record. OVERVIEW/README swept clean (no single-service-identity finality to update). STATUS: P1-5 closed, Next step repointed to Phase 2, hygiene applied. Deliverable committed as 117711e. Moved to done.
