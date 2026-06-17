# COR-T-054 Kickoff Report

## Deliverables completed

All three deliverables from the kickoff are complete:

1. `app/api/.dockerignore` (new file) -- created with the exact eight-entry exclusion set: `.env`, `.env.example`, `__pycache__/`, `*.pyc`, `.pytest_cache/`, `gen-admin-hash.sh`, `Dockerfile`, `Dockerfile.test`.

2. `app/db/.dockerignore` (new file) -- created with the exact eight-entry exclusion set: `.env`, `.env.example`, `__pycache__/`, `*.pyc`, `.pytest_cache/`, `Dockerfile`, `Dockerfile.test`, `Dockerfile.test-roundtrip`. Notably does NOT list `tests/`, `alembic/`, `alembic.ini`, or `requirements*.txt` per the shared-context constraint.

3. `app/api/Dockerfile` line 9 edited: `COPY . ./app/api/` changed to `COPY *.py ./app/api/`. All other lines (`WORKDIR`, `COPY requirements.txt`, `RUN pip install`, `ENV PYTHONPATH`, `CMD`) left unchanged.

## Decisions made

All decisions were pre-resolved by the Orchestrator in the kickoff. No new decisions were required during execution.

- The `.dockerignore` lists are exactly as pinned; no entries were added, dropped, or reordered.
- The api `Dockerfile` edit was the single `COPY` line only, as instructed.
- The db `.dockerignore` deliberately omits `tests/`, `alembic/`, `alembic.ini`, and `requirements*.txt` because the db build context is shared by three Dockerfiles that each need subsets of those files.

## Surprises

None. The files matched the kickoff's descriptions exactly. `app/api/Dockerfile` line 9 was `COPY . ./app/api/` as specified. The docker build context for `api` and `db` services matched the compose file mapping (`./api` and `./db` respectively).

## Follow-ups

- **Multi-stage build-target restructure (triage to orchestrator):** Collapsing each `Dockerfile` / `Dockerfile.test` pair into one file with runtime and test targets is OUT OF SCOPE for COR-T-054. This work is anchored to pending `ai-infrastructure/project-manager/decisions/ADR-043-dockerfile-structure-convention.md`. Once ADR-043 is accepted it becomes department-owned restructure tasks (API-T / DB-T candidates). Tag: triage to orchestrator.

## Files touched

- `app/api/.dockerignore` (created)
- `app/db/.dockerignore` (created)
- `app/api/Dockerfile` (edited: line 9, single COPY change)
- `.claude/artifacts/handoffs/COR-T-054-KICKOFF-REPORT.md` (this report, dual-channel)

## Build / verification status

All acceptance gates passed:

**a. File content verified** -- `app/api/.dockerignore` and `app/db/.dockerignore` both exist with the exact exclusion lists from the kickoff. `app/api/Dockerfile` line 9 reads `COPY *.py ./app/api/`. Verified with `cat` and `sed -n '9p'`.

**b. `docker compose build` succeeded** -- All five services (`api`, `api-test`, `migrate`, `test`, `test-roundtrip`) built without errors. Build log shows step `[api 5/5] COPY *.py ./app/api/` executing for the api service and `.dockerignore` being loaded (`transferring context: 137B`) for the api context and (`transferring context: 145B`) for the db context.

**c. Api runtime image contents verified** -- `docker compose run --rm --entrypoint sh api -c 'ls -R /app/app/api'` shows only: `__init__.py`, `admin_seed.py`, `auth.py`, `db.py`, `main.py`, `settings.py`. No `tests/`, no `gen-admin-hash.sh`, no `.env.example`. `docker compose run --rm --entrypoint python api -c 'import app.api.main; print("import OK")'` printed `import OK`, confirming the import path resolves.

**d. Api test image ran successfully** -- `docker compose run --rm api-test` collected and ran 22 tests, all passing (22 passed in 5.13s), confirming `tests/` is present in the `api-test` image.

**e. Db test and test-roundtrip images ran successfully** -- `docker compose run --rm test` ran 130 tests, all passing (130 passed in 1.17s). `docker compose run --rm test-roundtrip` ran 1 test, passing (1 passed in 0.80s), confirming `alembic/` and `alembic.ini` are still copyable and the migration round-trip boundary is intact.
