---
schema_version: 1
id: COR-T-015
title: "Port the dispatched worker-agent flow (ADR-028); retire /corral-worker"
status: done
labels: [dept:agent-development]
priority: P2
created: 2026-06-09
updated: 2026-06-09
epic: COR-E-001
---

## Description

Implement ADR-028: replace the parallel human-driven `/corral-worker` session with an
orchestrator-dispatched `worker-agent` subagent. The orchestrator dispatches the worker directly via
the Task tool (`model: sonnet`, foreground) after drafting and checking a kickoff; the user interacts
only with the orchestrator. Port the design from Corral's exemplar (rogue ADR-025 and the rogue
`worker-agent`), de-rogued for Corral. Land files at their current paths now; the pending COR-T-012
restructure carries them to their final home.

Reference sources (rogue, the exemplar per ADR-009):

- `~/rogue/.claude/agents/worker-agent.md` (the universal agent file)
- `~/rogue/.claude/agents/specs/WORKER-AGENT-SPEC.md` (the execution spec: inputs, phases, return schemas)
- `~/rogue/docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md` §Dispatched-worker flow (the 7-step sequence)
- `~/rogue/ai-workspaces/project-manager/decisions/ADR-025-worker-as-universal-orchestrator-dispatched-subagent.md`

### Deliverables

1. **`./.claude/agents/worker-agent.md`** - universal dispatched-worker agent, de-rogued: workspace
   name `corral`; reads `./docs/ai-orchestration/roles/WORKER-ROLE.md`; two verdict-lined return modes
   (`RETURN: COMPLETED` / `RETURN: ESCALATION`); leaf node (no subagent dispatch); Sonnet, foreground.
2. **`./.claude/agents/specs/WORKER-AGENT-SPEC.md`** - the execution spec (inputs incl. `explicit_reads`,
   workflow phases, both return schemas, STATUS-once rule, error handling), de-rogued. Match the format
   of the existing specs in `./.claude/agents/specs/`.
3. **`./docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md`** - add a `§Dispatched-worker flow` section:
   the routing rule (deliverable work routes to a dispatched worker; the orchestrator edits only its
   own coordination surface directly), the 7-step sequence (draft+check -> orchestrator-run prelaunch
   -> dispatch worker -> branch on verdict -> orchestrator-run close -> verify against disk -> close
   discipline), and the spike-grounded mechanics. Adapt close discipline to Corral's markdown `tasks/`
   lifecycle (stage changes, orchestrator commits at the gate, task move backlog->done), NOT rogue's
   GitHub `closes #N`.
4. **`./docs/ai-orchestration/roles/WORKER-ROLE.md`** - add the Identity-delta note for the dispatched
   path: the worker returns to the orchestrator (not the user), escalates by return value (not by
   asking), and runs no checker subagents (the orchestrator runs prelaunch/close).
5. **`./.claude/commands/corral-orchestrator.md`** - wire the dispatched-worker flow into the
   "Draft a kickoff for X" / "Review the worker session's output" directions in Phase 5, pointing at
   the new `ORCHESTRATOR-ROLE.md §Dispatched-worker flow`.
6. **Delete `./.claude/commands/corral-worker.md`** and sweep dangling references to it
   (`grep -rn 'corral-worker' .`), including the `/corral-worker` mentions in `WORKER-ROLE.md`,
   `ORCHESTRATOR-ROLE.md`, and any agent/spec files.

### Acceptance

- `grep -rn 'corral-worker' .` returns no live references (only historical ADR/STATUS/task mentions).
- `grep -rn 'worker-agent' .` shows the agent wired into the orchestrator role doc and command.
- No em dashes in any authored file (CLAUDE.md writing rule).
- The dispatched-worker flow documents: explicit context pass-down, leaf-node (orchestrator-run
  checkers), return-and-re-dispatch escalation with a 2-round-trip ceiling, verify-against-disk, and
  Corral-native (markdown `tasks/`) close discipline.

## Related tasks and ADRs

- ADR-028 (this task's decision): worker as dispatched subagent; retire `/corral-worker`.
- ADR-023 (dispatch loop day zero): the checker fleet the worker joins; orchestrator as dispatcher.
- ADR-024 (git-tracked handoff artifacts): kickoff/report paths under `./.claude/artifacts/handoffs/`.
- ADR-009 (rogue conventions): the exemplar source; gains the ADR-028 forward-pointer note.
- COR-T-012 (pending restructure): will relocate these files; land at current paths now.

## Activity log

- 2026-06-09: Created in backlog. Queued from ADR-028 (accepted same day) as its implementation task.
- 2026-06-09: Picked up; moved to in-progress. Executed directly (not via /corral-worker, which this task retires).
- 2026-06-09: Done. Decision committed as ce414d5 (ADR-028 acceptance); implementation committed in this same task's implementation commit (the COR-T-015 deliverables, the /corral-worker deletion, and this done-move are folded into it at the user's two-commit request, rather than a separate move-to-done commit). All six deliverables complete. Created `worker-agent.md` + `WORKER-AGENT-SPEC.md`; added ORCHESTRATOR-ROLE.md "Dispatched-worker flow"; reframed WORKER-ROLE.md (Identity deltas + checkers orchestrator-run, replacing the "Worker-side checker dispatch" section); repointed the prelaunch/close checker agents+specs and the kickoff-drafter/checker Worker-pointer convention; wired /corral-orchestrator; deleted /corral-worker. Acceptance: `grep -rn 'corral-worker'` shows no live references (only ADR-028/009/023, STATUS, task, and frozen handoff history); em-dash clean (one pre-existing intentional detection regex in KICKOFF-CHECKER-SPEC.md). Awaiting commit gate before done-move.
- 2026-06-10: Relabeled dept:ai-infra -> dept:agent-development per ADR-018 (COR-T-008): ai-infra is a domain not a department (ADR-021), so dept:ai-infra was invalid taxonomy. Label-only edit; task otherwise unchanged.
