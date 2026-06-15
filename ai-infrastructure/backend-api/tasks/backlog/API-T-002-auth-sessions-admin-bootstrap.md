---
schema_version: 1
id: API-T-002
title: "Auth, sessions, and admin-user bootstrap for the api service (ADR-011, ADR-006)"
status: backlog
labels: []
priority: P2
created: 2026-06-15
updated: 2026-06-15
epic: API-E-001
---

## Description

Second task of epic API-E-001 (Phase 2, API + DB core). Add the authentication and session layer to the FastAPI `api` service plus the admin-user bootstrap that makes it usable: the ADR-011 auth/session mechanism (credential verification, session establishment and teardown, password hashing) enforced on the api service, and ADR-006 admin-user seeding from the gitignored `.env` password hash on first boot. With this in place the issue/label/view endpoints from API-T-001 become authenticated.

Built test-first per ADR-016: routes through the TDD two-phase flow when picked up (a `test-designer` dispatch, then an `executor` implementation dispatch), each through the standard dispatched-worker flow.

**Pairs with API-T-001.** API-T-001's open question (whether its endpoints ship with a provisional identity and auth layers on here, or API-T-001 depends on this task first) is the shared sequencing decision between the two; it is resolved when the first of the pair is picked up.

**In scope**
- The ADR-011 auth and session mechanism on the api service: credential verification, session establishment/teardown, password hashing.
- Admin-user seeding from the env-supplied password hash on first boot (ADR-006), reading the gitignored `.env` only. No secret or password hash is written into any tracked file (CLAUDE.md secrets rule).
- Applying the auth layer to the API-T-001 issue/label/view endpoints so they require an authenticated identity.

**Out of scope (sibling tasks under API-E-001)**
- Invite-token minting and invite-only user creation (ADR-007) -> a future sibling (API-T-003).
- MCP per-agent identity wiring beyond what the api auth layer needs (ADR-026); the `mcp` service is Phase 3.
- The React login UI (Phase 4).

**Open questions to resolve at kickoff (recorded, not answered here)**
- The API-T-001 <-> API-T-002 sequencing (provisional identity vs auth-first), as above.
- Whether the users schema (ADR-011) is already present in the `app/db` baseline migration or requires a database-department migration first. This is a cross-department dependency: schema/migrations are owned by the database department (DB-E-001), not built here. Confirm at kickoff and, if missing, route the migration to the database department rather than scoping it into this task.
- ADR-011 mechanism specifics left as implementation choices (e.g. how the session is carried), and idempotent admin re-seed behaviour on reboot / hash rotation (ADR-006).

References:
- `ai-infrastructure/project-manager/decisions/ADR-011-auth-session-mechanism.md` (auth/session mechanism + the users/invites schema)
- `ai-infrastructure/project-manager/decisions/ADR-006-admin-bootstrap-env-hash.md` (admin seeding from the env-supplied hash)
- `ai-infrastructure/project-manager/decisions/ADR-007-invite-only-tokens-no-smtp.md` (the deferred invite sibling)
- `ai-infrastructure/project-manager/decisions/ADR-026-per-agent-mcp-identity.md` (identity context)
- `ai-infrastructure/project-manager/decisions/ADR-016-testing-strategy-test-designer-agent.md` (TDD two-phase flow)
- `ai-infrastructure/project-manager/decisions/ADR-003-docker-compose-runtime.md` (compose-only run path)
- `ai-infrastructure/project-manager/docs/architecture/OVERVIEW.md` (target runtime shape)
- `ai-infrastructure/backend-api/tasks/backlog/API-T-001-fastapi-issue-view-endpoints.md` (the endpoints this protects), `app/db/` (schema layer), `app/docker-compose.yml`

## Activity log

- 2026-06-15: Created in backlog. Second task of epic API-E-001, picking up the auth/sessions (ADR-011) and admin-seeding (ADR-006) concerns fenced out of API-T-001; invites (ADR-007) left to a future sibling. Filed unlabelled per ADR-031. Clears the transient 1-task cardinality advisory on API-E-001 (the epic now holds 2 tasks).
