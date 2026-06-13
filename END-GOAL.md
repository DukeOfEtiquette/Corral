# End Goal

## What this project is building toward

Corral is building toward a reusable, portable project-manager that any project can install as a native Claude Code plugin. Installing it in a new project yields, out of the box:

- `/create-department` to stamp out department workspaces on demand
- A dashboard that auto-tracks newly created departments as they are added
- A config hook that points issue-tracking at a remote Corral deploy (see `./ai-infrastructure/project-manager/decisions/ADR-033-remote-deployment-topology.md`)

The plugin carries the generic coordinator machinery: the orchestrator role, the dispatch loop, the checker fleet, the cross-department agents (executor, test-designer, the prelaunch/close checkers, the drafter and checker per `./ai-infrastructure/project-manager/decisions/ADR-032-cross-department-agent-tier.md`), `/create-department` plus the department template, and the dashboard. It carries none of the Corral-specific content: not the backend-api, database, mcp-server, frontend-ui, or devops departments (see `./ai-infrastructure/project-manager/decisions/ADR-021-candidate-departments.md`), nor Corral's own ADRs or task trees.

Corral becomes both the app being built and the first consumer of the plugin extracted from it (roadmap Phase 8).

## Why

The motivation is one reusable plugin instead of per-project forks. The same orchestration infrastructure (the roles, dispatch loop, checkers, dashboard, department machinery) is already running in multiple projects as hand-maintained copies. The end goal replaces those forks with a single installed plugin that every project points at a shared Corral deploy for issue tracking.

The exact extraction boundary is open: `./ai-infrastructure/project-manager/decisions/ADR-034-project-manager-plugin-extraction-boundary.md` frames the open dimensions and gates Phase 8.

## Where we are now: the dogfood boundary

The roadmap's incremental phases (see `./README.md` and `./ai-infrastructure/project-manager/STATUS.md`) are the path to this destination. The project currently tracks itself through a markdown task convention and a local docker compose stack.

The dogfood milestone (`./ai-infrastructure/project-manager/decisions/ADR-008-bootstrap-tasks-dogfood-milestone.md`) is the boundary that separates "building Corral" from "using Corral": once Phases 1-5 land, the project imports its own tasks into the app and the markdown trees freeze. The end goal described in this document is what comes after that boundary.

## The three phases that reach the destination

After the dogfood milestone, three incremental phases close the gap:

- **Phase 6: Remote deployment and concurrency.** Deploy Corral to a remote server and prove multiple concurrent agent sessions work. Gated on `./ai-infrastructure/project-manager/decisions/ADR-033-remote-deployment-topology.md`.
- **Phase 7: Repoint ai-infrastructure at the remote.** Switch this project's dashboard and task seam from local markdown to the remote Corral deploy.
- **Phase 8: Extract the project-manager plugin.** Generalize the project-manager into a portable Claude Code plugin and dogfood Corral with it. Gated on `./ai-infrastructure/project-manager/decisions/ADR-034-project-manager-plugin-extraction-boundary.md`.

The full phase-by-phase plan lives in `./README.md` (the roadmap table) and `./ai-infrastructure/project-manager/STATUS.md` (the authoritative live status with epics). Phases 6-8 are the incremental steps; this document is the destination they point at.
