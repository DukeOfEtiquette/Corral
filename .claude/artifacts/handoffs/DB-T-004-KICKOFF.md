# Restructure app/db to one multi-stage Dockerfile with runtime + test + test-roundtrip targets (ADR-043), and switch the compose db services to build.target

## Target

This is web-app (domain-1) build work per ADR-005: you edit Docker build files under `./app/db/` and the db service blocks in `./app/docker-compose.yml`. ADR-043 accepted the multi-stage-Dockerfile-with-named-targets convention (Option B) for every web-app build context; this task ships the **db half** of that convention. (The sibling api half, API-T-008, already landed; its compose blocks are already on `target:` and are out of scope here.) This is NOT a TDD surface: no test-designer ran ahead of you, and you edit no test files. The `./app/db/tests/` suite is untouched.

## Decisions resolved by the Orchestrator

- **Adopt ADR-043 Option B for the `./db` build context.** Collapse the three current db Dockerfiles into one multi-stage Dockerfile with a `base` stage plus named `runtime`, `test`, and `test-roundtrip` targets, selected from compose via `build.target`. The convention is accepted and binding. Source: `ai-infrastructure/project-manager/decisions/ADR-043-dockerfile-structure-convention.md`, Decision point 4.
- **The db context produces THREE images with genuinely different needs; preserve each target EXACTLY as specified in Deliverables.** Do NOT tidy them into fewer targets, and do NOT hoist `requirements.txt` into the shared `base`. The `test` image deliberately installs NO app deps and copies NO `alembic/`, so the db `base` cannot share a deps layer the way the api context could. This is the expected "uneven win" ADR-043 names: the db context gains one file plus a legible boundary, not layer reuse. Source: ADR-043 Decision point 4 and Consequences ("The db context gains 'one file plus a legible, preserved boundary,' but little layer reuse... This uneven win is expected, not a defect").
- **The deliberate boundary to keep visible as a COPY-diff:** the `test` target excludes `alembic/` so schema-characterization tests assert against the live DB (never against the migration source), while `test-roundtrip` includes `alembic/` for the migration round-trip. This two-axis split (different deps AND different copied files) is exactly why ADR-043 chose two targets over a single build-arg. Keep the explanatory comment that the current `Dockerfile.test` carries (verified on disk at `app/db/Dockerfile.test` lines 8-10) on the new `test` target, so the boundary stays legible at the COPY level. Source: ADR-043 Decision point 4 and 5.
- **The new `runtime` target tightens the current migrate image, intentionally.** The current `app/db/Dockerfile` ends with `COPY . .` (verified on disk, line 8), which rakes `tests/` and everything else into the migrate image. The `runtime` target instead copies only `alembic.ini` + `alembic/`, which is all `alembic upgrade head` needs. This narrowing is intended, not incidental.
- **`.dockerignore` is per build context, not per Dockerfile.** It must NOT exclude `tests/`, `alembic/`, `alembic.ini`, or `requirements*.txt`, because sibling targets in `./db` consume them. Per-target exclusion is the job of selective `COPY` inside each target, never of `.dockerignore`. Source: ADR-043 Decision point 2; COR-T-054 already established the per-context `app/db/.dockerignore`.
- **Run-order constraint is already satisfied; co-commit the compose edits with the Dockerfile conversion.** API-T-008 (the sibling api restructure that shares `app/docker-compose.yml`) is already in `done/`, and the `api`/`api-test` services are already on `target:`. This task edits a DISJOINT set of compose blocks (`migrate`, `test`, `test-roundtrip` only) and must NOT touch the `api`/`api-test` blocks. A `target:` only builds once the matching Dockerfile is multi-stage, so the compose edits and the Dockerfile conversion are one logical change; do not split them across commits.

## Deliverables

