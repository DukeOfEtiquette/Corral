---
schema_version: 1
id: API-T-008
title: "Restructure app/api to one multi-stage Dockerfile with runtime + test targets (ADR-043)"
status: done
labels: []
priority: P2
created: 2026-06-22
updated: 2026-06-22
---

## Description

Adopt the accepted Dockerfile-structure convention (`ai-infrastructure/project-manager/decisions/ADR-043-dockerfile-structure-convention.md`, Option B) for the `./api` build context: collapse the `Dockerfile` / `Dockerfile.test` pair into a single multi-stage Dockerfile with named build targets, selected from compose via `build.target`. Standalone task (build hygiene; not part of API-E-001's endpoint/auth capability, same as API-T-006). Routes through the backend-api dispatched-worker flow (a domain-1 web-app deliverable: an executor edits build files under `app/api/` and `app/docker-compose.yml`). This is not a TDD surface; no test-designer dispatch, and the executor edits no test files.

**What is already done (do not redo).** COR-T-054 already added `app/api/.dockerignore` and switched the runtime `COPY . ./app/api/` to `COPY *.py ./app/api/`. This task does the remaining Option-B piece: the multi-stage collapse. The duplication smell (ADR-043 smell 1) is what this closes for api.

### Current state (verified on disk 2026-06-22; re-verify at execution, it may have drifted)

`app/api/Dockerfile` (runtime):
```
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY *.py ./app/api/
ENV PYTHONPATH=/app
CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8123"]
```
`app/api/Dockerfile.test`: same base, but installs `requirements.txt` + `requirements-test.txt`, does `COPY . ./app/api/` (source + tests, filtered by `.dockerignore`), and `CMD ["pytest", "-v", "app/api/tests/"]`.

The two share `FROM`, `WORKDIR /app`, the requirements install, the `COPY ... ./app/api/` layout, and `ENV PYTHONPATH=/app`; they differ only in the extra test dep and the `CMD`. The api context can share its deps layer (both images install `requirements.txt`), so api benefits fully from multi-stage layer reuse, unlike db (see DB-T-004).

### Deliverable

1. **Replace `app/api/Dockerfile` with a single multi-stage file** carrying a shared `base` stage and `runtime` + `test` targets. Recommended structure (adapt to the actual current file; the acceptance tests are the real gate):
```dockerfile
FROM python:3.12-slim AS base
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
ENV PYTHONPATH=/app

FROM base AS runtime
COPY *.py ./app/api/
CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8123"]

FROM base AS test
COPY requirements-test.txt .
RUN pip install --no-cache-dir -r requirements-test.txt
COPY *.py ./app/api/
COPY tests/ ./app/api/tests/
CMD ["pytest", "-v", "app/api/tests/"]
```
2. **Delete `app/api/Dockerfile.test`** (folded into the `test` target).
3. **Update `app/docker-compose.yml`** api-context services to select targets (edit only these two blocks):
   - `api`: add `build.target: runtime` (context stays `./api`).
   - `api-test`: replace `build.dockerfile: Dockerfile.test` with `build.target: test` (context stays `./api`).
4. **Update `app/api/.dockerignore`**: remove the now-stale `Dockerfile.test` entry (that file no longer exists); keep `Dockerfile` excluded. Leave every other entry as COR-T-054 set it.

### Constraints (the convention, ADR-043 Decision)

- **`.dockerignore` is per context, not per Dockerfile.** Do not exclude anything a target in `./api` needs. The runtime image keeps tests/ out via its selective `COPY *.py` (a per-target concern), NOT via `.dockerignore`.
- **Preserve the `app.api.*` import layout.** Both targets must place the package at `/app/app/api/` with `PYTHONPATH=/app` so `import app.api.main` resolves. Keep the uvicorn `--port 8123` (set by API-T-007).
- **Selective COPY per target** (ADR-043): runtime copies only `*.py`; test copies `*.py` + `tests/`. Prefer this over `COPY .`.
- **Edit no test files.** This is build config only; `app/api/tests/` is untouched.

### Cross-task coordination

DB-T-004 also edits `app/docker-compose.yml`, but a **different, disjoint set of service blocks** (`migrate` / `test` / `test-roundtrip`). The two tasks are run **sequentially**, not concurrently (operator-controlled), so there is no file collision. Rules that keep this clean:

- **This task edits ONLY the `api` and `api-test` blocks** in `app/docker-compose.yml`. Do not touch the db service blocks.
- **Co-commit the compose edit with the api Dockerfile conversion.** A `target:` only builds once the api Dockerfile is multi-stage; never split them across commits.
- **Run order: API-T-008 first, then DB-T-004** (interchangeable for correctness, but this is the designated order). At this task's completion the db services still build via their existing single-stage Dockerfiles, so acceptance test (b), full-fleet `docker compose build`, passes with only the api side converted.

### Acceptance tests

(a) `app/api/Dockerfile` is a single multi-stage file with `base`, `runtime`, `test` stages; `app/api/Dockerfile.test` no longer exists.
(b) `cd app && docker compose build` succeeds for all services.
(c) The api **runtime** image (`api` service) contains the `.py` source under `/app/app/api/` and `python -c "import app.api.main"` resolves, and does NOT contain `tests/`, `gen-admin-hash.sh`, or `.env.example`.
(d) The api **test** image (`api-test` service) runs its suite: `cd app && docker compose run --rm api-test` collects and runs the tests (expect the 22 from COR-T-054's run; they need not all pass for unrelated reasons, but the suite must collect and run, proving `tests/` is present).
(e) `app/api/.dockerignore` no longer lists `Dockerfile.test`.
ESCALATION: if the docker daemon / `docker compose` is unavailable in the execution environment, do NOT claim build success. Complete the file edits and escalate (RETURN: ESCALATION) reporting that gates (b)-(d) could not run, and ask whether to accept on static grounds or defer verification (per COR-09, a green-test one-shot is not a runtime gate; honest "could not verify" beats a fabricated green).

References:
- `ai-infrastructure/project-manager/decisions/ADR-043-dockerfile-structure-convention.md` (the accepted convention; the Decision section is binding)
- `ai-infrastructure/project-manager/decisions/ADR-006-admin-bootstrap-env-hash.md` (secrets-never-in-images, the COR-T-054 grounding the `.dockerignore` enforces)
- `ai-infrastructure/project-manager/decisions/ADR-003-docker-compose-runtime.md` (compose is the runtime; api context is `./api`)
- `ai-infrastructure/project-manager/tasks/done/COR-T-054-dockerignore-per-build-context.md` (the already-shipped `.dockerignore` + selective-runtime-COPY slice this builds on)
- `app/api/Dockerfile`, `app/api/Dockerfile.test` (the pair to collapse), `app/api/.dockerignore` (the stale `Dockerfile.test` entry to drop)
- `app/docker-compose.yml` (the `api` + `api-test` service blocks to switch to `target:`)
- `ai-infrastructure/backend-api/tasks/backlog/API-T-008` and `ai-infrastructure/database/tasks/backlog/DB-T-004-multistage-dockerfile-restructure.md` (the sibling db restructure; coordinate on `docker-compose.yml`)

## Activity log

- 2026-06-22: Created in backlog by the Project Manager Orchestrator under coordinator write authority (ADR-027), at user direction, so the Backend API Orchestrator can pick it up with full context. Filed standalone, P2. Implements the api half of accepted ADR-043 (Option B multi-stage); the `.dockerignore` + selective-runtime-COPY slice already landed under COR-T-054. Pairs with DB-T-004 (they share `app/docker-compose.yml`; run sequentially). Unlabelled per ADR-031. Filing committed as 4dbe7ba.
- 2026-06-22: Picked up by the Backend API Orchestrator at user direction; moved to in-progress. Routes through the dispatched-worker flow (domain-1 web-app build deliverable; not a TDD surface).
- 2026-06-22: Done. Dispatched-worker flow ran clean (kickoff-checker PASS, prelaunch PASS, executor RETURN: COMPLETED, close-checker PASS). Deliverable committed as 6e50dfe: `app/api/Dockerfile` collapsed to base/runtime/test stages, `app/api/Dockerfile.test` deleted, `app/docker-compose.yml` api+api-test blocks switched to `build.target`, stale `Dockerfile.test` entry pruned from `app/api/.dockerignore`. Orchestrator independently re-ran all acceptance gates (a)-(e) against disk: compose build green for all services, runtime image imports `app.api.main` and excludes tests/gen-admin-hash.sh/.env.example, api-test suite 22 passed. Compose edit disjoint from DB-T-004's db blocks (untouched). Kickoff/report pair committed with the deliverable (ADR-024).
