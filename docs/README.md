# Docs

Navigation index for Corral documentation. All `.md` files live in sanctioned locations (this tree, the repo-root docs files, `../ai-infrastructure/project-manager/decisions/`, `../ai-infrastructure/project-manager/tasks/`), never in source directories.

## This tree

| Doc | Purpose |
|---|---|
| `./ai-orchestration/roles/ORCHESTRATOR-ROLE.md` | Orchestrator role: coordination, review, pattern mining, the dispatch loop |
| `./ai-orchestration/roles/EXECUTOR-ROLE.md` | Executor role: kickoff execution, pinned report shape, checker dispatches |
| `./ai-orchestration/roles/TEST-DESIGNER-ROLE.md` | Test Designer role: authoring failing tests against a surface's contract (TDD red phase, ADR-016) |

## AI-infrastructure workspace (project-manager)

| Doc | Purpose |
|---|---|
| `../ai-infrastructure/project-manager/docs/architecture/OVERVIEW.md` | One-page runtime shape: services, data flow, the MCP seam |
| `../ai-infrastructure/project-manager/STATUS.md` | Thin pointer to the derived dashboard surface (ADR-040); current phase, next step, and blocked are on the dashboard |
| `../ai-infrastructure/project-manager/OBSERVATIONS.md` | Append-only pattern log (`COR-NN` IDs) |
| `../ai-infrastructure/project-manager/decisions/` | ADRs: every binding choice and every queued open question |
| `../ai-infrastructure/project-manager/tasks/README.md` | Bootstrap task convention (canonical for the markdown era) |

## Elsewhere in the repo

| Doc | Purpose |
|---|---|
| `../README.md` | Human orientation: what this is, roadmap, getting started |
| `../CLAUDE.md` | Global operating rules for AI agents working in this repo |
| `../.claude/` | AI-infrastructure artifacts (ADR-023, ADR-024): slash commands (`commands/`), agent definitions (`agents/`), agent specs (`agents/specs/`), tracked handoffs (`artifacts/handoffs/`), gitignored scratch (`artifacts/tmp/`) |

## Expected to grow here (Phase 1+)

- A canonical task-coordination policy doc at the dogfood milestone (ADR-008)
