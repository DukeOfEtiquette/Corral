# API-T-008 Kickoff Report

Executor: dispatched subagent (Sonnet), attempt 1.
Kickoff: `.claude/artifacts/handoffs/API-T-008-KICKOFF.md`

## Deliverables completed

All four deliverables completed as specified.

1. **`app/api/Dockerfile` rewritten to pinned multi-stage content.** The file now contains three named stages: `base` (python:3.12-slim, WORKDIR /app, requirements.txt install, ENV PYTHONPATH=/app), `runtime` (COPY *.py ./app/api/, CMD uvicorn --port 8123), and `test` (COPY requirements-test.txt, pip install, COPY *.py ./app/api/, COPY tests/ ./app/api/tests/, CMD pytest). Content written verbatim as pinned; no added comments, no reordering.

2. **`app/api/Dockerfile.test` deleted.** File removed; `ls app/api/` confirms it is absent.

3. **`app/docker-compose.yml` edited - only the `api` and `api-test` blocks.** The `api` block gained `target: runtime` under `build:` (alongside `context: ./api`). The `api-test` block had `dockerfile: Dockerfile.test` replaced with `target: test` (keeping `context: ./api`). The `postgres`, `migrate`, `test`, and `test-roundtrip` blocks were not touched.

4. **`app/api/.dockerignore` pruned.** The `Dockerfile.test` line was removed. The `Dockerfile` line and all other entries (`.env`, `.env.example`, `__pycache__/`, `*.pyc`, `.pytest_cache/`, `gen-admin-hash.sh`) are unchanged.

## Decisions made

No decisions were required. All choices were pinned by the kickoff (Orchestrator-resolved per ADR-043 Option B). The pinned Dockerfile content, selective COPY lines, compose block edits, and .dockerignore edit were applied exactly as specified.

## Surprises

None. On-disk state matched the kickoff's verified description exactly:
- `app/api/Dockerfile` was single-stage runtime as described.
- `app/api/Dockerfile.test` existed with `COPY . ./app/api/` and `CMD pytest`.
- `app/docker-compose.yml` api block had only `context: ./api`; api-test block had `context: ./api` plus `dockerfile: Dockerfile.test`.
- `app/api/.dockerignore` contained exactly the entries the kickoff listed, including `Dockerfile.test`.

## Follow-ups

- **DB-T-004 is the sibling task** (database build-context multi-stage restructure). It edits the `postgres`, `migrate`, `test`, and `test-roundtrip` blocks in `app/docker-compose.yml` plus the db Dockerfiles. This task is complete; DB-T-004 can now run against the current state. Target: DB-T-004 task, triage to orchestrator for scheduling.

## Files touched

- `app/api/Dockerfile` (rewritten to multi-stage content)
- `app/api/Dockerfile.test` (deleted)
- `app/docker-compose.yml` (api and api-test blocks updated)
- `app/api/.dockerignore` (Dockerfile.test line removed)
- `.claude/artifacts/handoffs/API-T-008-KICKOFF-REPORT.md` (this report)

## Build / verification status

Docker 29.4.3, Compose v5.1.3 available. All acceptance gates run and passed.

**(a) Static check - multi-stage Dockerfile, Dockerfile.test absent.**
`grep "^FROM" app/api/Dockerfile` returns:
```
FROM python:3.12-slim AS base
FROM base AS runtime
FROM base AS test
```
`ls app/api/Dockerfile.test` returns: No such file or directory. PASS.

**(b) `cd app && docker compose build` - all services.**
All five images built successfully: `app-migrate`, `app-test`, `app-test-roundtrip`, `app-api`, `app-api-test`. The `api-test` image was rebuilt (not cached) since it is now selecting the `test` target from the new multi-stage Dockerfile. PASS.

**(c) Runtime image contents and import check.**
`docker run --rm app-api python -c "import app.api.main; print('import OK')"` returned `import OK`. The runtime image `/app/app/api/` contains: `__init__.py`, `admin_seed.py`, `auth.py`, `db.py`, `main.py`, `settings.py`. Confirmed absent: `tests/` directory, `gen-admin-hash.sh`, `.env.example`. PASS.

**(d) `cd app && docker compose run --rm api-test` - suite collects and runs.**
22 tests collected and all 22 passed (same count as COR-T-054's run). Suite ran in 2.81s. Full output:
```
collected 22 items
app/api/tests/test_admin_seed.py::... 4 PASSED
app/api/tests/test_auth_login.py::... 9 PASSED
app/api/tests/test_healthz.py::... 3 PASSED
app/api/tests/test_sessions.py::... 6 PASSED
22 passed in 2.81s
```
PASS.

**(e) `.dockerignore` no longer lists `Dockerfile.test`.**
`grep "Dockerfile.test" app/api/.dockerignore` returns no match. PASS.

All acceptance gates (a)-(e): PASS.
