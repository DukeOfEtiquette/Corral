# Restructure app/api to one multi-stage Dockerfile with runtime + test targets (ADR-043)

## Target

This is web-app work (domain-1 per ADR-005): build configuration for the FastAPI `api` service under `app/api/`. You collapse the two separate api Dockerfiles (`Dockerfile` runtime + `Dockerfile.test`) into one multi-stage `Dockerfile` with named build targets (`base`, `runtime`, `test`), switch compose to select targets via `build.target`, prune the now-stale `.dockerignore` entry, and delete the old test Dockerfile. The binding convention is `./ai-infrastructure/project-manager/decisions/ADR-043-dockerfile-structure-convention.md`; its Decision section is authoritative. This is the `./api` half of ADR-043's Option B restructure; the `./db` half (DB-T-004) is a separate task that edits disjoint files.

This is NOT a TDD surface. There is no test-design phase. Do not create or edit any file under `app/api/tests/`.

## Decisions resolved by the Orchestrator

- **ADR-043 Option B is the binding convention.** One multi-stage Dockerfile per build context with named build targets, selected from compose via `build.target` (a 1:1 replacement for `build.dockerfile`), plus a mandatory per-context `.dockerignore`. This task implements the `./api` half only. Source: ADR-043 Decision, items 1-3.
- **On-disk state was verified by the Orchestrator on 2026-06-22 and matches this kickoff exactly (no drift).** The current `app/api/Dockerfile` is single-stage runtime (`FROM python:3.12-slim`, `WORKDIR /app`, `COPY requirements.txt .`, `RUN pip install`, `COPY *.py ./app/api/`, `ENV PYTHONPATH=/app`, `CMD uvicorn ... --port 8123`). The current `app/api/Dockerfile.test` installs `requirements.txt` + `requirements-test.txt`, does `COPY . ./app/api/`, and `CMD ["pytest", "-v", "app/api/tests/"]`. Apply the pinned target content below as written; do not re-derive it from the current files.
- **The final `app/api/Dockerfile` content is PINNED to exactly this.** Write this verbatim:

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

- **Selective COPY is PINNED and verified complete for the test target.** The `./api` context's test-needed files are exactly the top-level `*.py` (`admin_seed.py`, `auth.py`, `db.py`, `__init__.py`, `main.py`, `settings.py`) plus the `tests/` directory (`conftest.py`, `test_healthz.py`, `test_sessions.py`, `test_auth_login.py`, `test_admin_seed.py`). There is no `pytest.ini`, `pyproject.toml`, `setup.cfg`, or data file in the context that the suite needs. So `COPY *.py ./app/api/` plus `COPY tests/ ./app/api/tests/` is sufficient. Do NOT fall back to `COPY .`. Rationale: ADR-043 Decision item 3 (selective COPY per target, never `COPY .`).
- **Compose edits are PINNED to exactly two blocks in `app/docker-compose.yml`.**
  - The `api` service block: its `build:` currently has only `context: ./api`. Add `target: runtime` under `build:`, keeping `context: ./api`. Do NOT modify its `ports`, `environment`, `healthcheck`, or `depends_on`.
  - The `api-test` service block: its `build:` currently has `context: ./api` and `dockerfile: Dockerfile.test`. Replace the `dockerfile: Dockerfile.test` line with `target: test`, keeping `context: ./api`.
- **Do NOT touch any other service block in `app/docker-compose.yml`.** The `postgres`, `migrate`, `test`, and `test-roundtrip` blocks are owned by DB-T-004. The two tasks share this file but edit disjoint blocks and run sequentially, so there is no collision as long as you touch only `api` and `api-test`.
- **The `app/api/.dockerignore` edit is PINNED.** Remove the line `Dockerfile.test` (that file is being deleted). Keep the `Dockerfile` line. Leave every other entry exactly as-is: `.env`, `.env.example`, `__pycache__/`, `*.pyc`, `.pytest_cache/`, `gen-admin-hash.sh`.
- **Delete `app/api/Dockerfile.test`** (folded into the `test` target).
- **`.dockerignore` is per-context, not per-Dockerfile.** Keeping `tests/` out of the runtime image is the job of the runtime target's selective `COPY *.py`, NOT of `.dockerignore`. The `.dockerignore` must not exclude `tests/` or `requirements-test.txt`, because the `test` target consumes them. Source: ADR-043 Decision item 2.
- **Preserve the `app.api.*` import layout.** Both targets place the package at `/app/app/api/` with `PYTHONPATH=/app` so `import app.api.main` resolves. Keep the uvicorn `--port 8123` (set by API-T-007); do not change it.
- **Docker is available; run the full acceptance gate.** The Orchestrator verified the Docker daemon is reachable on 2026-06-22 (Docker 29.4.3, Compose v5.1.3, `docker info` succeeds). Run all of the acceptance checks (a)-(e) under "Build / verification status". The "if docker is unavailable, escalate on static grounds" fallback does NOT apply here; do not take it.

## Deliverables

1. Replace `app/api/Dockerfile` with the pinned multi-stage content above (the `base`, `runtime`, and `test` targets).
2. Delete `app/api/Dockerfile.test`.
3. Edit `app/docker-compose.yml`: add `build.target: runtime` to the `api` block; in the `api-test` block, replace `build.dockerfile: Dockerfile.test` with `build.target: test`. Edit only these two blocks.
4. Edit `app/api/.dockerignore`: remove the `Dockerfile.test` entry; keep `Dockerfile` excluded; leave all other entries unchanged.

