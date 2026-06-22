# DB-T-004-KICKOFF-REPORT

Executor: dispatched subagent (Sonnet), attempt 1.
Kickoff: `.claude/artifacts/handoffs/DB-T-004-KICKOFF.md`
Workspace: corral

## Deliverables completed

All four deliverables completed:

1. **`app/db/Dockerfile` replaced with a single multi-stage file** containing `base`, `runtime`, `test`, and `test-roundtrip` stages. Targets match the exact installs/copies/CMD split specified in the kickoff: `runtime` installs `requirements.txt` and copies `alembic.ini` + `alembic/` with no CMD; `test` installs `requirements-test.txt` only and copies `tests/` only (no `alembic/`) with CMD `pytest -v tests/ --ignore=tests/test_migration_roundtrip.py`; `test-roundtrip` installs both requirements files, copies `alembic.ini` + `alembic/` + `tests/`, with CMD `pytest -v tests/test_migration_roundtrip.py`. The alembic-split explanatory comment from the old `Dockerfile.test` lines 8-10 is preserved verbatim on the new `test` target (lines 13-15 of the new Dockerfile).

2. **`app/db/Dockerfile.test` and `app/db/Dockerfile.test-roundtrip` deleted.** Verified absent on disk after deletion.

3. **`app/docker-compose.yml` updated** -- only the three db-context service blocks were edited:
   - `migrate` (line 14): added `target: runtime` under `build:`
   - `test` (line 26): replaced `dockerfile: Dockerfile.test` with `target: test`
   - `test-roundtrip` (line 36): replaced `dockerfile: Dockerfile.test-roundtrip` with `target: test-roundtrip`
   The `api` and `api-test` blocks (lines 48-79) are untouched.

4. **`app/db/.dockerignore` updated:** removed `Dockerfile.test` and `Dockerfile.test-roundtrip` lines; now 6 lines ending at `Dockerfile`. All other COR-T-054 entries retained.

## Decisions made

No decisions needed beyond those pinned in the kickoff. The kickoff fully specified: target structure, stage names, installs/copies/CMD split, alembic-split comment preservation, dockerignore line removal, and compose key replacements. All choices were pre-resolved.

## Surprises

None. All current file contents matched the kickoff's "Verified current state" claims exactly:
- `app/db/Dockerfile` line 8: `COPY . .` (as claimed)
- `app/db/Dockerfile.test` lines 8-10: alembic-split comment (as claimed)
- `app/db/.dockerignore`: 8 lines including both stale entries (as claimed)
- `app/docker-compose.yml` `migrate` block had no `target:` or `dockerfile:` (as claimed)
- `app/docker-compose.yml` `test`/`test-roundtrip` blocks had `dockerfile:` (as claimed)

## Follow-ups

- COR-T candidate: The `test-roundtrip` image `ls` output does not include `alembic.ini` at the top-level listing but it does appear as `alembic.ini` and `alembic` separately -- both are present. No action needed; this is expected from the COPY sequence.
- No other follow-ups. The db multi-stage restructure is complete; the only remaining ADR-043 work would be any future new build contexts, which are mandated to follow this convention at creation time.

## Files touched

- `app/db/Dockerfile` (replaced with multi-stage file)
- `app/db/Dockerfile.test` (deleted)
- `app/db/Dockerfile.test-roundtrip` (deleted)
- `app/docker-compose.yml` (three db service blocks updated: lines 17, 29, 39)
- `app/db/.dockerignore` (two stale entries removed; now 6 lines)
- `.claude/artifacts/handoffs/DB-T-004-KICKOFF-REPORT.md` (this report, dual-channel)

## Build / verification status

All five acceptance gates satisfied:

(a) PASSED: `app/db/Dockerfile` is a single multi-stage file with `base`, `runtime`, `test`, and `test-roundtrip` stages (verified by `grep FROM`). `Dockerfile.test` and `Dockerfile.test-roundtrip` are absent on disk (verified by `test -f`).

(b) PASSED: `cd app && docker compose build` succeeded for ALL services -- `app-api`, `app-api-test`, `app-migrate`, `app-test`, `app-test-roundtrip` all built green (no cache misses required; layers resolved from cache).

(c) PASSED: `docker compose run --rm --entrypoint sh test -c 'ls /app/db'` shows only `requirements-test.txt` and `tests/` -- `alembic/` is absent. `docker compose run --rm test` collected and ran 130 tests, all passed (matching the COR-T-054 ~130-test characterization reference).

(d) PASSED: `docker compose run --rm test-roundtrip` collected and ran 1 test (`test_baseline_downgrade_is_a_clean_drop_then_upgrade_restores`), passed. `alembic/` confirmed present in the image (`ls /app/db` shows `alembic`, `alembic.ini`, both requirements files, `tests/`).

(e) PASSED: The `migrate` service ran successfully as a dependency of `test-roundtrip` (exited successfully, applying `alembic upgrade head` without error).

(f) PASSED: `app/db/.dockerignore` is 6 lines ending at `Dockerfile`; no `Dockerfile.test` or `Dockerfile.test-roundtrip` entries; COR-T-054 entries retained.
