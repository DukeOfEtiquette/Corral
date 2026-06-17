# COR-T-054: Add a .dockerignore per build context (api, db) and switch api to selective COPY (ADR-006 hygiene)

## Target

This is web-app (domain-1, ADR-005) build-configuration work. The task is COR-T-054, a security/convention hygiene item that crosses the backend-api and database Docker build contexts. The artifacts in scope are the two Docker build contexts under `app/`: the api context (`app/api/`, the build context `./api` for both the runtime `Dockerfile` and `Dockerfile.test`) and the db context (`app/db/`, the build context `./db` for `Dockerfile`, `Dockerfile.test`, and `Dockerfile.test-roundtrip`). You add one `.dockerignore` per context and make the api runtime `Dockerfile`'s `COPY` selective. This is the narrow Option-C slice of ADR-043 only; you do not do the multi-stage build-target restructure.

## Decisions resolved by the Orchestrator

- **Scope is the `.dockerignore` + selective-COPY slice only.** Add `app/api/.dockerignore`, add `app/db/.dockerignore`, and switch the api runtime `Dockerfile` to a selective `COPY`. The multi-stage build-target restructure (collapsing each `Dockerfile` / `Dockerfile.test` pair into one file with runtime and test targets) is explicitly OUT OF SCOPE; it stays with pending `ai-infrastructure/project-manager/decisions/ADR-043-dockerfile-structure-convention.md`. Rationale: this slice ships now on ADR-006 (secrets-hygiene) grounds alone, independent of ADR-043; keep the change small.

- **`.dockerignore` is per BUILD CONTEXT, not per Dockerfile.** A `.dockerignore` applies to EVERY build that uses its context. The api context `./api` is shared by the runtime `Dockerfile` and `Dockerfile.test`; the db context `./db` is shared by `Dockerfile`, `Dockerfile.test`, and `Dockerfile.test-roundtrip`. Therefore a `.dockerignore` may exclude ONLY files that NO build in that context needs. Rationale: this is the central landmine of the task; an over-broad `.dockerignore` silently breaks a sibling image.

- **The api `.dockerignore` must NOT exclude `tests/`.** Runtime-only exclusion of `tests/` is achieved by the selective `COPY` in `app/api/Dockerfile`, NOT by the `.dockerignore`, because `Dockerfile.test` (same context) needs `tests/`. Rationale: `.dockerignore` cannot distinguish runtime from test builds in the same context.

- **The db `.dockerignore` must NOT exclude `tests/`, `alembic/`, `alembic.ini`, or `requirements*.txt`.** The db test images need `tests/`; `Dockerfile.test-roundtrip` needs `alembic/` and `alembic.ini`; all builds need `requirements*.txt`. Rationale: same shared-context constraint; excluding any of these breaks a db build.

- **`app/api/.dockerignore` excludes exactly these entries:** `.env`, `.env.example`, `__pycache__/`, `*.pyc`, `.pytest_cache/`, `gen-admin-hash.sh`, `Dockerfile`, `Dockerfile.test`. Rationale: `.env` exclusion is preventive (no `.env` is in the `./api` context today; `app/.env` is outside it), `gen-admin-hash.sh` is a dev/admin helper that no Dockerfile copies or runs, and the Dockerfiles themselves never need to be inside the build.

- **`app/db/.dockerignore` excludes exactly these entries:** `.env`, `.env.example`, `__pycache__/`, `*.pyc`, `.pytest_cache/`, `Dockerfile`, `Dockerfile.test`, `Dockerfile.test-roundtrip`. Rationale: the same preventive/hygiene set, minus `gen-admin-hash.sh` (which is an api-context file). It deliberately does NOT list `tests/`, `alembic/`, `alembic.ini`, or `requirements*.txt`.

- **The api runtime `COPY` becomes `COPY *.py ./app/api/`.** In `app/api/Dockerfile`, replace the current `COPY . ./app/api/` (line 9) with `COPY *.py ./app/api/`. This copies the runtime Python source (`admin_seed.py`, `auth.py`, `db.py`, `main.py`, `settings.py`, `__init__.py`) and excludes `tests/`, `gen-admin-hash.sh`, `.env.example`, `requirements-test.txt`, and the Dockerfiles. Rationale: selective COPY is how the runtime image drops `tests/` while the shared `.dockerignore` keeps `tests/` available to `Dockerfile.test`.

