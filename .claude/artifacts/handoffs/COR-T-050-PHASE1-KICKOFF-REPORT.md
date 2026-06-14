## Deliverables completed

All five deliverables shipped:

1. `ai-infrastructure/project-manager/dashboard/etl.py`: blocked-set derivation added.
   - New helper `_extract_activity_log_reason(path)` parses the last `- ` bullet under `## Activity log`, strips a leading `YYYY-MM-DD: ` date prefix when present, returns `""` when no log or no bullet exists.
   - New `collect_blocked_tasks_for_workspace(workspace_slug, tasks_root)` walks `tasks/blocked/`, skips `.gitkeep` and files with no parseable frontmatter, returns `[{workspace, id, title, reason}]`.
   - New `collect_all_blocked_tasks(repo_root)` calls the per-workspace collector for the coordinator and every department, returns `(all_blocked, per_workspace_blocked)` where `all_blocked` is sorted by `(workspace, id)`.
   - `run_etl` now calls `collect_all_blocked_tasks` and threads the results into:
     - `workspace_details[slug]["blocked"]` for every workspace (coordinator and all departments, both existing and planned branches).
     - `data["blocked"]` at the top-level assembly (sorted, `[]` when empty).
   - The ETL-never-writes-STATUS invariant (ADR-039) is preserved; `collect_all_blocked_tasks` only reads.
   - Module docstring updated to document the new `blocked` and `workspace_details.blocked` contract fields.

2. `ai-infrastructure/project-manager/dashboard/src/panels/BlockedPanel.jsx` (new file):
   - Receives `blocked` prop (the top-level `data.blocked` list).
   - Always renders as a `card`. Shows literal `No blocked work` when empty; shows an ordered list of entries (`id`, `workspace`, `title`, `reason`) when non-empty.
   - Uses `activity-list` / `activity-item` base classes plus new `blocked-*` classes consistent with `styles.css`.

3. `ai-infrastructure/project-manager/dashboard/src/views/LandingView.jsx`:
   - Added `import BlockedPanel from '../panels/BlockedPanel.jsx'`.
   - Rendered `<BlockedPanel blocked={data.blocked} />` immediately after `<PulsePanel .../>` and before the roster row, placing it in the current-state area alongside phase and next step.
   - `PulsePanel` is untouched (verified via `git diff --name-only`).

4. `ai-infrastructure/project-manager/dashboard/src/views/WorkspaceView.jsx` (`WorkspaceDetailFull`):
   - Added a conditional "Blocked" card rendered only when `detail.blocked && detail.blocked.length > 0`.
   - Each row shows `id`, `title`, and `reason` (when non-empty).
   - Placed before the ADRs card, following the established conditional-card pattern.

5. `ai-infrastructure/project-manager/dashboard/src/styles.css`:
   - Added `.blocked-item`, `.blocked-id`, `.blocked-workspace`, `.blocked-title`, `.blocked-reason` classes in the "Blocked work panel" section, following existing class conventions (`activity-list`, `muted`, `color-danger` for the id).

Verification:
- Fixture `COR-T-999-blocked-fixture.md` created in `tasks/blocked/`, derivation verified by code-path tracing (see "Build / verification status"), fixture deleted. Working tree contains only `.gitkeep` in the blocked dir.
- Empty path verified: `collect_blocked_tasks_for_workspace` with the actual empty blocked dir returns `[]`.
- `etl.py` syntax verified: `python3 -c "import ast; ast.parse(...)"` returns OK.
- No em dashes in any file written (grep confirmed exit 0 on all written files).

## Decisions made

- **Panel placement in LandingView**: placed `BlockedPanel` immediately after `PulsePanel` and before the roster row. The kickoff said "in or beside the current-state area that PulsePanel occupies"; immediately after is the most readable position without altering the PulsePanel card itself.
- **WorkspaceView card placement**: placed the Blocked card before the ADRs card (after Observations). This follows the data-importance ordering: blocked work is more urgent than ADR history.
- **`blocked-item` layout**: used a CSS grid with three columns (`id`, `workspace`/`title`, `reason`) to align entries cleanly. The `reason` field wraps to the third column via `grid-column: 3`. The kickoff specified `id`, `title`, `workspace`, `reason` for the landing view and `id`, `title`, `reason` for the workspace view; both are implemented.
- **`.gitkeep` handling**: `*.md` glob naturally excludes `.gitkeep` (no `.md` extension); added an explicit `if md_file.name == ".gitkeep": continue` guard as a defence-in-depth measure.
- **`blocked` key on planned workspace entries**: the kickoff's `workspace_details` contract update covers all workspaces; planned (non-existing) department entries also receive `"blocked": []`. This is consistent and avoids a None/missing key on the frontend.

