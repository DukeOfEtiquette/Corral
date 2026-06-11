# Dashboard: trim WORKSPACE/ORCHESTRATOR roster columns; add orphan-department row warning (COR-T-031)

## Target

This is AI-infrastructure work (ADR-005), in the coordinator's project-manager insight dashboard. The task is frontend-only: trim two redundant columns from the department roster and add a latent integrity warning to the roster rows. The artifacts in scope are the roster panel component and its stylesheet. The ETL that produces the dashboard data is explicitly out of scope; both data fields the view consumes are already emitted and stay.

## Decisions resolved by the Orchestrator

- **Remove the WORKSPACE column.** Drop the `<th>Workspace</th>` header and its `<td>` (the EXISTS/PLANNED badge). Rationale: workspace planned-ness is already conveyed by the dimmed-row styling (`.dept-planned`, applied when `dept.exists` is false), so the explicit badge is redundant.
- **Remove the ORCHESTRATOR column.** Drop the `<th>Orchestrator</th>` header and its `<td>` (the yes/no badge). Rationale: the create-department recipe (ADR-030) stamps a workspace and its orchestrator command together, so this column is an always-yes/no value; its only interesting case (exists-but-unwired) is replaced by the targeted row warning below. After both removals the table is 7 columns: Department, Domain, Backlog, In progress, Blocked, Done, Total.
- **Add an orphan-department row warning.** On each department's `<tr>`, when `dept.exists && !dept.orchestrator_command`, apply a new CSS class that highlights the row yellow, and add a native HTML `title` attribute to that same row with the EXACT string `⚠ Department exists, orchestrator missing ⚠` (a U+26A0 warning sign at the start and at the end of the text). The native `title` attribute supplies the hover tooltip; do not add a custom tooltip component or any JavaScript for this. Rationale: this surfaces a half-run of the create-department recipe (a workspace stamped without its orchestrator command).
- **The orphan-warning CSS class is a new, distinct class.** Name it descriptively (for example `dept-orphaned`); the exact class name is your mechanical choice, but it must be a NEW class, separate from `.dept-planned`. Do not overload `.dept-planned`.
- **Keep the existing `.dept-planned` row logic intact.** Planned rows (where `dept.exists` is false) keep their current `dept-planned` class and current dimming rule. A row is dimmed (planned) OR orphan-warned (exists-but-unwired) but never both; the two conditions (`!dept.exists` versus `dept.exists && !dept.orchestrator_command`) are mutually exclusive, so no row carries both classes.
- **`etl.py` and the data.json contract are UNCHANGED.** Both `dept.exists` and `dept.orchestrator_command` are already emitted and stay emitted; the row dimming consumes `exists`, and the new warning consumes both. This task only stops rendering them as columns and adds view logic. Do not touch `etl.py` and do not change the data.json shape.
- **The orphan warning is dormant in the current data.** All departments are currently consistent (`exists == orchestrator_command`), so no row is yellow today; the warning is a latent indicator. Confirm it works through the temporary spot-test described under Build and verification, then revert the spot-test.

## Deliverables

1. `ai-infrastructure/project-manager/dashboard/src/panels/DepartmentsPanel.jsx`: the `<th>Workspace</th>` and `<th>Orchestrator</th>` headers and their two `<td>` cells removed (table renders 7 columns: Department, Domain, Backlog, In progress, Blocked, Done, Total); the new orphan-warning CSS class and the native `title` tooltip applied to each `<tr>` when `dept.exists && !dept.orchestrator_command`; the existing `.dept-planned` class logic preserved unchanged.
2. `ai-infrastructure/project-manager/dashboard/src/styles.css`: a new row rule for the orphan-warning class giving a yellow row highlight; the `.dept-planned` rule left exactly as-is.

## Files in scope

- `ai-infrastructure/project-manager/dashboard/src/panels/DepartmentsPanel.jsx`
- `ai-infrastructure/project-manager/dashboard/src/styles.css`

## Files out of scope

