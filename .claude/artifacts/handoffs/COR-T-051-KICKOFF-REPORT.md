## Deliverables completed

All four deliverables from the kickoff are done:

1. **`ai-infrastructure/project-manager/dashboard/etl.py`** - Added `dept_epic_count` helper (lines 1256-1266) and `no_epic_warning` field (lines 1277-1293) to the departments assembly loop. The helper counts `*.yml` files in `ai-infrastructure/<slug>/epics/` (excluding dotfiles) directly, not via `collect_roadmap_from_files` (per the pinned decision). The warning fires when `exists` is `true` AND `epic_count == 0`; null otherwise. Follows the `phase_warning`/`epic_warning`/`cross_dept_warning` string-or-null shape exactly. No derived statuses changed; the change is purely additive.

2. **`ai-infrastructure/project-manager/dashboard/src/panels/DepartmentsPanel.jsx`** - Added `isNoEpic` flag driven by `dept.no_epic_warning`, a `dept-no-epic` row class, and a `title` tooltip carrying the warning string. The logic follows the `isOrphaned` precedent precisely (same structure, same rendering approach). Row class priority: `dept-planned` > `dept-orphaned` > `dept-no-epic` > default.

3. **`ai-infrastructure/project-manager/dashboard/src/styles.css`** - Added two lines for `dept-no-epic` (background `rgba(240, 106, 106, 0.10)` normal, `rgba(240, 106, 106, 0.20)` hover) and updated the hover-exclusion selector to include `not(.dept-no-epic)`. Uses `--color-danger` hue to distinguish from the orphaned amber, following the `dept-orphaned` lines 354-355 as the style template.

4. **`.claude/commands/create-department.md`** - Four edits applied:
   - (a) Added fifth argument `<phase>` to "Inputs" section; updated example invocation to include `2`.
   - (b) Added `{{DEPT_PHASE}}` row to "Token substitution" table.
   - (c) Added `epics/.next-epic-id` (seeded to `2`) and the forming epic YAML to "What this command creates".
   - (d) Expanded Step 4 to describe the forming epic creation (inline, no template file, per ADR-041 decision 1); updated Step 6 verification to include the `epics/` tree and the forming epic file.

5. **`ai-infrastructure/project-manager/tasks/README.md`** - Amended "Lazy creation" subsection (line 90) to reflect the eager-forming-epic convention (ADR-041): a department files at least one forming epic when stood up; the `epics/` tree is created then. Reconciled with the no-empty-placeholders rule by noting a forming epic carries real content. Added ADR-041 to the cross-references; ADR-021, ADR-031, and ADR-036 references retained.

## Decisions made

- **CSS color for `dept-no-epic`:** Used `--color-danger` hue (`rgba(240, 106, 106, ...)`) at 0.10/0.20 alpha, mirroring the `dept-orphaned` amber pattern. This visually distinguishes no-epic (danger-red) from orphaned (warning-amber), which is appropriate since missing epics is a roadmap correctness issue. This was not pinned in the kickoff but follows the style convention exactly (same alpha levels, same pattern).
- **Row class priority:** `dept-planned` > `dept-orphaned` > `dept-no-epic`. A department that is orphaned AND has no epic shows `dept-orphaned` (the more directly actionable condition). In practice the ordering is academic because an orphaned department (exists but no orchestrator command) would typically have an epic if it was properly stood up.

## Surprises

- The `*.yml` glob in Python's `pathlib` does NOT match dotfiles (files beginning with `.`), so the `.next-epic-id` counter is naturally excluded without any extra filtering. The `if not f.name.startswith(".")` guard in `dept_epic_count` is therefore redundant but harmless and serves as documentation of intent (ADR-041 specifies to exclude the counter file).
- The `DepartmentsPanel.jsx` already had `title` on `<tr>` wired for the `isOrphaned` case but passed `undefined` otherwise. Extending to `rowTitle` with a conditional cleanly handles both cases without touching the existing orphaned tooltip.

## Follow-ups

- **COR-T candidate:** The `dept-no-epic` hover exclusion selector is now a four-`not()` chain (`dept-planned`, `dept-orphaned`, `dept-no-epic`). If future warning classes are added, the selector grows. A triage note for the orchestrator: if a third warning class is ever added, consider whether to refactor to a shared `.dept-exists:hover td` rule or keep the exclusion pattern. Low priority; flag for ADR-036 / warning-family triage.
- **Render gate:** The orchestrator's visual render gate (the dashboard running for close verification) is the confirmation step for the visual surface. The no-epic warning row is not currently triggered for any live department (`backend-api` and `database` each have one epic), so the render gate will confirm the table renders correctly with no warnings visible (all null). The warning-fires path was verified by code inspection and the Python simulation below; no temporary edit was left on disk.

## Files touched

- `ai-infrastructure/project-manager/dashboard/etl.py`
- `ai-infrastructure/project-manager/dashboard/src/panels/DepartmentsPanel.jsx`
- `ai-infrastructure/project-manager/dashboard/src/styles.css`
- `.claude/commands/create-department.md`
- `ai-infrastructure/project-manager/tasks/README.md`
- `.claude/artifacts/handoffs/COR-T-051-KICKOFF-REPORT.md` (this report)

## Build / verification status

**Verified by code inspection:**

- `no_epic_warning` is `null` for all departments in the current repo: `backend-api` (`epic_count=1`) and `database` (`epic_count=1`) both pass; all six non-existing departments have `exists=False` so the condition does not fire. Confirmed by running the warning logic in Python directly against the repo tree.
- The `dept_epic_count` helper counts `*.yml` files directly (not via `collect_roadmap_from_files`), excluding dotfiles. The `.next-epic-id` counter is not a `.yml` file so the glob excludes it naturally; the explicit dotfile guard adds documentation.
- The `no_epic_warning` field is additive to the departments dict; all other fields (`slug`, `domain`, `exists`, `orchestrator_command`, `label`, `status`, `task_counts`) are byte-for-byte unchanged.
- The derived `current_phase` (2), `next_step`, roadmap statuses, and blocked surface are untouched by this change (no paths through `derive_current_phase`, `derive_epic_status`, or `derive_roadmap_status` were altered).
- Warning-fires path: verified by inspection -- `exists and epic_count == 0` is the exact condition; if either `backend-api` or `database` lost its epic YAML, `epic_count` would drop to `0` and `no_epic_warning` would be set. No temporary edits were left on disk.

**Requires orchestrator visual gate:**

- The dashboard render gate: the orchestrator confirms visually that the departments table renders cleanly (no warning rows for the current repo state, since `no_epic_warning` is null for all departments). No browser launch needed by the executor; this is the orchestrator's gate per the kickoff's verification expectations.

**Not run (compose-only per ADR-003):**

- No `docker compose` run was performed. ETL correctness is verified by code inspection and Python simulation above.
