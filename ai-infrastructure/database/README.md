# Database

Department workspace under `ai-infrastructure/database/`, created 2026-06-10.

## Scope

Schema, migrations, seed logic

## Boundary

This workspace owns the artifacts and decisions that fall within the scope above. Cross-cutting concerns and project-wide decisions belong in the coordinator workspace at `ai-infrastructure/project-manager/`.

Tasks for this department live in the department's own task tree at `ai-infrastructure/database/tasks/`, using `DB-T-NNN` IDs (ADR-031). The `dept:database` label is applied at the dogfood import (ADR-008), not hand-applied in the markdown era.

## Coordinator

The project-manager coordinator workspace (`ai-infrastructure/project-manager/`) has write authority over this workspace for coordination purposes: status alignment, cross-references, decision propagation, and consistency fixes. See `ai-infrastructure/project-manager/README.md` for the coordinator's role.

## Operated by

The `/database-orchestrator` slash command instantiates the Orchestrator role for this department. See `./CLAUDE.md` for the full operating rules.
