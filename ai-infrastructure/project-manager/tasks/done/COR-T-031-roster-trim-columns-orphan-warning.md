---
schema_version: 1
id: COR-T-031
title: "Dashboard: trim WORKSPACE/ORCHESTRATOR roster columns; add orphan-department row warning"
status: done
labels: []
priority: P2
created: 2026-06-11
updated: 2026-06-11
epic: COR-E-004
---

## Description

Two columns in the department roster (`DepartmentsPanel`) are redundant with signals the roster already carries, and one of them can be replaced by a more useful warning. Directed by the user during the COR-T-030 close review. Follows COR-T-030 (which removed the dead PHASE column from the same panel).

1. **Remove the WORKSPACE column** (the EXISTS/PLANNED badge). Planned-ness is already conveyed by the dimmed-row styling (`.dept-planned`, applied when `dept.exists` is false), so the explicit badge is redundant.

2. **Remove the ORCHESTRATOR column** (the yes/no badge). It currently shows whether the department's `/<slug>-orchestrator` command exists, which is coupled to workspace existence by the create-department recipe (both stamped together). Instead of an always-"yes"/"no" column, surface the only interesting case: a department that exists but is not fully wired.

3. **Add an orphan-department row warning.** When a department `exists` but has no orchestrator command (`dept.exists && !dept.orchestrator_command`), highlight that table row yellow and give it a hover tooltip reading exactly `⚠ Department exists, orchestrator missing ⚠` (a native `title` attribute; warning triangles bracketing the string). This is a latent integrity indicator that catches a half-run of create-department; it is dormant while every department is consistent.

This is a frontend-only change. Both `dept.exists` and `dept.orchestrator_command` stay in the emitted `data.json` (the row dimming consumes `exists`; the new warning consumes both), so `etl.py` is NOT touched - unlike COR-T-030, this removes columns from the view without removing any data field.

Known affected surfaces:
- `src/panels/DepartmentsPanel.jsx` - remove the `<th>Workspace</th>` and `<th>Orchestrator</th>` headers and their two `<td>` cells (the table drops from 9 columns to 7: Department, Domain, Backlog, In progress, Blocked, Done, Total). Add the orphan-warning logic to the `<tr>`: a CSS class when `dept.exists && !dept.orchestrator_command`, plus the `title` tooltip on that row. Keep the existing `dept-planned` class logic intact.
- `src/styles.css` - add the new orphan-warning row rule (yellow highlight). Leave `.dept-planned` as-is.

Decisions pinned (resolved with the user): remove both columns; divergence condition is `exists && !orchestrator_command`; row highlight is yellow via a new CSS class; tooltip is a native `title` attribute with the exact string `⚠ Department exists, orchestrator missing ⚠`; `etl.py` and the data.json contract are unchanged.

Out of scope: `etl.py` and the data.json fields (both `exists` and `orchestrator_command` stay); the `WorkspaceView` and all other panels; the coordinator's derived phase; the `.dept-planned` dimming rule (keep it; the a11y point that planned-ness becomes a row-styling-only signal once the badge is gone is accepted, not addressed here). Routes through the `/project-manager-orchestrator` dispatched-worker flow.

Verification: `docker compose up --build` in `ai-infrastructure/project-manager/dashboard/` renders the roster with 7 columns (no WORKSPACE or ORCHESTRATOR), planned rows still dimmed, and no yellow rows (all departments are currently consistent). The orphan warning is verified structurally and by a temporary spot-test (flip one department's orchestrator-command presence to confirm the row turns yellow and the tooltip reads `⚠ Department exists, orchestrator missing ⚠`, then revert).

## Activity log

- 2026-06-11: Created and picked up (directed work; user instruction during the COR-T-030 close review). Moved straight to in-progress; routing through the dispatched-worker flow. Decisions resolved with the user (remove WORKSPACE + ORCHESTRATOR columns; add a yellow row highlight + native-title tooltip `⚠ Department exists, orchestrator missing ⚠` when exists && !orchestrator_command; etl.py untouched). Unlabelled per ADR-031.
- 2026-06-11: Executed via dispatched worker-agent and closed. Kickoff drafter+checker PASSed on iteration 1 (0 findings); prelaunch W1 PASS, close W2 PASS. DepartmentsPanel.jsx down to 7 columns (WORKSPACE + ORCHESTRATOR removed), orphan-warning class + native-title tooltip added; styles.css gains .dept-orphaned (yellow) with the hover selector updated to exclude it, .dept-planned unchanged; etl.py and data.json untouched. Independently verified on disk including that the worker's spot-test (a temporary rename of .claude/commands/database-orchestrator.md to force the orphan condition) was fully reverted - the command file is restored, no backup leftover, git status clean of command-file changes. Visually confirmed by the user. Committed in b715601. Follow-up: .badge-exists and .badge-missing CSS rules are now dead (badge-planned still used by WorkspaceView); folded into the COR-T-032 split-roster task scope rather than a separate cleanup.
