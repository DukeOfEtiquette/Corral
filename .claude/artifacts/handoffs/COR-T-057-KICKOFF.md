# Implement ADR-046 concurrent-session git workflow (worktree-per-session, trunk-based, enforced flock merge lock, hooks, seeding)

## Target

This is AI-infrastructure (domain-2) work per ADR-005: it implements the repo-level operating policy accepted in ADR-046 (concurrent local Claude sessions isolated by one worktree each, trunk-based branching, and integration into `master` funneled through a single enforced `flock` merge lock). The deliverables are the operational doc, the integration wrapper, the enforcement hooks, the worktree-seeding settings, two small edits to existing repo-root policy files, and one intentional touch of a single domain-1/web-app file (`app/docker-compose.yml`) to parameterize a host port. The app stack at `app/docker-compose.yml` is real and partially built (postgres/migrate/test/test-roundtrip/api/api-test services with real api+db tests); build the app-coupled steps concretely against that stack, not as stubs.

## Decisions resolved by the Orchestrator

All of the following are pinned. Do not re-open any of them; do not substitute your own design.

- **Wrapper script location.** A NEW top-level `bin/` directory holds the integration wrapper at `bin/git-integrate`, executable (`chmod +x`). Operator-approved.
- **Sanction marker mechanism.** The wrapper exports an ENVIRONMENT VARIABLE (`CORRAL_SANCTIONED_MERGE=1`) for the lifetime of the critical section; the enforcement hooks check for that env var being set. The hooks refuse a `master` update when the marker env var is absent. The marker is an env var, NOT a tracked file (ADR-046 Decision items 4 and 5: "exports the marker the hook checks").
- **Lock file path.** `.claude/artifacts/tmp/merge.lock`, in gitignored scratch (ADR-046 Decision item 8). `.claude/artifacts/tmp/` is already gitignored (verified at `.gitignore` line 8). Never a tracked file.
- **Hooks directory and hooks.** A tracked `.githooks/` directory wired via `git config core.hooksPath .githooks`. Implement `pre-merge-commit` and `pre-commit` (ADR-046 Decision item 5). `--no-ff` is mandatory on merges into `master`; this closes the fast-forward bypass (ADR-046 Decision item 5, Consequence 7).
- **`.env` seeding.** Worktree seeding SYMLINKS the main checkout's `app/.env` into the new worktree's `app/.env`. The env file lives at `app/.env`, NOT at the repo root (verified: `app/docker-compose.yml` lines 56-57 consume `ADMIN_EMAIL` and `ADMIN_PASSWORD_HASH`, gitignored per ADR-006). The seed step must behave gracefully if the source `app/.env` is absent: skip with a clear note, do not fail the worktree creation.
- **Dependency seeding.** Dependencies are baked into the Docker images (requirements.txt in the Dockerfiles), so "install dependencies" means `docker compose build` for the worktree's stack, NOT a host pip or npm install (run policy is compose-only per ADR-003).
- **Unique test port.** Each worktree gets a distinct host port for the `api` service to avoid local collisions. The published port in `app/docker-compose.yml` is parameterized from the hard-coded `"8123:8123"` to `"${API_HOST_PORT:-8123}:8123"` (backward-compatible default). The `WorktreeCreate` seeding writes a distinct `API_HOST_PORT` value into the worktree's `app/.env`. Operator-approved domain-1 touch.
- **Pre-lock testing.** The test suite runs on the feature branch IN ITS WORKTREE via the existing compose test services (`test`, `test-roundtrip`, `api-test` in `app/docker-compose.yml`) BEFORE the merge lock is acquired. The locked critical section is ONLY the `--no-ff` merge plus a fast post-merge sanity check (ADR-046 Decision item 7). Tests are never run inside the lock.
- **Post-merge sanity check.** Inside the wrapper, inside the lock: a FAST check only (seconds). Confirm the merge commit was formed, the working tree and index are clean, and `master` is not in a conflicted state. It is NOT a test-suite run.
- **Escalate-on-contention.** `flock -n` (non-blocking). When the lock is held the wrapper does NOT block: it prints an escalate-to-user message and exits non-zero, leaving integration to be re-initiated by the user once the in-flight merge completes (ADR-046 Decision item 6). `flock` auto-release on process exit covers stale locks.
- **`worktree.baseRef: head`.** Set in `.claude/settings.json` so new worktrees branch from local `master` HEAD, not `origin/master` (ADR-046 Decision item 2; rationale ADR-033, remote is a deploy target, not the in-progress source of truth). `.claude/settings.json` does NOT currently exist (verified): create it.
- **`.gitignore` addition.** Add `.claude/worktrees/` (ADR-046 Decision item 1 places worktrees there; verified not currently ignored).
- **Build concrete against the real app.** The compose stack at `app/docker-compose.yml` exists with real services and tests. Do NOT write app-coupled steps as stubs or as if "there is no app yet."
- **Verification safety.** The acceptance scenarios that exercise the hook refusal, the wrapped `--no-ff` merge, and the flock contention/auto-release MUST NOT mutate the real repo's `master`, leave stray commits, leftover branches or worktrees, or a leftover lock file. Verify the hook + wrapper + flock mechanics in a DISPOSABLE throwaway git repo: `git init` a temp dir under the gitignored scratch `.claude/artifacts/tmp/`, copy in `.githooks/` + `bin/git-integrate`, wire `core.hooksPath`, and simulate two concurrent sessions there. For the worktree-seeding check (acceptance a), create ONE real worktree via the actual flow, confirm it is seeded, then tear it down cleanly. Leave the real repo exactly as found.

