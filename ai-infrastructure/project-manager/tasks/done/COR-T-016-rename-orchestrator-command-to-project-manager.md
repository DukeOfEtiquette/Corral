---
schema_version: 1
id: COR-T-016
title: "Rename the coordinator orchestrator command to /project-manager-orchestrator"
status: done
labels: [dept:agent-development]
priority: P2
created: 2026-06-10
updated: 2026-06-10
epic: COR-E-001
---

## Description

Rename the coordinator's instantiation command from `/corral-orchestrator` to `/project-manager-orchestrator`, and its user-facing role name from "Corral Orchestrator" to "Project Manager Orchestrator", to match the `/<slug>-orchestrator` convention established for departments (ADR-021, ADR-030; the coordinator workspace slug is `project-manager`). The current name is the lone command named after the repo rather than its workspace, which misleadingly implies `/corral-orchestrator` is the project-manager. This is a naming/consistency fix, not a behaviour change; no new ADR (it is alignment with an accepted convention).

Resolved decisions (pinned by the orchestrator with the user, 2026-06-10):

- New command/skill name: `/project-manager-orchestrator`. The skill name derives from the command filename, so the `git mv` renames both.
- Role display name becomes "Project Manager Orchestrator" everywhere the coordinator's own name appears (the command file, and the `ORCHESTRATOR-ROLE.md` Instantiation section).
- `worker-agent.md`'s two "Corral Orchestrator" mentions are generalised to "the Orchestrator", NOT pinned to "Project Manager Orchestrator": the `worker-agent` is the universal worker dispatched by every orchestrator (coordinator and departments, ADR-028/ADR-029), so naming one orchestrator there would be inaccurate.
- ADRs (023, 024, 028, 030) keep their historical `/corral-orchestrator` references unchanged: ADRs are append-only, and the precedent is the `/corral-worker` references left intact across ADR-023/024/028 when that command was deleted (COR-T-015). Same for settled history: STATUS `recent_updates` lines, the COR-T-012/013 handoff pairs, the done COR-T-015 task.
- The current-state STATUS narrative line (Current phase section) is updated as a task-specific STATUS delta.

Live edit set: `.claude/commands/corral-orchestrator.md` (git mv + the description/heading/role-name lines), `docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md` (command refs + the Instantiation role name), `docs/ai-orchestration/roles/WORKER-ROLE.md` (the one command ref), `.claude/agents/worker-agent.md` (two generic mentions), `ai-infrastructure/project-manager/STATUS.md` (Current-phase narrative + universal hygiene). Routed through the dispatched-worker flow per the routing rule (command + role-doc edits are deliverables).

## Activity log

- 2026-06-10: Created in backlog. New consistency task (not an ADR-027 follow-on); surfaced by the user as a naming gap: the coordinator command is still `/corral-orchestrator` while the `/<slug>-orchestrator` convention (ADR-030) implies `/project-manager-orchestrator`.
- 2026-06-10: Picked up; moved to in-progress. Decisions resolved with the user (display name changes to "Project Manager Orchestrator"; `worker-agent.md` generalised to "the Orchestrator"; ADRs and settled history untouched). Routing through the dispatched-worker flow next.
- 2026-06-10: Executed via the dispatched-worker flow. Kickoff drafted+checked (PASS), prelaunch PASS (W1), worker returned COMPLETED, close PASS (W2); the orchestrator re-derived every claim against disk. Deliverables and coordination artifacts (the renamed command, `worker-agent.md`, both role docs, STATUS.md, `.next-task-id`, the kickoff/report pair) committed as a617888. At the user's direction, also generalised the `WORKER-ROLE.md` "Not in scope" bullet to any `/<slug>-orchestrator` (an orchestrator-direct exception to the deliverable-routing rule, folded into a617888). Moved to done; this task-resolution move committed separately.