- **Leave the rest of `app/api/Dockerfile` unchanged.** `WORKDIR /app`, the `COPY requirements.txt .` line, the `RUN pip install` line, `ENV PYTHONPATH=/app`, and the `CMD ["uvicorn", "app.api.main:app", ...]` stay exactly as they are. The import path `app.api.main` must still resolve. Rationale: the change is the one COPY line only.

- **Preserve the db `Dockerfile.test` vs `Dockerfile.test-roundtrip` semantic split.** `Dockerfile.test` deliberately excludes `alembic/` (its tests assert against the live DB); `Dockerfile.test-roundtrip` includes `alembic/` (migration round-trip). The `.dockerignore` must leave both files copyable; do not collapse or alter that boundary. Rationale: the split is about what each image copies, and it must survive untouched.

## Deliverables

1. `app/api/.dockerignore` (new file) containing exactly the api exclusion set above: `.env`, `.env.example`, `__pycache__/`, `*.pyc`, `.pytest_cache/`, `gen-admin-hash.sh`, `Dockerfile`, `Dockerfile.test`.
2. `app/db/.dockerignore` (new file) containing exactly the db exclusion set above: `.env`, `.env.example`, `__pycache__/`, `*.pyc`, `.pytest_cache/`, `Dockerfile`, `Dockerfile.test`, `Dockerfile.test-roundtrip`.
3. `app/api/Dockerfile` edited so line 9's `COPY . ./app/api/` becomes `COPY *.py ./app/api/`, with everything else in the file unchanged.

## Files in scope

- `app/api/.dockerignore` (create)
- `app/db/.dockerignore` (create)
- `app/api/Dockerfile` (edit the single `COPY` line only)

## Files out of scope

- `app/api/Dockerfile.test` (read-only: confirm it still receives `tests/` from the shared `./api` context after the `.dockerignore` lands; do not edit)
- `app/db/Dockerfile` (read-only: confirm the db `.dockerignore` does not break it; do not edit)
- `app/db/Dockerfile.test` (read-only: confirm the `alembic/` boundary is unchanged; do not edit)
- `app/db/Dockerfile.test-roundtrip` (read-only: confirm it still receives `alembic/` and `alembic.ini`; do not edit)
- `app/docker-compose.yml` (read-only: the service/build-context definitions; do not edit)
- Any test file under `app/api/tests/` or `app/db/tests/` (this task changes build config only, never test code)

## References

- `ai-infrastructure/project-manager/tasks/in-progress/COR-T-054-dockerignore-per-build-context.md` (the task: the gap, the goal, the preserve constraint, the scope boundary)
- `ai-infrastructure/project-manager/decisions/ADR-006-admin-bootstrap-env-hash.md` (the binding secrets rule this task enforces: deployment credentials live in gitignored `.env` files only; never build them into an image layer)
- `ai-infrastructure/project-manager/decisions/ADR-003-docker-compose-runtime.md` (compose is the runtime; the build contexts are `./api` and `./db`; verification runs through `docker compose`)
- `app/docker-compose.yml` (the service / build-context / dockerfile mapping; the source of the exact service names used in the acceptance commands below: `api`, `api-test`, `migrate`, `test`, `test-roundtrip`, `postgres`)
- `app/api/Dockerfile` (the runtime `COPY . ./app/api/` on line 9 to make selective)
- `app/api/Dockerfile.test` (read-only: confirm it still gets `tests/` from the context)
- `app/db/Dockerfile` (read-only: confirm the `.dockerignore` does not break the db runtime build)
- `app/db/Dockerfile.test` (read-only: carries the `alembic/`-exclusion comment; preserve the split)
- `app/db/Dockerfile.test-roundtrip` (read-only: includes `alembic/`; confirm it stays copyable)
- `ai-infrastructure/project-manager/decisions/ADR-043-dockerfile-structure-convention.md` (pending; the broader convention this task is the Option-C slice of; the multi-stage restructure anchors here, OUT OF SCOPE)

## Related tasks and ADRs

