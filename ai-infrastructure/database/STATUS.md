---
schema_version: 1
department: "database"
---

# Status

Single source of truth for current progress in the `Database` department. Update at the end of any session that makes progress.

## Current phase

**P2-1 delivered and test-covered.** `DB-T-001` (Postgres schema) is authored and verified: the Alembic baseline migration `0001` under `app/db/` builds the full eleven-table v1 schema and applies cleanly against a Postgres compose service (`app/docker-compose.yml`). This is the first domain-1 (web-app) code in the repo; the `app/` root is now established. `DB-T-002` then added a retroactive characterization test suite (`app/db/tests/` plus a compose one-shot `test` service, ADR-016): authored blind from the contract, all 130 schema-shape assertions pass against the migrated schema with zero schema-vs-contract divergences. The department's scope is: Schema, migrations, seed logic.

## Next step

`DB-T-001`, `DB-T-002`, and `DB-T-003` are all closed; epic `DB-E-001` (schema & migrations) is complete. No database task is currently open. The full schema test suite now runs as two clean compose jobs with no skip anywhere: `test` (the 130 read-only shape assertions, against a migrated DB) and `test-roundtrip` (the Alembic up/down round-trip). Immediate downstream is backend-api P2-2 (FastAPI endpoints) and P2-3 (auth/sessions), built against this tested schema. Further schema changes use the same `app/db/` Alembic setup (new revisions after `0001`).

## Blocked on

Nothing. The workspace is ready for work.
