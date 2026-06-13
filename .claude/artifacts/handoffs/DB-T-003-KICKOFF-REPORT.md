## Deliverables completed

- `./app/db/Dockerfile.test-roundtrip` (NEW): the Alembic + pytest round-trip runner image. Installs both `requirements.txt` and `requirements-test.txt`, copies `alembic.ini`, `alembic/`, and `tests/` into `/app/db`, and runs `pytest -v tests/test_migration_roundtrip.py` as CMD. The `_alembic_available()` guard evaluates true (Alembic importable + `/app/db/alembic.ini` present), so the test runs rather than skips.
- `./app/docker-compose.yml` (ADDITIVE): new `test-roundtrip` service added. Build context `./db`, dockerfile `Dockerfile.test-roundtrip`, `DATABASE_URL` identical to `migrate` and `test`, `depends_on` both `postgres` (service_healthy) and `migrate` (service_completed_successfully). The existing `postgres`, `migrate`, and `test` services are unchanged.

## Decisions made

No decisions were deferred to the executor. All parameters (Dockerfile content, service shape, dependency conditions) were fully pinned in the kickoff and followed as authored.

## Surprises

None. The file state matched the kickoff exactly: `Dockerfile`, `Dockerfile.test`, `requirements.txt`, `requirements-test.txt`, `docker-compose.yml` all present at the paths the kickoff named. No unfamiliar files in the working tree. The duplicate `psycopg2-binary==2.9.10` pin across both requirements files was called out in the kickoff as harmless; pip confirmed this during the image build (no conflict, last writer wins for identical pins).

## Follow-ups

None surfaced during execution. The harness is complete: the round-trip test runs in its own one-shot service without affecting the shape suite's red-check properties.

## Files touched

- `./app/db/Dockerfile.test-roundtrip` (created)
- `./app/docker-compose.yml` (edited: `test-roundtrip` service added)
- `./.claude/artifacts/handoffs/DB-T-003-KICKOFF-REPORT.md` (this report)

## Build / verification status

Both verifications run and passed via `docker compose` (ADR-003):

**`docker compose run --rm test-roundtrip`**

```
============================= test session starts ==============================
platform linux -- Python 3.12.12, pytest-8.3.3, pluggy-1.6.0 -- /usr/local/bin/python3.12
cachedir: .pytest_cache
rootdir: /app/db
collecting ... collected 1 item

tests/test_migration_roundtrip.py::test_baseline_downgrade_is_a_clean_drop_then_upgrade_restores PASSED [100%]

============================== 1 passed in 0.65s ===============================
```

The round-trip test ran (NOT skipped) and passed. Contract satisfied: 0 contract tables after `alembic downgrade base`, all 11 restored after `alembic upgrade head`.

**`docker compose run --rm test`** (schema shape suite, unaffected check)

```
collected 131 items

tests/test_migration_roundtrip.py::test_baseline_downgrade_is_a_clean_drop_then_upgrade_restores SKIPPED [  0%]
... (130 shape tests) ...

======================== 130 passed, 1 skipped in 1.09s ========================
```

The shape suite is unaffected: 130 shape tests pass, the round-trip test correctly self-skips in the test-only image (Alembic absent), preserving the red-check property.
