---
schema_version: 1
adr: 43
title: "Dockerfile structure convention: multi-stage build targets and mandatory per-context .dockerignore"
status: "accepted"
date: "2026-06-22"
related_adrs: [3, 6, 15]
supersedes: []
superseded_by: null
---

# ADR-043: Dockerfile structure convention: multi-stage build targets and mandatory per-context .dockerignore

> Accepted 2026-06-22 (filed pending 2026-06-16). Adopts Option B: one multi-stage Dockerfile per build context with named build targets, plus a mandatory per-context `.dockerignore`. The `.dockerignore`/selective-COPY slice (Option C) already shipped under COR-T-054 on ADR-006 grounds; the remaining multi-stage restructure is department-owned (API-T / DB-T). The Alternatives below keep their deliberation-time leanings as a record; the Decision and Consequences sections are authoritative.

## Context

The web-app build contexts now carry five Dockerfiles across two departments, verified on disk 2026-06-16:

- `app/api/Dockerfile` (runtime: `CMD uvicorn`) and `app/api/Dockerfile.test` (`CMD pytest`)
- `app/db/Dockerfile`, `app/db/Dockerfile.test` (`CMD pytest`, ignores the roundtrip test), and `app/db/Dockerfile.test-roundtrip` (`CMD pytest` the roundtrip test only)

Compose selects them by `build.context` (`./api`, `./db`) plus `build.dockerfile`. A "dedicated test image per context" principle is therefore already in place. The open question is whether the *way* the contexts are separated is clean. Surfaced by the Backend API Orchestrator on 2026-06-16 while reviewing the five Dockerfiles; routed to the coordinator because it crosses both the backend-api and database departments and is a convention, not a one-off, so it relates to ADR-003 (docker-compose is the runtime) rather than belonging to a backend-api-local ADR.

Three structural smells, all verified on disk:

1. **Duplication, not separation.** `app/api/Dockerfile` and `app/api/Dockerfile.test` share `FROM`, `WORKDIR`, `COPY`, and `PYTHONPATH` and differ only in `requirements-test.txt` and `CMD`. That is copy-paste drift waiting to happen across one file pair per context.
2. **No `.dockerignore` anywhere** (`find . -name .dockerignore` returns nothing). The api images do `COPY . ./app/api/`, raking the entire build context (tests, `gen-admin-hash.sh`, `.env.example`) into the runtime image: bloat and surface. Latent secret risk: the live secret is at `app/.env`, which is *outside* the `./api` build context (so nothing leaks today, verified), but a future `app/api/.env` would be baked into an image layer with no `.dockerignore` guarding it: an ADR-006 concern.
3. **Inconsistent copy discipline between departments.** `app/db/Dockerfile.test` copies selectively (`COPY tests/`) and documents why; the api Dockerfiles copy everything. The db pattern is the better one.

One existing split is deliberate and worth preserving: `app/db/Dockerfile.test` excludes `alembic/` so schema-characterization tests assert against the live DB, while `Dockerfile.test-roundtrip` includes `alembic/` for the migration round-trip. That is a real "what is copied" semantic boundary, well-commented; it must survive any restructure (it is about *what* is copied, not *how many files*).

## Alternatives considered

### Option A: Status quo (separate Dockerfile + Dockerfile.test per context, `COPY .`, no `.dockerignore`)

Keep the current layout untouched.

**Against (leaning):** preserves all three smells above. Every new context adds another drift-prone file pair; no guard against future `.env` bake-in.

### Option B: Multi-stage Dockerfile per context with build targets + mandatory per-context `.dockerignore` (SELECTED)

One Dockerfile per context with a shared `base` stage and `runtime` / `test` targets, selected from compose via `build: { target: ... }`. One file per context, shared cached layers, zero deps/CMD drift. Plus a mandatory `.dockerignore` per build context (`./api`, `./db`) excluding `.env`, `__pycache__`, `*.sh`, and `tests/` where not needed. Selective `COPY` to match the db pattern. The db test vs test-roundtrip semantic split is preserved as two test targets (or one target plus a build-arg) so the `alembic/` boundary survives.

**For (leaning):** directly answers "one image, several processes" with targets instead of duplicated files; eliminates the drift surface; the `.dockerignore` closes the bloat and the latent ADR-006 gap. **Trade-off:** multi-stage Dockerfiles are slightly less obvious to a reader than two named files; the db two-test-target shape needs care to keep the semantic boundary legible.

