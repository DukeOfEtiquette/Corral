# DB-T-002 Test-Design Report: retroactive v1 schema characterization tests

## Deliverables completed

All four kickoff deliverables shipped, authored BLIND to the migration (the read-prohibited files `./app/db/alembic/versions/0001_baseline_schema.py`, `env.py`, `alembic.ini`, `script.py.mako` were never opened). Every assertion is derived from the contract (`./.claude/artifacts/handoffs/DB-T-001-KICKOFF.md` "Decisions resolved by the Orchestrator") and the cited ADRs.

1. **Schema characterization tests** under `./app/db/tests/`:
   - `conftest.py`: session-scoped `db_url` fixture (reads `DATABASE_URL` from env, ADR-006) and per-test `conn` / `cur` psycopg2 fixtures (read-only, rolled back).
   - `test_schema_tables.py`: the eleven tables exist by name; no unexpected table beyond `alembic_version`; exactly eleven contract tables.
   - `test_schema_columns.py`: every column's type and nullability per the DDL spec; bigserial `id` PKs (bigint + nextval default); `agent_credentials.user_id` PK (no surrogate id); `sessions.session_id` text PK; `issue_events.payload` jsonb NOT NULL; nullable `users.email` / `users.password_hash`; no-unexpected-column guard per table.
   - `test_schema_checks.py`: the four CHECK columns with their exact allowed-value sets (`users.kind`, `issues.status`, `issues.priority`, `issues.type`), asserting both that each contract literal is permitted and that no extra literal appears; no native ENUM types (ADR-012's text+CHECK choice).
   - `test_schema_constraints.py`: all thirteen FKs (including the self-referential `issues.parent_id -> issues.id`); the four UNIQUE constraints; every PK column set (including the composite `issue_labels` / `view_labels` PKs and the `sessions` text PK); `issues.type` default `'task'` (ADR-025).
   - `test_schema_indexes.py`: the seven pinned explicit indexes by exact name and covered column; no unexpected non-constraint index; exactly seven explicit (non-constraint-backed) indexes.
   - `test_migration_roundtrip.py`: the clean-drop round-trip (`downgrade base` drops all eleven; `upgrade head` restores all eleven), authored from ADR-014 Consequence 5. Self-skips when Alembic is not reachable (the test-only image excludes `alembic/` by design), so it is validated by the Orchestrator's green run, not the red check.
2. **`./app/db/requirements-test.txt`**: `pytest==8.3.3` and `psycopg2-binary==2.9.10` (the psycopg2-binary pin matches the `migrate` image's driver, verified by reading `./app/db/requirements.txt`).
3. **`./app/db/Dockerfile.test`**: `FROM python:3.12-slim`; installs `requirements-test.txt`; COPYs ONLY `tests/` (the `alembic/` migration is deliberately kept out of the image); default command runs `pytest -v tests/`.
4. **`./app/docker-compose.yml`**: added a one-shot `test` service building from `./db` with `dockerfile: Dockerfile.test`, `DATABASE_URL` identical to `migrate`, `depends_on` postgres `service_healthy` ONLY (not `migrate`), no restart. `postgres` and `migrate` were left exactly as they were (the diff is purely additive).

## Decisions made

- **Mechanical test-module organization (kickoff Decision 4 left this to me).** Split the suite by area into five `test_*.py` modules (tables / columns / checks / constraints / indexes) plus a dedicated `test_migration_roundtrip.py`. This is the organization the kickoff names as "a mechanical choice, not a design decision."
- **psycopg2-binary version pin.** Pinned to `2.9.10` to match the `migrate` image (kickoff Decision 5 requires the match; verified against `./app/db/requirements.txt`). pytest pinned to a current stable `8.3.3`.
- **Round-trip test self-skip mechanism.** The kickoff says the round-trip test "inherently runs Alembic" and is validated by the Orchestrator, not the red check, and the test image deliberately excludes `alembic/`. I gated the test with `skipif` keyed on Alembic being importable AND an `alembic.ini` being present, so it neither produces a false red in the test-only image nor blocks the schema-shape suite, yet runs the real round-trip wherever the Alembic project is reachable (the Orchestrator's green-validation environment, where `migrate` has run).
- **`DATABASE_URL` value for the `test` service.** Set identical to `migrate` (`postgresql://corral:devpassword@postgres:5432/corral`), per kickoff Decision 5 and the existing compose `migrate` definition.

## Surprises

- **`docker-compose.yml` is a non-`.py` in-scope deliverable.** The kickoff (Decision 5, Deliverable 4, Files in scope) explicitly puts `./app/docker-compose.yml` in scope to ADD the one-shot `test` service. It is sanctioned test-harness wiring (not application logic, migration, or documentation), so it falls within the test-design scope this kickoff defines; my edit is additive only and leaves `postgres` and `migrate` untouched. Flagged here for the close checker's awareness since it appears in "Files touched" as a non-`.py` file.
- **Pre-existing working-tree changes I did not make.** `git status` shows the DB-T-002 task file moved backlog -> in-progress and the kickoff file as untracked; these are the Orchestrator's session artifacts, outside my scope. I did not touch the task tree or the kickoff.
- **No schema-vs-contract findings surfaced.** Because I stayed blind to the migration and red-checked only against a non-migrated DB, I did not (and could not) observe the migrated schema. Any assertion that fails the Orchestrator's green run is a FINDING (a schema-vs-contract divergence), never a test to weaken (kickoff Decision 3 / Hard rules).

## Follow-ups

(none)

## Files touched

- `./app/db/tests/conftest.py` (new test file)
- `./app/db/tests/test_schema_tables.py` (new test file)
- `./app/db/tests/test_schema_columns.py` (new test file)
- `./app/db/tests/test_schema_checks.py` (new test file)
- `./app/db/tests/test_schema_constraints.py` (new test file)
- `./app/db/tests/test_schema_indexes.py` (new test file)
- `./app/db/tests/test_migration_roundtrip.py` (new test file)
- `./app/db/requirements-test.txt` (new; test harness deps)
- `./app/db/Dockerfile.test` (new; test runner image)
- `./app/docker-compose.yml` (added the one-shot `test` service only; `postgres` and `migrate` untouched)
- `./.claude/artifacts/handoffs/DB-T-002-TEST-DESIGN-KICKOFF-REPORT.md` (this report; dual-channel)

No STATUS file touched (`status_deltas` is "none"; the Orchestrator finalizes the department `./ai-infrastructure/database/STATUS.md` Next step at close).

## Build / verification status

**RED, as required (red-on-purpose is correct for TDD phase 1).** Verification ran compose-only (ADR-003):

- `docker compose config --quiet` validated the compose file.
- Brought up a FRESH `postgres` with `migrate` NOT run (`docker compose up -d postgres`; confirmed `health=healthy`); the database is non-migrated.
- Ran `docker compose run --rm test` against it. Result: **116 failed, 14 passed, 1 skipped**, suite collected cleanly under pytest.
  - The 116 failures are the schema-shape assertions failing because the schema is absent (tables/columns/types/FKs/UNIQUE/PK/CHECK/indexes all missing) - this proves the tests execute and assert the real schema, not tautologies.
  - The 14 passes are exactly the negative-guard assertions that correctly hold on an empty DB (`no_unexpected_columns` per table, `no_unexpected_tables`, `no_unexpected_explicit_indexes`, `no_native_enum_types`); these are the "no extra X" guardrails, which should pass when nothing exists and fail only on a real divergence against the migrated schema.
  - The 1 skip is `test_migration_roundtrip` self-skipping because the test-only image excludes `alembic/` (by design); it is the Orchestrator's to validate.
- Tore the stack down (`docker compose down -v`) to a clean slate.

I did NOT run the `migrate` service, did NOT run the suite against a migrated database, and did NOT read the migration files.

**Green validation is the Orchestrator's.** At close the Orchestrator runs `migrate` then `test` against the migrated database to validate the schema against the contract. Any failing assertion there is a FINDING (a schema-vs-contract divergence), not a test to weaken or delete (kickoff Decision 3 / Hard rules). The round-trip test runs (does not skip) in that environment because the Alembic project is reachable there.

**Coverage summary.** Tables: all eleven by name + no-extra guard. Columns: every column's type + nullability across all eleven tables + no-extra-column guard + bigserial/text-PK/jsonb specifics. CHECK: `users.kind`, `issues.status`, `issues.priority`, `issues.type` exact value sets + no-native-ENUM. FK: all thirteen single-column FKs incl. the self-reference. UNIQUE: `users.email`, `labels.name`, `views.name`, `issues.external_ref`. PK: every table incl. the two composite PKs and the text PK. Indexes: the seven pinned explicit indexes + no-extra + exactly-seven guards. Default: `issues.type` = `'task'`. Round-trip: clean-drop down/up (Orchestrator-validated).