- COR-T-054 (this task): the `.dockerignore` + selective-COPY hygiene slice.
- ADR-006 (admin-bootstrap-env-hash): the binding secrets rule; the standing justification that makes this slice shippable now, independent of ADR-043.
- ADR-043 (dockerfile-structure-convention, pending): the broader Dockerfile-structure question; this task is its Option-C slice, and the multi-stage build-target restructure is deferred to it.
- ADR-003 (docker-compose-runtime): compose is the runtime; defines the `./api` and `./db` build contexts and the compose-only verification path.

## Hard rules

- **The `.dockerignore` exclusion lists are exact.** Do not add, drop, or reorder entries beyond the two sets pinned in "Decisions resolved" above. In particular, do NOT add `tests/`, `alembic/`, `alembic.ini`, or `requirements*.txt` to either file.
- **Edit only the one `COPY` line in `app/api/Dockerfile`.** Do not touch `WORKDIR`, the `requirements.txt` COPY, the `pip install` RUN, `ENV PYTHONPATH`, or the `CMD`.
- **Do not edit any other Dockerfile.** The db Dockerfiles and `app/api/Dockerfile.test` are read-only context reads to confirm the `.dockerignore` does not break them.
- **Do not edit any test file** under `app/api/tests/` or `app/db/tests/`, and do not edit `app/docker-compose.yml`.
- **Run policy is docker compose only** (ADR-003). Run the acceptance commands below; do not assume host-installed Python or run pytest on the host.

## Acceptance gate

All of the following hold (this is the single acceptance gate; report each in "Build / verification status"):

a. `app/api/.dockerignore` and `app/db/.dockerignore` both exist with the exact exclusion lists pinned above, and `app/api/Dockerfile` line 9 now reads `COPY *.py ./app/api/`.

b. `cd app && docker compose build` succeeds for all services.

c. The api runtime image does NOT contain `tests/`, `gen-admin-hash.sh`, or `.env.example` under `/app/app/api/`, while `main.py` and the other `.py` modules ARE present and the import resolves. Verify with something equivalent to `cd app && docker compose run --rm --entrypoint sh api -c 'ls -R /app/app/api'` and `cd app && docker compose run --rm --entrypoint python api -c 'import app.api.main'`.

d. The api test image still collects and runs its suite: `cd app && docker compose run --rm api-test` executes the tests (the suite must COLLECT and RUN, proving `tests/` is present in that image; individual tests need not all pass for reasons unrelated to this change).

e. The db `test` and `test-roundtrip` images still build and run with the `alembic/` boundary unchanged: `cd app && docker compose run --rm test` and `cd app && docker compose run --rm test-roundtrip`.

**Escalation path if docker is unavailable.** If the docker daemon or `docker compose` is not available in the execution environment, do NOT claim build success. Return `RETURN: ESCALATION` reporting that the three file edits (deliverables 1-3) are complete and statically correct but that the docker-level acceptance tests (b through e) could not be executed, and ask the Orchestrator whether to accept on static grounds or defer verification. Per COR-09, a green-test one-shot is not a runtime gate; an honest "could not verify" beats a fabricated green.

## Follow-ups anchoring

In your closing report's "Follow-ups" section, record this anchoring (and file no new tasks yourself): the multi-stage build-target restructure (collapsing each `Dockerfile` / `Dockerfile.test` pair into one file with runtime and test targets) is OUT OF SCOPE for COR-T-054 and is anchored to pending `ai-infrastructure/project-manager/decisions/ADR-043-dockerfile-structure-convention.md`. Once ADR-043 is accepted it becomes department-owned restructure tasks (API-T / DB-T). Tag it as a "triage to orchestrator" follow-up.

## Executor pointer

The executor is the dispatched `executor` (ADR-028). Universal executor conventions (the six-section report shape, the dual-channel write, the compose-only run policy, git boundaries, the writing rules, and Agent Discipline) live in `docs/ai-orchestration/roles/EXECUTOR-ROLE.md` and are not restated here. The task file in `ai-infrastructure/project-manager/tasks/` is already in `in-progress/` and is a read-only reference; you do not move, edit, or create task files. The closing report is written to `./.claude/artifacts/handoffs/COR-T-054-KICKOFF-REPORT.md` per EXECUTOR-ROLE.md, section "Report shape".
