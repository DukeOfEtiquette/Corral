# COR-T-047 Phase A: derive the dashboard activity surface from git (ETL + container), contract stable

## Target

This is AI-infrastructure work (ADR-005, domain 2: the tooling that builds and maintains the web app). The artifact in scope is the project-manager dashboard's ETL and its container, at `./ai-infrastructure/project-manager/dashboard/`. This is Phase A of COR-T-047, implementing ADR-039: make the dashboard ETL derive each workspace's activity surface (`last_updated` plus the `recent_updates` / `recent_activity` feed) from git history instead of from `STATUS.md` frontmatter, while keeping the generated `data.json` contract shape byte-for-byte compatible so the frontend needs no change. This is the same surgical source-only pattern ADR-037 / COR-T-045 used when it moved the roadmap source to files: change where the data comes from, preserve the contract it flows into.

Phase B (a separate later dispatch) removes the now-vestigial `STATUS.md` frontmatter fields and runs the ADR-039 doctrine cascade. None of Phase B is in scope here. The sequencing is deliberate: the derive-ETL and container change land and are render-verified first, so there is never a window where the activity surface is neither hand-maintained nor derived.

## Decisions resolved by the Orchestrator

Every decision below is pinned. Implement them as written; do not re-derive or re-open them.

- **Two new git collectors, returning the EXISTING contract shapes.** Add both to `./ai-infrastructure/project-manager/dashboard/etl.py`:
  - A per-workspace **activity collector** returning a list of `{date, text}` dicts, newest-first, capped at the existing `RECENT_UPDATES_CAP` (= 10, etl.py line 125). Source it from `git log` over the workspace's owned paths, with `date` = `%cs` (committer short date, `YYYY-MM-DD`) and `text` = `%s` (commit subject). Use a field separator that cannot appear in a commit subject (use `%x1f`, the ASCII unit separator) and split on it. Run git against the repo root via the existing `REPO_ROOT` env / `repo_root` value (which is `/repo` in-container): `git -C <repo_root> log --format=...%x1f... -- <paths>`.
  - A per-workspace **last_updated collector** returning the date string of the most recent commit that touched the workspace's owned paths: `git -C <repo_root> log -1 --format=%cs -- <paths>`. Return the empty string when there are no commits for those paths.
- **Workspace path ownership (which paths each feed covers).** Pinned per workspace:
  - **coordinator** (slug `project-manager`): the path set `ai-infrastructure/project-manager/`, `docs/`, `.claude/commands/`, `.claude/agents/`. The coordinator owns its workspace AND the shared role docs / commands / agents per ADR-029, so role-doc and command work surfaces in its feed.
  - **each department**: `ai-infrastructure/<slug>/` only (phases and role docs are not department-owned).
  - A single commit that touches multiple workspaces legitimately appears in each of their feeds. This is how cross-workspace coordinator writes get captured, and it is the exact drift ADR-039 exists to fix. Do NOT add cross-workspace dedup.
- **Wire the collectors in, replacing the four frontmatter reads.** In etl.py:
  - coordinator `last_updated` (~line 903, currently `str(coordinator_fm.get("last_updated", ""))`) -> the git last_updated collector over the coordinator path set. This value already flows to the coordinator dict (~line 1094), the coordinator header (~line 1111), and `meta` (~line 1191); keep all of those wired to the new value.
  - coordinator `recent_updates` (currently `parse_recent_updates(coordinator_fm)` ~line 1101) -> the git activity collector over the coordinator path set.
  - department `recent_updates` (currently `parse_recent_updates(fm)` ~line 1150) and department `last_updated` (currently `str(fm.get("last_updated", ""))` ~line 1163) -> the git collectors over `ai-infrastructure/<slug>/`.
  - The `recent_activity` aggregate (~lines 1171-1182, capped at `RECENT_ACTIVITY_CAP` = 30) keeps its existing logic; it reads `workspace_details[*]['recent_updates']` and now simply consumes git-sourced entries. No change beyond that.
