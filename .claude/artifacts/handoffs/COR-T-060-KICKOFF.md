# COR-T-060: ADR-046 follow-on - make the worktree workflow usable by dispatched executors and at the resolve gate

## Target

This is AI-infrastructure work (domain 2, ADR-005). It refines the worktree-per-session git workflow established by ADR-046 so that two cases it did not anticipate are documented and consistent: a dispatched executor subagent that cannot call the harness worktree tools, and the resolve gate where untracked handoff artifacts and the task-tree move must be committed without breaking the unconditional worktree-first hard gate. The work touches four coordination-surface docs: `docs/ai-orchestration/roles/EXECUTOR-ROLE.md`, `docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md`, `GIT_WORKFLOW.md`, and `./CLAUDE.md`. No code, no compose run.

These three gaps surfaced on the first real firing of the dispatched-executor path (the COR-T-059 execution; see its report under References). The orchestrator has resolved all three with the user; the resolutions are pinned below. Do not re-investigate or reopen them.

## Decisions resolved by the Orchestrator

- **Gap 1 - dispatched executors use plain git, not the harness worktree tools.** A dispatched executor subagent cannot call `EnterWorktree` / `ExitWorktree`; the harness refuses with "cannot create a worktree from a subagent with a cwd override". `EnterWorktree` / `ExitWorktree` is the interactive-session path. A dispatched subagent uses the equivalent plain-git commands: create with `git worktree add <abs-path>/.claude/worktrees/<branch> -b <branch> <base>`, edit through absolute paths inside that worktree, commit on the feature branch, and leave the worktree on disk for the orchestrator (no `ExitWorktree`). This must be documented so the orchestrator no longer improvises a per-dispatch "GIT HANDLING" block.

- **Gap 2a - under the worktree workflow the executor commits on its feature branch.** The current EXECUTOR-ROLE.md rule "Stage, do not commit ... Commits happen at the Orchestrator's commit gate when the task resolves ..." conflicts with the worktree workflow, which needs a committed feature branch for `bin/git-integrate` to merge. Pinned resolution: under the worktree workflow the executor commits its work on its feature branch inside the worktree. This does not violate the commit gate, because those commits never reach `master`; integration into `master` stays the orchestrator's gated `bin/git-integrate` step. The executor still never runs `bin/git-integrate` and never pushes.

- **Gap 2b - handoff artifacts and the task-tree move route through a worktree.** The kickoff and the executor report are authored as untracked files in the main checkout's `.claude/artifacts/handoffs/`, so a fresh worktree cannot see them and they cannot be committed at the resolve gate without either a copy-into-worktree step or a forbidden direct main-checkout commit. Pinned decision (user, 2026-06-29): keep the unconditional hard gate; route handoff-artifact and task-tree commits through a worktree. Do not re-permit direct main-checkout coordination commits. The documented resolve procedure: the executor's dual-channel report is written into its own worktree and committed on the feature branch; the orchestrator's resolve gate copies the untracked kickoff into a resolve worktree, `git add`s it alongside the in-progress-to-done task-tree move, and commits there before integrating.

- **Hard-gate mechanism broadened, gate unchanged.** The `./CLAUDE.md` "Git workflow" hard gate currently says to "switch to a worktree first (via `EnterWorktree`, branched from local `master` HEAD)". Clarify it so the gate is satisfied by either the harness `EnterWorktree` tool (interactive sessions) or the equivalent `git worktree add` commands (dispatched executor using git). The gate stays unconditional and worktree-first; only the mechanism is broadened. Do not weaken the gate, do not add an exception, do not re-permit edits in the main checkout.

## Deliverables

