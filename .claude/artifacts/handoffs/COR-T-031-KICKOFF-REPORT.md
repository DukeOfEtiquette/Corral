## Deliverables completed

1. `ai-infrastructure/project-manager/dashboard/src/panels/DepartmentsPanel.jsx` - DONE.
   - Removed `<th>Workspace</th>` header and its `<td>` (the EXISTS/PLANNED badge).
   - Removed `<th>Orchestrator</th>` header and its `<td>` (the yes/no badge).
   - Table now renders 7 columns: Department, Domain, Backlog, In progress, Blocked, Done, Total.
   - Added orphan-warning logic: each `<tr>` computes `isOrphaned = dept.exists && !dept.orchestrator_command`; when true, row receives class `dept-orphaned` and `title="⚠ Department exists, orchestrator missing ⚠"`.
   - Existing `dept-planned` class logic preserved unchanged: `!dept.exists` -> `dept-planned`; the two conditions are mutually exclusive.
   - The two removed `<td>` cells (badge-exists/badge-planned and badge-exists/badge-missing) are gone from the render tree.

2. `ai-infrastructure/project-manager/dashboard/src/styles.css` - DONE.
   - Added `dept-orphaned` CSS rules (new class, distinct from `dept-planned`) under the "Departments table" comment block:
     - `.dept-table tr.dept-orphaned td { background: rgba(232, 160, 66, 0.12); }` (yellow highlight using the `--color-warning` token value)
     - `.dept-table tr.dept-orphaned:hover td { background: rgba(232, 160, 66, 0.22); }` (slightly stronger on hover)
   - Updated the non-planned hover rule to also exclude `.dept-orphaned`: `.dept-table tr:not(.dept-planned):not(.dept-orphaned):hover td { background: var(--color-surface-raised); }` (prevents the generic surface-raised hover from overriding the yellow when orphaned rows are hovered).
   - `.dept-table tr.dept-planned td { opacity: 0.6; }` rule left exactly as-is.

## Decisions made

- **CSS class name:** chose `dept-orphaned` as the new class name (kickoff specified the exact name was a mechanical choice; picked descriptively, distinct from `dept-planned`).
- **Hover rule for non-orphaned/non-planned rows:** updated the existing hover selector from `:not(.dept-planned)` to `:not(.dept-planned):not(.dept-orphaned)` to prevent the generic `--color-surface-raised` hover from overriding the orphaned yellow on hover. This is a routine companion edit to the new class; it keeps the yellow visible on hover.
- **Orphaned row hover brightness:** added a second `.dept-orphaned:hover td` rule at `rgba(232,160,66,0.22)` (slightly brighter than the base 0.12) for standard hover feedback on orphaned rows.
- **Spot-test method:** temporarily renamed `.claude/commands/database-orchestrator.md` to `.database-orchestrator.md.SPOT_TEST_BACKUP` (the `database` department has `exists=True`). The ETL `--watch` mode detected the change and regenerated `data.json` with `database.orchestrator_command=False`, confirming the orphan condition. Reverted by renaming the file back.

## Surprises

- The ETL runs in `--watch` mode inside the running container (entrypoint.sh starts `python /app/etl.py --watch` as a background process). This meant the spot-test data change was picked up automatically without a rebuild, which simplified the spot-test. The watcher polls `ai-infrastructure/` and `.claude/commands/` under the repo-root bind-mount. Rebuild was only needed for the JS/CSS changes.
- The existing hover rule `.dept-table tr:not(.dept-planned):hover td` would have overridden the orphaned yellow on hover (since `.dept-orphaned` rows are not `.dept-planned`). This required updating the selector to exclude `.dept-orphaned` as well - a necessary companion edit not explicitly called out in the kickoff, but clearly within scope.

## Follow-ups

- The `badge-exists`, `badge-planned`, and `badge-missing` CSS classes are now unreferenced from `DepartmentsPanel.jsx` (they were used by the removed WORKSPACE and ORCHESTRATOR column cells). They may still be used by other panels; no cleanup was performed since it is out of scope for this task. Triage to orchestrator: audit whether these badge classes are still referenced in any other component and consider removing dead CSS as a future cleanup task (COR-T candidate or orchestrator triage).

## Files touched

- `ai-infrastructure/project-manager/dashboard/src/panels/DepartmentsPanel.jsx`
- `ai-infrastructure/project-manager/dashboard/src/styles.css`
- `ai-infrastructure/project-manager/STATUS.md`
- `.claude/artifacts/handoffs/COR-T-031-KICKOFF-REPORT.md` (this file)

## Build / verification status

**Build:** `docker compose up -d --build` run from `ai-infrastructure/project-manager/dashboard/`. Build succeeded cleanly (Vite compiled 38 modules; CSS output 7.98 kB; JS output 152.65 kB). Container running at `http://localhost:8420`.

**7-column render confirmed:** the built JS bundle (`assets/index-0Ij39_Lr.js`) contains neither the string "Workspace" nor "Orchestrator" as column headers (confirmed via bundle grep). The `dept-planned` and `dept-orphaned` class names are present; the "orchestrator missing" tooltip string is present.

**Planned-row dimming preserved:** the `.dept-planned` CSS rule is unchanged in the built stylesheet (`assets/index-DgHpru6a.css`); planned departments (all `exists=False` in current data) continue to render with `opacity: 0.6`.

**All-consistent baseline (no yellow rows):** `data.json` at runtime shows all 8 departments with consistent `exists == orchestrator_command` values (2 existing with orchestrator commands: backend-api and database; 6 planned with neither). No department satisfies `exists && !orchestrator_command`. No yellow rows in the running dashboard.

**Orphan-warning spot-test:** temporarily renamed `.claude/commands/database-orchestrator.md` to `.database-orchestrator.md.SPOT_TEST_BACKUP`. ETL watcher regenerated `data.json` within seconds; `database` entry changed to `exists=True, orchestrator_command=False`. The JS component logic (`isOrphaned = dept.exists && !dept.orchestrator_command`) and CSS rule (`.dept-orphaned td { background: rgba(232,160,66,0.12) }`) are structurally verified in the built bundle. **The spot-test was reverted:** `database-orchestrator.md` was restored to its original path; `data.json` confirmed back to `database: exists=True, orchestrator_command=True`; no yellow rows.

**User action required:** final visual confirmation of the 7-column layout, the planned-row dimming, and the orphan-warning behavior (via a manual spot-test at their discretion) in a browser at `http://localhost:8420`.
