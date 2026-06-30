---
schema_version: 1
adr: 46
title: "Concurrent-session git workflow: worktree-per-session, trunk-based integration behind an enforced merge lock"
status: "accepted"
date: "2026-06-24"
related_adrs: [3, 5, 6, 33, 34]
supersedes: []
superseded_by: null
---

# ADR-046: Concurrent-session git workflow: worktree-per-session, trunk-based integration behind an enforced merge lock

## Context

Work on this repo is routinely driven by **several concurrent Claude sessions on one local machine, in one clone**. Both domains (the web app and the AI infrastructure, per ADR-005) are built this way. The standing coordination mechanism has been an advisory policy: "only commit your work." Verified state at decision time (2026-06-24): the repo has a single `master` branch, a single worktree at the repo root, and an `origin` on GitHub that is used lightly.

The advisory policy is a band-aid and has demonstrably failed. A single working directory has one index and one `HEAD`, so every session sees the same uncommitted changes. When two sessions edit, a `git add`/commit in one session can sweep up the other session's changes, and sessions have committed each other's work by accident. The failure is structural, not a discipline lapse: the shared working tree makes cross-session contamination possible no matter how careful the policy text is.

Two obvious-looking fixes do not work under the local constraint:

- **Branch-in-place**: asking each session to branch fails because all sessions share one working directory and therefore one current branch. Sessions would compete for which branch is checked out and commit onto each other's branches: strictly worse than the status quo, and harder to untangle than an accidental sweep onto `master`.
- **Run sessions in the cloud** (the documented path for safe per-session branching) is rejected by a hard requirement: substantial testing must happen locally (docker compose stack, per ADR-003) and cannot be reproduced in a hosted environment. Staying local is a constraint, not a preference.

The question: under a local-only constraint, can concurrent sessions be given true isolation, and can integration into `master` be made safe without a human serializing every merge?

## Alternatives considered

### Option A: Keep the advisory "only commit your work" policy (rejected)

Status quo. Rejected: it is the demonstrated failure this ADR exists to fix. Advisory text cannot prevent a structurally-shared working tree from leaking changes between sessions.

### Option B: One shared working directory, sessions branch in place (rejected)

Have each session create and switch to its own branch in the single working directory. Rejected: a single working tree has one `HEAD`. Concurrent sessions would fight over the checked-out branch and commit onto one another's branches. Worse than Option A and harder to recover from.

### Option C: Run sessions in the cloud and branch on GitHub (rejected)

The conventional safe-isolation path. Rejected by the local-testing constraint above: the test environment cannot be stood up remotely, so the work cannot leave the local machine.

### Option D: A worktree per session, trunk-based, integration behind an enforced merge lock (selected)

`git worktree` gives each session its own working directory and its own branch while sharing one `.git` object store, so isolation is local and complete. Integration into `master` is allowed autonomously from any session but is funneled through a single enforced critical section so two merges cannot interleave. Selected; the sub-choices within it are recorded below.

Sub-decisions settled within Option D:

- **Branching model: trunk-based, not GitFlow.** A long-lived `develop` integration branch (feature branches off `develop`, `develop` to `master` at release) suits scheduled multi-developer releases with a QA gate. For a solo operator driving agents against a self-hosted app with no external release cadence, it adds a merge hop and ceremony for no gain. Trunk-based (short-lived feature branches off `master`, merged straight back, `master` always green) is the same lifecycle as a worktree, so the two concepts coincide. A `develop` branch is **deferred**, not rejected: it is the recorded escalation if integrating parallel agent branches together before they reach `master` ever causes real pain.
- **Merge serialization: enforced, not advisory.** An advisory "please take the lock" line in a workflow doc can be skipped by a session that does not run the step. The lock is enforced by a git hook, so an un-sanctioned merge into `master` is refused outright.
- **Lock primitive: `flock`.** Atomic acquire by construction (no check-then-write TOCTOU race), and it releases automatically when the holding process exits, which neutralizes the stale-lock failure mode without hand-rolled PID/timestamp logic. `flock -n` (non-blocking) gives try-and-fail-immediately, which is the escalate-on-contention behavior wanted rather than an unbounded block.
- **Who integrates: any session, autonomously.** A single-human-integrator model needs no lock but requires hand-holding on every merge. The requirement is autonomous integration, so sessions self-merge; the lock plus the escalate-to-user path covers the contention and conflict edge cases.
- **Enforcement hook surface: pragmatic now, airtight upgrade recorded.** A git hook cannot itself *hold* the `flock` across the merge: a hook is a short-lived child of the merge and any lock it takes releases when it exits, before the merge completes. So the lock is held by a wrapper around the whole merge, and the hook's job is to enforce that the wrapper was used (it refuses a `master` update that does not carry the wrapper's marker). Fast-forward merges create no commit and therefore skip `pre-merge-commit`, a bypass hole; closed pragmatically by mandating `--no-ff` on `master` (so a merge commit always forms and the hook always fires) plus `pre-commit` for the conflicted-then-`git commit` path. The airtight alternative, a `reference-transaction` hook (fires on every ref update including fast-forwards, cannot be bypassed), is recorded as the upgrade path rather than adopted now, to keep the first implementation simple.

