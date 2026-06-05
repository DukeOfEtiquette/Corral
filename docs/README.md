# Docs

Navigation index for Corral documentation. All `.md` files live in sanctioned locations (this tree, the repo-root docs files, `../decisions/`, `../tasks/`), never in source directories.

## This tree

| Doc | Purpose |
|---|---|
| `./architecture/OVERVIEW.md` | One-page runtime shape: services, data flow, the MCP seam |

## Elsewhere in the repo

| Doc | Purpose |
|---|---|
| `../README.md` | Human orientation: what this is, roadmap, getting started |
| `../CLAUDE.md` | Operating rules for AI agents working in this repo |
| `../STATUS.md` | Current phase and progress (single source of truth) |
| `../OBSERVATIONS.md` | Append-only pattern log (`COR-NN` IDs) |
| `../decisions/` | ADRs: every binding choice and every queued open question |
| `../tasks/README.md` | Bootstrap task convention (canonical for the markdown era) |

## Expected to grow here (Phase 1+)

- `./ai-orchestration/roles/` : orchestrator and worker role docs (task COR-T-001)
- A canonical task-coordination policy doc at the dogfood milestone (ADR-008)
