# DB-T-002: retroactive schema characterization tests for the v1 Postgres schema, authored blind from the contract (ADR-016 test-design)

## Target

This is web-app work (domain 1, ADR-005): a TEST-DESIGN dispatch under the two-phase TDD flow (ADR-016 phase 1, red). You are the dispatched `test-designer` (Opus, ADR-016), not the implementation executor. You are executing task DB-T-002 inside the `database` department. The artifact in scope is a schema characterization test suite under `./app/db/tests/` plus the compose test harness (a test runner image and a one-shot `test` service added to `./app/docker-compose.yml`) that runs it.

DB-T-001 shipped the v1 Postgres schema (the Alembic baseline migration `0001`, eleven tables) before the test-designer / TDD flow existed. This task retroactively authors the schema test suite the TDD discipline would have produced first. The load-bearing constraint, pinned below: you author every assertion from the CONTRACT only and you stay BLIND to the implementation, so the suite validates the schema against its intended design rather than being catered to whatever the migration happened to build. A test catered to the implementation is tautological and cannot catch a divergence; the whole point is to validate the implementation against the contract.

Every decision below is pinned. You implement the suite; you do not re-decide its content or shape, and you do not weaken or delete an assertion to make it pass.

## Decisions resolved by the Orchestrator

**1. Blind to the implementation (the load-bearing constraint).** Author every schema assertion from the CONTRACT only.

- THE CONTRACT is `./.claude/artifacts/handoffs/DB-T-001-KICKOFF.md`, specifically its section "Decisions resolved by the Orchestrator", which pins every table, column, type, nullability, CHECK constraint, FK, UNIQUE constraint, and the exact seven named indexes. That handoff artifact is the authoritative DDL specification (a spec, not implementation code); treat it as the binding source. The ADRs it derives from (ADR-012, ADR-011, ADR-025, ADR-026, ADR-014, cited in References) supply authority and rationale where you need it.
- DO NOT READ THE IMPLEMENTATION. You must NOT open any of: `./app/db/alembic/versions/0001_baseline_schema.py` (the migration), `./app/db/alembic/env.py`, `./app/db/alembic.ini`, `./app/db/alembic/script.py.mako`. Reading these is prohibited, not merely editing them. Reading `./app/docker-compose.yml` IS allowed (it is harness topology, not schema DDL) for wiring the test service.

**2. Test content: assert what the contract requires.** Assert against the live migrated database via `information_schema` / `pg_catalog` queries. Cover:

