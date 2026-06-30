---
schema_version: 1
id: COR-T-060
title: "ADR-046 follow-on: make the worktree workflow usable by dispatched executors and at the resolve gate"
status: done
labels: []
priority: P2
created: 2026-06-29
updated: 2026-06-30
---

## Description

The ADR-046 worktree-per-session workflow (`GIT_WORKFLOW.md`, `bin/git-integrate`, the `.githooks/`, the unconditional worktree-first hard gate in `./CLAUDE.md` from commit `5592cc4`) was written for interactive sessions driving the harness `EnterWorktree`/`ExitWorktree` tools. Two gaps surfaced on the first real firings of the dispatched-executor path (COR-T-059 execution, session-reviewed alongside `79f3e0a0` and `18483dae`): the workflow as documented is not actually followable by a dispatched executor subagent, and the handoff-artifact + task-tree commit step at the resolve gate does not compose with the hard gate. This task reconciles the docs so both paths are followable without ad hoc per-dispatch instructions.

### Gap 1: dispatched executors cannot use EnterWorktree/ExitWorktree

The COR-T-059 executor (a dispatched subagent) tried `EnterWorktree` and got refused: "cannot create a worktree from a subagent with a cwd override." It fell back to `git worktree add /abs/path/.claude/worktrees/<branch> -b <branch> master`, edited via absolute paths, committed on the branch, and left the worktree on disk (no `ExitWorktree`). So `GIT_WORKFLOW.md` and `./CLAUDE.md` describe a harness-tool flow that a dispatched executor structurally cannot follow; today the orchestrator has to improvise a per-dispatch "GIT HANDLING" block (as it did for COR-T-059) to tell the executor to use raw git instead.

Pinned resolution: the `EnterWorktree`/`ExitWorktree` flow is the interactive-session path; dispatched subagents use the equivalent plain-git commands. Document the dispatched-executor worktree procedure in `docs/ai-orchestration/roles/EXECUTOR-ROLE.md` (git-command create, edit via absolute paths, commit on the branch, leave the worktree on disk for the orchestrator) so no per-dispatch improvisation is needed, and note the interactive-vs-dispatched split in `GIT_WORKFLOW.md`.

### Gap 2a: "stage, do not commit" vs the mandatory commit-in-worktree

`docs/ai-orchestration/roles/EXECUTOR-ROLE.md` line ~58 says "Stage, do not commit. Commits happen at the Orchestrator's commit gate." But the worktree workflow needs a committed feature branch for `bin/git-integrate` to merge (a subagent-scoped worktree's staged-but-uncommitted changes are not durable). The two rules are in tension.

Pinned resolution: under the worktree workflow the executor COMMITS its work on its feature branch inside the worktree. This does not violate the commit-gate: those commits never reach master; integration into master remains the orchestrator's gated `bin/git-integrate` step. Reword the EXECUTOR-ROLE.md rule to say exactly this (commit on the feature branch; never integrate; master stays the orchestrator's gate).

### Gap 2b: handoff artifacts + task-tree commits do not compose with the hard gate

The kickoff (authored by `kickoff-drafter`) and the executor's report (dual-channel write) are written as UNTRACKED files in the main checkout's `.claude/artifacts/handoffs/`. Under the hard gate, those files are invisible to any fresh worktree, so committing them at the resolve gate (ADR-024 requires the kickoff/report pair be committed at resolve) requires either a copy-into-worktree step or a direct main-checkout commit.

Pinned decision (user, 2026-06-29): KEEP the hard gate; route these commits THROUGH a worktree. Do NOT re-permit direct main-checkout coordination commits (that would re-add the coordination-edit exception `5592cc4` deliberately removed and reintroduce the concurrent-main-checkout-conflict risk for those commits). Concretely:
- The executor writes its dual-channel report INTO its own worktree and commits it on the feature branch (so the report rides the same merge as the deliverable), rather than writing it to the main checkout.
- The orchestrator's resolve gate copies the untracked kickoff into a resolve worktree, `git add`s it alongside the task-tree move (in-progress -> done), and commits there, then integrates. Document this resolve procedure in `docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md` ("Dispatched-worker flow" close step / "Task lifecycle" Resolve step).

