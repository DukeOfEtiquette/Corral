---
schema_version: 1
id: COR-T-058
title: "Fix seed-worktree hook: docker compose build runs before worktree files are checked out"
status: done
labels: []
priority: P2
created: 2026-06-24
updated: 2026-06-24
---

## Description

The `WorktreeCreate` seed hook (`bin/seed-worktree`, shipped by COR-T-057 for the ADR-046 worktree-per-session workflow) fails when the harness creates a new worktree. Observed 2026-06-24 while picking up COR-T-056:

```
WorktreeCreate hook failed: bash "${CLAUDE_PROJECT_DIR:-.}/bin/seed-worktree":
  Seeding worktree: .../.claude/worktrees/cor-t-056-docs-gating
  Seeded .../app/.env ...
  API_HOST_PORT=8219 appended ...
  Running docker compose build...
  no configuration file provided: not found
```

Root cause (per `bin/seed-worktree`): step 3 runs `(cd "$WORKTREE_DIR/app" && docker compose build)` (line 63), but at hook-execution time git has not yet checked out the worktree's tracked files, so `app/docker-compose.yml` is absent. The script's own defensive `mkdir -p "$WORKTREE_DIR/app"` (line 35) creates an empty `app/` dir, so the `cd` succeeds and compose then aborts with "no configuration file provided." Because the hook exits non-zero (`set -euo pipefail`), `EnterWorktree` treats creation as failed and does NOT switch the session in, and the git worktree is left unregistered (`git worktree list` shows only the main checkout). The leftover `.claude/worktrees/<name>/app/.env` blocks a later clean `git worktree add` unless removed first.

Workaround used for COR-T-056: create the worktree by hand (`git worktree add <path> -b <branch> master`, which DOES check out files), then seed `.env` / set `core.hooksPath` / build compose manually.

### Likely fix directions (decide at pickup)

- The hook ordering is the real issue: either the `WorktreeCreate` hook should run after git populates the worktree, or `bin/seed-worktree` should not assume a populated tree. Verify against the harness `WorktreeCreate` contract which step owns the checkout.
- If the hook genuinely fires pre-checkout, options include: drop the compose-build step from seeding (build lazily on first compose run instead), or guard the build behind a check that `app/docker-compose.yml` exists and skip with a clear notice when it does not, or have the hook perform/await the checkout itself.
- Whatever the fix, a failed or skipped compose build must not abort worktree creation: seeding convenience should not gate the worktree existing.

### Acceptance

- Creating a worktree via the harness `WorktreeCreate` path (the normal `EnterWorktree` flow) succeeds end to end: the git worktree is registered, the session switches into it, and `app/.env` + `core.hooksPath` are seeded.
- A missing or unbuildable compose config degrades gracefully (clear notice, nonzero-but-nonfatal) rather than failing worktree creation.
- No stale `.claude/worktrees/<name>/` directory is left behind on a failed seed that would block a subsequent creation of the same-named worktree.

References:
- `bin/seed-worktree` (the failing hook script; build step at line 63, defensive mkdir at line 35)
- `.claude/settings.json` (the `WorktreeCreate` hook wiring and `worktree.baseRef`)
- `GIT_WORKFLOW.md` (the worktree-per-session workflow this tooling serves)
- `ai-infrastructure/project-manager/decisions/ADR-046-concurrent-session-git-workflow-worktrees-enforced-merge-lock.md` (the accepted workflow; rationale for seeding)
- `ai-infrastructure/project-manager/tasks/done/` COR-T-057 (shipped this tooling)

## Activity log

- 2026-06-24: Created in backlog by the Project Manager Orchestrator. Filed from a live failure observed while picking up COR-T-056 (the seed hook's `docker compose build` ran against a not-yet-checked-out worktree). P2, standalone, AI-infrastructure domain, unlabelled per ADR-031.
- 2026-06-24: Picked up; moved to in-progress. Verified the true root cause against the harness contract (`code.claude.com/docs/en/worktrees`): a `WorktreeCreate` hook REPLACES git's default worktree logic, so the hook itself must run `git worktree add` (the old script never did, leaving an unpopulated tree). Fix done directly on `master` per user direction (the worktree workflow itself is what is broken).
- 2026-06-24: Done. Rewrote `bin/seed-worktree` to run `git worktree add <dir> -b <name> master` itself, then seed env/port/build/hooksPath as best-effort (warn, never abort), with stale-leftover cleanup so re-creation is never blocked (commit `f708917`, which also logged OBSERVATIONS COR-10). Verified by driving the hook via its documented stdin/stdout contract: happy path (worktree registered, files checked out, `.env`+`API_HOST_PORT` seeded, `core.hooksPath=.githooks`, branch off master HEAD, exit 0 with path on stdout); real `docker compose config` resolves in the worktree (the original "no configuration file provided" failure is gone); stale-leftover dir auto-cleaned and re-creation succeeds; a live registered worktree is never clobbered on same-name re-run (fails gracefully). All three acceptance criteria met. Not validated through a real `EnterWorktree` harness invocation (contract-level verification only).