## Deliverables

1. **`GIT_WORKFLOW.md`** at the repo root: OPERATIONAL FLOW ONLY. Research happens in the main checkout; switch into a worktree before the first edit; test in the worktree via compose; integrate via `bin/git-integrate`; escalate on lock contention. NO rationale, NO rejected options (those live in ADR-046). A single footer line points to ADR-046 at `ai-infrastructure/project-manager/decisions/ADR-046-concurrent-session-git-workflow-worktrees-enforced-merge-lock.md`.
2. **`bin/git-integrate`** (new, executable): `flock -n` on `.claude/artifacts/tmp/merge.lock` around a `git merge --no-ff <feature-branch>` into `master` plus the fast post-merge sanity check; exports `CORRAL_SANCTIONED_MERGE=1` so the hooks pass; on `flock -n` failure prints the escalate-to-user message and exits non-zero. Merges run from the main checkout against the feature branch ref (a feature worktree never checks out `master`).
3. **`.githooks/pre-merge-commit`** and **`.githooks/pre-commit`** (new, executable): refuse any update to `master` that does not carry the wrapper's marker env var (`CORRAL_SANCTIONED_MERGE`), making the wrapper mandatory.
4. **`.claude/settings.json`** (new). The shape below is PINNED; implement exactly this. (Sourced from the official Claude Code docs at code.claude.com/docs worktrees and hooks references; you are not investigating the event name or contract, you are implementing the resolved answer.)
   - **`worktree.baseRef`**: set to the string `"head"`. The key accepts ONLY `"fresh"` or `"head"`; default is `"fresh"` (branch from `origin/HEAD`). `"head"` branches from local HEAD per ADR-046 item 2.
   - A **`WorktreeCreate`** hook (exact event key, camelCase: `WorktreeCreate`). JSON structure:
     ```
     {
       "worktree": { "baseRef": "head" },
       "hooks": {
         "WorktreeCreate": [
           { "hooks": [ { "type": "command", "command": "bash <seeding-script>" } ] }
         ]
       }
     }
     ```
   - **Hook I/O contract (pinned).** The hook command receives JSON on STDIN containing a `.name` field (the worktree name); read it with `jq -r .name`. `CLAUDE_PROJECT_DIR` is available in the environment (the project root). The hook MUST echo the seeded worktree directory path to STDOUT; diagnostics go to STDERR (`>&2`).
   - **Seeded worktree directory** is `.claude/worktrees/<name>` (ADR-046 item 1).
   - **Seeding command behavior.** The seeding command is a `command` hook; you may implement it inline in `settings.json` or as a small tracked script the command invokes (implementation detail, your call: this is not a design decision). Against the worktree dir it performs: (1) symlink the main checkout's `app/.env` into `<worktree>/app/.env` (skip gracefully if the source is absent); (2) `docker compose build` for the worktree's stack; (3) assign a distinct `API_HOST_PORT` and write it into `<worktree>/app/.env`; (4) ensure `git config core.hooksPath .githooks` is set; then echo the worktree dir to STDOUT.
   - Acceptance test (a) (create one real worktree, confirm it comes up seeded) is how you confirm your OWN seeding script works end to end. This is verifying your own implementation, NOT investigating a design question.
