---
schema_version: 1
adr: 47
title: "Single-worktree task resolve: the resolve-gate commit lands on the deliverable's feature branch"
status: "accepted"
date: "2026-06-30"
related_adrs: [23, 24, 28, 46]
supersedes: []
superseded_by: null
---

# ADR-047: Single-worktree task resolve: the resolve-gate commit lands on the deliverable's feature branch

## Context

ADR-046 established worktree-per-session with trunk-based integration behind an enforced merge lock. Its resolve-gate procedure (the "Gap-2b" note, recorded in ADR-046 forward-pointer item 11c and in `docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md` "Dispatched-worker flow" step 7) routed a task's resolve-gate commit -- the untracked kickoff plus the in-progress-to-done task-tree move -- through a SEPARATE short-lived "resolve worktree" created from `master` after the deliverable had been integrated.

For a dispatched task this produces **two worktrees and two merges per task**: the executor's deliverable worktree (merge 1) and the orchestrator's resolve worktree (merge 2). Verified live on DB-T-006 (session `13d596a8-a094-4020-8fe6-a22762c13998`), 2026-06-30: branch `db-t-006` (deliverable, merged `0dc5e70`) and branch `db-t-006-resolve` (resolve, merged `91e979a`) -- two worktrees and two integrates for a single task. The operator flagged this as a hard block on all other work.

The second worktree is structurally unnecessary. ADR-046 Gap-2b itself observes that the executor's dual-channel report is already committed on the feature branch; only the untracked kickoff and the task-tree move remain to be committed at resolve, and both can land on that same feature branch. The separate worktree existed only because the resolve was modeled as a step that happens AFTER the deliverable's own integration, rather than as the final commit on the deliverable's branch. This is the COR-11 friction family: each real firing of the worktree workflow surfaces one more friction, fixed forward in the same family (COR-T-057/058/059/060/061).

## Decision

The resolve-gate commit lands on the deliverable's own feature branch. **One worktree, one `bin/git-integrate`, one teardown per task.** The separate ADR-046 Gap-2b resolve worktree is retired.

- **Dispatched path.** The executor leaves its worktree on disk at `.claude/worktrees/<branch>` and does not integrate (unchanged). After the close checks pass and the user authorizes the commit, the Orchestrator operates in that existing worktree (via `git -C .claude/worktrees/<branch> ...` or `EnterWorktree {path: ...}`): it MOVES (not copies) the untracked kickoff from the main checkout's `.claude/artifacts/handoffs/` into the worktree and `git add`s it, `git mv`s the task file from `in-progress/` to `done/` inside the worktree, and commits the resolve on the feature branch (the done activity-log line cites the executor's deliverable commit, already on the branch). A single `bin/git-integrate <branch>` from the main checkout then carries the deliverable, the report, the kickoff, and the task move to `master` in one merge, followed by one teardown.

- **Orchestrator-direct path.** The deliverable was produced in the orchestrator's own worktree; the resolve-gate commit (task-tree move plus any kickoff) lands in that same worktree before the single integrate. No second worktree was ever needed on this path; this ADR makes that explicit and removes the "resolve worktree" instruction that implied otherwise.

MOVE rather than copy the untracked kickoff, preserving the COR-T-061 lesson: a leftover untracked copy at the same path in the main checkout makes `bin/git-integrate` abort with "untracked working tree files would be overwritten by merge" when the branch adds that path as a tracked file.

## Consequences

- One worktree and one merge per task; the second integrate and its merge commit are gone. This directly removes the friction the operator flagged on DB-T-006.
- The deliverable lands on `master` at resolve-time -- when the task is fully closeable -- rather than in an earlier standalone merge. `master` still receives only wrapped `--no-ff` merges through the lock; the always-green and contamination-isolation properties of ADR-046 are unchanged.
- The worktree-first hard gate (`./CLAUDE.md`) remains unconditional: the resolve commit happens inside a worktree, never the main checkout. This ADR changes WHICH worktree (the deliverable's, not a fresh one), not WHETHER a worktree is used.
- This amends ADR-046's resolve-gate procedure only (Gap-2b / forward-pointer item 11c). It does not change ADR-046's worktree-per-session decision, the enforced merge lock, or the `bin/git-integrate` wrapper. Per ADR-035's owned-but-advisory convention the procedural text lives in the workflow docs (`GIT_WORKFLOW.md`, `ORCHESTRATOR-ROLE.md`, `EXECUTOR-ROLE.md`); ADR-046 carries an appended forward pointer (item 12) to this ADR.
- COR-T-062, which records this decision, was itself executed under the new procedure: its deliverable and resolve both land on one branch (`cor-t-062`) through one merge, dogfooding the fix.