- **Remove `parse_recent_updates`.** With the wiring above it becomes unused; remove the function. Keep both caps: `RECENT_UPDATES_CAP` (now used by the new activity collector) and `RECENT_ACTIVITY_CAP` (still used by the aggregate). Do NOT remove either cap.
- **Container: install git so the in-container ETL can read git against the read-only `/repo` mount.**
  - `./ai-infrastructure/project-manager/dashboard/Dockerfile` (the `serve` stage, `python:3.12-slim`): install git, e.g. `RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*`.
  - `./ai-infrastructure/project-manager/dashboard/entrypoint.sh`: before the ETL runs, mark the mount safe for git under host ownership: `git config --global --add safe.directory /repo`. The bind-mount is read-only and owned by the host UID, which trips git's dubious-ownership check; this config clears it.
  - The git binary is the chosen route. dulwich (pure-Python, added to the pip install) is the FALLBACK only if the git-binary route proves unworkable in-container; prefer the git binary and do not reach for dulwich unless the git route is genuinely blocked.
- **Update the etl.py module docstring.** Update the sources list and the JSON-contract description to state that `last_updated` and the `recent_updates` / `recent_activity` feed are now git-derived (per ADR-039), not read from `STATUS.md` frontmatter. State that the `data.json` contract SHAPE is unchanged: same fields, same `{date, text}` and `{workspace, date, text}` structures, same caps.

## Deliverables

- `./ai-infrastructure/project-manager/dashboard/etl.py`: the two git collectors, the wiring that replaces the four frontmatter reads, the removal of `parse_recent_updates`, and the docstring update.
- `./ai-infrastructure/project-manager/dashboard/Dockerfile`: git installed in the `serve` stage.
- `./ai-infrastructure/project-manager/dashboard/entrypoint.sh`: the `safe.directory` config added before the ETL runs.

## Files in scope

- `./ai-infrastructure/project-manager/dashboard/etl.py`
- `./ai-infrastructure/project-manager/dashboard/Dockerfile`
- `./ai-infrastructure/project-manager/dashboard/entrypoint.sh`

## Files out of scope

Do NOT modify any of these. They are Phase B, contract-preserved, or accepted-and-frozen.

- All `STATUS.md` files. Removing the `last_updated` / `recent_updates` frontmatter fields is Phase B. In Phase A the fields stay on disk; the ETL simply stops reading them. Do not edit, remove, or rewrite any frontmatter.
- `./docs/ai-orchestration/roles/*.md`, `./.claude/commands/*orchestrator*.md`, `./ai-infrastructure/project-manager/templates/department/*`: the Phase B doctrine cascade. Untouched here.
- `./ai-infrastructure/project-manager/dashboard/src/views/RoadmapPanel.jsx`, `./ai-infrastructure/project-manager/dashboard/src/views/LandingView.jsx`, `./ai-infrastructure/project-manager/dashboard/src/views/WorkspaceView.jsx`: the contract shape is preserved, so they need no change. You may read them to confirm the contract holds, but do NOT edit them.
- `./ai-infrastructure/project-manager/decisions/ADR-039-status-derived-activity-surface.md`: accepted; do not edit.

## References

Read these in order. The first is the decision being implemented; the rest are the target and the precedent.