- `ai-infrastructure/project-manager/dashboard/etl.py` (do NOT touch; both `exists` and `orchestrator_command` stay emitted)
- `ai-infrastructure/project-manager/dashboard/src/views/WorkspaceView.jsx` and every other panel
- The `.dept-planned` dimming rule in `styles.css` (keep it exactly as-is; do not restyle it)
- The roster's task-count columns and the Department and Domain columns (Backlog, In progress, Blocked, Done, Total, Department, Domain all stay)

## References

- `ai-infrastructure/project-manager/tasks/in-progress/COR-T-031-roster-trim-columns-orphan-warning.md` (the task file; full pinned spec and rationale)
- `ai-infrastructure/project-manager/dashboard/src/panels/DepartmentsPanel.jsx` (the roster component you edit; current 9-column table)
- `ai-infrastructure/project-manager/dashboard/src/styles.css` (the stylesheet you edit; see `.dept-table` and `.dept-planned` rules near the "Departments table" comment, and the `--color-warning` token at `:root`)

## Related tasks and ADRs

- COR-T-030: removed the dead PHASE column from this same panel; its output is the 9-column starting state this task builds directly on.
- COR-T-014: built the dashboard and this department roster.
- ADR-030 (with COR-T-013): the create-department recipe that stamps a workspace and its orchestrator command together; the orphan warning catches a half-run of it (a department that exists but has no orchestrator command).
- ADR-008: the data.json contract is interim (it repoints at the dogfood milestone); it is unchanged by this task anyway.

## STATUS deltas

Universal hygiene only: bump `last_updated` and prepend a `recent_updates` entry to `ai-infrastructure/project-manager/STATUS.md` noting that the WORKSPACE and ORCHESTRATOR roster columns were removed and the orphan-department row warning was added (COR-T-031). No phase change, no roadmap change, no "Next step" change, no data.json contract change.

## Hard rules

- The `title` tooltip string is exact: `⚠ Department exists, orchestrator missing ⚠`. Both bracketing characters are the U+26A0 warning sign; do not substitute a different symbol, drop a triangle, or alter the spacing or wording.
- The orphan-warning class must be a NEW class distinct from `.dept-planned`. Do not extend, rename, or restyle `.dept-planned`.
- Do not edit `etl.py` or change the data.json shape; both `exists` and `orchestrator_command` remain emitted.
- This is the project-manager workspace: per its `CLAUDE.md`, paths into the root-staying shared tree (`docs/ai-orchestration/`, `.claude/`) are written bare (no `./` prefix); workspace-relative references use `./`.

## Build and verification

Run the dashboard through the compose pipeline per ADR-003: `docker compose up -d --build` from `ai-infrastructure/project-manager/dashboard/`.

Confirm in the rendered roster:
1. The table renders 7 columns with no WORKSPACE column and no ORCHESTRATOR column.
2. Planned departments (where `dept.exists` is false) still appear dimmed via `.dept-planned`.
3. No row is yellow in the current (all-consistent) data.

Spot-test the orphan warning, then revert it: temporarily make one EXISTING department satisfy `dept.exists && !dept.orchestrator_command` for a single row (your choice of a reversible local nudge, for example renaming the relevant orchestrator-command file the ETL checks, or temporarily editing the data the view reads), rebuild or refresh, and confirm that one row turns yellow and its hover `title` reads exactly `⚠ Department exists, orchestrator missing ⚠`. Then REVERT the spot-test so the working tree and the running dashboard return to the all-consistent state (no yellow row). The spot-test is a verification-only nudge; it must not be committed and must not survive the session.

The user performs the final visual confirmation. In your report, confirm the 7-column render, the preserved dimming, the all-consistent (no-yellow) baseline, and the spot-tested warning behavior, and state explicitly that the spot-test was reverted.

## Worker pointer

You are the dispatched `worker-agent` (ADR-028). Universal worker conventions live in `docs/ai-orchestration/roles/WORKER-ROLE.md` (run policy, stage-do-not-commit, file-edit hygiene, the pinned six-section report shape). Write your closing report to `.claude/artifacts/handoffs/COR-T-031-KICKOFF-REPORT.md` per WORKER-ROLE.md, section "Report shape" (dual-channel: print to chat and write to file).
