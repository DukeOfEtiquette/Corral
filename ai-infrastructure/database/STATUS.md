---
schema_version: 1
department: "database"
last_updated: "2026-06-11"
recent_updates:
  - "2026-06-11: DB-T-001 delivered: Alembic baseline migration 0001 (eleven tables, ./app/db) and ./app/docker-compose.yml compose verification path authored and verified - migration applies cleanly against compose Postgres, all eleven tables and seven named indexes confirmed, downgrade/upgrade round-trip clean."
  - "2026-06-11: DB-T-001 (Postgres schema, P2-1) picked up: moved to tasks/in-progress/; residual DDL decisions resolved with the user. Coordinator ADR-014 (migrations tooling) accepted to unblock it: Alembic with hand-written migrations, no ORM in v1. Pinned for the kickoff: full v1 schema in a single baseline migration (core ADR-012 tables + ADR-025 epic columns + full ADR-011 auth tables); machine-user identity (ADR-026) via a separate agent_credentials table with a kind discriminator on users. Next: draft+check the kickoff and dispatch the worker."
  - "2026-06-11: ADR-031 cascade (COR-T-025): department now owns its own tasks/ tree at ai-infrastructure/database/tasks/; DB-T-001 (Postgres schema, P2-1) relocated from the coordinator pool and lives in backlog."
  - "2026-06-10: Department workspace created via /create-department."
---

# Status

Single source of truth for current progress in the `Database` department. Update at the end of any session that makes progress.

## Current phase

**P2-1 delivered.** `DB-T-001` (Postgres schema) is authored and verified: the Alembic baseline migration `0001` under `app/db/` builds the full eleven-table v1 schema and applies cleanly against a Postgres compose service (`app/docker-compose.yml`). This is the first domain-1 (web-app) code in the repo; the `app/` root is now established. The department's scope is: Schema, migrations, seed logic.

## Next step

`DB-T-001` is closed (in `tasks/done/`). No database task is currently open; the next database deliverable is filed when a downstream consumer needs it. Immediate downstream is backend-api P2-2 (FastAPI endpoints) and P2-3 (auth/sessions), built against this schema. Further schema changes use the same `app/db/` Alembic setup (new revisions after `0001`).

## Blocked on

Nothing. The workspace is ready for work.
