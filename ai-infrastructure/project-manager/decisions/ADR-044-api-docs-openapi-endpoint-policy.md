---
schema_version: 1
adr: 44
title: "API docs/OpenAPI endpoint exposure policy (Swagger UI, ReDoc, openapi.json)"
status: "accepted"
date: "2026-06-22"
related_adrs: [3, 6, 10, 45]
supersedes: []
superseded_by: null
---

# ADR-044: API docs/OpenAPI endpoint exposure policy (Swagger UI, ReDoc, openapi.json)

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

Option B. The `api` service configures the three FastAPI documentation endpoints explicitly rather than inheriting the framework default, and gates their exposure by environment.

- **Placement: keep at root.** Swagger UI stays at `/docs`, ReDoc at `/redoc`, and the OpenAPI schema at `/openapi.json`. They are deliberately NOT relocated under `/api/v1`: FastAPI's conventional root placement matches developer expectation and keeps the change minimal (only the exposure gate needs wiring, not a placement override). The path-root difference from the application's `/api/v1` routes is accepted as a conscious choice, no longer an accident.
- **Exposure: a single environment-driven gate.** All three endpoints are controlled by one setting. They are enabled in local/dev (preserving the live interactive docs that are genuinely useful for developing against the v1 surface, API-T-001) and fully disabled in remote deployment (Phase 6, ADR-003), where the api becomes reachable off-host. "Disabled" means all three are off together (`docs_url=None`, `redoc_url=None`, `openapi_url=None`); there is no behind-auth variant for remote at this stage.
- **Mechanism is implementation-phase detail.** The exact settings accessor, environment variable name, default value, and how `app/api/main.py` reads the flag at app construction are left to the executing task, consistent with ADR-010's "implementation-phase decisions, not ADR content" carve-out. The natural shape mirrors the existing `app/api/settings.py` env-accessor pattern (for example the `get_cookie_secure()` boolean parse), with the flag defaulting to enabled so local/dev keeps docs on with no `.env` change and the remote environment sets it off.

## Consequences

1. **Implementation task.** A follow-up task implements this against `app/api/main.py` (pass `docs_url`/`redoc_url`/`openapi_url` conditioned on the gate) and `app/api/settings.py` (a new env-read accessor mirroring `get_cookie_secure()`). It routes through the dispatched-worker flow when picked up.
2. **Default flips from implicit-always-on to explicit-gated.** The current behaviour (all three endpoints always on at root, undocumented, per FastAPI's default with no override at `app/api/main.py:37`) becomes a recorded, env-controlled policy. Local behaviour is unchanged in practice (docs stay on); remote gains an explicit off switch before Phase 6.
3. **Defined inventory value (ADR-045 / COR-T-055).** The api's docs-endpoint entry in the service inventory records `/docs`, `/redoc`, and `/openapi.json` at root, kind docs/openapi, enabled in local/dev and disabled in remote. COR-T-055 records this asserted value instead of its "per ADR-044 (pending)" fallback.
4. **Remote exposure posture closed before Phase 6.** The off-host exposure question (near the ADR-006 do-not-over-expose ethos, though docs are not secrets) is decided now: no interactive docs or schema in remote. Behind-auth remote docs remain a future revisit if a need arises, not built now.
5. **A settings flag to maintain.** The trade-off accepted under Option B: a small amount of env-conditional wiring and one settings flag whose remote value lives in deployment environment rather than code.