5. **`app/docker-compose.yml`** (edit): change the `api` service published port from `"8123:8123"` (line 59) to `"${API_HOST_PORT:-8123}:8123"`. No other compose changes.
6. **`CLAUDE.md`** (repo root, edit): add a short subsection pointing sessions at `GIT_WORKFLOW.md`, AND amend the documentation-placement rule (the sentence enumerating the sanctioned repo-root files: currently `CLAUDE.md`, `README.md`, `END-GOAL.md`) to add `GIT_WORKFLOW.md`.
7. **`.gitignore`** (edit): add `.claude/worktrees/`.

## Files in scope

- `GIT_WORKFLOW.md` (new)
- `bin/git-integrate` (new, executable)
- `.githooks/pre-merge-commit` (new, executable)
- `.githooks/pre-commit` (new, executable)
- `.claude/settings.json` (new)
- `app/docker-compose.yml` (edit: the single port-parameterization line, line 59)
- `CLAUDE.md` (edit: pointer subsection + sanctioned-root-file list)
- `.gitignore` (edit: add `.claude/worktrees/`)

## Files out of scope

- Any other file under `app/` (`api/`, `db/`, their source and tests) beyond the single `app/docker-compose.yml` port line.
- `ai-infrastructure/project-manager/dashboard/` and any dashboard files.
- `ai-infrastructure/project-manager/decisions/ADR-046-concurrent-session-git-workflow-worktrees-enforced-merge-lock.md` and any other ADR (accepted, append-only; do not edit).
- A `reference-transaction` hook (the recorded airtight upgrade, ADR-046 Consequence 7) - do NOT build it now. Scope-of-impact on this task: this task's hook enforcement does not depend on a reference-transaction hook. The `pre-merge-commit` plus `pre-commit` hooks, combined with the mandatory `--no-ff` on `master`, cover the enforced integration path for this task, and acceptance tests (b) through (e) exercise that path end to end. The reference-transaction hook is an additive, airtight future upgrade with no bearing on any deliverable here; deferring it changes nothing you build or verify.
- A `develop` branch (deferred per the ADR-046 sub-decision) - do NOT create one. Scope-of-impact on this task: this task implements the trunk-based model directly (short-lived feature branches off `master`, merged straight back into `master`); no deliverable above and no acceptance test (a) through (f) depends on a `develop` branch existing. Deferring `develop` per the ADR-046 sub-decision therefore has no bearing on any of this task's surfaces.
- Any task file, `STATUS.md`, `OBSERVATIONS.md` (orchestrator-owned; do not touch).

## References

Cite these verbatim; do not reconstruct paths from naming conventions.

- `ai-infrastructure/project-manager/decisions/ADR-046-concurrent-session-git-workflow-worktrees-enforced-merge-lock.md` (the accepted spec this implements; Decision items 1-11, Consequences 1-10).
- `CLAUDE.md` (repo root: the documentation-placement rule to amend, and the pointer subsection to add).
- `ai-infrastructure/project-manager/decisions/ADR-006-admin-bootstrap-env-hash.md` (gitignored `.env`; the seeding step reproduces `app/.env` per worktree without writing secrets into any tracked file).
- `ai-infrastructure/project-manager/decisions/ADR-003-docker-compose-runtime.md` (docker compose is the only run path; the pre-lock test run and the dependency build both go through compose).
- `ai-infrastructure/project-manager/decisions/ADR-033-remote-deployment-topology.md` (remote is a deploy target, not the source of truth for in-progress work: the `worktree.baseRef: head` rationale).
- `app/docker-compose.yml` (the stack: postgres/migrate/test/test-roundtrip/api/api-test; the `api` published port to parameterize is at line 59).
- `.gitignore` (already ignores `.env*`, with the `.env.example` exception, and `.claude/artifacts/tmp/`; add `.claude/worktrees/`).

## Related tasks and ADRs

