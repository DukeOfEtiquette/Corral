---
schema_version: 1
id: DB-T-002
title: "Author tests for the DB-T-001 Postgres schema (retroactive test-design, ADR-016)"
status: backlog
labels: []
priority: P2
created: 2026-06-13
updated: 2026-06-13
---

## Description

Author the test suite for the v1 Postgres schema delivered by DB-T-001 (the Alembic baseline migration 0001 building the eleven-table schema: ADR-012 core + ADR-025 epics + ADR-011 auth + ADR-026 machine users). This is **retroactive** test-design: DB-T-001 shipped before the universal `test-designer` agent and the TDD two-phase flow existed (both created later in COR-T-035), so this task back-fills the test coverage that the TDD discipline (ADR-016) would normally have produced first.

Because the schema already exists, these are characterization/contract tests that lock in the schema's shape rather than the red-phase failing tests of a greenfield surface. They should assert against a migrated Postgres instance: table set (11 tables), columns and types, CHECK constraints (status, priority, `issues.type` task|epic), FK relations (including the self-referential `parent_id` and the auth/machine-user relations), indexes, and the jsonb payload column; plus the migration up/down round-trip. Any assertion that does NOT hold against the current schema is a finding to surface (a real schema bug or a contract ambiguity), not a test to weaken.

Routes through the `/database-orchestrator` dispatched-worker flow as a **test-design dispatch** (the `test-designer` agent, ADR-016 phase 1). There is no paired implementation dispatch unless the tests surface a schema defect, in which case the correction routes per the normal flow.

This is the second task of the **E2.1 Database schema & migrations** epic (ADR-036 taxonomy), alongside DB-T-001; it brings the epic to the >=2-task minimum.

## Activity log

- 2026-06-13: Created in backlog by the project-manager coordinator (coordinator write authority, ADR-027). Surfaced during the ADR-036 roadmap restructure: the Database epic (E2.1) needed a second task, and DB-T-001's schema lacks the test coverage the post-COR-T-035 TDD flow now expects. Runs as a retroactive test-design dispatch under /database-orchestrator.
