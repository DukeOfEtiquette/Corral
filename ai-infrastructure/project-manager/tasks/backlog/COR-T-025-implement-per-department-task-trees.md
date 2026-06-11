---
schema_version: 1
id: COR-T-025
title: "Implement per-department task trees (ADR-031 cascade)"
status: backlog
labels: [dept:agent-development]
priority: P2
created: 2026-06-11
updated: 2026-06-11
---

## Description

Execute the implementation cascade that ADR-031 specifies. ADR-031 (accepted 2026-06-11) reverses ADR-027 Fork B's single shared `dept:`-labeled task pool in favour of per-department task trees, rogue-faithful: every workspace (the `project-manager` coordinator and each department) owns its own `tasks/` tree, with per-department ID prefixes (`DB-T`, `API-T`; the coordinator keeps `COR-T` unchanged), and the `dept:<slug>` label is applied at the dogfood import (ADR-008) rather than hand-applied in the markdown era. ADR-031 is the spec; this task is the deliverable work that brings the repo into line with it. This is coordinator/agent-development AI-infrastructure work.

Scope (the cascade named in ADR-031 Consequences):

1. **Template + recipe.** Update `ai-infrastructure/project-manager/templates/department/` so the scaffold includes a `tasks/` tree (`backlog/`, `in-progress/`, `blocked/`, `done/`, plus a `.next-task-id` seeded to the first ID) and a department task-ID-prefix token (e.g. `{{DEPT_TASK_PREFIX}}`). Re-point the template `orchestrator-command.md` Phase 3 survey to read the department's OWN `tasks/` tree instead of the coordinator pool filtered by `dept:<slug>`. Update `.claude/commands/create-department.md` (inputs gain the task-ID prefix; the deliverable file set gains the `tasks/` tree) and ADR-030's referenced contract via the forward pointer already added.
2. **Two live departments.** Create `ai-infrastructure/database/tasks/` and `ai-infrastructure/backend-api/tasks/` (the four state dirs plus `.next-task-id`). Re-point `.claude/commands/database-orchestrator.md` and `.claude/commands/backend-api-orchestrator.md` Phase 3 surveys to their own trees. Prefixes: `DB-T` and `API-T`.
3. **Relocate COR-T-024 to DB-T-001.** Move `ai-infrastructure/project-manager/tasks/backlog/COR-T-024-postgres-schema.md` to `ai-infrastructure/database/tasks/backlog/DB-T-001-postgres-schema.md`, renaming the `id` to `DB-T-001` and updating its activity log to note the relocation. Seed `database/tasks/.next-task-id` to `2`. The coordinator id 24 is freed and not reused (IDs are never reused; a gap is fine).
4. **Dashboard ETL.** Update `ai-infrastructure/project-manager/dashboard/etl.py` to read every workspace's `tasks/` tree (coordinator plus each department) instead of a single shared pool, preserving the JSON data contract. Verify under docker compose per ADR-003.
5. **Sweep shared-pool language.** Reframe `ai-infrastructure/project-manager/tasks/README.md` from "the single COR-T pool" to the per-workspace task convention (each workspace owns a tree with its own prefix and `.next-task-id`; the tree is the department partition; the `dept:<slug>` label is applied at import). Sweep the shared-pool framing in `ai-infrastructure/project-manager/CLAUDE.md` (the "Tasks" and coordinator-write sections), the template `CLAUDE.md` ("NO own tasks/" -> owns a tree), the repo-root `README.md`, and `STATUS.md` where they describe a shared pool.

Out of scope: the dogfood-era import behaviour itself (ADR-008, future); the Corral app's label/board implementation (Phase 4); any web-app code. This task only brings the markdown-era structure and its tooling into line with ADR-031.

When picked up, this routes through the dispatched-worker flow from `/project-manager-orchestrator` (resolve any residual decisions, e.g. the exact prefix-token name and the `.next-task-id` seeding convention, then draft+check the kickoff, prelaunch, dispatch the worker, close). Verification: a fresh `/database-orchestrator` should survey `database/tasks/` and find `DB-T-001`; the dashboard should render all trees; no shared-pool language should remain outside settled `done/` history and the ADRs' own records.

## Activity log

- 2026-06-11: Created in backlog. Filed as the ADR-031 implementation cascade (reversing ADR-027 Fork B to per-department task trees). Surfaced by the COR-T-023 department smoke tests, which exposed that departments had no task home of their own under the shared-pool model. Routed as a coordinator/agent-development deliverable through the dispatched-worker flow; not yet dispatched per user direction.
