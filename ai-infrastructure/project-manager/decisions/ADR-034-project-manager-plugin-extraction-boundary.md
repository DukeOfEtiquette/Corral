---
schema_version: 1
adr: 34
title: "project-manager plugin extraction boundary"
status: "pending"
date: "2026-06-12"
related_adrs: [4, 8, 21, 27, 30]
supersedes: []
superseded_by: null
---

# ADR-034: project-manager plugin extraction boundary

> Pending: gates roadmap Phase 8. Frames the open questions; decided when Phase 8 (extract the project-manager plugin) is taken up. Do not decide implicitly before then.

## Context

The roadmap's end goal (`./END-GOAL.md`) is to generalize the project-manager coordinator into a native Claude Code plugin that any project can install: drop it in, and immediately have `/create-department`, a dashboard that auto-tracks new departments, and a config hook pointing issue-tracking at the remote Corral deploy (ADR-033, Phase 6). The Corral-specific departments (backend-api, database, mcp-server, frontend-ui, devops) and Corral's own ADRs and tasks must NOT travel with the plugin. Corral then becomes both the app being built and the first consumer of the plugin extracted from it (roadmap Phase 8 dogfoods Corral via the installed plugin).

The hard part is the boundary: what is generic project-manager machinery (and goes in the plugin) versus what is Corral-the-app's own content (and stays). The coordinator today interleaves both: the orchestrator role, the dispatch loop, the checker fleet, the cross-department agents (ADR-028, ADR-032), `/create-department` (ADR-030), and the dashboard are generic; the web-app departments, the Corral roadmap, and Corral's accepted ADRs are app-specific.

Open dimensions:

- **Packaging format.** How the plugin is structured as a native Claude Code plugin (manifest, commands, agents, skills) and how its pieces map onto today's `.claude/` and `docs/ai-orchestration/` layout.
- **In/out boundary.** Confirming what travels: the orchestrator + executor + test-designer roles, the dispatch-loop checkers, `/create-department` and the department template (ADR-030), the dashboard, the create-department recipe. And what does not: the Corral web-app departments, Corral's roadmap, Corral's accepted/pending ADRs, Corral's task trees.
- **Dashboard generalization.** The dashboard ETL reads Corral-specific trees and frontmatter today (`ai-infrastructure/`, the roadmap in STATUS). What must be parameterized so a fresh install renders an empty-but-correct dashboard that fills in as departments are created.
- **Fresh-install bootstrap.** What a new project gets on install (the coordinator workspace scaffold, the first dashboard, the `decisions/`/`tasks/` conventions) and how that bootstrap runs.
- **Remote-endpoint configuration.** How an installed plugin is pointed at a remote Corral deploy (ADR-033) for issue tracking, and how that interacts with the ADR-004 MCP seam and the ADR-008 dogfood (markdown-to-app) migration the host project will run.
- **Versioning and distribution.** How the plugin is versioned and installed across the user's fleet (`~/rogue`, `~/src/wow_ah`, future projects) and how an existing project adopts a new version.
- **Relationship to prior plugin attempts.** Reconciling with earlier plugin lineage (the stale multiverse plugin) so the extraction starts from the current conventions rather than a superseded baseline.

## Alternatives considered

{Pending. Packaging format, the exact in/out boundary, and the dashboard-generalization strategy are the dimensions to enumerate options against when this ADR is taken up.}

## Decision

{Pending.}

## Consequences

{Pending.}