### Option C: `.dockerignore` + selective-COPY hygiene only (no multi-stage)

Add the per-context `.dockerignore` and switch api to selective `COPY`, but keep separate `Dockerfile` / `Dockerfile.test` files.

**For:** captures the security/bloat win (the ADR-006-adjacent part) with the least churn and no restructure. **Against:** leaves the duplication smell (1) unaddressed. This is effectively the COR-T-054 slice on its own; it is a strict subset of Option B and can ship first regardless of how this ADR resolves.

## Decision

Adopt **Option B** as the repo-wide convention for every web-app build context.

1. **One multi-stage Dockerfile per build context.** Each context (`./api`, `./db`, and any future context) has a single Dockerfile with a shared `base` stage and named build targets. Compose selects a target via `build.target`, replacing today's `build.dockerfile` selection 1:1. The separate `Dockerfile.test` / `Dockerfile.test-roundtrip` files are collapsed into targets of the one file.

2. **Mandatory `.dockerignore` per build context.** Every context has a `.dockerignore`. It is scoped to the context, not the Dockerfile: it may exclude only paths that no target in that context needs. It must never exclude paths a sibling target consumes (`tests/`, `alembic/`, `alembic.ini`, `requirements*.txt`). Per-target exclusion (for example keeping `tests/` out of the runtime image) is the job of selective `COPY` inside that target, not of `.dockerignore`. These files already exist for `./api` and `./db` from COR-T-054; the convention now mandates one for every context.

3. **Selective `COPY` per target.** Each target copies only what it needs, following the `app/db/Dockerfile.test` pattern rather than `COPY .`.

4. **The db test split is expressed as two distinct targets, not a build-arg.** `test` (characterization) and `test-roundtrip` (migration) branch from the shared `base` as two separate targets. This is chosen over a single `test` target plus a build-arg because the boundary is two-axis: the two images differ in both installed deps (`requirements-test.txt` only, versus `requirements.txt` + `requirements-test.txt`) and copied files (no `alembic/`, versus `alembic.ini` + `alembic/`). Keeping them as two targets keeps that boundary a visible `COPY`/`RUN` diff between stages, which is the "what is copied" criterion this ADR set out to preserve. A build-arg cannot do a conditional `COPY` and would force the boundary into an entrypoint script, the opposite of legible; it also expresses "how configured" rather than "what is copied".

5. **The deliberate db `alembic/` exclusion survives** as the COPY-diff between the `test` and `test-roundtrip` targets, with its existing comment carried over. It is preserved, not tidied away.

6. **Execution is department-owned.** The convention is coordinator-owned (this ADR); the restructure of `app/api/` and `app/db/` Dockerfiles is domain-1 web-app work, filed and run as department tasks (an API-T task for `./api`, a DB-T task for `./db`) by those department orchestrators, not coordinator-direct.

The `.dockerignore` + selective-COPY hygiene slice (Option C) is already in force from COR-T-054 and is subsumed by B; the outstanding work under this decision is the multi-stage restructure only.

## Consequences

- Compose moves from `dockerfile:` selection to `target:` selection, a 1:1 mapping with minimal churn; each existing service keeps its name and points at a target.
- **The api context gains the most.** Its runtime and test images differ only by test deps and `CMD`, so multi-stage kills the duplication and shares cached layers across both.
- **The db context gains "one file plus a legible, preserved boundary," but little layer reuse.** Its two test targets deliberately differ on deps and copied files, so they branch off `base` early. The restructure must preserve the exact dep/copy split and must not collapse the two test stages into one. This uneven win is expected, not a defect.
- The per-context `.dockerignore` files from COR-T-054 stay and are now convention-mandated; any future build context must add one at creation.
- **Downside accepted:** a multi-stage Dockerfile is slightly less obvious to a casual reader than separately-named files. Mitigated by clear target names (`runtime`, `test`, `test-roundtrip`) and by keeping the semantic boundary at the COPY level where a reader looks.
- **Follow-on work:** a department-owned API-T restructure task and a department-owned DB-T restructure task. Until they land, the current separate-file Dockerfiles remain valid; B is the target state, not an emergency migration.
