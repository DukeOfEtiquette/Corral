---
schema_version: 1
id: API-T-001
title: "FastAPI api service: the v1 issue/view/label/epic endpoint surface (ADR-013 + ADR-025 + ADR-018)"
status: backlog
labels: []
priority: P2
created: 2026-06-15
updated: 2026-06-15
epic: API-E-001
---

## Description

The core HTTP surface of epic API-E-001 (Phase 2, API + DB core): implement the issue / view / label / epic REST endpoints on the FastAPI `api` service (whose skeleton is stood up by API-T-002, which runs first), against the v1 schema, enforcing the ADR-013 (issue/view), ADR-025 (epic), and ADR-018 (label-family) house rules in the API layer (the single enforcement seam, ADR-010). The data layer is complete: the full v1 schema is already migrated in `app/db/alembic/versions/0001_baseline_schema.py` (issues with `type`/`parent_id`, labels, views, comments, events, `users` with `email`/`password_hash`/`kind`, `sessions`, `invites`, `agent_credentials`), so no further database-department migration is needed.

**Sequencing (resolved with the user 2026-06-15).** Built AFTER its one prerequisite:
- **API-T-002 (auth) first.** API-T-002 stands up the FastAPI `api` service skeleton (app, compose service, DB wiring) and the human auth layer; this task adds the resource endpoints onto the existing service. The endpoints are built against real identity (server-side sessions per ADR-011; per-agent API keys per ADR-026 arrive in Phase 3 with the MCP server), not a provisional stub: `issue_comments.author_id` and `issue_events.actor_id` are NOT NULL, so a real authenticated identity is required. API-T-002 must complete before this task.

Built test-first per ADR-016: TDD two-phase flow (a `test-designer` dispatch authors failing API-level pytest tests through the FastAPI ASGI app against a real Postgres in a compose one-shot `test` service; then an `executor` implements to green and may not touch the tests).

**In scope**
- The resource endpoints added onto the existing `app/api/` service (skeleton + compose wiring + DB connection established by API-T-002), all routes under `/api/v1` (ADR-010).
- The ADR-013 core surface as REST endpoints with server-side house rules: `issue_create` (priority P0-P3 required), `issue_list` (filter by status/labels/assignee), `issue_get` (full: metadata, labels, comments, events), `issue_move` (any-to-any across the four statuses; records an `issue_event`), `issue_comment` (append), `issue_claim` (set `assignee_id` + `force`; lease/concurrency deferred to ADR-020), `view_list`.
- The ADR-025 epic tools: `epic_create`, `epic_attach`, `epic_detach` over `issues.type`/`parent_id`, enforcing the ADR-025 invariants (children-are-tasks, epics-not-nested, at-most-one-parent) in the API layer.
- Label endpoints with full reserved-family rules per ADR-018 (accepted): `dept:*` is a reserved namespaced family, at-most-one per issue (2+ rejected), admin-managed and auto-sanctioned from the ADR-021 roster (not user-creatable); free-form labels creatable by any authenticated user; `phase:*` is a second reserved family per ADR-038 (at-most-one, epic-only). Backs `issue_label` and the label side of `issue_create`.

**Out of scope**
- The `api` service skeleton + the human auth layer + admin seeding (API-T-002, the prerequisite) and invite minting (API-T-003) as DELIVERABLES: this task consumes the service and identity API-T-002 establishes, it does not build them.
- `issue_import` (ADR-008 dogfood path, Phase 5).
- The `mcp` FastMCP service (Phase 3); this task only exposes the HTTP surface it will later call.
- The React frontend (Phase 4) and the concrete `dept:*` color palette (deferred to ADR-015/017).
- Claim lease/concurrency semantics beyond a simple `assignee_id` set + `force` (ADR-020, pending).

**Dependencies**
- API-T-002 (service skeleton + auth + admin bootstrap) -- must complete first: it stands up the `api` service and establishes the human session identity for the NOT NULL author/actor FKs. No ADR dependency: ADR-018 (labels) and ADR-025 (epics) are both accepted.

