---
schema_version: 1
id: COR-T-010
title: "Resolve ADR-026: per-agent MCP identity"
status: backlog
labels: [dept:backend-api]
priority: P3
created: 2026-06-08
updated: 2026-06-08
---

## Description

Take `./decisions/ADR-026-per-agent-mcp-identity.md` from pending to accepted. Decide the per-agent credential model (per-agent API keys, a single service key plus an asserted agent id, or per-agent service-account users), where agent identities are provisioned/rotated/revoked, how an agent identity maps onto the `users` table and `issues.assignee_id`, whether claim-as-lease (ADR-020) keys on it, and how per-agent attribution renders in `issue_events`. Deferred from COR-T-005/ADR-011, which pinned a single shared MCP service identity for v1. Gated on the MCP surface (Phase 3) being built and on ADR-020's concurrency model, since per-agent identity is premature before then; resolution extends ADR-011's service-credential model via a *new* ADR (the ADR-024 precedent: accepted ADRs are amended by a later ADR, not edited).

## Activity log

- 2026-06-08: Created in backlog. Surfaced as a COR-T-005 (ADR-011) Worker follow-up (single shared MCP service identity defers per-agent attribution); ADR-026 framed pending in the same change; triaged to backlog by the Orchestrator.
