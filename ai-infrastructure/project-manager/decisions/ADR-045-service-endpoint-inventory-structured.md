---
schema_version: 1
adr: 45
title: "Service/endpoint inventory as structured, dashboard-consumed data"
status: "pending"
date: "2026-06-22"
related_adrs: [5, 37, 39, 40, 44]
supersedes: []
superseded_by: null
---

# ADR-045: Service/endpoint inventory as structured, dashboard-consumed data

> Pending: frames the open question for how the project records its running and planned servers (ports, base URLs, endpoints including docs endpoints) as a structured artifact the dashboard can consume. No decision is taken yet. Alternatives carry leanings (clearly marked) to support deliberation; Decision and Consequences stay pending until taken up. Do not implement before this ADR is accepted. The authoring of the inventory itself is tracked as COR-T-055, gated on this ADR.

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

Pending.

## Consequences

Pending. (On acceptance, expect: a structured inventory format and location decided; the dashboard ETL extended to consume and render it; COR-T-055 unblocked to author the inventory covering api, postgres, dashboard, mcp, and frontend; and the dashboard server finally captured in a standing structured surface rather than only in handoff reports.)
