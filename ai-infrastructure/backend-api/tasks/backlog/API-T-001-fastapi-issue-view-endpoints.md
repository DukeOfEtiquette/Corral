---
schema_version: 1
id: API-T-001
title: "Stand up the FastAPI api service and the v1 issue/label/view endpoint surface (ADR-013 house rules)"
status: backlog
labels: []
priority: P2
created: 2026-06-15
updated: 2026-06-15
epic: API-E-001
---

## Description

First web-app surface of Phase 2 (API + DB core) and the first task of the forming epic API-E-001 (the current roadmap's derived next step). Stand up the FastAPI `api` service (the second `app/` service alongside the completed `db` layer) and implement the core issue/label/view REST endpoints against the v1 schema, enforcing the server-side house rules from ADR-013. The data layer this builds on (DB-E-001: schema + migrations under `app/db/`) is complete.

Built test-first per ADR-016: when this task is picked up it routes through the TDD two-phase flow (a `test-designer` dispatch authoring failing tests against the contract, then an `executor` implementation dispatch to green), each through the standard dispatched-worker flow.

**In scope**
- The FastAPI `api` service skeleton under docker compose (ADR-003): an `app/api/` service wired into `app/docker-compose.yml`, connecting to postgres over the v1 schema.
- The issue/label/view endpoint surface the `mcp` service will later call over HTTP (the ADR-010 data path): the reads and writes behind the ADR-013 v1 tool set (`issue_list`, `issue_get`, `issue_create`, `issue_claim`, `issue_move`, `issue_comment`, `issue_label`, `view_list`).
- The server-enforced house rules ADR-013 attaches to those operations (enforced in the api service, not the client).

**Out of scope (sibling tasks API-T-002+ under API-E-001)**
- Auth and sessions (ADR-011).
- Invite-token minting (ADR-007).
- Admin-user seeding from `.env` (ADR-006).
- The `mcp` FastMCP service itself (Phase 3); this task only exposes the HTTP surface that service will consume.
- The React frontend (Phase 4).

**Open questions to resolve at kickoff (recorded, not answered here)**
- Exact route shape and request/response contracts (ADR-010).
- Identity handling for `claim`/ownership before auth lands (ADR-011 / ADR-026): whether the endpoints ship with a provisional identity and auth layers on in a sibling task, or this task depends on the auth task first. This is the surface's primary sequencing decision.
- Whether labels are their own endpoints or a sub-resource of issues.

These are the anticipated decisions for the pick-up/kickoff-drafting step; they are captured so the scope boundary is visible, not to be resolved at filing time.

References:
- `ai-infrastructure/project-manager/decisions/ADR-010-api-shape-and-mcp-data-path.md` (API shape + the mcp-to-api data path)
- `ai-infrastructure/project-manager/decisions/ADR-013-mcp-tool-surface-house-rules.md` (the v1 tool surface this exposes + house rules)
- `ai-infrastructure/project-manager/decisions/ADR-012-issue-label-view-schema.md` (the v1 schema the endpoints read/write)
- `ai-infrastructure/project-manager/decisions/ADR-016-testing-strategy-test-designer-agent.md` (TDD two-phase flow)
- `ai-infrastructure/project-manager/decisions/ADR-003-docker-compose-runtime.md` (compose-only run path)
- `ai-infrastructure/project-manager/decisions/ADR-011-auth-session-mechanism.md`, `ai-infrastructure/project-manager/decisions/ADR-026-per-agent-mcp-identity.md` (sibling/sequencing context)
- `ai-infrastructure/project-manager/docs/architecture/OVERVIEW.md` (target runtime shape: the `api` service)
- `app/db/` (completed schema + migrations, DB-E-001) and `app/docker-compose.yml` (the compose file to extend)

## Activity log

- 2026-06-15: Created in backlog. First task of the forming epic API-E-001; scoped to the FastAPI service skeleton + the issue/label/view endpoint surface with ADR-013 house rules, with auth/sessions, invites, and admin seeding fenced to sibling tasks. Filed unlabelled per ADR-031 (the `dept:backend-api` label is applied at the dogfood import, derived from the tree).