- ADR-046 - the accepted spec this task implements (Decision item 11 anticipates this implementation task).
- ADR-006 - secrets live only in gitignored `.env`; the seeding step must reproduce `app/.env` per worktree without writing secrets into any tracked file.
- ADR-003 - docker compose is the only sanctioned run path; the pre-lock test run and dependency build both go through compose.
- ADR-033 - remote is a deploy target, not the in-progress source of truth; rationale for `worktree.baseRef: head`.
- ADR-005 - the two-domains framing; this is domain-2 policy that intentionally touches exactly one domain-1 file (`app/docker-compose.yml` port).
- COR-T-055 - recent dashboard task; context only, evidence that the web app is real and active (do not modify).

## Hard rules

- **Verification must leave the real repo unmutated.** Exercise the hook refusal, the wrapped `--no-ff` merge, and the `flock` contention/auto-release in a DISPOSABLE throwaway git repo created with `git init` under `.claude/artifacts/tmp/` (gitignored scratch). Copy `.githooks/` and `bin/git-integrate` into it, wire `core.hooksPath`, and simulate two concurrent sessions there. For the worktree-seeding check (acceptance a), create ONE real worktree via the actual flow, verify it, then tear it down cleanly. At the end, no stray commits on `master`, no leftover branches, no leftover worktrees, no leftover lock file. Leave the real repo exactly as found.
- **The marker is an env var, never a tracked file.** The wrapper exports `CORRAL_SANCTIONED_MERGE=1`; the hooks read that env var. Do not introduce a tracked sanction file.
- **`--no-ff` is mandatory on `master`.** Every integration into `master` forms a merge commit so `pre-merge-commit` always fires. Do not allow a fast-forward path into `master`.
- **Tests run before the lock, never inside it.** The locked critical section is only the `--no-ff` merge plus the fast post-merge sanity check (seconds). Do not run the test suite inside the lock.
- **No secrets in tracked files.** The `.env` seeding symlinks `app/.env`; never copy secret values into any tracked file, log, or the kickoff report (ADR-006, and the global secrets rule in `CLAUDE.md`).
- **Compose-only run path.** Any test run or dependency build goes through `docker compose` against `app/docker-compose.yml`; never assume host-installed Python or Node (ADR-003).
- **The `.claude/settings.json` shape is pinned, not yours to derive.** Implement Deliverable 4 exactly as pinned: `worktree.baseRef: "head"`, the `WorktreeCreate` event key (camelCase), and the STDIN/`jq -r .name`/`CLAUDE_PROJECT_DIR`/STDOUT-echo I/O contract. Do not redesign the event name or the I/O contract.
- **Do not edit any ADR.** ADR-046 and all ADRs are accepted and append-only.

## Acceptance gate

A single acceptance gate. The closing report confirms all of (a) through (f) plus the no-mutation guarantee:

- (a) A worktree created per the flow branches from local `master` HEAD (not `origin/master`) and comes up seeded: `app/.env` present (symlinked) and `core.hooksPath` set. (Create one real worktree, verify, tear it down.)
- (b) An un-wrapped `git merge <branch>` into `master` is refused by the hook. (Verify in a disposable throwaway repo.)
- (c) A merge through `bin/git-integrate` succeeds and is `--no-ff` (a merge commit is always formed). (Disposable repo.)
- (d) A second integration attempt while the lock is held fails immediately via `flock -n` and surfaces the escalate-to-user message rather than blocking. (Disposable repo.)
- (e) A holder that exits mid-merge releases the lock automatically (no stale lock stranded). (Disposable repo.)
- (f) `GIT_WORKFLOW.md` exists at the repo root, contains only the operational flow (no rationale), and its footer points to ADR-046; `CLAUDE.md` points at it and lists it among the sanctioned root files.
- Plus: the real repo is left unmutated by verification (no stray commits on `master`, no leftover branches, worktrees, or lock files).

## Executor pointer

The executor is the dispatched `executor` (ADR-028). Universal executor conventions (the writing rules and Agent Discipline in `CLAUDE.md`, the compose-only run policy, git boundaries, the pinned six-section report shape) live in `docs/ai-orchestration/roles/EXECUTOR-ROLE.md`; this kickoff references them rather than re-emitting them. The closing report is written to `.claude/artifacts/handoffs/COR-T-057-KICKOFF-REPORT.md` per EXECUTOR-ROLE.md, section "Report shape".
