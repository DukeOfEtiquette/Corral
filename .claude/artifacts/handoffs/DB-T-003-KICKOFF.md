# DB-T-003: make the migration round-trip test runnable via a dedicated compose test-roundtrip service

## Target

Web-app work (ADR-005), database department, task DB-T-003 (task file `./ai-infrastructure/database/tasks/in-progress/DB-T-003-roundtrip-test-runnable.md`). DB-T-002 delivered the schema test suite under `./app/db/tests/`, including `./app/db/tests/test_migration_roundtrip.py`, which asserts the ADR-014 clean-drop round-trip. That test currently self-skips in the delivered harness: the existing compose `test` service builds from `./app/db/Dockerfile.test`, which installs no Alembic and copies only `tests/` (not `alembic/`), so the test's `_alembic_available()` guard (Alembic importable AND `alembic.ini` present at `/app/db`) is false and the test skips. This task makes the round-trip runnable by adding a dedicated, one-shot compose service that DOES carry Alembic plus the Alembic project, running only the round-trip test against a migrated database.

This is a harness-only change. There is no test-file edit: the round-trip test's skip guard is correct as authored, and the test runs as-is when Alembic is present (per ADR-016, you may not edit test files, and none needs editing here).

## Decisions resolved by the Orchestrator

- **Approach: a new dedicated one-shot `test-roundtrip` compose service, not a change to the existing `test` service.** Add a new service backed by its own image that carries Alembic, pytest, psycopg2, the Alembic project, and the tests, running only the round-trip test. Do NOT fold the round-trip into the existing `test` service: the round-trip migrates the database (`downgrade base` then `upgrade head`), and the schema-shape `test` service is meant to run RED against a non-migrated database; a round-trip running first would migrate the DB and make the shape tests pass, destroying that red-check property. Keep the existing `test` service and `./app/db/Dockerfile.test` unchanged.

- **No edit to any file under `./app/db/tests/`.** The round-trip test's `pytest.mark.skipif` guard is correct: it skips where Alembic is absent and runs where Alembic is present (ADR-016 no-touch). You add the runtime that makes the guard evaluate true; you do not change the guard.

- **New file `./app/db/Dockerfile.test-roundtrip` (the Alembic + pytest round-trip runner image):**
  - `FROM python:3.12-slim`; `WORKDIR /app/db`.
  - COPY both `requirements.txt` and `requirements-test.txt`, then `pip install --no-cache-dir -r requirements.txt -r requirements-test.txt`. This yields Alembic 1.13.3 + psycopg2-binary from `requirements.txt` and pytest 8.3.3 + psycopg2-binary from `requirements-test.txt`; the duplicate `psycopg2-binary==2.9.10` pin is identical across both files and harmless.
  - COPY `alembic.ini` and the `alembic/` directory into `/app/db`, so the test's guard finds Alembic importable AND `/app/db/alembic.ini` present, and the round-trip's `alembic` subprocess runs with cwd `/app/db`.
  - COPY `tests/` into `/app/db/tests/` (the round-trip test plus `conftest.py`, which provides the `conn` / `cur` fixtures the test uses).
  - `CMD` runs only the round-trip test: `pytest -v tests/test_migration_roundtrip.py`.

- **New compose service `test-roundtrip` in `./app/docker-compose.yml` (additive only):**
  - `build`: context `./db`, dockerfile `Dockerfile.test-roundtrip`.
  - `environment`: `DATABASE_URL` identical to the existing `migrate` and `test` services (`postgresql://corral:devpassword@postgres:5432/corral`).
  - `depends_on`: `postgres` with condition `service_healthy`, AND `migrate` with condition `service_completed_successfully`, so the round-trip test runs against an already-migrated database (its intended environment) and avoids any downgrade-from-empty edge case.
  - Do NOT alter the existing `postgres`, `migrate`, or `test` services.

## Deliverables

- `./app/db/Dockerfile.test-roundtrip` (new): the Alembic + pytest round-trip runner image, per the decisions above.
- `./app/docker-compose.yml`: the added `test-roundtrip` one-shot service (the `postgres`, `migrate`, and `test` services left untouched).

## Files in scope

- `./app/db/Dockerfile.test-roundtrip` (NEW file)
- `./app/docker-compose.yml` (ADD the `test-roundtrip` service only; no other edit)

## Files out of scope

