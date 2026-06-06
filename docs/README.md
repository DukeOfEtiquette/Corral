# Docs

Navigation index for Corral documentation. All `.md` files live in sanctioned locations (this tree, the repo-root docs files, `../decisions/`, `../tasks/`), never in source directories.

## This tree

| Doc | Purpose |
|---|---|
| `./architecture/OVERVIEW.md` | One-page runtime shape: services, data flow, the MCP seam |
| `./ai-orchestration/roles/ORCHESTRATOR-ROLE.md` | Orchestrator role: coordination, review, pattern mining, the dispatch loop |
| `./ai-orchestration/roles/WORKER-ROLE.md` | Worker role: kickoff execution, pinned report shape, checker dispatches |

## Elsewhere in the repo

| Doc | Purpose |
|---|---|
| `../README.md` | Human orientation: what this is, roadmap, getting started |
| `../CLAUDE.md` | Operating rules for AI agents working in this repo |
| `../STATUS.md` | Current phase and progress (single source of truth) |
| `../OBSERVATIONS.md` | Append-only pattern log (`COR-NN` IDs) |
| `../decisions/` | ADRs: every binding choice and every queued open question |
| `../tasks/README.md` | Bootstrap task convention (canonical for the markdown era) |
| `../.claude/` | AI-infrastructure artifacts (ADR-023, ADR-024): slash commands (`commands/`), agent definitions (`agents/`), agent specs (`agents/specs/`), tracked handoffs (`artifacts/handoffs/`), gitignored scratch (`artifacts/tmp/`) |

## Expected to grow here (Phase 1+)

- A canonical task-coordination policy doc at the dogfood milestone (ADR-008)
