---
schema_version: 1
id: COR-T-030
title: "Dashboard: remove the dead PHASE column from the department roster"
status: backlog
labels: []
priority: P2
created: 2026-06-11
updated: 2026-06-11
---

## Description

The department roster (`DepartmentsPanel`) has a PHASE column that renders "Phase null" for every existing department and "--" for planned ones. It is a dead field, not stale data: it reads a `phase` key from each department's STATUS.md frontmatter (`etl.py` `dept_status`, `fm.get("phase")`), but department STATUS files have never carried a `phase` frontmatter field (they use `department`, `last_updated`, `recent_updates`, and a `## Current phase` prose body section per the department template). So `fm.get("phase")` is always `None`. Verified at filing: `database` and `backend-api` both return `{'phase': None, ...}`. Broken since the dashboard was built (COR-T-014); surfaced by the user during the COR-T-029 close review.

A per-department "phase" is not a meaningful concept: phases are global to the roadmap, and per-department progress is already shown by the adjacent Backlog/In-progress/Blocked/Done/Total count columns. Remove the column and the dead plumbing.

Known affected surfaces (verified at filing time):
- `src/panels/DepartmentsPanel.jsx` - the `<th>Phase</th>` header (line ~14) and the phase `<td>` cell `{dept.status ? `Phase ${dept.status.phase}` : '--'}` (lines ~52-54). This cell has no null-guard, which is why it prints "Phase null".
- `etl.py` - `dept_status(slug)` (lines ~405-413) returns `{"phase": fm.get("phase"), "last_updated": ...}`; the `phase` key is the dead one. The per-department `workspace_details` header also carries `"phase": fm.get("phase")` (line ~509), equally dead.
- `src/views/WorkspaceView.jsx` - lines ~65-66 render `{h.phase != null && <span ...>Phase {h.phase}</span>}`. This is null-guarded, so it already hides the badge for departments; for the COORDINATOR it shows the real DERIVED phase (header phase = current_phase). This guard is also why the roster and the workspace view disagree on the same dead field.

Scoping decision to resolve at pickup: whether to (a) remove only the roster column (UI-only) and leave the always-null `status.phase`/header field emitted, or (b) also strip the dead `phase` from `dept_status` and the department `workspace_details` header in `etl.py` so the data.json contract no longer carries a dead field. Lean: (b), the fuller removal, consistent with COR-T-029's "no dead fields that invite confusion"; update the JSON-contract docstring accordingly.

Out of scope: the COORDINATOR's derived phase (the `PulsePanel` current-phase line, the `RoadmapPanel` per-phase labels, and the coordinator's `WorkspaceView` header phase badge) - all correct and driven by the derived `current_phase`; do not touch. The milestone-status drift surface logged as COR-03 is a separate concern.

Coordinator/agent-development presentational deliverable; routes through the `/project-manager-orchestrator` dispatched-worker flow when picked up.

Verification: `docker compose up --build` in `ai-infrastructure/project-manager/dashboard/` renders the department roster with no PHASE column and no "Phase null" anywhere, the count columns intact, and (if option b) the rebuilt `data.json` department/workspace entries no longer carry a `phase` key while the coordinator's derived phase still renders in its workspace view.

## Activity log

- 2026-06-11: Created in backlog. Surfaced by the user during the COR-T-029 close review (the roster showed "Phase null" for database). Verified the root cause: the column reads a department STATUS frontmatter `phase` field that has never existed in the department STATUS schema, so it is structurally always null. Coordinator/agent-development presentational deliverable; routes through the dispatched-worker flow when picked up. P2 (user-visible incorrectness, though cosmetic). Unlabelled per ADR-031.