- `./app/db/tests/` (ALL test files, including `test_migration_roundtrip.py` and `conftest.py`): no edits. ADR-016 no-touch; the round-trip test runs as authored when Alembic is present.
- `./app/db/Dockerfile.test` and the existing `test` compose service: keep the schema-shape red-check pure.
- `./app/db/Dockerfile`, `./app/db/requirements.txt`, `./app/db/requirements-test.txt`: reused as-is via COPY, not edited.
- `./app/db/alembic/` (the migration and project, including `./app/db/alembic/versions/0001_baseline_schema.py`) and `./app/db/alembic.ini`: reused via COPY, not edited; do not touch the migration or any schema.
- `./ai-infrastructure/database/STATUS.md`: not touched (see STATUS deltas below).

## References

- `./app/db/tests/test_migration_roundtrip.py`: the test to make runnable. Read its `_alembic_available()` guard (Alembic importable AND `/app/db/alembic.ini` present) and the `ALEMBIC_PROJECT_DIR` default of `/app/db` to confirm the new image satisfies both. Do NOT edit it.
- `./app/db/Dockerfile`: the migrate-image pattern (installs `requirements.txt`, copies the whole project including the Alembic project).
- `./app/db/Dockerfile.test`: the test-image pattern to mirror (`FROM python:3.12-slim`, `WORKDIR /app/db`, COPY requirements, COPY `tests/`, `CMD pytest`).
- `./app/db/requirements.txt`: `alembic==1.13.3`, `psycopg2-binary==2.9.10`.
- `./app/db/requirements-test.txt`: `pytest==8.3.3`, `psycopg2-binary==2.9.10`.
- `./app/docker-compose.yml`: the `postgres` / `migrate` / `test` services to mirror and extend (copy the `DATABASE_URL` and the `depends_on` conditions from `migrate`).
- `./ai-infrastructure/project-manager/decisions/ADR-016-testing-strategy-test-designer-agent.md`: TDD and test no-touch context (you do not edit test files).
- `./ai-infrastructure/project-manager/decisions/ADR-003-docker-compose-runtime.md`: compose is the only run/verify path.
- `./ai-infrastructure/project-manager/decisions/ADR-014-db-migrations-tooling.md`: the clean-drop round-trip the test asserts (0 contract tables after `downgrade base`, all 11 after `upgrade head`).

## Related tasks and ADRs

- DB-T-002: delivered the round-trip test (currently self-skipping); this task makes it runnable.
- DB-T-001: the schema/migration the round-trip exercises.
- ADR-016: TDD and test-ownership; the executor may not edit test files (and here it does not).
- ADR-003: compose is the only run/verify path.
- ADR-014: the baseline downgrade is a clean drop (the round-trip contract).

## STATUS deltas

No task-specific STATUS deltas; none. The orchestrator finalizes the `./ai-infrastructure/database/STATUS.md` Next step at close.

## Hard rules

- Harness-only change: edit exactly the two in-scope files. Make NO edit to any file under `./app/db/tests/` (ADR-016 no-touch), to `./app/db/Dockerfile.test` or the existing `test` service, or to the Alembic project / migration / schema.
- The new `test-roundtrip` service is additive: do not alter the existing `postgres`, `migrate`, or `test` services in `./app/docker-compose.yml`.

## Verification expectations

Verify compose-only (ADR-003):

- `docker compose run --rm test-roundtrip` brings up `postgres`, runs the `migrate` one-shot, then RUNS the round-trip test (it must NOT skip) and it PASSES. The assertions are: 0 contract tables present after `alembic downgrade base`, and all 11 contract tables present after `alembic upgrade head`. Confirm the pytest output shows `1 passed` (not skipped).
- `docker compose run --rm test` (the schema-shape suite) is unaffected: it still passes against a migrated database, and the round-trip test still self-skips there.

Capture the round-trip pytest output (showing `1 passed`, not skipped) in the closing report. The orchestrator re-runs both at close.

## Executor pointer

The executor is the dispatched `executor` (ADR-028). Universal executor conventions live in `./docs/ai-orchestration/roles/EXECUTOR-ROLE.md`. Write the closing report to `./.claude/artifacts/handoffs/DB-T-003-KICKOFF-REPORT.md` per EXECUTOR-ROLE.md, section "Report shape" (dual-channel: chat and file).
