# project-manager

The coordinator workspace for Corral's AI-infrastructure. This workspace holds the project-wide STATUS, OBSERVATIONS, decisions (ADRs), and tasks that drive all AI-infrastructure work. It is the project-manager coordinator in the `ai-infrastructure/` directory structure decided in ADR-027.

## Purpose

- Owns the shared `COR-T-NNN` task pool (partitioned by `dept:` labels per ADR-018, not by separate task trees).
- Owns the single ADR sequence for the whole repo (AI-infra and web-app ADRs live here until web-app departments are lazily created, per ADR-027 Fork C).
- Holds the web-app architecture overview until a web-app department is created to receive it.
- The project-manager coordinator may create and edit files inside sibling department workspaces (`ai-infrastructure/<dept>/`) for coordination purposes: status alignment, cross-references, decision propagation.

## Contents

| Path | What it is |
|---|---|
| `./CLAUDE.md` | Operating rules for AI agents in this workspace |
| `./STATUS.md` | Thin pointer to the derived dashboard surface (ADR-040); current phase, next step, and blocked are on the dashboard |
| `./OBSERVATIONS.md` | Append-only pattern log, `COR-NN` IDs |
| `./decisions/` | All ADRs: accepted decisions and queued open questions |
| `./tasks/` | Project task pool, markdown convention (see `./tasks/README.md`) |
| `./docs/architecture/OVERVIEW.md` | One-page web-app runtime shape |

## Shared infrastructure (stays at repo root)

The `.claude/` tree (commands, agents, specs, handoff artifacts) and `docs/ai-orchestration/` (the shared role docs `ORCHESTRATOR-ROLE.md` and `EXECUTOR-ROLE.md`) live at the repo root as shared infrastructure usable by all workspaces. They are not inside this workspace directory.
