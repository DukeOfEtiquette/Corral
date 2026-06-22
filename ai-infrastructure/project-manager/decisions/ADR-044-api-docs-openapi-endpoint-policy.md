---
schema_version: 1
adr: 44
title: "API docs/OpenAPI endpoint exposure policy (Swagger UI, ReDoc, openapi.json)"
status: "pending"
date: "2026-06-22"
related_adrs: [3, 6, 10]
supersedes: []
superseded_by: null
---

# ADR-044: API docs/OpenAPI endpoint exposure policy (Swagger UI, ReDoc, openapi.json)

> Pending: frames the open question for whether and how the `api` service exposes interactive API docs and the OpenAPI schema. No decision is taken yet. Alternatives carry leanings (clearly marked) to support deliberation; Decision and Consequences stay pending until taken up. Do not implement before this ADR is accepted.

## Context

The `api` service is FastAPI. `app/api/main.py` constructs the app as `FastAPI(lifespan=lifespan)` with no `docs_url`, `redoc_url`, or `openapi_url` override (verified on disk 2026-06-22). FastAPI's documented default with no override is to serve three endpoints: `/docs` (Swagger UI), `/redoc` (ReDoc), and `/openapi.json` (the OpenAPI schema). So the api almost certainly already serves an interactive Swagger UI at `http://localhost:8123/docs` today, by default, with no decision recorded and nothing documenting it. (This is inferred from FastAPI's default behaviour plus the absence of any override in the code; it has not been confirmed by hitting the endpoint.)

Two wrinkles make this worth a decision rather than a silent default:

- **Path placement.** The application's own routes live under the `/api/v1` prefix (ADR-010), but the FastAPI default docs sit at the root (`/docs`, `/openapi.json`), not under the prefix. So the docs surface and the API surface are on different path roots, by accident rather than design.
- **Deployment posture.** docker compose is local-first today (ADR-003), but Phase 6 makes the stack remotely deployable. Interactive docs and a full OpenAPI schema that are harmless on localhost become a deliberate exposure decision once the api is reachable off-host. This sits near the ADR-006 secrets-hygiene ethos (do not expose more surface than intended), though the docs themselves are not secrets.

This decision also governs the value the service/endpoint inventory (ADR-045) records for the api's "docs endpoint": the inventory should report whatever this ADR decides, not the accidental default.

## Alternatives considered

### Option A: Keep FastAPI defaults (docs at `/docs`, schema at `/openapi.json`, always on)

Change nothing; accept the implicit behaviour as the decision.

**Against (leaning):** the current state is implicit and undocumented, leaves the docs surface at a different path root than the API, and leaves interactive docs on in remote deployment with no explicit choice. Accepting it should at least be a recorded choice, not an accident.

### Option B: Keep docs enabled, but make placement explicit and gate exposure by environment (leaning toward)

Explicitly configure the docs/schema URLs (for example align them under or alongside `/api/v1`, or consciously keep them at root), keep them on for local/dev, and gate them off (or behind auth) for remote deployment via settings/env. The exact mechanism (env flag read in `settings.py`, conditional `docs_url=None`) is an implementation detail for the executing task.

**For (leaning):** keeps the developer convenience of live docs locally, makes the path placement a decision, and closes the remote-exposure question before Phase 6 rather than after. **Trade-off:** a small amount of env-conditional wiring and a settings flag to maintain.

### Option C: Disable interactive docs entirely (`docs_url=None`, `redoc_url=None`), decide separately on `openapi_url`

Lock the api down: no Swagger UI, no ReDoc; optionally keep `/openapi.json` for tooling or disable it too.

**For:** smallest attack/maintenance surface; nothing to gate per environment. **Against:** loses live interactive docs even locally, where they are genuinely useful for developing against the v1 endpoint surface (API-T-001).

## Decision

Pending.

## Consequences

Pending. (On acceptance, expect: a recorded policy for the three FastAPI doc endpoints, their path placement, and their per-environment exposure; an implementation task against `app/api/main.py` + `app/api/settings.py`; and a defined value for the api's docs endpoint in the ADR-045 service inventory.)
