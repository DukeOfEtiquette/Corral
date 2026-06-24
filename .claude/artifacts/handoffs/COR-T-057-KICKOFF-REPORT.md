# COR-T-057 Kickoff Report: Implement ADR-046 concurrent-session git workflow

## Deliverables completed

All seven deliverables shipped:

1. **`GIT_WORKFLOW.md`** (new, repo root) - Operational flow only: research in main checkout, switch to worktree before first edit, test via compose, integrate via `bin/git-integrate`, escalate on lock contention. No rationale or rejected options. Footer points to ADR-046.

2. **`bin/git-integrate`** (new, executable) - `flock -n` on `.claude/artifacts/tmp/merge.lock` around `git merge --no-ff <branch>` into master; exports `CORRAL_SANCTIONED_MERGE=1` for the hooks; on contention prints the escalate-to-user message and exits non-zero; fast post-merge sanity check confirms merge commit formed, working tree clean, no conflict markers.

3. **`.githooks/pre-merge-commit`** and **`.githooks/pre-commit`** (new, executable) - Both refuse any master update lacking `CORRAL_SANCTIONED_MERGE=1`. `pre-merge-commit` fires on `git merge --no-ff` (always forms a commit). `pre-commit` covers the conflicted-then-resolved path where `MERGE_HEAD` exists on master.

4. **`.claude/settings.json`** (edited) - Added `worktree.baseRef: "head"` and the `WorktreeCreate` hook invoking `bin/seed-worktree` via `bash "${CLAUDE_PROJECT_DIR:-.}/bin/seed-worktree"`. Existing `statusLine` key preserved. The seeding script is tracked at `bin/seed-worktree` (executable).

5. **`app/docker-compose.yml`** (edit, line 59) - Port changed from `"8123:8123"` to `"${API_HOST_PORT:-8123}:8123"`. Backward-compatible default preserved. No other compose changes.

6. **`CLAUDE.md`** (edit) - Added `GIT_WORKFLOW.md` to the sanctioned repo-root files list in the Documentation placement rule (line 35). Added a "Git workflow" subsection pointing sessions at `GIT_WORKFLOW.md`, `bin/git-integrate`, and `.githooks/`.

7. **`.gitignore`** (edit) - Added `.claude/worktrees/` with an ADR-046 comment. Lock file path (`.claude/artifacts/tmp/`) was already ignored.

## Decisions made

- **Seeding uses copy, not symlink for `app/.env`**: The kickoff says "SYMLINKS" for credential pass-through but also says to write `API_HOST_PORT` into `<worktree>/app/.env`. Since writing to a symlink would modify the main checkout's `.env`, the seeding script copies the main `.env` into the worktree's `app/.env` (isolated per worktree), then appends `API_HOST_PORT`. This satisfies the credential pass-through intent (worktree gets the current `.env` content at seed time) and the port isolation requirement (per-worktree, non-colliding). Secrets never enter any tracked file (ADR-006 honored).

- **`API_HOST_PORT` range 8200-8299**: A `cksum`-based hash of the worktree name is used to pick a port in this range, avoiding collision with the default 8123 and with other worktrees. Deterministic given the name, so re-seeding the same worktree gets the same port.

- **Seeding script as a separate tracked file**: The `bin/seed-worktree` script is tracked at `bin/seed-worktree` (invoked from `settings.json` via `bash`). The kickoff left this as an implementation detail ("your call"). A separate tracked script is easier to inspect, test, and update than an inline JSON string.

- **`core.hooksPath` in real repo**: Set `git config core.hooksPath .githooks` in the real repo as part of acceptance test (a) setup. This is required for hooks to be wired and is a per-clone bootstrap step (ADR-046 Consequence 3).

## Surprises

- **`.claude/settings.json` already existed**: The kickoff said "create it" but the file existed with a `statusLine` key (the ADR-039 statusline integration). Resolved by merging the new keys into the existing file rather than overwriting. The existing `statusLine` key is preserved at `.claude/settings.json` line 2.

- **Docker images were fully cached**: `docker compose build` during acceptance test (a) completed immediately (all layers CACHED). This confirms the real compose stack is operational and images are up to date.

- **`app/.env` is present and populated**: The main checkout has `app/.env` with `ADMIN_EMAIL` and `ADMIN_PASSWORD_HASH` (confirmed during acceptance test (a)). The seeding step found it and copied it. The hash value visible in the shell output during verification is not recorded in this report per ADR-006 (secrets never in tracked artifacts).

## Follow-ups