## Decision

Adopt **Option D**. Concurrent local sessions are isolated by a worktree per session, branching is trunk-based, and integration into `master` runs autonomously behind an enforced `flock` merge lock with an escalate-to-user path for contention. Specifically:

1. **Worktree per session.** A session does research in the main checkout (research mutates nothing and needs no worktree). The moment research turns into a change, the session switches into a fresh worktree **before the first edit**, on its own short-lived branch. Worktrees are created via the harness `EnterWorktree` flow (worktrees live under `.claude/worktrees/`); because that tool only activates when "worktree" appears in the user's words or in project instructions, the workflow rule in `GIT_WORKFLOW.md` (item 8) is what makes a session eligible to self-create one.

2. **`worktree.baseRef: head`.** New worktrees branch from the local `master` `HEAD`, not from `origin/master`, because local `master` may lead `origin` and the work is local-first (ADR-033 keeps remote a deploy target, not the source of truth for in-progress work).

3. **Trunk-based branching.** Short-lived feature branches off `master`, deleted when merged. `master` stays always-green: every commit on it could be deployed. No long-lived `develop` branch (deferred per the sub-decision above). `master` receives merges, not direct feature commits.

4. **Integration through a wrapper that holds the lock.** Merging a feature branch into `master` runs through a single sanctioned wrapper (an `flock -n` around a `--no-ff` merge plus a fast post-merge sanity check). The wrapper holds the exclusive lock for the whole critical section and exports the marker the hook checks. Merges happen from the main checkout against the feature branch ref (`git merge <branch>`); a feature worktree never checks out `master` (git forbids the same branch in two worktrees regardless).

5. **Enforcement via a tracked hook.** A git hook (`pre-merge-commit` plus `pre-commit`) refuses any update to `master` that does not carry the wrapper's marker, making the wrapper mandatory rather than advisory. Hooks live in a tracked `.githooks/` directory wired up with `core.hooksPath` so they are version-controlled and apply across all worktrees of the clone. `--no-ff` on `master` closes the fast-forward bypass; a `reference-transaction` hook is the recorded airtight upgrade.

6. **Escalate on contention; auto-release covers staleness.** `flock -n` fails immediately if the lock is held; the losing session does not block, it surfaces the contention to the user, who investigates and re-initiates once the in-flight merge completes. A crashed or closed session cannot strand the lock because `flock` releases on process exit; the user-escalation path is the backstop for any residual case.

7. **Short critical section.** The test suite runs on the feature branch in its own worktree **before** the lock is acquired, so the locked section is only the merge plus a quick sanity check (seconds), minimizing contention. Tests are not run inside the lock.

8. **Lock file location.** The lock file lives in gitignored scratch (`.claude/artifacts/tmp/`), never a tracked file (a tracked lock would itself generate merge conflicts and pollute history).

9. **Documentation split (three artifacts, one job each).**
   - `GIT_WORKFLOW.md` at the repo root holds **only the operational flow** (how a session does work: research in main, worktree on first edit, test in the worktree, integrate via the wrapper, escalate on contention). No rationale, no rejected options. It carries a single footer pointer to this ADR.
   - This ADR (ADR-046) holds the rationale, alternatives, and upgrade paths.
   - The repo-root `CLAUDE.md` gains a short subsection pointing at `GIT_WORKFLOW.md`, and its documentation-placement rule is amended to add `GIT_WORKFLOW.md` to the sanctioned repo-root file list (otherwise a future tidy-up would flag it as a stray root file).

10. **Worktree seeding.** A `WorktreeCreate` hook in `settings.json` seeds per-worktree state that a fresh checkout lacks: symlink/seed the gitignored `.env` (ADR-006 keeps secrets in gitignored `.env` only, so it does not travel into a new worktree), install dependencies, assign a unique port to avoid local test collisions, and ensure `core.hooksPath` is set. `worktree.baseRef: head` is set in the same settings.

11. **Implementation is deferred to a follow-on task.** This ADR is the accepted spec. Authoring `GIT_WORKFLOW.md`, the `flock` wrapper, the `.githooks/` hook, the `settings.json` hook and settings, and the `CLAUDE.md` edit is a separate dispatched task to be filed later (operator will implement later); it routes through the dispatched-worker flow when filed.

## Consequences

1. **A structural guarantee replaces an advisory policy.** Each session's working tree physically contains only that session's changes, so a commit cannot sweep up another session's work. The "only commit your work" band-aid is retired in favor of isolation that holds regardless of discipline.

