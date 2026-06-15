---
schema_version: 1
id: API-T-003
title: "Invite-token minting and invite-only user creation for the api service (ADR-007)"
status: backlog
labels: []
priority: P2
created: 2026-06-15
updated: 2026-06-15
epic: API-E-001
---

## Description

Third task of epic API-E-001 (Phase 2, API + DB core), completing the epic's decomposition (endpoints, auth, invites). Add the ADR-007 invite surface to the FastAPI `api` service: an admin-only endpoint that mints single-use invite tokens, and a redemption path that creates an invite-only user account from a valid unused token. No SMTP or email dependency (ADR-007): tokens are returned to the admin and distributed out of band.

Built test-first per ADR-016: routes through the TDD two-phase flow when picked up (a `test-designer` dispatch, then an `executor` implementation dispatch), each through the standard dispatched-worker flow.

**Builds on API-T-002.** Minting is an admin action (the admin user and the auth/session layer from API-T-002 must exist), and a redeemed invite produces an authenticated user under that same mechanism.

**In scope**
- Admin-only invite-token minting on the api service: generate a single-use token, persist it against the invites schema (ADR-011), return it to the caller.
- Invite redemption: accept a token, create the user on first valid use, and enforce single-use (a redeemed or unknown token is rejected). No SMTP (ADR-007).
- The server-side house rules around invites (admin-only mint, single-use redemption), enforced in the api service.

**Out of scope (other tasks / phases)**
- Auth and sessions and admin seeding (API-T-002, the dependency).
- The React invite/registration UI (Phase 4).
- MCP per-agent identity wiring (ADR-026); the `mcp` service is Phase 3.
- Any email/SMTP delivery (explicitly excluded by ADR-007).

**Open questions to resolve at kickoff (recorded, not answered here)**
- Token format, length, and expiry/lifetime, and the single-use enforcement mechanism (ADR-007 specifics).
- Whether redemption auto-establishes a session or only creates the account, leaving login to the API-T-002 flow.
- Whether the invites schema (ADR-011) is present in the `app/db` baseline migration or needs a database-department migration first. Same cross-department boundary as API-T-002: schema/migrations are owned by the database department (DB-E-001), not built here; confirm at kickoff and route any migration there.

References:
- `ai-infrastructure/project-manager/decisions/ADR-007-invite-only-tokens-no-smtp.md` (the binding invite decision)
- `ai-infrastructure/project-manager/decisions/ADR-011-auth-session-mechanism.md` (the users/invites schema and the session a redeemed invite yields)
- `ai-infrastructure/project-manager/decisions/ADR-006-admin-bootstrap-env-hash.md` (the admin who mints, context)
- `ai-infrastructure/project-manager/decisions/ADR-016-testing-strategy-test-designer-agent.md` (TDD two-phase flow)
- `ai-infrastructure/project-manager/decisions/ADR-003-docker-compose-runtime.md` (compose-only run path)
- `ai-infrastructure/project-manager/docs/architecture/OVERVIEW.md` (target runtime shape: invites on the api service)
- `ai-infrastructure/backend-api/tasks/backlog/API-T-002-auth-sessions-admin-bootstrap.md` (the auth/admin foundation this builds on), `app/db/` (schema layer), `app/docker-compose.yml`

## Activity log

- 2026-06-15: Created in backlog. Third task of epic API-E-001, picking up the invite-token concern (ADR-007) fenced out of API-T-001/002 and completing the epic's decomposition (endpoints + auth + invites, matching the API-E-001 description). Filed unlabelled per ADR-031.