### Deliverables

- `docs/ai-orchestration/roles/EXECUTOR-ROLE.md`: reconcile the stage-vs-commit rule (Gap 2a), add the dispatched-executor git-worktree procedure (Gap 1), and point the dual-channel report write into the worktree branch (Gap 2b).
- `docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md`: document the resolve-gate procedure that routes the kickoff + task-tree-move commit through a worktree (Gap 2b), and that dispatched executors use git-worktree commands (so the orchestrator does not need a per-dispatch GIT HANDLING block).
- `GIT_WORKFLOW.md`: note the interactive (`EnterWorktree`/`ExitWorktree`) vs dispatched-subagent (plain git worktree commands) split (Gap 1).
- `./CLAUDE.md`: confirm the hard gate is satisfied by either the harness tool or the equivalent git worktree commands (so a dispatched executor using `git worktree add` is compliant), keeping the gate unconditional.
- A forward-pointer note in `ai-infrastructure/project-manager/decisions/ADR-046-concurrent-session-git-workflow-worktrees-enforced-merge-lock.md` recording this refinement (the dispatched-executor + resolve-gate mechanics) and pointing to this task and the updated docs (orchestrator-direct; the amendment lives in the docs per the owned-but-advisory convention).

Out of scope: changing the merge-lock, the `--no-ff` policy, the enforcement hooks, or the harness `EnterWorktree`/`ExitWorktree` tools themselves (harness-owned). No change to the COR-T-059 cleanup-ordering fix (held on branch `cor-t-059-impl`, to be landed together with this work).

## Activity log

- 2026-06-29: Created and picked up (in-progress) by the project-manager orchestrator. Triaged from two gaps the COR-T-059 dispatched-executor firing surfaced (recorded in the COR-T-059 report Follow-ups): EnterWorktree/ExitWorktree are unavailable to dispatched subagents, and handoff-artifact/task-tree commits do not compose with the `5592cc4` hard gate. Same family as COR-T-057/058/059 and the COR-10 observation (seam friction visible only on a real firing). Decisions pinned with the user 2026-06-29: hold COR-T-059 and land it together with these fixes; keep the hard gate and route handoff-artifact + task-tree commits through a worktree (gate-preserving), not via direct main-checkout commits. Gap-1 and gap-2a resolutions are forced/mechanical (git-command path; commit-on-feature-branch). P2: not phase-blocking, but it sits on every future dispatched task's path. Standalone (no epic): repo-global workflow tooling, like COR-T-057/058/059.
- 2026-06-30: Done. Kickoff drafted (PASS) and the dispatched executor ran clean (kickoff/prelaunch/close checkers all PASS; orchestrator disk re-derivation confirmed cross-file consistency, an unconditional hard gate, no COR-T-059 regression in `GIT_WORKFLOW.md`, and all cited section names resolving). Deliverable committed `d517ed5` (+ report-hash fixup `49445c7`): `EXECUTOR-ROLE.md` (commit-on-feature-branch reword; new "Worktree handling (dispatched executor)" section; report-into-worktree path note), `ORCHESTRATOR-ROLE.md` (Gap-2b resolve-gate-worktree note + dispatched-executor git-command note), `GIT_WORKFLOW.md` step 2 (interactive-vs-dispatched split), `CLAUDE.md` hard-gate mechanism broadened (gate stays unconditional). Stacked on COR-T-059 and landed together on `master` via merge `155963b`. ADR-046 Consequences item 11 (forward-pointer note) added with this resolution; kickoff/report pair committed (ADR-024; the report rode the feature branch per the new Gap-2b behavior, the kickoff via the resolve worktree). The executor's report Follow-up (cross-reference the new section from `executor.md` / `EXECUTOR-AGENT-SPEC.md`) is left for orchestrator triage.
