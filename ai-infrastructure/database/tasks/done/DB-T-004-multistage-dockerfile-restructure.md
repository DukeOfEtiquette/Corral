---
schema_version: 1
id: DB-T-004
title: "Restructure app/db to one multi-stage Dockerfile with runtime + test + test-roundtrip targets (ADR-043)"
status: done
labels: []
priority: P2
created: 2026-06-22
updated: 2026-06-22
---

## Description

Adopt the accepted Dockerfile-structure convention (`ai-infrastructure/project-manager/decisions/ADR-043-dockerfile-structure-convention.md`, Option B) for the `./db` build context: collapse `Dockerfile` / `Dockerfile.test` / `Dockerfile.test-roundtrip` into a single multi-stage Dockerfile with named build targets, selected from compose via `build.target`. Standalone task (build hygiene; not part of DB-E-001's schema/migrations capability). Routes through the database dispatched-worker flow (a domain-1 web-app deliverable: an executor edits build files under `app/db/` and `app/docker-compose.yml`). Not a TDD surface; no test-designer dispatch, and the executor edits no test files.

**What is already done (do not redo).** COR-T-054 already added `app/db/.dockerignore`. This task does the remaining Option-B piece: the multi-stage collapse.

### The db split is the crux (ADR-043 Decision point 4, preserve exactly)

The db context produces **three** images with genuinely different needs. Preserve each exactly; do NOT tidy them into fewer:

| target | installs | copies | CMD | used by compose service |
|---|---|---|---|---|
| `runtime` | `requirements.txt` | `alembic.ini`, `alembic/` | (none; service overrides) | `migrate` (`command: alembic upgrade head`) |
| `test` | `requirements-test.txt` ONLY (no app deps) | `tests/` ONLY (no alembic) | `pytest tests/ --ignore=tests/test_migration_roundtrip.py` | `test` |
| `test-roundtrip` | `requirements.txt` + `requirements-test.txt` | `alembic.ini`, `alembic/`, `tests/` | `pytest tests/test_migration_roundtrip.py` | `test-roundtrip` |

The deliberate, well-commented boundary: `test` excludes `alembic/` so schema-characterization tests assert against the **live DB**, never the migration source; `test-roundtrip` includes `alembic/` for the migration round-trip. This must remain a visible COPY-diff between the two test targets (the reason ADR-043 chose two targets over a build-arg).

Note the db base **cannot share a deps layer** the way api can: the `test` image deliberately installs no app deps, so each target installs its own deps after a minimal `base`. This is the expected "uneven win" from ADR-043 Consequences (db gains one file + a legible boundary, not layer reuse). Do not "fix" it by hoisting `requirements.txt` into `base`; that would put app deps into the `test` image and break the deliberate minimalism.

### Current state (verified on disk 2026-06-22; re-verify at execution)

- `app/db/Dockerfile` (runtime/migrate): `WORKDIR /app/db`, installs `requirements.txt`, then `COPY . .` (rakes the whole context, filtered by `.dockerignore`). No `CMD` (the `migrate` service supplies `command: alembic upgrade head`).
- `app/db/Dockerfile.test`: installs `requirements-test.txt` only, `COPY tests/ ./tests/`, `CMD pytest -v tests/ --ignore=tests/test_migration_roundtrip.py`.
- `app/db/Dockerfile.test-roundtrip`: installs `requirements.txt` + `requirements-test.txt`, copies `alembic.ini` + `alembic/` + `tests/`, `CMD pytest -v tests/test_migration_roundtrip.py`.

### Deliverable

1. **Replace `app/db/Dockerfile` with a single multi-stage file** with a minimal `base` and `runtime` + `test` + `test-roundtrip` targets. Recommended structure (adapt to the actual current files; acceptance tests are the real gate):
```dockerfile
FROM python:3.12-slim AS base
WORKDIR /app/db

FROM base AS runtime
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY alembic.ini .
COPY alembic/ ./alembic/
# used by the compose `migrate` service, which overrides: command: alembic upgrade head

FROM base AS test
COPY requirements-test.txt .
RUN pip install --no-cache-dir -r requirements-test.txt
COPY tests/ ./tests/
CMD ["pytest", "-v", "tests/", "--ignore=tests/test_migration_roundtrip.py"]

FROM base AS test-roundtrip
COPY requirements.txt requirements-test.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-test.txt
COPY alembic.ini .
COPY alembic/ ./alembic/
COPY tests/ ./tests/
CMD ["pytest", "-v", "tests/test_migration_roundtrip.py"]
```
   Note this also tightens the `runtime`/`migrate` image: it currently does `COPY . .` (drags in `tests/`); the `runtime` target copies only `alembic.ini` + `alembic/`, which is all `alembic upgrade head` needs.
2. **Delete `app/db/Dockerfile.test` and `app/db/Dockerfile.test-roundtrip`** (folded into targets).
3. **Update `app/docker-compose.yml`** db-context services to select targets (edit ONLY these three blocks):
   - `migrate`: add `build.target: runtime` (context stays `./db`; keep its `command: alembic upgrade head`).
   - `test`: replace `build.dockerfile: Dockerfile.test` with `build.target: test`.
   - `test-roundtrip`: replace `build.dockerfile: Dockerfile.test-roundtrip` with `build.target: test-roundtrip`.
4. **Update `app/db/.dockerignore`**: remove the now-stale `Dockerfile.test` and `Dockerfile.test-roundtrip` entries (those files no longer exist); keep `Dockerfile` excluded. Leave every other entry as COR-T-054 set it.

### Constraints (the convention, ADR-043 Decision)

- **`.dockerignore` is per context, not per Dockerfile.** It must NOT exclude `tests/`, `alembic/`, `alembic.ini`, or `requirements*.txt` (sibling targets in `./db` consume them). Per-target exclusion is the job of selective `COPY` inside each target.
- **Preserve all three images' exact dep/copy split** per the table above. The `test` image must end up with NO `alembic/` and NO app deps; verify both.
- **Edit no test files.** `app/db/tests/` is untouched.

### Cross-task coordination

API-T-008 also edits `app/docker-compose.yml`, but a **different, disjoint set of service blocks** (`api` / `api-test`). The two tasks are run **sequentially**, not concurrently (operator-controlled), so there is no file collision. Rules that keep this clean:

- **This task edits ONLY the `migrate`, `test`, and `test-roundtrip` blocks** in `app/docker-compose.yml`. Do not touch the api service blocks.
- **Co-commit the compose edits with the db Dockerfile conversion.** A `target:` only builds once the db Dockerfile is multi-stage; never split them across commits.
- **Run order: API-T-008 first, then DB-T-004.** If API-T-008 has already landed when this runs, the api services are already on targets and untouched here; the full-fleet build covers both.

### Acceptance tests

(a) `app/db/Dockerfile` is a single multi-stage file with `base`, `runtime`, `test`, `test-roundtrip` stages; `app/db/Dockerfile.test` and `app/db/Dockerfile.test-roundtrip` no longer exist.
(b) `cd app && docker compose build` succeeds for all services.
(c) The `test` image has NO `alembic/` and NO app deps: `cd app && docker compose run --rm test` runs the characterization suite (expect ~130 tests, per COR-T-054's run) and collects/runs green; verify `alembic/` is absent from the image (e.g. `docker compose run --rm --entrypoint sh test -c 'ls'` shows no `alembic`).
(d) The `test-roundtrip` image runs the migration round-trip: `cd app && docker compose run --rm test-roundtrip` (expect 1 test) collects and runs; `alembic/` IS present.
(e) The `migrate` service still applies migrations: `cd app && docker compose run --rm migrate` runs `alembic upgrade head` against postgres without error (its image carries `alembic.ini` + `alembic/`).
(f) `app/db/.dockerignore` no longer lists `Dockerfile.test` or `Dockerfile.test-roundtrip`.
ESCALATION: if the docker daemon / `docker compose` is unavailable, do NOT claim build success. Complete the file edits and escalate (RETURN: ESCALATION) reporting gates (b)-(e) could not run, and ask whether to accept on static grounds or defer (per COR-09, a green-test one-shot is not a runtime gate; honest "could not verify" beats a fabricated green).

References:
- `ai-infrastructure/project-manager/decisions/ADR-043-dockerfile-structure-convention.md` (the accepted convention; Decision point 4 and Consequences cover the db split and the uneven-win nuance)
- `ai-infrastructure/project-manager/decisions/ADR-014-db-migrations-tooling.md` and `ai-infrastructure/project-manager/decisions/ADR-003-docker-compose-runtime.md` (alembic + compose-runtime context; db context is `./db`)
- `ai-infrastructure/project-manager/tasks/done/COR-T-054-dockerignore-per-build-context.md` (the already-shipped `.dockerignore` slice this builds on)
- `app/db/Dockerfile`, `app/db/Dockerfile.test`, `app/db/Dockerfile.test-roundtrip` (the three to collapse; the latter two carry the alembic-split comment to preserve), `app/db/.dockerignore` (the stale entries to drop)
- `app/docker-compose.yml` (the `migrate` + `test` + `test-roundtrip` blocks to switch to `target:`)
- `ai-infrastructure/backend-api/tasks/backlog/API-T-008-multistage-dockerfile-restructure.md` (the sibling api restructure; run it first; coordinate on `docker-compose.yml`)

## Activity log

- 2026-06-22: Created in backlog by the Project Manager Orchestrator under coordinator write authority (ADR-027), at user direction, so the Database Orchestrator can pick it up with full context. Filed standalone, P2. Implements the db half of accepted ADR-043 (Option B multi-stage), preserving the three-image dep/copy split exactly (ADR-043 Decision point 4); the `.dockerignore` slice already landed under COR-T-054. Pairs with API-T-008 (shared `app/docker-compose.yml`, disjoint blocks, run API-T-008 first). Unlabelled per ADR-031.
- 2026-06-22: Picked up by the Database Orchestrator at user direction; moved to in-progress. Verified prerequisites on disk: all three db Dockerfiles present, `.dockerignore` carries the two stale `Dockerfile.test*` entries to drop, and API-T-008 is in done/ with the `api`/`api-test` compose services already on `target:` (run-order constraint satisfied, no compose collision). Routing through the dispatched-worker flow (domain-1 build deliverable).
- 2026-06-22: Done (commit e70b112). Dispatched-worker flow: kickoff drafted + checked (PASS, 0 findings), prelaunch PASS (no deferrals), executor (Sonnet) returned COMPLETED, close checker PASS (W2 clean, W3 inert). Orchestrator independently re-derived all six acceptance gates against disk, not trusting the report: (a) single multi-stage `app/db/Dockerfile` with base/runtime/test/test-roundtrip, `Dockerfile.test*` deleted; (b) `docker compose build` green for all 5 services; (c) `test` image has no `alembic/` and 130 tests pass; (d) `test-roundtrip` image has `alembic/` and its 1 test passes; (e) `migrate` ran `alembic upgrade head` (exit 0); (f) `.dockerignore` drops the two stale entries, keeps `Dockerfile`. Scope clean: only the 5 intended files changed, no test files and no `app/api/` files touched. Deliverable + kickoff/report pair (ADR-024) + the filing `.next-task-id` bump committed in e70b112; this done move is the second commit.
