---
schema_version: 1
id: DB-T-005
title: "Make the db `test` compose service depend on `migrate` so characterization tests always run against a migrated DB"
status: done
labels: []
priority: P2
created: 2026-06-22
updated: 2026-06-22
---

## Description

Orchestrator-direct fix (Project Manager Orchestrator, at user direction, immediate). Surfaced during the DB-T-004 review on 2026-06-22.

**The footgun.** The `test` service in `app/docker-compose.yml` declared `depends_on: postgres (service_healthy)` only. The schema-characterization suite asserts against the *live* DB (this is the deliberate design preserved through DB-T-004), so it requires the schema to already be migrated. With no dependency on `migrate`, a clean-room `docker compose run --rm test` against a fresh postgres runs before any migration and fails: a clean run produced **116 failed, 14 passed** out of 130 (e.g. `test_exactly_eleven_contract_tables` cannot find the tables). The suite only passes if `migrate` (or `test-roundtrip`, which depends on `migrate`) happened to run first and populate the same postgres instance. This was a latent, state-dependent trap, not introduced by DB-T-004 (the DB-T-004 compose diff touched only the three `build.target` lines; `depends_on` was pre-existing).

**The fix (in the build, not in docs).** Add `migrate: condition: service_completed_successfully` to the `test` service's `depends_on`, mirroring what the `test-roundtrip` service already declares. This makes compose bring up postgres (healthy) and run `migrate` to completion before the characterization suite runs, so the migrate-first invariant is enforced by the compose graph rather than by an operator or agent remembering to run `migrate` first. Per ADR-016 the characterization tests assert against the live migrated schema; this wires that precondition into the runtime.

**Verification (clean room).** `docker compose down` (fresh, unmigrated DB), then `docker compose run --rm test` with no manual `migrate`: compose auto-ran `migrate` to completion and the suite reported **130 passed**. The same clean-room scenario produced 116 failures before the fix. `test-roundtrip` already carried the dependency and is unaffected; `api`/`api-test`/`migrate` blocks untouched; the change is `depends_on` only (no image rebuild needed, build unaffected).

References:
- `app/docker-compose.yml` (the `test` service block; the `test-roundtrip` block was the pattern to mirror)
- `ai-infrastructure/project-manager/decisions/ADR-016-testing-strategy-test-designer-agent.md` (characterization tests assert against the live migrated DB)
- `ai-infrastructure/project-manager/decisions/ADR-003-docker-compose-runtime.md` (compose is the runtime), `ai-infrastructure/project-manager/decisions/ADR-014-db-migrations-tooling.md` (alembic migrations)
- `ai-infrastructure/database/tasks/done/DB-T-004-multistage-dockerfile-restructure.md` (the restructure during whose review this was found)

## Activity log

- 2026-06-22: Created and resolved in one step by the Project Manager Orchestrator (orchestrator-direct, coordinator write authority ADR-027, at user direction). Found during the DB-T-004 review: a clean-room `docker compose run --rm test` failed 116/130 because `test` depended only on `postgres`, not `migrate`. Fixed by adding `migrate: service_completed_successfully` to the `test` service's `depends_on` (mirroring `test-roundtrip`). Verified clean-room: `down` then `run --rm test` auto-migrated and passed 130. Filed P2, standalone. Unlabelled per ADR-031.