## Files in scope

- `app/api/Dockerfile` (rewrite to the pinned multi-stage content)
- `app/api/Dockerfile.test` (delete)
- `app/api/.dockerignore` (remove the `Dockerfile.test` line only)
- `app/docker-compose.yml` (edit the `api` and `api-test` blocks only)

## Files out of scope

- `app/api/tests/` and everything under it (not a TDD surface; no test edits).
- `app/api/*.py` source files (`admin_seed.py`, `auth.py`, `db.py`, `__init__.py`, `main.py`, `settings.py`): no source changes.
- `app/api/requirements.txt`, `app/api/requirements-test.txt`, `app/api/.env.example`, `app/api/gen-admin-hash.sh`: unchanged.
- `app/db/` (all db Dockerfiles: `Dockerfile`, `Dockerfile.test`, `Dockerfile.test-roundtrip`, and `app/db/.dockerignore`): owned by DB-T-004.
- The `postgres`, `migrate`, `test`, and `test-roundtrip` service blocks in `app/docker-compose.yml`: owned by DB-T-004.

## References

- `./ai-infrastructure/project-manager/decisions/ADR-043-dockerfile-structure-convention.md` (the accepted convention; the Decision section is binding, especially items 1-3 on multi-stage targets, context-scoped `.dockerignore`, and selective COPY).
- `./ai-infrastructure/project-manager/decisions/ADR-006-admin-bootstrap-env-hash.md` (secrets-never-in-images; grounds why the `.dockerignore` keeps `.env`, `.env.example`, and `gen-admin-hash.sh` out of build context).
- `./ai-infrastructure/project-manager/decisions/ADR-003-docker-compose-runtime.md` (docker compose is the runtime; the api build context is `./api`).
- `./ai-infrastructure/project-manager/tasks/done/COR-T-054-dockerignore-per-build-context.md` (the already-shipped `.dockerignore` plus selective-runtime-COPY slice this task builds on).
- `app/api/Dockerfile` (the runtime file to rewrite to multi-stage).
- `app/api/Dockerfile.test` (the test file to delete after folding into the `test` target).
- `app/api/.dockerignore` (the file to prune the `Dockerfile.test` entry from).
- `app/docker-compose.yml` (the `api` and `api-test` blocks to switch to `target:`).

## Related tasks and ADRs

- ADR-043: the binding convention for this task; its Decision section is authoritative.
- ADR-006: secrets-never-in-images; why the `.dockerignore` keeps `.env`, `.env.example`, and `gen-admin-hash.sh` out.
- ADR-003: docker compose is the runtime; the api build context is `./api`.
- COR-T-054: shipped `app/api/.dockerignore` plus the selective runtime `COPY *.py`; this task does the remaining multi-stage collapse.
- DB-T-004: the sibling db restructure; shares `app/docker-compose.yml` but edits disjoint blocks; run sequentially.
- API-T-007: moved the api service to port 8123; the uvicorn `CMD` must keep `--port 8123`.

## Hard rules

- Write the `app/api/Dockerfile` content exactly as pinned above. Do not reorder stages, rename targets, or add layers.
- Do not use `COPY .` in any target. Use the pinned selective `COPY` lines.
- Touch only the `api` and `api-test` blocks in `app/docker-compose.yml`. Leave `postgres`, `migrate`, `test`, and `test-roundtrip` byte-for-byte unchanged (DB-T-004 owns them; this task and DB-T-004 run sequentially).
- In `app/api/.dockerignore`, remove only the `Dockerfile.test` line. Do not remove or reorder any other entry; in particular, keep `tests/` and `requirements-test.txt` out of `.dockerignore` (the `test` target consumes them).
- Keep `--port 8123` in the runtime `CMD` (API-T-007).

## Build / verification status

Docker is available (verified by the Orchestrator on 2026-06-22), so run the full acceptance gate. All of the following must hold:

- (a) `app/api/Dockerfile` is a single multi-stage file with `base`, `runtime`, and `test` stages, and `app/api/Dockerfile.test` no longer exists.
- (b) `cd app && docker compose build` succeeds for all services.
- (c) The api runtime image (the `api` service) contains the `.py` source under `/app/app/api/` and `python -c "import app.api.main"` resolves, and does NOT contain `tests/`, `gen-admin-hash.sh`, or `.env.example`.
- (d) `cd app && docker compose run --rm api-test` collects and runs the suite. (The COR-T-054 run had 22 tests; they need not all pass for unrelated reasons, but the suite must collect and run, proving `tests/` is present in the test image.)
- (e) `app/api/.dockerignore` no longer lists `Dockerfile.test`.

Run policy is docker compose only (ADR-003). Report what was verified and what was not in the closing report's "Build / verification status" section, with the command output that proves each check.

## Executor pointer

The executor is the dispatched `executor` (ADR-028). Universal executor conventions (the writing rules and Agent Discipline in `./CLAUDE.md`, the compose-only run policy, git boundaries, the file-edit hygiene rules, and the pinned six-section report shape) live in `./docs/ai-orchestration/roles/EXECUTOR-ROLE.md`; follow them rather than re-deriving them here. Write the closing report to `./.claude/artifacts/handoffs/API-T-008-KICKOFF-REPORT.md` per EXECUTOR-ROLE.md, section "Report shape".
