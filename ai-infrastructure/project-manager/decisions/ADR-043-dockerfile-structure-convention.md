---
schema_version: 1
adr: 43
title: "Dockerfile structure convention: multi-stage build targets and mandatory per-context .dockerignore"
status: "pending"
date: "2026-06-16"
related_adrs: [3, 6, 15]
supersedes: []
superseded_by: null
---

# ADR-043: Dockerfile structure convention: multi-stage build targets and mandatory per-context .dockerignore

> Pending: frames the open question for a repo-wide Dockerfile structure convention. No decision is taken yet. Body Alternatives carry leanings (clearly marked) to support deliberation; Decision and Consequences stay pending until taken up. Do not implement before this ADR is accepted. Note: the `.dockerignore`/COPY-hygiene piece is separable and justified by ADR-006 alone; it is tracked independently as COR-T-054 and does not wait on this ADR.

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

### Option B: Multi-stage Dockerfile per context with build targets + mandatory per-context `.dockerignore` (leaning toward)

One Dockerfile per context with a shared `base` stage and `runtime` / `test` targets, selected from compose via `build: { target: ... }`. One file per context, shared cached layers, zero deps/CMD drift. Plus a mandatory `.dockerignore` per build context (`./api`, `./db`) excluding `.env`, `__pycache__`, `*.sh`, and `tests/` where not needed. Selective `COPY` to match the db pattern. The db test vs test-roundtrip semantic split is preserved as two test targets (or one target plus a build-arg) so the `alembic/` boundary survives.

**For (leaning):** directly answers "one image, several processes" with targets instead of duplicated files; eliminates the drift surface; the `.dockerignore` closes the bloat and the latent ADR-006 gap. **Trade-off:** multi-stage Dockerfiles are slightly less obvious to a reader than two named files; the db two-test-target shape needs care to keep the semantic boundary legible.

### Option C: `.dockerignore` + selective-COPY hygiene only (no multi-stage)

Add the per-context `.dockerignore` and switch api to selective `COPY`, but keep separate `Dockerfile` / `Dockerfile.test` files.

**For:** captures the security/bloat win (the ADR-006-adjacent part) with the least churn and no restructure. **Against:** leaves the duplication smell (1) unaddressed. This is effectively the COR-T-054 slice on its own; it is a strict subset of Option B and can ship first regardless of how this ADR resolves.

## Decision

Pending.

## Consequences

Pending. (On acceptance, expect: a convention statement applying to all web-app build contexts; the db semantic-split exception recorded explicitly; department executors restructuring `app/api/` and `app/db/` Dockerfiles under their own tasks; and COR-T-054 either already landed or folded in.)
