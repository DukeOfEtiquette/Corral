---
schema_version: 1
adr: 9
title: "Adopt rogue-derived AI-orchestration conventions, right-sized; not the multiverse plugin"
status: "accepted"
date: "2026-06-05"
related_adrs: [5, 21]
supersedes: []
superseded_by: null
---

# ADR-009: Adopt rogue-derived AI-orchestration conventions, right-sized; not the multiverse plugin

> **Forward pointer (2026-06-09):** ADR-028 partially supersedes the worker-invocation mechanism this
> ADR established (the parallel human-driven `/corral-worker` session): the worker becomes an
> orchestrator-dispatched subagent and `/corral-worker` is retired. The role split, report shape, and
> handoff artifacts adopted here are retained. Per the partial-supersession convention the
> `superseded_by` field is left null; see ADR-028.

## Context

ADR-005 makes AI infrastructure a first-class domain, which raises the question of which conventions that infrastructure follows. The user maintains two candidate sources: the mature orchestration system in `~/rogue` (orchestrator/worker roles, kickoff/report handoffs, ADRs with YAML frontmatter, append-only OBSERVATIONS logs with stable IDs, STATUS.md as single source of truth, a coordinator workspace with departments), and the `~/claude_multiverse` plugin, which packages similar ideas as reusable skills.

## Alternatives considered

### Option A: Mirror rogue conventions directly, right-sized for a single fresh repo

Adopt the ADR format, the append-only `OBSERVATIONS.md` with stable IDs (`COR-NN` here), `STATUS.md` as the single source of truth for progress, orchestrator/worker role docs (authored in Phase 1), and the project-manager-style coordinator-plus-departments structure (ADR-021). Skip the parts a day-zero single project does not need (multiple workspaces, frontmatter query tooling, dashboards).

**Selected because:** rogue is the user's most mature and actively maintained instance of these patterns. Per the user (2026-06-05), `~/rogue/ai-workspaces/project-manager` is the specific exemplar. Trade-off accepted: conventions are copied, not shared; improvements here do not automatically flow back.

### Option B: Register this project as a multiverse-plugin universe

**Rejected because:** per the user (2026-06-05), the plugin is stale and underdeveloped relative to rogue, with a dirty working tree, and should be avoided for now. Note: the ADR file format used here matches the multiverse `decisions/` conventions because that is the cleanest written form of the user's own format; this is format reuse only, with no dependency on the plugin.

### Option C: Invent fresh conventions for this repo

**Rejected because:** the existing conventions are proven, and consistency across the user's projects has direct value for the agents that work in them.

## Decision

This repo adopts the rogue-derived conventions: numbered frontmatter ADRs in `./decisions/`, an append-only `./OBSERVATIONS.md` with `COR-NN` IDs, `./STATUS.md` as the single source of truth for current progress, orchestrator/worker role docs to be authored in Phase 1, and a coordinator-plus-departments structure (candidates recorded in ADR-021). The multiverse plugin is not used.

## Consequences

- Phase 1 includes right-sizing rogue's `ORCHESTRATOR-ROLE.md` and `WORKER-ROLE.md` for this repo (seeded as task COR-T-001).
- The Agent Discipline rule (verify before asserting) is carried into `./CLAUDE.md` as the authoritative copy for this repo.
- The no-em-dashes-in-files writing rule is inherited.
- If the multiverse plugin matures later, registering this project remains possible; nothing here conflicts with it.
