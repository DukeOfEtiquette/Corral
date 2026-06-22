---
schema_version: 1
adr: 45
title: "Service/endpoint inventory as structured, dashboard-consumed data"
status: "accepted"
date: "2026-06-22"
related_adrs: [5, 21, 31, 37, 39, 40, 41, 44]
supersedes: []
superseded_by: null
---

# ADR-045: Service/endpoint inventory as structured, dashboard-consumed data

## Context

The project runs (or will run) several servers, and there is no single place that records them with their ports and endpoints. Verified on disk 2026-06-22:

- **api** (FastAPI) on host port 8123; routes under `/api/v1`; `/healthz`; and, by FastAPI default, `/docs` + `/redoc` + `/openapi.json` (the subject of ADR-044). Port recorded only in `app/docker-compose.yml` and the API-T-007 handoff.
- **postgres** on 5432 (`app/docker-compose.yml`).
- **dashboard** (Vite/React + ETL) on host port 8420, a real running server, recorded only in a COR-T-031 handoff report; it appears in no standing doc.
- **mcp** (FastMCP, Phase 3, not built) and **frontend** (React, Phase 4, not built).

`ai-infrastructure/project-manager/docs/architecture/OVERVIEW.md` lists the four web-app services by role only: no ports, no endpoints, no docs endpoints; and it omits the dashboard entirely (the dashboard is domain-2 AI-infra, deliberately outside the domain-1 OVERVIEW). The result: no inventory of "what servers run, on what ports, with what endpoints."

The requirement is not just a doc: the inventory must be a **structured artifact the dashboard can consume** (operator direction, 2026-06-22), so the running-services picture is surfaced on the dashboard alongside the existing derived surfaces, not buried in prose.

There is a strong precedent to mirror. Epics and phases are first-class **pure YAML files** (ADR-037, ADR-038), discovered generically across workspaces and `yaml.safe_load`-ed by the dashboard ETL, then emitted into `data.json` and rendered (ADR-039, ADR-040). The service inventory fits the same shape: structured source files, consumed by the ETL, rendered as a panel.

## Alternatives considered

### Option A: A prose doc (for example `docs/architecture/SERVICES.md`)

Write a human-readable services/ports/endpoints page alongside OVERVIEW.

**Against (leaning):** human-readable but not machine-consumable, so it fails the core requirement (dashboard consumption) and re-introduces the drift problem (a prose table goes stale silently). Acceptable only as a rejected baseline.

### Option B: Structured YAML files consumed by the dashboard ETL, mirroring epics/phases (leaning toward)

Store the inventory as pure YAML in a coordinator-owned tree (for example `ai-infrastructure/project-manager/services/`, one file per service, or a single `services.yml`), and extend the dashboard ETL to read them into `data.json` and render a services panel. Same file-type-as-structured-data discipline as ADR-037, same derived-surface consumption as ADR-039/040.

**For (leaning):** reuses an established, working pattern (generic discovery + `yaml.safe_load` already in `etl.py`); keeps the inventory close to the other coordinator structured data; surfaces services on the dashboard for free once the ETL reads them. **Trade-off:** the inventory is hand-maintained, so it can drift from compose/code unless a consistency check is added later (the COR-03..COR-08 consistency-check lineage, ADR-041, is the natural home for a "declared port matches compose" check).

### Option C: Derive the inventory from compose + code (parse `docker-compose.yml` ports, introspect FastAPI routes)

Generate the inventory automatically rather than hand-authoring it.

**For:** zero hand-maintenance; cannot drift from the running stack. **Against:** brittle and complex (route introspection, multi-service parsing), and it cannot capture intent the source files do not carry: planned-but-unbuilt services (mcp, frontend), domain (1 vs 2), owning workspace, governing ADRs, or the human-meaningful description. Best considered a later enhancement layered on Option B (derive what is derivable, declare the rest), not the first step.

## Open dimensions to settle on acceptance

- **Format and location:** YAML (leaning, per ADR-037) vs JSON; single `services.yml` vs a per-service `services/` tree; coordinator-owned location.
- **Schema (fields to frame, not finalised):** `schema_version`, `id`, `name`, `domain` (1 web-app / 2 ai-infra), `status` (running / planned), `runtime` (compose service name or process), `host`, `port(s)`, `base_url`, `endpoints` (a list of `{path, kind}` where kind is one of api / docs / openapi / health / ui), `workspace`/owning dept, `adrs` (governing ADR numbers). The api's docs endpoint value is governed by ADR-044.
- **Dashboard consumption:** how the ETL reads the files and what the rendered panel shows; consistent with the ADR-039/040 derived-surface model.
- **Drift guard:** whether to add a consistency check (declared port vs `app/docker-compose.yml`) into the ADR-041 check lineage now or defer it.