- **`docs/ai-orchestration/roles/EXECUTOR-ROLE.md`**, three changes:
  1. Reword the "Stage, do not commit." bullet under "Universal conventions" to the Gap-2a resolution: under the worktree workflow the executor commits on the feature branch inside the worktree; those commits never reach `master`; the executor never runs `bin/git-integrate`; never pushes; integration into `master` stays the orchestrator's gate.
  2. Add a short "Worktree handling (dispatched executor)" subsection giving the Gap-1 git-command procedure: create with `git worktree add <abs-path>/.claude/worktrees/<branch> -b <branch> <base>`, edit through absolute paths, commit on the branch, leave the worktree on disk for the orchestrator, never call `EnterWorktree` / `ExitWorktree` (they are refused in a dispatched subagent), never run `bin/git-integrate`.
  3. Point the dual-channel report write (the "Dual-channel: print to chat AND write to file" subsection under "Report shape") into the executor's own worktree on the feature branch per Gap 2b, rather than into the main checkout. The derived path `<kickoff-dir>/<KICKOFF-BASENAME>-REPORT.md` is unchanged; it now resolves inside the worktree and is committed on the feature branch.

- **`docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md`**, two changes:
  1. In the "Dispatched-worker flow" close step (step 7) and/or the "Task lifecycle" Resolve bullet, document the Gap-2b resolve procedure: copy the untracked kickoff into a resolve worktree, `git add` it alongside the in-progress-to-done task-tree move, commit there, then integrate with `bin/git-integrate`. Never a direct main-checkout coordination commit.
  2. Note that dispatched executors use the plain git-worktree commands (Gap 1), so the orchestrator does not need a bespoke per-dispatch "GIT HANDLING" block.

- **`GIT_WORKFLOW.md`**: add a note distinguishing the interactive path (`EnterWorktree` / `ExitWorktree`) from the dispatched-subagent path (plain `git worktree add` / `git worktree remove`), per Gap 1. ADD only; do not redo or revert the COR-T-059 cleanup-ordering changes already present on the base branch (see Hard rules).

- **`./CLAUDE.md`**: clarify the "Git workflow" section's hard-gate sentence so the gate is satisfied by either `EnterWorktree` (interactive) or the equivalent `git worktree add` (dispatched subagent). Keep the gate unconditional and worktree-first; do not weaken it.

## Files in scope

- `docs/ai-orchestration/roles/EXECUTOR-ROLE.md`
- `docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md`
- `GIT_WORKFLOW.md`
- `./CLAUDE.md`

## Files out of scope

- `ai-infrastructure/project-manager/decisions/ADR-046-concurrent-session-git-workflow-worktrees-enforced-merge-lock.md` (read-only context; the orchestrator adds the forward-pointer note itself, ADRs are orchestrator-direct).
- `bin/git-integrate`, `bin/seed-worktree`, `.githooks/pre-commit`, `.githooks/pre-merge-commit` (unchanged).
- The COR-T-059 cleanup-ordering changes already present in `GIT_WORKFLOW.md` on the base branch (the 9-step Flow, the `ExitWorktree {action: "keep"}` step, the exact teardown commands). Do not touch them.
- The harness `EnterWorktree` / `ExitWorktree` tools themselves (harness-owned).

## References

- `.claude/artifacts/handoffs/COR-T-059-KICKOFF-REPORT.md` - the executor report whose "Surprises" and "Follow-ups" sections are the evidence for both gaps (the `EnterWorktree` refusal and the `git worktree add` workaround it used).
- `docs/ai-orchestration/roles/EXECUTOR-ROLE.md` - the file you edit; the bullet to reword reads exactly: "Stage, do not commit. Surface changes for review. Commits happen at the Orchestrator's commit gate when the task resolves, or earlier only when the user explicitly asks. Never push." (under "Universal conventions"). The report-write target lives under "Report shape" -> "Dual-channel: print to chat AND write to file".
- `docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md` - the file you edit; sections "Task lifecycle" (Resolve bullet) and "Dispatched-worker flow" (close step 7).
- `GIT_WORKFLOW.md` - the file you edit; "Flow" and "Enforcement" sections. On the base branch this already carries COR-T-059's 9-step Flow.
- `./CLAUDE.md` - the file you edit; "Git workflow" section (the sentence naming `EnterWorktree`).
- `ai-infrastructure/project-manager/decisions/ADR-046-concurrent-session-git-workflow-worktrees-enforced-merge-lock.md` - the governing decision being refined (read-only). Decision item 1 is the worktree-creation flow this work clarifies for the dispatched case.

