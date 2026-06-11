---
schema_version: 1
department: "database"
last_updated: "2026-06-11"
recent_updates:
  - "2026-06-11: ADR-031 cascade (COR-T-025): department now owns its own tasks/ tree at ai-infrastructure/database/tasks/; DB-T-001 (Postgres schema, P2-1) relocated from the coordinator pool and lives in backlog."
  - "2026-06-10: Department workspace created via /create-department."
---

# Status

Single source of truth for current progress in the `Database` department. Update at the end of any session that makes progress.

## Current phase

**Newly created.** The `Database` department workspace has been scaffolded. No work has been dispatched yet. The department's scope is: Schema, migrations, seed logic

## Next step

Pick up `DB-T-001` (Postgres schema, P2-1) from `ai-infrastructure/database/tasks/backlog/` and route it through the `/database-orchestrator` dispatched-worker flow.

## Blocked on

Nothing. The workspace is ready for work.
