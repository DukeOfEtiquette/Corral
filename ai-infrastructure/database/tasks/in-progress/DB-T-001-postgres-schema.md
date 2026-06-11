---
schema_version: 1
id: DB-T-001
title: "Author the Postgres schema (P2-1) in the database department"
status: in-progress
labels: []
priority: P2
created: 2026-06-11
updated: 2026-06-11
---

## Description

The first web-app deliverable: the Postgres schema for Corral, authored inside the `database` department workspace (`ai-infrastructure/database/`, stood up by COR-T-023). This is roadmap milestone P2-1 and the upstream dependency for the backend-api work (P2-2 endpoints, P2-3 auth/sessions); it should land before those.

The binding schema decisions are already pinned in accepted coordinator ADRs; this task implements them, it does not re-decide them:

- ADR-012 (issue/label/view/comment/event schema): the core tables - `issues`, `labels` (and the issue-label join), `views`, `comments`, `issue_events` - and their columns, including first-class `status` and `priority` columns on `issues`.
- ADR-025 (native epics): amends the ADR-012 schema with an `issues.type` column (`task | epic`, CHECK-constrained, default `task`) plus a nullable self-referential `issues.parent_id` FK. Invariants (at-most-one parent, children are tasks, epics not nested in v1, `type` backfills `task`) are API-enforced per ADR-010, not all DB-enforced; the DDL provides the columns and the FK.
- ADR-026 (per-agent MCP identity): machine users are first-class rows in `users` (display_name + hashed key, no human-auth fields) with a discriminator separating machine from human users, so `issues.assignee_id` and `issue_events.actor_id` resolve per-agent.
- ADR-011 (auth/session mechanism): the `users` / invite-token / session schema delta (argon2id-hashed credentials, invite tokens, server-side sessions). ADR-012 Consequence #3 assigns the auth schema delta to this schema layer.

Scope: the schema definition and its initial migration, expressed through the migrations tooling chosen in ADR-014 (read it before authoring; the exact DDL form - for example whether machine vs human users use a discriminator column or a separate credential table, and how hashed keys are stored - is the ADR-014 implementation-phase decision flagged in ADR-026). Out of scope here: FastAPI endpoints and the house rules (P2-2, `backend-api`), the MCP tool surface (Phase 3), and admin seeding beyond what the migration baseline needs (ADR-006/ADR-014, P2-4).

When picked up, this routes through the dispatched-worker flow from the `database` department's `/database-orchestrator` (resolve any residual DDL decisions with the user first, since several are flagged as implementation-phase in the ADRs above, then draft+check the kickoff, prelaunch, dispatch the worker, close). Per ADR-003, docker compose is the only supported run path once code exists; verify the schema by applying the migration against a Postgres service in compose, not a host-installed Postgres.

## Activity log

- 2026-06-11: Created in backlog. Allocated as the P2-1 deliverable after COR-T-023 stood up the `database` and `backend-api` departments; the database department had no filed work, which both department-orchestrator smoke tests flagged. Tagged `dept:database` so it surfaces in that department's scoped survey.
- 2026-06-11: Relocated from coordinator pool as COR-T-024 to database department tree as DB-T-001 per ADR-031 (per-department task trees). ID updated, dept:database label stripped (tree is now the partition; label applied at dogfood import per ADR-008).
- 2026-06-11: Picked up via /database-orchestrator; status -> in-progress, moved to tasks/in-progress/. Resolving residual implementation-phase DDL decisions (flagged in ADR-014/ADR-026) with the user before drafting the kickoff for the dispatched-worker flow.
