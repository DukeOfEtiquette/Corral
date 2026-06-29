---
schema_version: 1
id: COR-T-059
title: "Reconcile ExitWorktree / git-integrate ordering so worktree cleanup does not require a discard_changes override"
status: in-progress
labels: []
priority: P2
created: 2026-06-29
updated: 2026-06-29
---

## Description

The ADR-046 worktree-per-session workflow (`GIT_WORKFLOW.md`, `bin/git-integrate`, `.githooks/`, the `WorktreeCreate` seed hook in `.claude/settings.json`) has a papercut on its cleanup happy path: after a clean `bin/git-integrate`, the harness `ExitWorktree` tool refuses the first `action: remove` and forces a `discard_changes: true` override. The override is safe in the integrate-then-exit case (the work is already on `master`), but our sanctioned success path should not route through a "discard" flag, and an agent that learns "ExitWorktree refused -> add discard_changes: true" can carry that reflex to a worktree with genuinely un-integrated work and lose it.

### Observed instance (the trigger)

Session `79f3e0a0-2398-4676-80dc-3ddc9feacf52` (a `/backend-api-orchestrator` run) executed the workflow correctly end to end: research in main checkout, `EnterWorktree`, edit + commit in the worktree (`c7af286`), `bin/git-integrate api-stale-xref-fix` from the main checkout (merge `32ebb07`, flock acquired, sanity check passed), then cleanup. At cleanup:

```
ExitWorktree {action: "remove"}
  -> "Could not verify worktree state at <path>. Refusing to remove
      without explicit confirmation. Re-invoke with discard_changes: true
      -- or use action: \"keep\" to preserve the worktree."
ExitWorktree {action: "remove", discard_changes: true}   -> succeeded
git branch -d api-stale-xref-fix                          -> deleted (was c7af286)
```

Note the refusal message was "Could not verify worktree state," NOT the clean "this worktree has unmerged commits: ..." report `ExitWorktree`'s own contract describes. At that point `c7af286` was already reachable from `master` (merged via `--no-ff` as `32ebb07`), so `git log master..api-stale-xref-fix` was empty and there was nothing genuinely unmerged to discard. So the failure is a *verification* failure, not a true dirty-state detection. The first deliverable below is to pin down the actual cause before designing the fix.

### What is and is not ours to change

- `ExitWorktree` (and its clean-check) is a harness-owned tool; we do not control its verification logic. The reconciliation must live on our side: the documented flow order in `GIT_WORKFLOW.md`, `bin/git-integrate`, and/or the hook wiring in `.claude/settings.json`.
- `bin/git-integrate` runs from the main checkout, merges the branch, and ends by printing "Next steps: delete the feature branch and remove its worktree" -- it does the merge but performs no teardown. Teardown is left to the session via `ExitWorktree` + a manual `git branch -d`.
- There is a `WorktreeCreate` hook (`bin/seed-worktree`) but no `WorktreeRemove` hook configured.

### Candidate directions (resolve at kickoff, do not pre-commit here)

1. **Reorder the documented flow.** `ExitWorktree {action: "keep"}` (or remove) before `bin/git-integrate`, so the worktree is gone or detached before integration and the verification never straddles a mid-integrate state. The branch ref survives worktree removal (the observed session proves it: `git branch -d` ran after the worktree was gone), so integrate-after-exit is mechanically possible. Risk: `ExitWorktree` may also refuse a pre-integration worktree whose branch carries committed-but-unmerged work; verify what its check actually requires (this is the COR-10 "verify the seam against its real contract" lesson) before adopting.
2. **Make `bin/git-integrate` own the teardown.** After a successful merge, have the wrapper run `git worktree remove` + `git branch -d` itself, so the session never calls `ExitWorktree` for cleanup. Risk: harness/`ExitWorktree` state desync if the harness still believes the session is "in" a worktree the script deleted, and the cwd-inside-the-worktree case (the observed session's shell cwd was inside the worktree when `git-integrate` ran). Possibly pair with a `WorktreeRemove` hook.
3. **Document `discard_changes: true` as the deliberate, expected post-integrate step.** Cheapest; least satisfying -- it normalizes the override and keeps the reflex-risk. Acceptable only as a fallback if 1 and 2 prove infeasible.

### Deliverables

- A root-cause note on why `ExitWorktree` reports "Could not verify worktree state" after a clean `git-integrate` (reproduce, or read the harness contract, per COR-10).
- A chosen reconciliation (one of the directions above, or a better one surfaced by the root-cause work) implemented across the affected files: `GIT_WORKFLOW.md` (the documented flow), and `bin/git-integrate` and/or `.claude/settings.json` as the chosen approach requires.
- The change verified against a real worktree create -> edit -> integrate -> cleanup cycle, not just by reading (this is a seam whose correctness only shows on a real firing -- COR-10).

Out of scope: changing the merge-lock mechanism, the enforcement hooks (`.githooks/`), or the `--no-ff` policy; those are working as designed.

## Activity log

- 2026-06-29: Created in backlog. Triaged by the project-manager orchestrator from a review of session `79f3e0a0` (the second live run of the ADR-046 worktree workflow). The `ExitWorktree`-refusal-after-`git-integrate` papercut forced a `discard_changes: true` override on the cleanup happy path. Kin to COR-10 (seam behavior diverging from the assumed contract, visible only on a real firing). P2: not blocking any phase, but it sits on the cleanup path every concurrent session traverses and the discard-reflex it trains is a correctness hazard. Standalone (no epic): the worktree workflow infra is repo-global tooling, like its predecessors COR-T-057/058. An OBSERVATIONS entry (`COR-11`) for the pattern was offered separately and not taken at filing time.
- 2026-06-29: Picked up -> in-progress. A review of session `18483dae-e56c-4077-9b1d-410240321995` (the API-T-006 run) surfaced a third data point that pins the root cause and a proven clean pattern. `18483dae` cleaned up with `ExitWorktree {action: keep}` BEFORE integrating, then `bin/git-integrate` from the main checkout, then plain `git worktree remove` + `git branch -d` -- and hit NO refusal and used NO discard flag. So the refusal is exclusively on the harness `ExitWorktree {action: remove}` verification path; `action: keep` plus plain `git worktree remove` avoids it entirely (confirmed across three sessions: `79f3e0a0` and the COR-T-059 filing run both hit the refusal via `remove`; `18483dae` stayed clean via `keep`). Root cause is therefore empirically settled, not open; the investigation deliverable collapses to documenting it. Scope decision pinned with the user (2026-06-29): **docs + git-integrate message only** (candidate direction 1), NOT git-integrate-owns-teardown. Deliverable narrows to: make `GIT_WORKFLOW.md` steps 6-8 prescribe the proven sequence explicitly (`ExitWorktree keep` before integrate; plain `git worktree remove` + `git branch -d` for teardown), and update `bin/git-integrate`'s closing "Next steps" line to print those exact commands. No new automation; `.githooks/` and the merge-lock untouched. Next: draft the kickoff.
