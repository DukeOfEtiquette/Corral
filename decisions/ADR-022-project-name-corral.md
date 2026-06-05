---
schema_version: 1
adr: 22
title: "Project name: Corral"
status: "accepted"
date: "2026-06-05"
related_adrs: [1, 9]
supersedes: []
superseded_by: null
---

# ADR-022: Project name: Corral

## Context

The project began under the expressive placeholder "GHIssuesClone." With the scope and decisions now well defined (ADR-001..021), the user requested a real name. Naming constraints: short, easy to type (it becomes the repo directory, the docker compose project name, and likely the MCP server name), no collision with established issue-tracking or dev tools, and ideally consistent with the naming streak in the user's ecosystem (`rogue`, Maverick).

## Alternatives considered

### Option A: Corral

Where stray issues get penned and sorted; boards are pens, agents are the hands working them. Fits the western theme beside rogue and Maverick. Only known collision is the Pony language's small dependency tool, irrelevant for a self-hosted app.

**Selected because:** most descriptive of the app itself (the place work is organized), strongest ecosystem fit, negligible collisions.

### Option B: Posse

Names the agent fleet rounding up issues. Charming next to rogue, but describes the crew more than the kanban app; minor social-app collisions.

**Rejected because:** less descriptive of the product.

### Option C: Andon

Toyota's factory signal board, the literal ancestor of kanban. Real lineage, but no ecosystem fit and shared by a few small startups.

**Rejected because:** Corral fits the ecosystem better.

### Option D: Docket

A queue of cases awaiting work. Professional, accurate, but shared by a meeting-notes SaaS and a PyPI package, and stylistically flat next to rogue/Maverick.

**Rejected because:** weaker fit, more collisions.

### Names ruled out by collision

Roundup (existing Python issue tracker), Wrangler (Cloudflare), Foreman (Red Hat), Lasso (language), and anything near Kanboard/Wekan/Plane/Taiga.

## Decision

The project is named **Corral**. The repository directory becomes `~/src/corral`. Stable ID prefixes derived from the old name are renamed in place before any external reference exists: task IDs `GHI-T-NNN` become `COR-T-NNN`, observation IDs `GHI-NN` become `COR-NN`.

## Consequences

- All docs, ADRs, and task files now read Corral / `COR-*`; the six seeded task files were renamed accordingly.
- The docker compose project name will derive from the `corral` directory name with no override needed.
- The ID-prefix rename is a one-time exception to "IDs are never reused," taken on day zero while the only references are in-repo; after this ADR, prefixes are frozen.
- The "narrow-scope GitHub Issues clone" description remains accurate and stays in the README; only the name changes.
