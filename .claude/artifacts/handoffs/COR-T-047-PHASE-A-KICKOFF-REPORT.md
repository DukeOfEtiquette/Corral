# COR-T-047 Phase A Kickoff Report

## Deliverables completed

All three deliverables shipped:

1. **`./ai-infrastructure/project-manager/dashboard/etl.py`** -- all four changes made:
   - Added `git_last_updated(repo_root, paths)` function: runs `git -C <repo_root> log -1 --format=%cs -- <paths>`, returns `YYYY-MM-DD` string or empty string on no commits / error.
   - Added `git_recent_updates(repo_root, paths)` function: runs `git -C <repo_root> log -10 --format=%cs%x1f%s -- <paths>`, splits on ASCII unit separator, returns list of `{date, text}` dicts newest-first, capped at `RECENT_UPDATES_CAP` (10).
   - Wired the collectors in, replacing all four frontmatter reads:
     - coordinator `last_updated` (was `str(coordinator_fm.get("last_updated", ""))`) -> `git_last_updated(repo_root, COORDINATOR_PATHS)`. `COORDINATOR_PATHS` is `["ai-infrastructure/project-manager/", "docs/", ".claude/commands/", ".claude/agents/"]`.
     - coordinator `recent_updates` (was `parse_recent_updates(coordinator_fm)`) -> `git_recent_updates(repo_root, COORDINATOR_PATHS)`.
     - department `last_updated` (was `str(fm.get("last_updated", ""))`) -> `git_last_updated(repo_root, [f"ai-infrastructure/{slug}/"])`.
     - department `recent_updates` (was `parse_recent_updates(fm)`) -> `git_recent_updates(repo_root, [f"ai-infrastructure/{slug}/"])`.
     - `dept_status()` helper (used by the `departments` list) also updated: was reading `last_updated` from frontmatter; now calls `git_last_updated`.
   - Removed `parse_recent_updates` (confirmed zero residual references via grep).
   - Updated module docstring: added source (h) describing git-by-path activity surface (ADR-039), annotated source (b) noting last_updated/recent_updates are no longer read from STATUS.md frontmatter, updated `meta.last_updated` contract line and `recent_activity` / `recent_updates` entries to state DERIVED from git history. Contract shape is unchanged.
   - Added `import subprocess` to imports.

2. **`./ai-infrastructure/project-manager/dashboard/Dockerfile`** -- git installed in the `serve` stage before the pip install: `RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*`.

3. **`./ai-infrastructure/project-manager/dashboard/entrypoint.sh`** -- `git config --global --add safe.directory /repo` added after `set -e` and before `python /app/etl.py`, with an explanatory comment.

## Decisions made

- **`dept_status()` helper also updated to git-derived.** The kickoff listed four frontmatter reads to replace; the `dept_status()` helper (which produces the `departments[*].status.last_updated` field in data.json) is a fifth frontmatter read of `last_updated`. Since the kickoff's intent is a source-only change (git replaces frontmatter as the source of this field everywhere it appears), the helper was updated to call `git_last_updated` too. This is consistent with ADR-039 and keeps the data.json contract coherent (all `last_updated` values in the output come from the same git source). Recorded here per the kickoff's instruction to note any deviation.

- **git binary used (not dulwich).** The kickoff pins git binary as the preferred route. Git was added to the Dockerfile and no dulwich fallback was needed.

## Surprises

- No surprises. The etl.py line-number anchors in the kickoff were approximate but accurate enough to locate every target. The `dept_status()` helper was not in the kickoff's explicit list but was a clear parallel case; resolved by analogy (see Decisions made).

## Follow-ups

- **COR-T candidate: Phase B (ADR-039 doctrine cascade + frontmatter removal).** The doctrine cascade (removing universal STATUS hygiene from EXECUTOR-ROLE.md, TEST-DESIGNER-ROLE.md, ORCHESTRATOR-ROLE.md, the three orchestrator commands, the department template, and the R6 convention) plus the frontmatter field removal from all STATUS.md files. Explicitly sequenced after Phase A is render-verified (ADR-039 decision 6). Target: the existing COR-T-047 task file (Phase B is the second dispatch under the same task).

- **COR-T candidate: COR-07 headless-render gate.** The kickoff notes that the Orchestrator runs the COR-07 headless-render gate at close. This is the Orchestrator's job, not surfaced here as an executor follow-up, but recorded so the Orchestrator's close-checker can confirm it.

## Files touched

- `./ai-infrastructure/project-manager/dashboard/etl.py`
- `./ai-infrastructure/project-manager/dashboard/Dockerfile`
- `./ai-infrastructure/project-manager/dashboard/entrypoint.sh`
- `./ai-infrastructure/project-manager/STATUS.md`
- `./.claude/artifacts/handoffs/COR-T-047-PHASE-A-KICKOFF-REPORT.md`

## Build / verification status

- **Python syntax check**: `python3 -c "import ast; ast.parse(...)"` returned `syntax OK` on the modified etl.py.
- **Scope guard**: `git diff --name-only` confirmed only the three in-scope files plus STATUS.md (hygiene) and the report file were modified. The JSX views (`RoadmapPanel.jsx`, `LandingView.jsx`, `WorkspaceView.jsx`) and all `STATUS.md` source files (other than the coordinator STATUS hygiene update) are untouched.
- **em-dash check**: `grep -P "[--]"` over all three modified source files found no em dashes.
- **parse_recent_updates removal**: `grep -n "parse_recent_updates"` in etl.py returned no output; fully removed.
- **Compose build + data.json inspection**: NOT run by this executor (ADR-003 run policy; the kickoff delegates this to the Orchestrator's close gate). The Orchestrator is expected to run `docker compose build` against the dashboard and inspect the generated data.json to confirm git-sourced feeds, then run the COR-07 headless-render gate.
- **data.json contract shape**: not changed. Same field names, same nesting, same `{date, text}` and `{workspace, date, text}` structures, same caps (`RECENT_UPDATES_CAP` = 10, `RECENT_ACTIVITY_CAP` = 30). Source-only change per ADR-037 pattern.