## Related tasks and ADRs

- ADR-046 - the worktree-per-session workflow being refined for the dispatched-agent and resolve-gate cases.
- COR-T-059 - the cleanup-ordering fix whose dispatched-executor firing surfaced these gaps; its deliverable is the base branch this work stacks on.
- COR-T-057 - implemented ADR-046.
- COR-T-058 - fixed the seed-worktree hook bug (same worktree family).
- COR-10 (`ai-infrastructure/project-manager/OBSERVATIONS.md`) - seam-contract mismatch visible only on a real firing; this papercut family is kin.

## Hard rules

- **Branch your worktree from `cor-t-059-impl`, not from `master`.** This work stacks on COR-T-059, which is not yet integrated into `master`. The COR-T-059 cleanup-ordering changes (the 9-step Flow, the `ExitWorktree {action: "keep"}` step, the exact teardown commands) live only on that branch; you must branch from it so `GIT_WORKFLOW.md` already contains them. Your `git worktree add` base is `cor-t-059-impl`.
- **You are the Gap-1 procedure you are documenting.** You are a dispatched executor, so you cannot call `EnterWorktree` / `ExitWorktree`; the harness will refuse. Create your worktree with `git worktree add <abs-path>/.claude/worktrees/<branch> -b <branch> cor-t-059-impl`, edit through absolute paths inside it, and commit on the feature branch. This is exactly the procedure you are writing into the docs; execute it as you document it.
- **Do not redo or revert the COR-T-059 changes in `GIT_WORKFLOW.md`.** Only ADD the interactive-vs-dispatched note. The 9-step Flow and the teardown commands are already correct on the base branch.
- **Keep the hard gate unconditional.** Every edit to `./CLAUDE.md` and `GIT_WORKFLOW.md` broadens the worktree-creation mechanism only. Do not weaken the gate, do not add a "too minor to branch" exception, do not re-permit direct main-checkout coordination commits.
- **Cross-file consistency.** After editing, the Gap-1 git-command procedure in `EXECUTOR-ROLE.md`, the dispatched-path note in `GIT_WORKFLOW.md`, and the broadened hard-gate sentence in `./CLAUDE.md` must agree on the same `git worktree add`-based mechanism; and the Gap-2b resolve procedure in `ORCHESTRATOR-ROLE.md` must match the report-into-worktree change in `EXECUTOR-ROLE.md`.

## Verification expectations

- Re-read each of the four edited files end-to-end for internal consistency. Confirm the three Gap-1 surfaces (`EXECUTOR-ROLE.md` procedure, `GIT_WORKFLOW.md` dispatched-path note, `./CLAUDE.md` broadened sentence) describe the same `git worktree add`-based mechanism, and confirm the Gap-2b resolve procedure in `ORCHESTRATOR-ROLE.md` matches the report-into-worktree change in `EXECUTOR-ROLE.md`.
- Confirm the `./CLAUDE.md` and `GIT_WORKFLOW.md` hard gate remains unconditional and worktree-first after the edit (mechanism broadened, gate not weakened).
- Confirm no COR-T-059 content in `GIT_WORKFLOW.md` was changed or removed (only the new dispatched-path note was added).
- No em dashes in any of the four files (repo writing rule, `./CLAUDE.md`).
- No code change and no compose run is involved.

## Executor pointer

The executor is the dispatched `executor` (ADR-028). Universal executor conventions live in `docs/ai-orchestration/roles/EXECUTOR-ROLE.md`. The closing report is written to `.claude/artifacts/handoffs/COR-T-060-KICKOFF-REPORT.md` per that doc's "Report shape" section; per the Gap-2b change you are making, that path resolves inside your worktree and is committed on your feature branch.
