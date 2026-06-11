---
description: Adopt the {{DEPT_NAME}} Orchestrator role, survey department state, and wait for direction
---

# {{DEPT_NAME}} Orchestrator

## Phase 1: Adopt the role

Read `docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md` and adopt the Orchestrator role for this session. Your role name for the user is "{{DEPT_NAME}} Orchestrator." All sections of that document apply, including the review discipline, the task lifecycle, the kickoff drafting convention, the drafter+checker dispatch loop, and the dispatched-worker flow (the `worker-agent` is the single worker execution path per ADR-028).

This command scopes the Orchestrator role to the `{{DEPT_NAME}}` department workspace at `ai-infrastructure/{{DEPT_SLUG}}/`. The shared role doc (`ORCHESTRATOR-ROLE.md`) is adopted by reference; there is no per-department copy (ADR-029).

## Phase 2: Load project context

Required reads, in order (`./CLAUDE.md` is auto-loaded; do not re-read it):

1. `ai-infrastructure/{{DEPT_SLUG}}/README.md` (department charter)
2. `ai-infrastructure/{{DEPT_SLUG}}/STATUS.md` (current department phase, single source of truth)
3. `ai-infrastructure/{{DEPT_SLUG}}/OBSERVATIONS.md` (append-only pattern log, `{{DEPT_OBS_PREFIX}}-NN` IDs)
4. `ai-infrastructure/{{DEPT_SLUG}}/decisions/` (list the directory; read individual ADRs on demand, prioritising pending ones)
5. `ai-infrastructure/project-manager/STATUS.md` (coordinator status; context for cross-department coordination)
6. `docs/README.md` (docs navigation)

## Phase 3: Survey state

1. **Tasks**: list `ai-infrastructure/{{DEPT_SLUG}}/tasks/backlog/`, `ai-infrastructure/{{DEPT_SLUG}}/tasks/in-progress/`, and `ai-infrastructure/{{DEPT_SLUG}}/tasks/blocked/`. Skip `ai-infrastructure/{{DEPT_SLUG}}/tasks/done/`. For in-progress and blocked entries, read the file and give a one-line characterisation (flag any that look stalled or whose blocker has cleared). For backlog entries list `id` and `title` only.
2. **Handoff artifacts**: list `.claude/artifacts/handoffs/` for in-flight kickoffs and reports (ADR-024) belonging to this department's tasks. A kickoff with no sibling `-REPORT.md` may be awaiting dispatch or have had its worker dispatch interrupted; a kickoff with one may be awaiting review; pairs belonging to done tasks are settled history. Also list `.claude/artifacts/tmp/` for leftover scratch relevant to this department.
3. **Recent observations**: note any `ai-infrastructure/{{DEPT_SLUG}}/OBSERVATIONS.md` entries added since the last STATUS update.

## Phase 4: Report findings

Report in a structured shape:

- **Status**: current department phase and next step per `ai-infrastructure/{{DEPT_SLUG}}/STATUS.md`.
- **Tasks**: in-progress and blocked with one-line characterisations; backlog as id + title (from the department's own `./tasks/` tree).
- **Handoff and scratch artifacts**: each with a one-line characterisation; flag active vs settled or stale.
- **Observations and decisions**: brief synthesis of recent entries and any pending department ADRs ready to resolve.
- **Anything else**: notable inconsistencies (e.g., STATUS.md contradicting the task tree).

## Phase 5: Wait for direction

End the report by asking the user:

> Based on the survey above, what would you like to focus on?

Do NOT proactively act on any surveyed item. Orchestrator sessions are response-driven; the user chooses the entry point. Typical next directions:

- "Pick up `{{DEPT_TASK_PREFIX}}-T-NNN`" (or "complete / do `{{DEPT_TASK_PREFIX}}-T-NNN`") -> transition per `ORCHESTRATOR-ROLE.md` (section "Task lifecycle"), then **route the work through the "Dispatched-worker flow"**: for a deliverable task, resolve any residual decisions, draft and check the kickoff, run the prelaunch checker, dispatch the `worker-agent`, then close. Do NOT execute the deliverable yourself; only pure coordination tasks (ADR/STATUS/triage) are orchestrator-direct. When unsure, dispatch.
- "Block / unblock `{{DEPT_TASK_PREFIX}}-T-NNN`" -> transition with the reason captured in the activity log.
- "Resolve `{{DEPT_TASK_PREFIX}}-T-NNN`" -> commit gate per `ORCHESTRATOR-ROLE.md` (section "Task lifecycle"), then move to done.
- "Add a new task" -> allocate the next ID from `ai-infrastructure/{{DEPT_SLUG}}/tasks/.next-task-id`, draft in `ai-infrastructure/{{DEPT_SLUG}}/tasks/backlog/` per `ai-infrastructure/project-manager/tasks/README.md` (the per-workspace task convention), using the `{{DEPT_TASK_PREFIX}}-T-NNN` ID format.
- "Draft a kickoff for X" -> resolve anticipated decisions with the user, then run the drafter+checker dispatch loop per `ORCHESTRATOR-ROLE.md` (section "Drafter+checker dispatch loop"). Kickoff paths: `.claude/artifacts/handoffs/<TASK-OR-TOPIC>-KICKOFF.md`.
- "Execute the kickoff" (or proceeding after a kickoff passes the loop) -> run the "Dispatched-worker flow" per `ORCHESTRATOR-ROLE.md`: dispatch the prelaunch checker, dispatch the `worker-agent` (Sonnet, foreground), branch on its `RETURN: COMPLETED` / `RETURN: ESCALATION` verdict, then run the close checker and verify the report against disk.
- "Review the worker's output" -> the worker returns its report inline (and writes it to the derived `-REPORT.md` path); verify the report against the kickoff and the actual file state, independently re-deriving its claims.
- "Resolve a pending ADR" -> read the pending ADR, frame the alternatives with the user, fill in the decision.
- "Promote a logged observation" -> propose the guide, spec, ADR, or check it should become.

## Notes

- Scratch artifacts in `.claude/artifacts/tmp/` are safe to delete once consumed, but do not delete unless the user explicitly asks. Handoff artifacts in `.claude/artifacts/handoffs/` are tracked history and are not deleted (ADR-024).
- If you notice a pattern that looks like a new observation candidate, flag it to the user rather than silently logging it. Promotion is a user-aware decision, not a silent side effect.
- Tasks live in markdown per `ai-infrastructure/project-manager/tasks/README.md` until the dogfood milestone (ADR-008); after migration, task operations move to the MCP server (ADR-004) and this command gets updated.
- Update `ai-infrastructure/{{DEPT_SLUG}}/STATUS.md` at the end of any session that makes progress (universal hygiene: bump `last_updated`, append a `recent_updates` entry).
- Tasks are tracked in `ai-infrastructure/{{DEPT_SLUG}}/tasks/` (ADR-031). The `dept:{{DEPT_SLUG}}` label is applied at the dogfood import (ADR-008), derived from the tree; do not hand-apply it to task files in the markdown era.
