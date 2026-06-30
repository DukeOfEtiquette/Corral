# COR-T-059: Reconcile ExitWorktree / git-integrate cleanup ordering in GIT_WORKFLOW.md and bin/git-integrate

## Target

This is AI-infrastructure work (ADR-005, domain 2). The artifacts in scope are the worktree-per-session workflow doc `./GIT_WORKFLOW.md` and the sanctioned merge wrapper `./bin/git-integrate`. The worktree workflow established by ADR-046 (and implemented in COR-T-057) has a cleanup-ordering papercut: the documented "delete the feature branch and worktree" step is ambiguous about the harness-owned `ExitWorktree` tool, and on the post-integrate path one `ExitWorktree` action refuses with a verification error that pushes the operator toward discarding already-merged work. This task clarifies the docs and the wrapper's printed guidance so the proven clean cleanup sequence is unambiguous. It changes no enforcement, no automation, and no decision.

## Decisions resolved by the Orchestrator

These are settled. Do not re-investigate them, re-derive the root cause, or reopen the scope.

- **Root cause is empirically pinned; do not re-investigate.** The harness `ExitWorktree {action: "remove"}` verification refuses with "Could not verify worktree state" when invoked AFTER `bin/git-integrate` has merged the feature branch, forcing a `discard_changes: true` override even though the work is already on master. `ExitWorktree {action: "keep"}` does NOT trigger this, and plain `git worktree remove` has no such check. Evidence across three sessions: sessions 79f3e0a0 and the COR-T-059 filing run both hit the refusal via `remove`; session 18483dae stayed clean via `keep`. You encode this conclusion; you do not reproduce it.
- **The proven clean cleanup sequence to codify** (observed in session 18483dae, the API-T-006 run): (1) commit all work inside the worktree; (2) `ExitWorktree {action: "keep"}` to return to the main checkout while preserving the branch (NOT `remove`); (3) run `bin/git-integrate <branch>` from the main checkout; (4) run `git worktree remove .claude/worktrees/<branch>` then `git branch -d <branch>` from the main checkout.
- **Scope is docs plus the git-integrate printed message ONLY** (user decision, 2026-06-29). No new automation: `bin/git-integrate` must NOT perform the teardown itself; it only improves the guidance it prints.
- **`ExitWorktree` is harness-owned and out of our control.** The entire fix lives in `./GIT_WORKFLOW.md` and `./bin/git-integrate`. Do not attempt to change, wrap, or work around the `ExitWorktree` tool.
- **Naming invariant the fix relies on.** `EnterWorktree` creates `.claude/worktrees/<name>` on a branch named `<name>`, so the worktree directory name equals the branch name. `bin/git-integrate` may therefore reference `.claude/worktrees/$FEATURE_BRANCH` when it prints the teardown commands.

## Deliverables

- **`./GIT_WORKFLOW.md`: revise the "Flow" section so cleanup is unambiguous.**
  - (a) Add an explicit step, ahead of the integrate step (current step 6), to leave the worktree with `ExitWorktree {action: "keep"}` (preserving the branch) and return to the main checkout BEFORE integrating.
  - (b) In the teardown step (current step 8), prescribe the exact commands run from the main checkout: `git worktree remove .claude/worktrees/<branch>` and `git branch -d <branch>`.
  - (c) Add an explicit caution NOT to use `ExitWorktree {action: "remove"}` on the post-integrate path, because its verification refuses with "Could not verify worktree state" and pushes toward a `discard_changes: true` override even when the work is already merged.
  - Preserve the existing ADR-046 rationale-footer reference at the bottom of the file.
- **`./bin/git-integrate`: improve the printed teardown guidance.** Replace the vague closing line `echo "Next steps: delete the feature branch and remove its worktree."` with output that prints the exact teardown commands to run from the main checkout, using `$FEATURE_BRANCH` for both the worktree path (`.claude/worktrees/$FEATURE_BRANCH`) and the branch name. Do NOT add teardown execution; improve the printed guidance only. The closing `echo "Merge complete. '$FEATURE_BRANCH' integrated into master."` line and the script's existing behaviour (locking, merge, sanity checks) stay unchanged.

## Files in scope

- `./GIT_WORKFLOW.md`
- `./bin/git-integrate`

## Files out of scope

- `./.githooks/pre-commit` and `./.githooks/pre-merge-commit` (enforcement hooks, working as designed)
- `./.claude/settings.json` (the `WorktreeCreate` hook and `worktree.baseRef`, unchanged)
- The merge-lock mechanism and the `--no-ff` policy (unchanged)
- `./ai-infrastructure/project-manager/decisions/ADR-046-concurrent-session-git-workflow-worktrees-enforced-merge-lock.md` (no decision change; only its workflow doc is being clarified)
- `./bin/seed-worktree` (unchanged)

## References

- `./ai-infrastructure/project-manager/decisions/ADR-046-concurrent-session-git-workflow-worktrees-enforced-merge-lock.md` (the workflow this clarifies; `./GIT_WORKFLOW.md`'s footer already points here)
- `./GIT_WORKFLOW.md`, "Flow" steps 6-8 plus the "Enforcement" and "Lock file" sections (the surface to edit)
- `./bin/git-integrate`, closing lines `echo "Merge complete. '$FEATURE_BRANCH' integrated into master."` followed by `echo "Next steps: delete the feature branch and remove its worktree."` (the message to improve)

## Related tasks and ADRs

- ADR-046 - the worktree-per-session workflow being clarified
- COR-T-057 - implemented ADR-046 (the workflow doc, git-integrate, the hooks)
- COR-T-058 - fixed the seed-worktree hook bug (a prior ADR-046 papercut in the same family)
- COR-10 (`./ai-infrastructure/project-manager/OBSERVATIONS.md`) - seam-contract mismatch visible only on a real firing; this papercut is kin

## Hard rules

- **No new automation in `bin/git-integrate`.** The script prints improved guidance and nothing more. It must not run `git worktree remove`, `git branch -d`, or any teardown command itself. Adding execution is out of scope and reverses the user's decision.
- **Do not touch the `ExitWorktree` tool or attempt to work around it.** It is harness-owned. The fix is documentation and printed-string changes only.
- **Keep the script parseable and its existing behaviour intact.** Only the closing guidance message changes; locking, the `--no-ff` merge, and the sanity checks are unchanged.
- **Internal consistency between the two artifacts.** The keep-before-integrate step you add to `./GIT_WORKFLOW.md`, the teardown commands in its teardown step, and the teardown commands `bin/git-integrate` prints must all agree (same `ExitWorktree {action: "keep"}` guidance, same `git worktree remove .claude/worktrees/<branch>` and `git branch -d <branch>` commands).

## Verification expectations

- Run `bash -n bin/git-integrate` to confirm the script still parses after the message change.
- Re-read the revised `./GIT_WORKFLOW.md` "Flow" section for internal consistency: the keep-before-integrate step and the teardown commands agree, and the no-`remove` caution is present.
- A full end-to-end worktree cycle is NOT required of you. The Orchestrator verifies against disk at close.

## Executor pointer

The executor is the dispatched `executor` (ADR-028). Universal executor conventions (the six-section report shape, dual-channel write, the writing rules and git boundaries in `./CLAUDE.md`, the compose run policy) live in `./docs/ai-orchestration/roles/EXECUTOR-ROLE.md`; reference them rather than re-deriving them. Write the closing report to `./.claude/artifacts/handoffs/COR-T-059-KICKOFF-REPORT.md` per EXECUTOR-ROLE.md, section "Report shape".
