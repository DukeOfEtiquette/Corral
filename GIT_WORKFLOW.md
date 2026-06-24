# Git Workflow

This file describes the operational flow for working on this repo across concurrent Claude sessions. For the rationale, alternatives, and upgrade paths, see the footer reference.

## Flow

1. **Research in the main checkout.** Start any task in the main worktree. Research (reading files, running git log, surveying state) mutates nothing and requires no worktree.

2. **Switch to a fresh worktree before the first edit.** The moment a task turns into a change, switch into a dedicated worktree before writing any file. The harness creates and seeds the worktree automatically via the `WorktreeCreate` hook in `.claude/settings.json`. Worktrees live under `.claude/worktrees/<name>/`.

3. **Branch from local `master` HEAD.** New worktrees branch from local `master` HEAD (not `origin/master`) because local `master` may lead `origin` and the work is local-first.

4. **Work in the worktree.** Make all edits, stage, and commit on the feature branch inside the worktree. The working tree is isolated: no other session sees uncommitted changes.

5. **Test in the worktree via compose.** Run tests through `docker compose` against the worktree's stack. Each worktree gets a distinct `API_HOST_PORT` to avoid port collisions.

6. **Integrate via `bin/git-integrate`.** When the feature branch is ready, run `bin/git-integrate <branch-name>` from the main checkout. The wrapper:
   - Runs `flock -n` on `.claude/artifacts/tmp/merge.lock` to acquire the exclusive merge lock.
   - Merges the feature branch into `master` with `--no-ff` (a merge commit is always formed).
   - Runs a fast post-merge sanity check (merge commit present, working tree and index clean, no conflict markers).
   - Releases the lock automatically on exit.

7. **Escalate on lock contention.** If `bin/git-integrate` exits with a contention message, another session holds the merge lock. Do not attempt a manual merge. Wait for the in-flight merge to complete, then re-run `bin/git-integrate`.

8. **Delete the feature branch and worktree after a successful merge.** Clean up: remove the worktree and delete the short-lived feature branch. `master` should stay always-green.

## Enforcement

Un-wrapped merges into `master` are refused by the `.githooks/pre-merge-commit` and `.githooks/pre-commit` hooks. The hooks are wired via `git config core.hooksPath .githooks` (set by the seeding step on each worktree). `--no-ff` is mandatory on `master`; no fast-forward merges are allowed.

## Lock file

The merge lock lives at `.claude/artifacts/tmp/merge.lock` (gitignored scratch). It is held only for the duration of the `bin/git-integrate` critical section. `flock` auto-releases on process exit, so a dead or closed session cannot strand the lock.

---

See `ai-infrastructure/project-manager/decisions/ADR-046-concurrent-session-git-workflow-worktrees-enforced-merge-lock.md` for rationale, alternatives, and upgrade paths.