## Decision

**Option B selected, with per-workspace ownership and generic discovery.**

1. **Format: pure YAML, one `services.yml` per workspace.** The inventory is structured-data-as-files, consistent with ADR-037's epics/phases file-type choice (YAML over JSON; JSON would be the lone exception in the work-item-and-structured-data family for no gain). A workspace owns few services, so a single `services.yml` per workspace is the right granularity, not a per-service tree.

2. **Location and ownership: per-workspace, generically discovered.** Each workspace that runs or plans a service owns a `services.yml` in its own tree (`ai-infrastructure/<workspace>/services.yml`), discovered by the dashboard ETL across all `ai-infrastructure/*/` workspaces, the same generic discovery the ETL already performs for `epics/` trees (`collect_roadmap_from_files` in `etl.py`). A new department adds its own `services.yml` and the dashboard picks it up with **no coordinator edit**. Planned services whose owning department does not exist yet (mcp, frontend, per the ADR-021 lazy-creation rule) are declared in the coordinator's `ai-infrastructure/project-manager/services.yml` until that department is stood up, then migrate to it. An explicit `workspace`/owner field decouples *where* a service is declared from *which* department owns it, so a coordinator-held planned entry still renders as owned by its eventual department.

3. **Schema (each file holds a list of service entries).** Each entry carries: `schema_version`; `id`; `name`; `domain` (1 web-app / 2 ai-infra); `status` (running / planned); `runtime` (compose service name or process); `host`; `port(s)`; `base_url`; `endpoints` (a list of `{path, kind}` where `kind` is one of api / docs / openapi / health / ui); `workspace` (owning department or coordinator slug); and `adrs` (governing ADR numbers). The api's docs/openapi endpoint entries record the values ADR-044 (accepted) pins: `/docs`, `/redoc`, `/openapi.json` at root, enabled in local/dev and disabled in remote.

4. **Dashboard consumption.** The ETL reads every `ai-infrastructure/*/services.yml`, aggregates the entries into `data.json`, and the dashboard renders a services panel listing each service with its ports and endpoints, consistent with the ADR-039/040 derived-surface model. The rendered panel is the consolidated read; the source files stay per-workspace.

5. **Drift guard built now (owned-but-advisory).** A consistency check joins the ADR-041 ETL warning family: it flags when a service's declared port does not match `app/docker-compose.yml`. Warn-only, like the existing `phase_warning`/`epic_warning`/`no_epic_warning` checks; it does not alter or suppress rendering. Built as part of the authoring task rather than deferred, while the context is fresh.

6. **Authoring is COR-T-055.** Writing the inventory files (covering api, postgres, dashboard, mcp, frontend), extending the ETL discovery and adding the services panel, and adding the drift-guard check is the dispatched follow-on COR-T-055, now unblocked. This ADR is the spec it executes against; the implementation routes through the dispatched-worker flow.

## Consequences

1. **Reuses the epics discovery pattern; near-zero new machinery.** The ETL already walks `ai-infrastructure/*/` for `epics/` trees and `yaml.safe_load`s them; the services reader is the same loop over `services.yml`. This extends ADR-037's generic-discovery model to a new file family; a forward-pointer note is added to ADR-037.

2. **A new per-workspace file family (amends ADR-031).** Each workspace gains an optional `services.yml` alongside its `tasks/` and (where present) `epics/` trees. No ID counter is needed: services are not ID-allocated the way tasks and epics are. A forward-pointer note is added to ADR-031.

3. **No coordinator chokepoint.** Adding a department service needs no coordinator edit; the new department's `services.yml` is discovered automatically. The single-file alternative (one coordinator-owned `services.yml`) was rejected for exactly this chokepoint.

4. **Planned services handled before their department exists.** mcp and frontend are declared in the coordinator file until their departments are stood up, then migrate; the explicit owner field keeps their rendered ownership correct throughout. This mirrors the forming-epic handling (ADR-041).

5. **The dashboard server gets a standing structured surface.** The dashboard (host 8420), previously recorded only in a COR-T-031 handoff report, is captured in the coordinator's `services.yml`.

6. **Drift guard joins the ADR-041 lineage (extends ADR-041).** The declared-port-vs-compose check is one more owned-but-advisory warning in the existing ETL warning family; a forward-pointer note is added to ADR-041. It does not gate or alter any derived status.

7. **OVERVIEW.md unchanged.** The domain-1 runtime-shape narrative in `ai-infrastructure/project-manager/docs/architecture/OVERVIEW.md` stays as prose; the inventory is its structured, machine-consumed companion, not a replacement.

8. **Full derivation (Option C) remains a future layer.** Auto-deriving ports and routes from compose plus FastAPI introspection is deliberately not done now; the drift guard is the first step toward "derive what is derivable, declare the rest."
