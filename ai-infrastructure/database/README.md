# Database

Department workspace under `ai-infrastructure/database/`, created 2026-06-10.

## Scope

Schema, migrations, seed logic

## Boundary

This workspace owns the artifacts and decisions that fall within the scope above. Cross-cutting concerns and project-wide decisions belong in the coordinator workspace at `ai-infrastructure/project-manager/`.

Tasks for this department live in the shared coordinator task pool at `ai-infrastructure/project-manager/tasks/`, tagged with the `dept:database` label.

## Coordinator

The project-manager coordinator workspace (`ai-infrastructure/project-manager/`) has write authority over this workspace for coordination purposes: status alignment, cross-references, decision propagation, and consistency fixes. See `ai-infrastructure/project-manager/README.md` for the coordinator's role.

## Operated by

The `/database-orchestrator` slash command instantiates the Orchestrator role for this department. See `./CLAUDE.md` for the full operating rules.
