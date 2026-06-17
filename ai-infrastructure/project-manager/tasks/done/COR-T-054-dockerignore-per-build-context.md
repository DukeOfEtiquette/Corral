---
schema_version: 1
id: COR-T-054
title: "Add a .dockerignore per build context (api, db) and switch api to selective COPY (ADR-006 hygiene)"
status: done
labels: []
priority: P2
created: 2026-06-16
updated: 2026-06-16
---

## Description

Filed into the coordinator tree (cross-workspace, mirroring the COR-T-053 precedent): this is a security/convention-driven hygiene item that crosses the backend-api and database build contexts, so it lives here as a `COR-T` task rather than in a single department tree. Surfaced by the Backend API Orchestrator on 2026-06-16 while reviewing the five web-app Dockerfiles.

**The gap (verified on disk 2026-06-16).** There is no `.dockerignore` anywhere in the repo (`find . -name .dockerignore` returns nothing). The api images do `COPY . ./app/api/`, raking the entire `./api` build context (tests, `gen-admin-hash.sh`, `.env.example`) into the runtime image. The live secret at `app/.env` is *outside* the `./api` context, so nothing leaks today, but a future `app/api/.env` would be baked into an image layer with no guard. That is an ADR-006 (admin-bootstrap-env-hash; secrets never in tracked/built artifacts) concern, which is why this is justified and shippable *now* on ADR-006 alone, independent of the still-pending ADR-043.

**Goal.** Add a `.dockerignore` to each build context (`app/api/`, `app/db/`) excluding at least `.env`, `__pycache__/`, `*.sh` (where not needed in the image), and `tests/`/`.env.example` where not needed by that image's `CMD`. Switch `app/api/Dockerfile` (runtime) to selective `COPY`, matching the better-disciplined db pattern (`app/db/Dockerfile.test` already copies `tests/` selectively and documents why).

**Preserve.** Do NOT collapse the db `Dockerfile.test` vs `Dockerfile.test-roundtrip` split: `Dockerfile.test` deliberately excludes `alembic/` (tests assert against the live DB) while `test-roundtrip` includes it (migration round-trip). That semantic boundary is about *what* is copied and must survive.

**Scope boundary.** This task is the `.dockerignore` + selective-COPY slice only (Option C in ADR-043). It does NOT do the multi-stage build-target restructure (the duplication smell); that is the broader question deferred to ADR-043 and, once accepted, to department-owned restructure tasks. Keep this task small.

**Acceptance test.** After the change: (a) a `.dockerignore` exists in both `app/api/` and `app/db/`; (b) `.env` and `.env.example` are excluded from the runtime image; (c) the api runtime image no longer carries `gen-admin-hash.sh` or `tests/`; (d) the db `test` vs `test-roundtrip` `alembic/` boundary is unchanged; (e) `docker compose build` succeeds for all services and the existing test images still run their suites green.

Routes through the dispatched-worker flow when picked up (a domain-1 web-app deliverable: an executor edits files under `app/`). Standalone task (no epic). Unlabelled per ADR-031; the `dept:*` label is applied from the tree at dogfood import.

References:
- `ai-infrastructure/project-manager/decisions/ADR-006-admin-bootstrap-env-hash.md` (the binding secrets rule this task enforces; the standing justification)
- `ai-infrastructure/project-manager/decisions/ADR-043-dockerfile-structure-convention.md` (pending; the broader convention this task is the Option-C slice of)
- `ai-infrastructure/project-manager/decisions/ADR-003-docker-compose-runtime.md` (compose is the runtime; build contexts are `./api` and `./db`)
- `app/api/Dockerfile`, `app/api/Dockerfile.test` (the `COPY .` raking; need `.dockerignore` + selective COPY)
- `app/db/Dockerfile.test` (the better selective-COPY pattern to match; carries the `alembic/`-exclusion comment to preserve)
- `app/docker-compose.yml` (build contexts/targets)

## Activity log

- 2026-06-16: Created in backlog by the Project Manager Orchestrator (cross-workspace into the coordinator tree, at user direction). Surfaced by the Backend API Orchestrator during a five-Dockerfile review; routed up because it crosses the api and db contexts. Filed P2 (security-adjacent ADR-006 hygiene, latent not active) and standalone. Scoped to the `.dockerignore` + selective-COPY slice only; the multi-stage restructure is deferred to pending ADR-043.
- 2026-06-16: Moved to in-progress by the Project Manager Orchestrator on kickoff authoring (kickoff = active-work signal). Running the drafter+checker loop for `.claude/artifacts/handoffs/COR-T-054-KICKOFF.md`.
- 2026-06-17: Executed via the dispatched-worker flow. Kickoff drafter+checker PASS (iter 1); prelaunch W1 PASS; executor (Sonnet) RETURN COMPLETED with the docker acceptance gate actually run (`docker compose build` all services green; api runtime image confirmed to drop `tests/`/`gen-admin-hash.sh`/`.env.example` with imports resolving; suites green: api 22, db 130, roundtrip 1); close-check W2 PASS (W3 inert). Orchestrator re-derived every report claim against disk. Deliverables: `app/api/.dockerignore`, `app/db/.dockerignore` (exact pinned lists), `app/api/Dockerfile` line 9 `COPY . ./app/api/` -> `COPY *.py ./app/api/`. Report: `.claude/artifacts/handoffs/COR-T-054-KICKOFF-REPORT.md`. Resolved and moved to done.