- `./ai-infrastructure/project-manager/decisions/ADR-039-status-derived-activity-surface.md`: the decision being implemented. Phase A is the derive-ETL plus container half (decisions 2 and 4); source-only, contract preserved.
- `./ai-infrastructure/project-manager/dashboard/etl.py`: the target. Key anchors: `RECENT_ACTIVITY_CAP` = 30 (line 124), `RECENT_UPDATES_CAP` = 10 (line 125), `parse_recent_updates` (~line 165), coordinator `last_updated` (~line 903), coordinator `recent_updates` (~line 1101), department `recent_updates` / `last_updated` (~lines 1150 / 1163), the `recent_activity` aggregate (~lines 1171-1182), `meta` `last_updated` (~line 1191). Line numbers are approximate anchors; confirm the exact lines on read.
- `./ai-infrastructure/project-manager/dashboard/Dockerfile`: the `serve` stage gets the git install.
- `./ai-infrastructure/project-manager/dashboard/entrypoint.sh`: gets the `safe.directory` config before the ETL runs.
- `./ai-infrastructure/project-manager/decisions/ADR-037-work-item-storage-representation.md`: the source-only-change precedent. COR-T-045 moved the roadmap source to files while preserving the `data.json` contract; this task follows the same pattern for the activity surface.
- `./ai-infrastructure/project-manager/decisions/ADR-003-docker-compose-runtime.md`: docker compose is the only supported run path; the build and verification run through compose.

## Related tasks and ADRs

- ADR-039: the decision this implements. Phase A is its derive-ETL plus container half (decisions 2 and 4); the doctrine cascade and frontmatter removal are decision 6 (Phase B).
- ADR-037 / COR-T-045: the precedent. A source-only ETL change to this same file, contract preserved, with a render gate at close.
- ADR-008: the post-dogfood source swap (git -> `issue_events`) reuses this contract. Future, not now; no action in Phase A.
- ADR-003: the compose-only run policy used for the build and verify.

## STATUS deltas

No task-specific STATUS deltas; universal hygiene only.

## Hard rules

- **Source-only change.** The `data.json` contract shape is unchanged: same field names, same nesting, the same `{date, text}` and `{workspace, date, text}` structures, the same caps (`RECENT_UPDATES_CAP` = 10, `RECENT_ACTIVITY_CAP` = 30). If a change you are about to make would alter any of those, stop; the change is out of scope for Phase A.
- **Prefer the git binary; dulwich is a fallback only.** Do not add dulwich unless the git-binary route proves genuinely unworkable in-container. If you do fall back to dulwich, record it under "Decisions made" in your report so the Orchestrator sees the deviation.
- **Do not touch the three JSX views or any `STATUS.md`.** The contract is preserved precisely so the frontend stays unchanged; the frontmatter removal is Phase B.
- The universal repo rules (no em dashes in files, `./` repo-root-relative paths, no secrets, compose-only run policy, stage-do-not-commit, the pinned six-section report shape) apply per `./docs/ai-orchestration/roles/EXECUTOR-ROLE.md` and `./CLAUDE.md`; they are not restated here.

## Verification expectations

Verify through docker compose (ADR-003, the only sanctioned run path). Specifically:

- Build the dashboard via compose and confirm it builds with git installed and the ETL runs without git errors (the `safe.directory` config clears the dubious-ownership check on the read-only `/repo` mount).
- Inspect the generated `data.json` and confirm `last_updated` and `recent_activity` are populated from git: the coordinator feed should show recent COR-T-046 / COR-T-047 commit subjects, and the database workspace feed should show the COR-T-044 commit that touched `ai-infrastructure/database/` (the cross-workspace-write capture that motivated ADR-039).
- Confirm the `data.json` contract shape is unchanged: same fields and the same `{date, text}` / `{workspace, date, text}` structures.
- Confirm via `git diff` that `RoadmapPanel.jsx`, `LandingView.jsx`, and `WorkspaceView.jsx` were not modified, and that no `STATUS.md` was modified.
- Note in your report that the COR-07 headless-render gate is the Orchestrator's to run at close; you are not expected to run it. Your verification is the compose build plus the `data.json` inspection above.

## Executor pointer

The executor is the dispatched `executor` (ADR-028). Universal executor conventions live in `./docs/ai-orchestration/roles/EXECUTOR-ROLE.md`. Write the closing report to `./.claude/artifacts/handoffs/COR-T-047-PHASE-A-KICKOFF-REPORT.md` per EXECUTOR-ROLE.md, section "Report shape" (dual-channel: chat and file).