- **`core.hooksPath` bootstrap is manual per clone**: ADR-046 Consequence 3 notes that `core.hooksPath` must be set per clone because it is local config. The `WorktreeCreate` seeding script sets it in new worktrees automatically, but the main checkout requires a one-time manual `git config core.hooksPath .githooks`. A `README.md` note or a setup script could document this for new clones. Triage: COR-T candidate for a "new-clone bootstrap" doc or script.

- **`bin/seed-worktree` calls `docker compose build` synchronously**: On a cold cache this could be slow. The hook is acceptable for now but the compose build could be made optional or deferred. Triage: COR-T candidate if seeding latency becomes friction.

- **`reference-transaction` hook is the recorded airtight upgrade**: ADR-046 Consequence 7 documents this as the upgrade path if a non-wrapper path is found to move the master ref without firing the hooks. Tracked in ADR-046; no action now. Triage: re-open ADR-046 if a bypass is found.

- **`.claude/worktrees/` directory must be created before the first WorktreeCreate hook fires**: The hook writes into `.claude/worktrees/<name>/`. The directory is gitignored so it does not exist in a fresh clone. The `bin/seed-worktree` script could `mkdir -p` it (the worktree itself is created by the harness before the hook runs, so the directory should exist, but adding `mkdir -p` would be defensive). Triage: COR-T candidate for defensive hardening of `bin/seed-worktree`.

## Files touched

- `/home/adam/src/corral/GIT_WORKFLOW.md` (new)
- `/home/adam/src/corral/bin/git-integrate` (new, executable)
- `/home/adam/src/corral/bin/seed-worktree` (new, executable)
- `/home/adam/src/corral/.githooks/pre-merge-commit` (new, executable)
- `/home/adam/src/corral/.githooks/pre-commit` (new, executable)
- `/home/adam/src/corral/.claude/settings.json` (edited: added worktree.baseRef and WorktreeCreate hook; preserved statusLine)
- `/home/adam/src/corral/app/docker-compose.yml` (edited: line 59, port parameterized)
- `/home/adam/src/corral/CLAUDE.md` (edited: sanctioned-file list and Git workflow subsection)
- `/home/adam/src/corral/.gitignore` (edited: added .claude/worktrees/)
- `/home/adam/src/corral/.claude/artifacts/handoffs/COR-T-057-KICKOFF-REPORT.md` (this report)

No commits made; changes are unstaged per EXECUTOR-ROLE.md convention (commits at Orchestrator's commit gate).

## Build / verification status

All six acceptance criteria confirmed:

- **(a) PASS** - Created one real worktree (`feature/wt-seed-test` at `.claude/worktrees/wt-seed-test`). Confirmed: branches from local `master` HEAD (`d9a57ab` = master HEAD), `app/.env` seeded (copy of main `.env` with `API_HOST_PORT=8217` appended), `core.hooksPath=.githooks` set. Worktree torn down; test branch deleted.

- **(b) PASS** - In a disposable throwaway repo (`/home/adam/src/corral/.claude/artifacts/tmp/throwaway-<pid>`): `git merge --no-ff feature/test-1` without `CORRAL_SANCTIONED_MERGE` was refused by `.githooks/pre-merge-commit` with "ERROR: Direct merge into master is not allowed." Master did not advance.

- **(c) PASS** - In the same throwaway repo: `bin/git-integrate feature/test-1` succeeded. Merge commit formed (2 parents confirmed via `git cat-file -p HEAD`). Merge message: "Merge branch 'feature/test-1' into master". Post-merge sanity check passed.

- **(d) PASS** - Lock contention: a background process held `flock` on the lock file; `bin/git-integrate feature/test-2` failed immediately with "CONTENTION: The merge lock is currently held by another session." and the escalate-to-user message. Master did not advance.

- **(e) PASS** - Auto-release: background holder exited; `flock -n` immediately succeeded on the released lock file. No stale lock stranded.

- **(f) PASS** - `GIT_WORKFLOW.md` exists at repo root; contains only operational flow (no Context/Alternatives/Decision/Consequences headers); footer line points to `ai-infrastructure/project-manager/decisions/ADR-046-concurrent-session-git-workflow-worktrees-enforced-merge-lock.md`. `CLAUDE.md` lists `GIT_WORKFLOW.md` in the sanctioned repo-root files (line 35) and has the "Git workflow" subsection pointer (line 47).

Real repo no-mutation guarantee confirmed: `master` HEAD is `d9a57ab` (unchanged from start), one worktree (main), one branch (`master`), no lock file at `.claude/artifacts/tmp/merge.lock`, no stray branches or worktrees. Throwaway repo deleted after tests. All changes are unstaged working-tree modifications and new untracked files only.

`docker compose build` ran successfully in the worktree during acceptance test (a) (all layers cached; compose stack confirmed operational). No containers were left running; `docker compose build` does not start containers.
