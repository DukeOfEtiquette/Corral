---
schema_version: 1
id: COR-T-057
title: "Implement ADR-046 concurrent-session git workflow (worktrees, trunk-based, enforced flock merge lock)"
status: done
labels: []
priority: P2
created: 2026-06-24
updated: 2026-06-24
---

## Description

Implement the workflow accepted in `ai-infrastructure/project-manager/decisions/ADR-046-concurrent-session-git-workflow-worktrees-enforced-merge-lock.md`: give concurrent local Claude sessions true isolation via a worktree per session, branch trunk-based, and make integration into `master` autonomous but serialized behind an enforced `flock` merge lock with an escalate-to-user path on contention. AI-infrastructure (domain-2) repo operating policy. Standalone coordinator-filed task (no epic); the deliverable routes through the dispatched-worker flow when picked up.

ADR-046 is the accepted spec; this task makes it real. The mechanism details left to implementation are noted in the ADR Decision (items 1-10) and below.

### Scope (per the accepted ADR-046 decision)

1. **`GIT_WORKFLOW.md` at the repo root, operational content only.** The flow a session follows: research in the main checkout, switch into a worktree before the first edit, test in the worktree, integrate via the wrapper, escalate on lock contention. No rationale and no rejected options (those live in ADR-046). A single footer line points to ADR-046.

2. **The integration wrapper.** A sanctioned script that holds the lock for the whole critical section: `flock -n` around a `--no-ff` merge of the feature branch into `master` plus a fast post-merge sanity check, exporting the marker the hook checks, and surfacing an escalate-to-user message (not a block) when `flock -n` fails because the lock is held. The lock file lives in gitignored scratch (`.claude/artifacts/tmp/`), never a tracked file. Keep the locked section minimal: tests run on the feature branch in its worktree BEFORE the lock is acquired, not inside it.

3. **The enforcement hook.** A git hook (`pre-merge-commit` plus `pre-commit`) that refuses any update to `master` not carrying the wrapper's marker, making the wrapper mandatory. Hooks live in a tracked `.githooks/` directory wired up via `core.hooksPath`. `--no-ff` on `master` closes the fast-forward bypass (a ff merge creates no commit and would skip the commit hooks). The `reference-transaction` hook is the recorded airtight upgrade (ADR-046 Consequence 7), not built now.

4. **Worktree settings and seeding.** In the project Claude Code settings (`.claude/settings.json`): set `worktree.baseRef: head` (branch from local `master`, not `origin/master`), and add a `WorktreeCreate` hook that seeds per-worktree state a fresh checkout lacks: the gitignored `.env` (per ADR-006 it does not travel into a new worktree), dependencies, a unique test port to avoid local collisions, and ensures `core.hooksPath` is set.

5. **Repo-root `CLAUDE.md` edit.** Add a short subsection pointing sessions at `GIT_WORKFLOW.md`, and amend the documentation-placement rule to add `GIT_WORKFLOW.md` to the sanctioned repo-root file list (currently `CLAUDE.md`, `README.md`, `END-GOAL.md`), so a future tidy-up does not flag it as a stray root file (ADR-046 Consequence 2).

### Acceptance tests

(a) A worktree created per the flow branches from the local `master` HEAD (not `origin/master`) and comes up seeded: `.env` present and `core.hooksPath` set.
(b) An un-wrapped `git merge <branch>` into `master` is refused by the hook.
(c) A merge through the wrapper succeeds and is `--no-ff` (a merge commit is always formed).
(d) A second integration attempt while the lock is held fails immediately (`flock -n`) and surfaces the escalate-to-user message rather than blocking.
(e) A holder that exits mid-merge releases the lock automatically (no stale lock stranded).
(f) `GIT_WORKFLOW.md` exists at the repo root, contains only the operational flow (no rationale), and its footer points to ADR-046; `CLAUDE.md` points at it and lists it among the sanctioned root files.

References:
- `ai-infrastructure/project-manager/decisions/ADR-046-concurrent-session-git-workflow-worktrees-enforced-merge-lock.md` (the accepted spec this implements)
- `CLAUDE.md` (repo-root: the documentation-placement rule to amend, and the pointer subsection to add)
- `ai-infrastructure/project-manager/decisions/ADR-006-admin-bootstrap-env-hash.md` (gitignored `.env`; the seeding step must reproduce it per worktree)
- `ai-infrastructure/project-manager/decisions/ADR-003-docker-compose-runtime.md` (local test stack run in each worktree; the local-testing constraint behind staying local)
- `ai-infrastructure/project-manager/decisions/ADR-033-remote-deployment-topology.md` (remote is a deploy target, not the source of truth for in-progress work: the `baseRef: head` rationale)

## Activity log

- 2026-06-24: Created in backlog at the ADR-046 acceptance close. Filed as the implementation follow-up that ADR-046 Decision item 11 anticipates. P2, standalone, AI-infrastructure domain, unlabelled per ADR-031.
- 2026-06-24: Picked up; moved to in-progress. Decisions resolved with operator: wrapper at new top-level `bin/git-integrate`; seeding built concrete against the real `app/docker-compose.yml` stack (corrected from a stale "no app yet" premise); `app/docker-compose.yml` published port parameterized to `${API_HOST_PORT:-8123}:8123` to make per-worktree unique ports real; marker = env var the wrapper exports and the hooks check; lock file at `.claude/artifacts/tmp/merge.lock`; `.claude/worktrees/` to be gitignored. Routing through the dispatched-worker flow.
- 2026-06-24: Done. Dispatched-worker flow executed: kickoff drafted/checked (3 iterations: W1 deferral framing on iter 2, R2 WorktreeCreate-literal pinning on iter 3, both cleared), prelaunch W1 PASS, executor RETURN: COMPLETED, close-checker W2 PASS, orchestrator re-derived all six acceptance tests (a-f) against disk with `master` left unmutated. All 7 deliverables shipped (GIT_WORKFLOW.md, bin/git-integrate, bin/seed-worktree, .githooks/pre-merge-commit, .githooks/pre-commit, .claude/settings.json, app/docker-compose.yml port, CLAUDE.md, .gitignore). Accepted one executor deviation: seeding copies (not symlinks) app/.env per worktree, reconciling the kickoff's mutually-incompatible symlink-plus-write-port pins, ADR-006-safe (worktree app/.env is gitignored). Operator added the defensive `mkdir -p` guard request and ran the main-checkout `git config core.hooksPath .githooks` bootstrap. Deliverable + kickoff/report pair committed in 70fc7de (ADR-024).
