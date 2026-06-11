# Dashboard: remove the dead PHASE column from the department roster (COR-T-030)

## Target

This is AI-infrastructure work (ADR-005): the coordinator's project-manager insight dashboard under `ai-infrastructure/project-manager/dashboard/`. The department roster (`DepartmentsPanel`) renders a PHASE column that shows "Phase null" for every existing department and "--" for planned ones, because it reads a department STATUS frontmatter `phase` field that has never existed in the department STATUS schema. The field is structurally dead (always `None`), not stale data. Your task is to remove that dead PHASE column from the roster UI and strip the dead department `phase` from the ETL's department plumbing and the `data.json` contract, while leaving the coordinator's separate, real, derived phase fully intact.

## Decisions resolved by the Orchestrator

- **The PHASE column is a dead field, confirmed.** The roster's PHASE column reads each department's `phase` from STATUS.md frontmatter via `etl.py` `dept_status` (`fm.get("phase")`), but department STATUS files have never carried a `phase` frontmatter field, so it is always `None`. Verified at filing: `database` and `backend-api` both return `{'phase': None, ...}`; the roster prints "Phase null" for existing departments and "--" for planned ones. This is the dead surface you are removing.
- **Scope is the fuller removal (the no-dead-fields path).** Remove the roster column AND strip the dead `phase` from the ETL's department plumbing and the `data.json` contract, not just the UI. This is consistent with COR-T-029's precedent of leaving no dead fields that invite confusion.
- **The coordinator's derived phase is preserved everywhere and is out of scope to change.** Only the DEPARTMENT phase (which is dead) is removed. The coordinator's phase comes from the derived `current_phase` (COR-T-029) and still drives `PulsePanel`, `RoadmapPanel`, and the coordinator's own `WorkspaceView` header badge. Do not touch any coordinator phase surface.
- **`src/views/WorkspaceView.jsx` needs no edit; verify, do not change.** Its phase badge (lines ~65-66) is rendered behind the guard `{h.phase != null && ...}`. Once the department header drops its `phase` key, `h.phase` is `undefined`, and `undefined != null` is `false` in JavaScript, so the badge stays hidden for departments while the coordinator (which keeps `phase`) still renders it. Confirm this holds by reading the file; do not add, remove, or change the guard.

### Exact edits (line numbers are as of filing; re-confirm each by content, they may have drifted)