1. **Replace `app/db/Dockerfile` with a SINGLE multi-stage Dockerfile** having a minimal `base` stage plus `runtime`, `test`, and `test-roundtrip` targets. The recommended structure below reproduces the verified current behavior of the three files being collapsed; adapt to the actual current files as needed, but the acceptance gate (below) is the real arbiter:

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
   # Copy ONLY the tests directory into the image. The migration (alembic/) is
   # deliberately kept out of the test image so the schema characterization tests
   # assert against the live database, never against the migration source.
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

   The three targets MUST end up with exactly this installs/copies/CMD split:
   - `runtime`: installs `requirements.txt`; copies `alembic.ini` + `alembic/`; NO CMD (the compose `migrate` service supplies `command: alembic upgrade head`). Consumed by the compose `migrate` service.
   - `test`: installs `requirements-test.txt` ONLY (no app deps); copies `tests/` ONLY (no `alembic/`); CMD `pytest -v tests/ --ignore=tests/test_migration_roundtrip.py`. Consumed by the compose `test` service.
   - `test-roundtrip`: installs `requirements.txt` + `requirements-test.txt`; copies `alembic.ini` + `alembic/` + `tests/`; CMD `pytest -v tests/test_migration_roundtrip.py`. Consumed by the compose `test-roundtrip` service.

2. **Delete `app/db/Dockerfile.test` and `app/db/Dockerfile.test-roundtrip`** (folded into the `test` and `test-roundtrip` targets). Preserve the alembic-split explanatory comment those files carry: the current comment lives at `app/db/Dockerfile.test` lines 8-10 (verified on disk) and must reappear on the new `test` target, exactly as the recommended structure in deliverable 1 shows.

3. **Update `app/docker-compose.yml`, editing ONLY these three db-context service blocks** (do not touch any other block):
   - `migrate`: add `build.target: runtime` (keep `build.context: ./db`, and keep its `command: alembic upgrade head`). Verified current state: the `migrate` block has `build.context: ./db` with NO `dockerfile:` or `target:` key today (`app/docker-compose.yml` lines 14-23).
   - `test`: replace `build.dockerfile: Dockerfile.test` with `build.target: test` (keep `build.context: ./db`). Verified current state: `app/docker-compose.yml` lines 25-33.
   - `test-roundtrip`: replace `build.dockerfile: Dockerfile.test-roundtrip` with `build.target: test-roundtrip` (keep `build.context: ./db`). Verified current state: `app/docker-compose.yml` lines 35-45.

4. **Update `app/db/.dockerignore`:** remove the now-stale `Dockerfile.test` and `Dockerfile.test-roundtrip` lines (those files will no longer exist); KEEP the `Dockerfile` line excluded; leave every other entry exactly as COR-T-054 set it. Verified current `app/db/.dockerignore` entries (8 lines): `.env`, `.env.example`, `__pycache__/`, `*.pyc`, `.pytest_cache/`, `Dockerfile`, `Dockerfile.test`, `Dockerfile.test-roundtrip`. The result is 6 lines (the first six, ending at `Dockerfile`).

## Acceptance gate

This is the single acceptance gate for the task. Re-verify each item on disk, and run the build/run gates if the docker daemon is available. (If it is not, see "Escalation" under Hard rules.)

(a) `app/db/Dockerfile` is a single multi-stage file with `base`, `runtime`, `test`, and `test-roundtrip` stages; `app/db/Dockerfile.test` and `app/db/Dockerfile.test-roundtrip` no longer exist on disk.

(b) `cd app && docker compose build` succeeds for ALL services.