References:
- `ai-infrastructure/project-manager/decisions/ADR-010-api-shape-and-mcp-data-path.md` (REST shape, `/api/v1`, mcp-to-api data path, single enforcement seam)
- `ai-infrastructure/project-manager/decisions/ADR-013-mcp-tool-surface-house-rules.md` (core tool surface + house-rule mechanism)
- `ai-infrastructure/project-manager/decisions/ADR-025-native-epics.md` (epic tools + `type`/`parent_id` invariants)
- `ai-infrastructure/project-manager/decisions/ADR-018-department-label-taxonomy.md` (accepted: `dept:*` family, at-most-one, creation rights)
- `ai-infrastructure/project-manager/decisions/ADR-038-phase-as-first-class-view.md` (`phase:*` reserved family)
- `ai-infrastructure/project-manager/decisions/ADR-012-issue-label-view-schema.md` (the v1 schema the endpoints read/write)
- `ai-infrastructure/project-manager/decisions/ADR-011-auth-session-mechanism.md`, `ai-infrastructure/project-manager/decisions/ADR-026-per-agent-mcp-identity.md` (the identity this consumes; built by API-T-002)
- `ai-infrastructure/project-manager/decisions/ADR-016-testing-strategy-test-designer-agent.md` (TDD two-phase flow)
- `ai-infrastructure/project-manager/decisions/ADR-003-docker-compose-runtime.md` (compose-only run path)
- `ai-infrastructure/project-manager/docs/architecture/OVERVIEW.md` (target runtime shape: the `api` service)
- `ai-infrastructure/backend-api/tasks/in-progress/API-T-002-auth-sessions-admin-bootstrap.md` (the prerequisite), `app/db/` (schema layer), `app/docker-compose.yml`

## Activity log

- 2026-06-15: Created in backlog. First task of the forming epic API-E-001; scoped to the FastAPI service skeleton + the issue/label/view endpoint surface with ADR-013 house rules, with auth/sessions, invites, and admin seeding fenced to sibling tasks. Filed unlabelled per ADR-031 (the `dept:backend-api` label is applied at the dogfood import, derived from the tree).
- 2026-06-15: Picked up; moved to in-progress (Backend API Orchestrator). Routes through the TDD two-phase flow per ADR-016 (test-designer red, then executor green). Orchestrator homework done (ADR-010/011/012/013/016/026 + the `app/db` baseline migration + compose). Key finding: the full v1 schema is already migrated in `app/db/alembic/versions/0001_baseline_schema.py` (users with `email`/`password_hash`/`kind`, sessions, invites, agent_credentials all present), so no further database-department migration is needed for this task or its siblings. Resolving the anticipated decisions with the user before drafting the kickoff: the identity seam, label scope, and whether the ADR-025 epic tools are in scope.
- 2026-06-15: Reverted to backlog and rescoped (user direction). Three anticipated decisions resolved: (1) identity -> build auth (API-T-002) FIRST, so this task consumes real identity rather than a provisional stub; (2) labels -> full reserved-family rules per ADR-018; (3) epic tools -> ADR-025 `epic_create`/`attach`/`detach` now IN scope. Correction recorded: the labels decision was initially framed (including in the prior log line) as "resolve ADR-018 first," but ADR-018 was already accepted on 2026-06-10 -- the "pending" reading came from ADR-013's stale 2026-06-07 cross-reference, not from the ADR-018 file. There is nothing to resolve; the label rules are settled. Net effect: this task re-sequences from first to last of the Phase-2 backend items, gated solely on API-T-002 (no ADR dependency). Scope/dependencies above updated accordingly.
- 2026-06-15: Scope trimmed (user-confirmed). Standing up the FastAPI `api` service skeleton (app, compose service, DB wiring) moves to API-T-002, which now runs first; this task adds the resource endpoints onto the existing service. Per-agent API-key identity (ADR-026) is Phase 3, so the endpoints authenticate via the human session identity API-T-002 establishes. The COR-08/ADR-013 "pending" correction is recorded as coordinator task COR-T-053.