- **`src/panels/DepartmentsPanel.jsx`:** Remove the `<th>Phase</th>` header cell (line ~14) and the phase `<td>` body cell (`<td className="muted">{dept.status ? `Phase ${dept.status.phase}` : '--'}</td>`, lines ~52-54). The table drops from 10 columns to 9. Leave the Department, Domain, Workspace, Orchestrator columns and the Backlog/In-progress/Blocked/Done/Total count columns intact.
- **`etl.py` `dept_status(slug)` (lines ~405-413):** Remove the `"phase": fm.get("phase")` key from the returned dict; keep `"last_updated"`.
- **`etl.py` department `workspace_details` headers:** Remove the dead department `phase` key from BOTH department branches so the department header no longer carries `phase` in either case. The existing-department branch has `"phase": fm.get("phase")` (line ~509); the planned-department branch has `"phase": None` (line ~485). Both are the same dead department field. Remove both. (The orchestrator's filing-time edit list named the existing-department line explicitly; the planned-department `phase: None` is the same dead key in the same department structure and is in scope for the same reason. See "Surface to verify" below.)
- **`etl.py` JSON-contract docstring (top of file, lines ~28-44):** Update the contract description so it no longer implies a department `phase` field. The `departments[].status` entry's content is the `dept_status` dict (now `{last_updated}` only); the `workspace_details` department header no longer carries `phase`. Keep the `coordinator: {slug, phase, phase_title, last_updated}` line exactly as written (that `phase` is the derived coordinator phase and stays). Do not alter the `meta` `current_phase`/`current_phase_title` descriptions.
- **Do NOT touch the coordinator phase plumbing in `etl.py`:** the `coordinator` struct `"phase": current_phase` (line ~437) and the coordinator `workspace_details` header `"phase": current_phase` (line ~455) are the derived coordinator phase and must stay exactly as written.

## Deliverables

1. `ai-infrastructure/project-manager/dashboard/src/panels/DepartmentsPanel.jsx` with no PHASE column: 9 columns, the count columns and all other columns intact, no `dept.status.phase` reference remaining.
2. `ai-infrastructure/project-manager/dashboard/etl.py` with the dead department `phase` removed from `dept_status` and from both department `workspace_details` header branches, the JSON-contract docstring updated to no longer describe a department `phase` field, and the coordinator's derived phase (the `coordinator` struct and the coordinator `workspace_details` header) untouched.

## Files in scope

- `ai-infrastructure/project-manager/dashboard/src/panels/DepartmentsPanel.jsx`
- `ai-infrastructure/project-manager/dashboard/etl.py`

## Files out of scope

- `ai-infrastructure/project-manager/dashboard/src/views/WorkspaceView.jsx` (verify the department badge stays hidden and the coordinator badge still renders; make NO edit)
- `ai-infrastructure/project-manager/dashboard/src/panels/PulsePanel.jsx` and `ai-infrastructure/project-manager/dashboard/src/panels/RoadmapPanel.jsx` (the coordinator's derived phase; do not touch)
- The coordinator `phase` plumbing in `etl.py`: the `coordinator` struct (line ~437) and the coordinator `workspace_details` header (line ~455). Keep as-is.
- Any STATUS file frontmatter or the department STATUS schema (do not add a `phase` field to departments)
- The roster's task-count columns and every other `DepartmentsPanel` column

## References

- `ai-infrastructure/project-manager/tasks/in-progress/COR-T-030-dashboard-remove-dead-department-phase-column.md` - the task file; full context and the verified affected surfaces. Read-only.
- `ai-infrastructure/project-manager/dashboard/src/panels/DepartmentsPanel.jsx` - the roster panel you edit; the PHASE header and body cell live here.
- `ai-infrastructure/project-manager/dashboard/etl.py` - the ETL you edit; `dept_status`, the two department `workspace_details` header branches, the coordinator phase surfaces to preserve, and the JSON-contract docstring all live here.
- `ai-infrastructure/project-manager/dashboard/src/views/WorkspaceView.jsx` - read-only reference for the null-guard verification (lines ~65-66); confirm the department badge stays hidden after the header drops `phase`.

## Related tasks and ADRs

- COR-T-029 - derived the coordinator phase and established the no-dead-fields precedent; the derived coordinator phase this task preserves comes from it.
- COR-T-014 - built the dashboard, including this dead column.
- COR-03 (OBSERVATIONS) - the sibling milestone-status drift surface; a SEPARATE concern, not part of this task. Do not conflate or touch milestone statuses.
- ADR-008 - the `data.json` contract is interim (it repoints to the app at the dogfood milestone), so removing a contract field is low-risk.

## STATUS deltas

Universal hygiene only. Apply the universal two (bump `last_updated`, prepend a `recent_updates` entry) to `ai-infrastructure/project-manager/STATUS.md` per WORKER-ROLE.md. The `recent_updates` entry should note that the dead department PHASE column and its plumbing were removed and the `data.json` department / `workspace_details` entries no longer carry a `phase` key. No phase, roadmap, or "Next step" change.

## Surface to verify (read by content before editing)

The orchestrator's filing-time edit list named the existing-department `workspace_details` header `phase` (around line 509) but not the planned-department branch `"phase": None` (around line 485). Both are the same dead department field in the same `workspace_details` department structure; remove both so the department header is consistent across the existing and planned branches. This is not a new decision: it is the same "strip the dead department `phase`" decision applied to both code paths it appears in. If you find a third department-header occurrence of a department `phase` not named here, remove it too (it is the same dead field); if you find anything that is NOT clearly the dead department field (for example, anything tied to `current_phase`), leave it and note it in your report's Surprises section rather than guessing.

## Hard rules

- Touch only the two in-scope files. Do not edit `WorkspaceView.jsx`, `PulsePanel.jsx`, `RoadmapPanel.jsx`, the coordinator phase plumbing in `etl.py`, or any STATUS frontmatter.
- Preserve the coordinator's derived phase end to end: the `coordinator` struct `"phase": current_phase` and the coordinator `workspace_details` header `"phase": current_phase` stay exactly as written, and the coordinator's `WorkspaceView` phase badge must still render after your change.
- Do not introduce unrelated cleanup or refactoring in the same edit pass (WORKER-ROLE.md, "File-edit hygiene").

## Verification

Run verification through the dashboard compose pipeline per ADR-003: `docker compose up -d --build` in `ai-infrastructure/project-manager/dashboard/`. Confirm, and report in the closing report's "Build / verification status" section:

- The department roster renders with no PHASE column and no "Phase null" string anywhere (9 columns; the count columns and all other columns intact).
- The rebuilt `data.json`'s `departments[].status` no longer carries a `phase` key, and neither department `workspace_details` header (existing or planned) carries a `phase` key.
- The coordinator's `workspace_details` header still carries its derived `phase`, and the coordinator's `WorkspaceView` still shows its phase badge.

The user performs the final visual confirmation of the rendered roster. Confirm the `data.json` structural checks and the no-PHASE-column render in your report; flag clearly which checks the user still needs to confirm visually.

## Worker pointer

You are the dispatched `worker-agent` (ADR-028). Universal worker conventions live in `docs/ai-orchestration/roles/WORKER-ROLE.md` (the compose-only run policy, the stage-do-not-commit rule, file-edit hygiene, and the pinned six-section report shape). Write your closing report to `.claude/artifacts/handoffs/COR-T-030-KICKOFF-REPORT.md` per WORKER-ROLE.md, section "Report shape".