(c) The `test` image has NO `alembic/` and NO app deps: `cd app && docker compose run --rm test` runs the characterization suite (expect ~130 tests, matching COR-T-054's recorded run) and collects/runs green; confirm `alembic/` is absent from the image, e.g. `cd app && docker compose run --rm --entrypoint sh test -c 'ls'` shows no `alembic`.

(d) The `test-roundtrip` image runs the migration round-trip: `cd app && docker compose run --rm test-roundtrip` (expect 1 test) collects and runs; `alembic/` IS present in this image.

(e) The `migrate` service still applies migrations: `cd app && docker compose run --rm migrate` runs `alembic upgrade head` against postgres without error (its image carries `alembic.ini` + `alembic/`).

(f) `app/db/.dockerignore` no longer lists `Dockerfile.test` or `Dockerfile.test-roundtrip`; it still excludes `Dockerfile` and retains its other COR-T-054 entries.

## Files in scope

- `app/db/Dockerfile` (replace with the multi-stage file from deliverable 1)
- `app/db/Dockerfile.test` (delete; folded into the `test` target)
- `app/db/Dockerfile.test-roundtrip` (delete; folded into the `test-roundtrip` target)
- `app/docker-compose.yml` (edit ONLY the `migrate`, `test`, and `test-roundtrip` blocks)
- `app/db/.dockerignore` (remove the two stale `Dockerfile.test*` lines; keep `Dockerfile`)

## Files out of scope

- `app/db/tests/` (the test suite is untouched; you edit no test files)
- `app/db/alembic/`, `app/db/alembic.ini`, `app/db/requirements.txt`, `app/db/requirements-test.txt` (consumed by the targets via COPY; not modified)
- The `api` and `api-test` service blocks in `app/docker-compose.yml` (API-T-008 territory, already on `target:`; do not touch)
- Everything under `app/api/` (API-T-008's already-shipped restructure)

## References

- `ai-infrastructure/project-manager/decisions/ADR-043-dockerfile-structure-convention.md` (the accepted convention; Decision point 4 is the db three-target split, point 5 is the alembic-exclusion preservation, and Consequences covers the uneven-win nuance)
- `ai-infrastructure/project-manager/decisions/ADR-014-db-migrations-tooling.md` (alembic tooling context; the db build context is `./db`)
- `ai-infrastructure/project-manager/decisions/ADR-003-docker-compose-runtime.md` (docker compose is the only supported run path, hence the compose build/run acceptance gates)
- `ai-infrastructure/project-manager/tasks/done/COR-T-054-dockerignore-per-build-context.md` (the already-shipped `.dockerignore` slice this builds on; source of the ~130-test characterization run reference)
- `app/db/Dockerfile` (the current runtime/migrate image with `COPY . .`; collapse into the `runtime` target)
- `app/db/Dockerfile.test` (the current characterization-test image; carries the alembic-split comment at lines 8-10 to preserve on the new `test` target; delete after folding)
- `app/db/Dockerfile.test-roundtrip` (the current migration-round-trip image; fold into the `test-roundtrip` target; delete after folding)
- `app/db/.dockerignore` (the per-context ignore file; drop the two stale `Dockerfile.test*` entries)
- `app/docker-compose.yml` (the `migrate` + `test` + `test-roundtrip` blocks to switch to `target:`; the `api`/`api-test` blocks are the already-shipped reference shape, not to be edited)

## Related tasks and ADRs

- ADR-043 - the accepted Dockerfile-structure convention this task implements (db half; Decision point 4 is the db three-target split).
- API-T-008 - the sibling api restructure (already in `done/`); shares `app/docker-compose.yml` but a disjoint set of blocks; the run-order constraint (api first) is already satisfied.
- COR-T-054 - shipped `app/db/.dockerignore`; this task only drops two now-stale entries from it and is the source of the ~130-test characterization run reference.
- ADR-014 - db migrations tooling (alembic); context for the `runtime`/`migrate` target.
- ADR-003 - docker-compose-runtime; the only supported run path, which is why the acceptance gate uses compose build/run commands.

## Hard rules

- **Co-commit the compose edits with the Dockerfile conversion.** A `build.target:` only resolves once the matching Dockerfile is multi-stage. Do not split the `app/docker-compose.yml` db-block edits and the `app/db/Dockerfile` conversion across separate commits; they are one logical change.
- **Do not touch the `api`/`api-test` compose blocks or anything under `app/api/`.** That is API-T-008's already-shipped territory. Your compose edits are confined to the `migrate`, `test`, and `test-roundtrip` blocks.
- **Do not hoist `requirements.txt` into `base` and do not collapse the two test targets.** The uneven deps/copy split across the three targets is intended per ADR-043; preserve it exactly as deliverable 1 specifies.
- **Escalation (docker daemon unavailable).** If `docker compose` / the docker daemon is unavailable in your environment, do NOT claim build success. Complete the file edits that do not need the daemon (acceptance items (a) and (f)), then return `RETURN: ESCALATION` reporting that gates (b) through (e) could not run, and ask whether to accept on static grounds or defer. Per COR-09, an honest "could not verify" beats a fabricated green; a green-test one-shot is not a runtime gate.

## Executor pointer

The executor is the dispatched `executor` (ADR-028). Universal executor conventions (the verify-before-asserting discipline and writing rules in `./CLAUDE.md`, the docker-compose-only run policy, git boundaries, the no-touch rule, and the pinned six-section report shape) live in `docs/ai-orchestration/roles/EXECUTOR-ROLE.md`; reference them rather than re-deriving them. Write the closing report to the dual-channel path derived in EXECUTOR-ROLE.md, section "Report shape" (`<kickoff-dir>/<KICKOFF-BASENAME>-REPORT.md`).