2. **A new sanctioned repo-root file (`GIT_WORKFLOW.md`) amends the documentation-placement rule.** The repo-root `CLAUDE.md` currently enumerates `CLAUDE.md`, `README.md`, `END-GOAL.md` as the sanctioned root files; this decision adds `GIT_WORKFLOW.md`. The amendment lands as part of the implementation task.

3. **Hooks become tracked infrastructure with a per-clone bootstrap.** `core.hooksPath` pointing at a tracked `.githooks/` makes the enforcement hook shared and version-controlled, but `core.hooksPath` is itself local config, so it must be set per clone. The `WorktreeCreate` seeding step owns that bootstrap.

4. **Integration into `master` is enforced, not requested.** An un-wrapped merge into `master` is refused by the hook, so the lock cannot be skipped by a session that forgets the step. Trade-off accepted: `master` integration is mandated `--no-ff`, which is desirable on a trunk (each integration is one revertable unit) but means no fast-forward merges to `master`.

5. **`master` integration is serialized; contention escalates to the user.** Only one merge holds the lock at a time. A contended merge surfaces to the user rather than blocking, which is appropriate because a contended or conflicting merge often needs human judgment anyway. The cost is occasional human involvement at exactly the moments it is warranted.

6. **Stale locks are handled without hand-rolled logic.** `flock` auto-releases on process exit, so a dead session cannot strand the lock; the escalate-to-user path is the backstop for any residual case.

7. **A residual enforcement gap is recorded with its fix.** With only `pre-merge-commit`/`pre-commit`, a fast-forward merge performed outside the wrapper would skip the commit hooks. It is closed pragmatically by the `--no-ff` mandate on `master`. Re-open trigger: if a non-wrapper path is found to move the `master` ref without firing the hooks, escalate to a `reference-transaction` hook (fires on every ref update, including fast-forwards) as the airtight enforcement point.

8. **Per-worktree setup cost is real but absorbed by automation.** A fresh worktree lacks gitignored files (`.env`), dependencies, and a distinct test port; left manual this is friction and a collision risk. The `WorktreeCreate` seeding hook absorbs it so spinning up an isolated session stays one step.

9. **`develop` deferral is on record.** The branching model can grow a `develop` integration branch later if parallel-branch integration pain materializes; this ADR records that as the escalation, not a present need, so trunk-based stays the default until evidence says otherwise.

10. **Scope: repo-level operating policy, not plugin machinery.** This workflow governs how sessions operate on this clone; it is not part of the project-manager machinery slated for plugin extraction (ADR-034). It stays with the repo and does not need to travel with the extracted plugin.

11. **Forward pointer (2026-06-30): dispatched-executor and resolve-gate refinements.** The first real firings of this workflow surfaced three gaps, fixed in COR-T-059 and COR-T-060 (the amendments live in the workflow docs per the owned-but-advisory convention, not by editing this ADR's decision): (a) the post-integrate cleanup happy path forced a `discard_changes: true` override on `ExitWorktree {action: "remove"}`, resolved by prescribing `ExitWorktree {action: "keep"}` before integrating plus exact `git worktree remove` / `git branch -d` teardown commands (COR-T-059; `GIT_WORKFLOW.md` Flow steps 6 and 9, `bin/git-integrate` closing guidance); (b) a dispatched executor subagent cannot call the harness `EnterWorktree` / `ExitWorktree` tools, so it uses the equivalent `git worktree add` commands, and the `CLAUDE.md` hard gate's mechanism was broadened to name both paths while staying unconditional (COR-T-060; `docs/ai-orchestration/roles/EXECUTOR-ROLE.md` section "Worktree handling (dispatched executor)", `GIT_WORKFLOW.md` step 2, `CLAUDE.md` "Git workflow"); (c) handoff artifacts authored as untracked files in the main checkout do not compose with the hard gate, resolved by routing the resolve-gate commit through a worktree (the executor writes its report inside its worktree; the orchestrator copies the untracked kickoff into a resolve worktree) rather than re-permitting direct main-checkout coordination commits (COR-T-060; `docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md` "Dispatched-worker flow" step 7).

12. **Forward pointer (2026-06-30): single-worktree resolve supersedes the Gap-2b resolve worktree.** Item 11(c)'s "resolve worktree" produced two worktrees and two merges per dispatched task (the deliverable worktree plus a separate resolve worktree), observed live on DB-T-006. ADR-047 amends the procedure: the resolve-gate commit (kickoff + task-tree move) now lands on the deliverable's own feature branch instead of a fresh worktree, so each task is one worktree and one merge. The worktree-per-session, merge-lock, and `bin/git-integrate` decisions of this ADR are unchanged; only the resolve-gate routing in item 11(c) is superseded. See `ai-infrastructure/project-manager/decisions/ADR-047-single-worktree-task-resolve.md` and the rewritten `ORCHESTRATOR-ROLE.md` "Dispatched-worker flow" step 7 note.
