---
schema_version: 1
adr: 14
title: "Database migrations tooling"
status: "accepted"
date: "2026-06-11"
related_adrs: [2, 3, 8, 11, 12, 26]
supersedes: []
superseded_by: null
---

# ADR-014: Database migrations tooling

## Context

Postgres (ADR-002) plus an evolving schema (ADR-012) means migrations. The tooling choice should fit the FastAPI ecosystem and run inside the compose topology (ADR-003), likely as a startup step or one-shot service.

## Alternatives considered

### Option A: Alembic

The standard for SQLAlchemy-based stacks; autogeneration support.

### Option B: Raw SQL migration files with a tiny runner

Maximum transparency, no magic; more hand maintenance.

### Option C: ORM-managed schema (e.g. SQLModel create_all) until v1 stabilizes

Fastest start; no real migration story, acceptable only while data is disposable.

## Decision

**Option A selected: Alembic, with migrations authored by hand.** Alembic is the migration runner; it runs inside the compose topology (ADR-003) as a one-shot `alembic upgrade head` step before the API serves. Migrations are written by hand (explicit `op.execute` / `op.*` calls carrying the SQL), not generated. Autogenerate is not used, because adopting it would require a SQLAlchemy ORM model layer as the schema's source of truth, and no ORM is adopted in v1.

This keeps separate two things ADR-014's Option A framing ("standard for SQLAlchemy-based stacks; autogeneration support") had bundled: the **migration runner** (Alembic, chosen here) and the **application data-access layer** (SQLAlchemy ORM vs Core vs a raw driver). The latter is a backend-api concern (P2-2), is explicitly not decided here, and is not forced by this choice; hand-written migrations mean Alembic needs no ORM models to function.

The v1 schema is introduced by a single baseline migration (`0001`) building the full schema in one revision: the ADR-012 core tables (with the `status`/`priority` CHECK columns), the ADR-025 epic columns (`issues.type`, `issues.parent_id`), the ADR-011 auth tables (`users` with `email`/`password_hash`, invites, sessions), and the ADR-026 machine-user identity (a `kind` discriminator on `users` plus a separate `agent_credentials` table). Authoring that baseline migration is DB-T-001.

Option B (raw SQL files plus a tiny custom runner) is rejected: migrations are hand-written SQL either way, so it buys the same transparency while requiring a bespoke runner and version-tracking table that Alembic supplies off the shelf as a vetted primitive (consistent with ADR-011's hand-rolled-on-vetted-primitives posture). Option C (ORM `create_all`, no migrations) is rejected: ADR-014's own framing admits it only while data is disposable, and the ADR-008 dogfood import makes tracker data durable, so a real migration story is needed from the first schema rather than retrofitted after the second change.

## Consequences

1. **ADR-002 migrations decision closed.** ADR-002's Consequence ("Postgres ... needs a migrations decision (ADR-014)") is resolved: Alembic with hand-written migrations. A forward-pointer note is added to ADR-002.

2. **No ORM adopted in v1; the data-access layer stays a backend-api decision.** Choosing Alembic does not adopt SQLAlchemy's ORM. Whether the API's data access uses SQLAlchemy Core, the ORM, or a raw driver (asyncpg/psycopg) is deferred to the backend-api department (P2-2) and is unconstrained by this choice. If an ORM is adopted later, autogenerate can be enabled then; until then migrations stay hand-authored.

3. **The exact DDL remains DB-T-001's deliverable.** This ADR pins the tooling and the single-baseline approach, not the column-level DDL. The concrete SQL (column names, types, indexes, constraints, the `agent_credentials` shape, token/session storage) lands in the baseline migration authored under DB-T-001, which is where the "implementation-phase (ADR-014)" deferrals in ADR-011, ADR-012, and ADR-026 are satisfied.

4. **Runs in compose (ADR-003).** Migrations apply via `alembic upgrade head` against the Postgres compose service as a one-shot/startup step (in the api service or a dedicated migration service). No host-installed Postgres or Alembic is assumed; verification is against the compose Postgres.

5. **Reversibility available, not mandated.** Alembic revisions carry `upgrade`/`downgrade`; the baseline's downgrade is a clean drop. Whether later migrations always author a downgrade is left to those migrations.