- **Tables.** Exactly the eleven tables exist, by name: `users`, `agent_credentials`, `issues`, `labels`, `issue_labels`, `views`, `view_labels`, `issue_comments`, `issue_events`, `invites`, `sessions`, and no unexpected extra tables beyond Alembic's version table.
- **Columns, types, nullability** per the DB-T-001 contract DDL. For example: every `id` PK is `bigint` backed by a sequence (bigserial); every timestamp column is `timestamptz NOT NULL`; `users.email` and `users.password_hash` are nullable; `sessions.session_id` is a `text` PK; `agent_credentials.user_id` is the PK; `issue_events.payload` is `jsonb NOT NULL`.
- **CHECK constraints with their exact allowed-value sets.** `users.kind` in (`human`, `machine`); `issues.status` in (`backlog`, `in-progress`, `blocked`, `done`); `issues.priority` in (`P0`, `P1`, `P2`, `P3`); `issues.type` in (`task`, `epic`).
- **FK relations**, including the self-referential `issues.parent_id` -> `issues.id`, `issues.assignee_id` -> `users.id`, `agent_credentials.user_id` -> `users.id`, the composite-PK link tables (`issue_labels`, `view_labels`), `issue_comments.issue_id` / `author_id`, `issue_events.issue_id` / `actor_id`, `invites.created_by`, `sessions.user_id`.
- **UNIQUE constraints.** `users.email`, `labels.name`, `views.name`, `issues.external_ref`.
- **Indexes.** Exactly the seven named explicit indexes exist with their names: `ix_issues_status`, `ix_issues_assignee_id`, `ix_issues_parent_id`, `ix_issue_labels_label_id`, `ix_view_labels_label_id`, `ix_issue_comments_issue_id`, `ix_issue_events_issue_id`. Assert no additional non-constraint indexes exist beyond those seven plus the indexes the PK and UNIQUE constraints create automatically.
- **No native ENUM types.** No native Postgres ENUM types exist; `status` / `priority` / `type` / `kind` are `text` + CHECK (ADR-012's explicit choice).
- **Migration up/down round-trip.** From the contract, the baseline `downgrade()` is a clean drop: after `alembic downgrade base` none of the eleven tables exist, and after `alembic upgrade head` all eleven exist again. Author this test from the contract. Note in the test and the report that it inherently runs Alembic, so it is validated by the Orchestrator's green run rather than by your red check (you stay blind to the migration during authoring).

**3. Findings discipline.** Any assertion that does NOT hold against the running schema is a FINDING to surface in your closing report (a real schema bug, or a contract ambiguity), NEVER a test to weaken or delete to make it pass. Do not adjust a test to match observed behavior. This is the design-implementation separation ADR-016 establishes.

**4. Test file location and structure.** Under `./app/db/tests/`:

- A `conftest.py` providing a psycopg2 database-connection fixture that reads `DATABASE_URL` from the environment.
- One or more `test_*.py` modules holding the assertions. You may organize the modules by area (for example tables / constraints / indexes); that organization is a mechanical choice, not a design decision.
- pytest is the framework (ADR-016).

**5. Compose test harness (mechanical, mirrors the existing `migrate` one-shot in `./app/docker-compose.yml`).**

- `./app/db/requirements-test.txt`: pytest and psycopg2-binary, each pinned to a current stable version (the psycopg2-binary pin matches the driver the `migrate` service already uses).
- `./app/db/Dockerfile.test`: `FROM python:3.12-slim`; install from `requirements-test.txt`; COPY ONLY the `tests/` directory into the image (do NOT COPY the `alembic/` directory; keep the migration out of the test image); default command runs `pytest` against the tests.
- `./app/docker-compose.yml`: ADD a one-shot `test` service mirroring `migrate`. Build from `./db` with `dockerfile: Dockerfile.test`; `depends_on` postgres with `condition: service_healthy` ONLY (NOT migrate, so the same service runs against a non-migrated DB for the red check and a migrated DB for the Orchestrator's green run); `environment` `DATABASE_URL` identical to the migrate service; no restart. Do NOT alter the existing `postgres` or `migrate` services.

**6. Green validation is the Orchestrator's, not yours.** State in your report that the Orchestrator runs `migrate` then `test` against the migrated database at close to validate the schema and surface any divergence as a finding. You do not perform that run.

## Deliverables

1. `./app/db/tests/conftest.py` plus one or more `./app/db/tests/test_*.py` modules: schema characterization tests authored from the contract, covering the tables / columns / types / nullability / CHECK / FK / UNIQUE / index / no-ENUM / round-trip assertions enumerated in Decision 2.
2. `./app/db/requirements-test.txt`: pytest plus psycopg2-binary, each pinned.
3. `./app/db/Dockerfile.test`: the test runner image; COPYs only `tests/`.
4. `./app/docker-compose.yml`: the added one-shot `test` service (postgres and migrate left untouched).

## Files in scope

- `./app/db/tests/conftest.py`
- `./app/db/tests/` (the test modules: `./app/db/tests/test_*.py`)
- `./app/db/requirements-test.txt`
- `./app/db/Dockerfile.test`
- `./app/docker-compose.yml` (ADD the `test` service only; do not alter `postgres` or `migrate`)

## Files out of scope

READ-PROHIBITED implementation (do not open, not merely do-not-edit):

- `./app/db/alembic/versions/0001_baseline_schema.py`
- `./app/db/alembic/env.py`
- `./app/db/alembic.ini`
- `./app/db/alembic/script.py.mako`

Out of scope (do not edit; reading not needed):

- `./app/db/Dockerfile` and `./app/db/requirements.txt` (the migrate image)
- The existing `postgres` and `migrate` services in `./app/docker-compose.yml` (add the `test` service; do not alter them)
- Any backend-api / MCP / other app code
- `./ai-infrastructure/database/STATUS.md` (STATUS deltas is "none"; the Orchestrator finalizes the department Next step at close)

## References

- `./.claude/artifacts/handoffs/DB-T-001-KICKOFF.md` (THE CONTRACT: the pinned DDL spec in its "Decisions resolved by the Orchestrator" section; author all assertions from here).
- `./ai-infrastructure/project-manager/decisions/ADR-012-issue-label-view-schema.md` (core-table DDL; the status/priority/type/kind text+CHECK choice and the no-native-ENUM rule).
- `./ai-infrastructure/project-manager/decisions/ADR-011-auth-session-mechanism.md` (auth schema: users.email/password_hash, invites, sessions, hashed-at-rest posture).
- `./ai-infrastructure/project-manager/decisions/ADR-025-native-epics.md` (the issues.type and parent_id epic columns; their invariants are API-enforced, not DB-enforced, so do not assert DB-level epic enforcement).
- `./ai-infrastructure/project-manager/decisions/ADR-026-per-agent-mcp-identity.md` (the separate agent_credentials table plus the kind discriminator on users).
- `./ai-infrastructure/project-manager/decisions/ADR-014-db-migrations-tooling.md` (Alembic baseline; the baseline downgrade is a clean drop, which is the round-trip contract).
- `./ai-infrastructure/project-manager/decisions/ADR-016-testing-strategy-test-designer-agent.md` (the TDD two-phase flow, the test-designer role, and the compose one-shot `test` service mirroring `migrate`).
- `./ai-infrastructure/project-manager/decisions/ADR-003-docker-compose-runtime.md` (compose is the only run / verify path).
- `./app/docker-compose.yml` (the harness topology to mirror: the postgres + migrate service shape; read for the service wiring, NOT for schema).

## Related tasks and ADRs

- DB-T-001: the schema under test; its kickoff (`./.claude/artifacts/handoffs/DB-T-001-KICKOFF.md`) is the contract these tests encode.
- ADR-016: the TDD project, the test-designer agent, and the compose one-shot `test` service mirroring `migrate`.
- ADR-012: the core schema contract source (tables, the text+CHECK columns, the no-native-ENUM choice).
- ADR-011: the auth schema contract source (users auth columns, invites, sessions).
- ADR-025: the native-epics contract source (issues.type, parent_id).
- ADR-026: the machine-identity contract source (agent_credentials, the kind discriminator).
- ADR-014: migrations tooling; the baseline downgrade is a clean drop (the round-trip contract).
- ADR-003: compose is the only run / verify path.

## STATUS deltas

No task-specific STATUS deltas; none. The Orchestrator finalizes the department `./ai-infrastructure/database/STATUS.md` Next step at close.

## Hard rules

- **Blind authoring.** Author every assertion from the contract (`./.claude/artifacts/handoffs/DB-T-001-KICKOFF.md`, "Decisions resolved by the Orchestrator") and the cited ADRs. Do NOT open the migration or any Alembic config file listed under "Files out of scope" as read-prohibited. Reading those is prohibited, not merely editing.
- **Assertions are contract-faithful, never implementation-faithful.** If an assertion does not hold against the running schema, it is a FINDING for your report, not a test to weaken or delete. Never adjust a test to match observed behavior.
- **Red check is yours; you stay blind.** Bring up a FRESH postgres (do NOT run the `migrate` service) and run the schema-shape tests via `docker compose run --rm test` against it. Confirm they are RED: the assertions fail because the schema is absent, which proves the tests execute and assert the real schema. You MUST NOT run the `migrate` service, MUST NOT run the suite against a migrated database, and MUST NOT read the migration files. The migration round-trip test inherently runs Alembic and so is not red-checked here; it is validated by the Orchestrator. Compose is the only run path (ADR-003).
- **Green validation is the Orchestrator's.** State in your report that the Orchestrator runs `migrate` then `test` against the migrated database at close, and that any failing assertion there is a finding (a schema-vs-contract divergence), not a test to weaken.
- **Do not alter the existing services.** Add the one-shot `test` service to `./app/docker-compose.yml`; leave `postgres` and `migrate` exactly as they are.

## Verification expectations

Confirm the schema-shape tests COLLECT cleanly under pytest and are RED against a non-migrated Postgres: bring up a fresh postgres with `migrate` NOT run, and run the suite via `docker compose run --rm test` against it. Report the coverage (which tables, constraints, indexes, and types your assertions cover). You MUST NOT run the `migrate` service, MUST NOT run the suite against a migrated schema, and MUST NOT read the migration files. Note in the report that the Orchestrator runs the green validation (migrate, then test) at close, and that any failing assertion there is a finding (schema-vs-contract divergence), not a test to weaken. This is the single acceptance gate for the dispatch.

## Test-designer pointer

You are the dispatched `test-designer` (ADR-016). Universal conventions (the staging-not-committing rule, the compose-only run policy in ADR-003, file-edit hygiene, and Agent Discipline) live in `./docs/ai-orchestration/roles/EXECUTOR-ROLE.md` and the global `./CLAUDE.md`; the test-design role specifics live in `./docs/ai-orchestration/roles/TEST-DESIGNER-ROLE.md`. Follow them without their being re-emitted here. Write your closing report in the pinned six-section shape to `./.claude/artifacts/handoffs/DB-T-002-TEST-DESIGN-KICKOFF-REPORT.md` per the role doc's "Report shape".