## Surprises

- The `tasks/blocked/` directory already existed with `.gitkeep` (confirmed by `ls -la`), so no directory creation was needed. The code handles both the "dir exists but empty" and "dir does not exist" cases correctly.
- `git diff --name-only` showed a pre-existing change to `ai-infrastructure/project-manager/tasks/backlog/COR-T-050-derive-status-narrative-body.md` (deleted from backlog, with the in-progress copy untracked). This is the Orchestrator's prior task-transition work, not part of this dispatch; it was not touched.

## Follow-ups

- COR-T candidate: The `blocked-item` CSS grid uses fixed column widths (`6rem`, `7rem`). On very narrow screens or with long workspace slugs, these may truncate. A future cosmetic pass could make the grid responsive. (triage to orchestrator)
- COR-T candidate: The workspace-view "Blocked" card does not show the `workspace` field (per the kickoff spec: only `id`, `title`, `reason` on the per-workspace view). If a cross-workspace view is ever added to WorkspaceDetailFull, this will need revisiting. (triage to orchestrator)
- Phase 2 (separate dispatch, not this kickoff): remove the hand-authored STATUS body sections from all `ai-infrastructure/*/STATUS.md` files and run the doctrine cascade across role docs, commands, and specs, per ADR-040 decision 7 and COR-T-050 description.

## Files touched

- `ai-infrastructure/project-manager/dashboard/etl.py` (modified)
- `ai-infrastructure/project-manager/dashboard/src/panels/BlockedPanel.jsx` (new)
- `ai-infrastructure/project-manager/dashboard/src/views/LandingView.jsx` (modified)
- `ai-infrastructure/project-manager/dashboard/src/views/WorkspaceView.jsx` (modified)
- `ai-infrastructure/project-manager/dashboard/src/styles.css` (modified)
- `.claude/artifacts/handoffs/COR-T-050-PHASE1-KICKOFF-REPORT.md` (this report, new)

Fixture `ai-infrastructure/project-manager/tasks/blocked/COR-T-999-blocked-fixture.md` was created and deleted within this dispatch; it does not appear in the working tree and was never committed.

STATUS.md: not touched (status_deltas is "none"; the STATUS body is explicitly out of scope in phase 1).

## Build / verification status

**Verified by inspection (no runtime available under ADR-003 compose-only):**

1. `etl.py` syntax: `python3 -c "import ast; ast.parse(...)"` returned OK.
2. Blocked derivation - populated path: created fixture `COR-T-999-blocked-fixture.md` with frontmatter `id: COR-T-999` and a one-line activity log. Ran inline Python tracing the exact `parse_frontmatter` + `_extract_activity_log_reason` code path. Output confirmed:
   - `id`: `COR-T-999`
   - `title`: correct from frontmatter
   - `status_dir`: `blocked` (directory-authoritative)
   - `reason`: activity log text with date prefix correctly stripped
3. Blocked derivation - empty path: ran `collect_blocked_tasks_for_workspace` against the actual `tasks/blocked/` dir (`.gitkeep` only). Confirmed `[]` returned.
4. No em dashes: grep for U+2014/U+2013 on all five written files returned exit 0.
5. `PulsePanel.jsx` untouched: confirmed via `git diff --name-only` (not in the changed-file list).
6. Fixture deleted: `ls -la tasks/blocked/` shows only `.gitkeep`; `git status` does not list the fixture.

**Requires compose runtime (user-gated visual check, per kickoff):**
- Live ETL run to confirm `data.json` shape matches the contract (top-level `blocked: []`, per-workspace `blocked: []` in `workspace_details`).
- Visual dashboard render: landing view shows "Blocked work" panel with "No blocked work"; workspace view "Blocked" card is absent (no blocked tasks = card not rendered).
- With a real blocked task: landing view shows entries with `id`, `workspace`, `title`, `reason`; workspace view shows `id`, `title`, `reason`.
