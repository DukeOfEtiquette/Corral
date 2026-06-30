# Git Workflow

This file describes the operational flow for working on this repo across concurrent Claude sessions. For the rationale, alternatives, and upgrade paths, see the footer reference.

## Flow

1. **Research in the main checkout.** Start any task in the main worktree. Research (reading files, running git log, surveying state) mutates nothing and requires no worktree.

2. **Switch to a fresh worktree before the first edit.** The moment a task turns into a change, switch into a dedicated worktree before writing any file. Worktrees live under `.claude/worktrees/<name>/`. Two paths, same gate:

   - **Interactive sessions** (human-facing Orchestrator, `/project-manager-orchestrator`, etc.): the harness creates and seeds the worktree automatically via the `WorktreeCreate` hook in `.claude/settings.json`. Use `EnterWorktree` to create and enter the worktree, and `ExitWorktree {action: "keep"}` before integrating (step 6).
   - **Dispatched executor subagents** (`executor`, `test-designer`): the harness `EnterWorktree` / `ExitWorktree` tools are refused in a subagent context. Create the worktree with the equivalent plain git commands: `git worktree add <abs-path>/.claude/worktrees/<branch> -b <branch> <base>`, make all edits via absolute paths inside it, commit on the feature branch, and leave the worktree on disk for the Orchestrator to integrate. See `docs/ai-orchestration/roles/EXECUTOR-ROLE.md`, section "Worktree handling (dispatched executor)".

3. **Branch from local `master` HEAD.** New worktrees branch from local `master` HEAD (not `origin/master`) because local `master` may lead `origin` and the work is local-first.

4. **Work in the worktree.** Make all edits, stage, and commit on the feature branch inside the worktree. The working tree is isolated: no other session sees uncommitted changes.

5. **Test in the worktree via compose.** Run tests through `docker compose` against the worktree's stack. Each worktree gets a distinct `API_HOST_PORT` to avoid port collisions.

6. **Leave the worktree before integrating.** Before running `bin/git-integrate`, return to the main checkout: call `ExitWorktree {action: "keep"}`, which preserves the feature branch on disk and switches the session back to master. Do NOT use `ExitWorktree {action: "remove"}` at this point or after the merge: its post-exit verification refuses with "Could not verify worktree state" once the branch has been merged, and pushes toward a `discard_changes: true` override even though the work is already on master. Use `keep`, not `remove`.

7. **Integrate via `bin/git-integrate`.** When the feature branch is ready, run `bin/git-integrate <branch-name>` from the main checkout. The wrapper:
   - Runs `flock -n` on `.claude/artifacts/tmp/merge.lock` to acquire the exclusive merge lock.
   - Merges the feature branch into `master` with `--no-ff` (a merge commit is always formed).
   - Runs a fast post-merge sanity check (merge commit present, working tree and index clean, no conflict markers).
   - Releases the lock automatically on exit.

8. **Escalate on lock contention.** If `bin/git-integrate` exits with a contention message, another session holds the merge lock. Do not attempt a manual merge. Wait for the in-flight merge to complete, then re-run `bin/git-integrate`.

9. **Delete the feature branch and worktree after a successful merge.** From the main checkout, run these exact teardown commands:

   ```
   git worktree remove .claude/worktrees/<branch>
   git branch -d <branch>
   ```

   Use `git worktree remove` directly, not `ExitWorktree {action: "remove"}`: on the post-integrate path, `ExitWorktree {action: "remove"}` refuses with "Could not verify worktree state" and pushes toward a `discard_changes: true` override even though the work is already merged. `master` should stay always-green.

## Enforcement

Un-wrapped merges into `master` are refused by the `.githooks/pre-merge-commit` and `.githooks/pre-commit` hooks. The hooks are wired via `git config core.hooksPath .githooks` (set by the seeding step on each worktree). `--no-ff` is mandatory on `master`; no fast-forward merges are allowed.

## Lock file

The merge lock lives at `.claude/artifacts/tmp/merge.lock` (gitignored scratch). It is held only for the duration of the `bin/git-integrate` critical section. `flock` auto-releases on process exit, so a dead or closed session cannot strand the lock.

---

See `ai-infrastructure/project-manager/decisions/ADR-046-concurrent-session-git-workflow-worktrees-enforced-merge-lock.md` for rationale, alternatives, and upgrade paths.
