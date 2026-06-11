# Dashboard: split the department roster into side-by-side AI Roster and Web App Roster tables (COR-T-032)

## Target

AI-infrastructure work (ADR-005), coordinator/agent-development surface: the project-manager insight dashboard, frontend only. The task splits the single full-width Department Roster on the dashboard landing view into two side-by-side tables (AI Roster, Web App Roster) that together occupy the same screen real estate the single table holds now, drops the now-redundant DOMAIN column, center-justifies the count columns, and folds in the dead-CSS cleanup the change orphans. The artifacts in scope are three frontend files under `ai-infrastructure/project-manager/dashboard/src/`; `etl.py` and the `data.json` contract are untouched.

## Decisions resolved by the Orchestrator

- **Split into two side-by-side roster tables.** Replace the single full-width Department Roster with two tables that together span the same width the single table spans now. Left table titled "AI Roster" (ai-infrastructure departments); right table titled "Web App Roster" (web-app departments). The request was fully specified by the user.
- **Domain partition happens in `LandingView`.** The `data.json` `departments` list already carries a `domain` field per entry (`"ai-infrastructure"` or `"web-app"`). Partition in `LandingView`: `aiDepts = data.departments.filter(d => d.domain === 'ai-infrastructure')` (agent-development, test-design, docs-curation) feeds the AI Roster; `webDepts = data.departments.filter(d => d.domain === 'web-app')` (backend-api, database, mcp-server, frontend-ui, devops) feeds the Web App Roster.
- **Parameterize `DepartmentsPanel` with a `title` prop.** Replace the hardcoded `<h3>Department roster</h3>` with `<h3>{title}</h3>`. Render `DepartmentsPanel` twice from `LandingView` (`title="AI Roster"` and `title="Web App Roster"`, each with its filtered list), wrapped in one new grid container that sits in the SAME single vertical slot the current single `DepartmentsPanel` occupies (between `PulsePanel` and `RoadmapPanel`). The panel order is otherwise unchanged: `PulsePanel` -> the two-roster grid -> `RoadmapPanel` -> `ActivityPanel`.
- **Drop the DOMAIN column.** Remove the `<th>Domain</th>` header and the domain `<td>` (the `<span className={`domain-tag domain-${dept.domain.replace('-', '')}`}>` cell) from `DepartmentsPanel`. Each table is domain-specific, so the column is redundant. After removal the table has 6 columns: Department, Backlog, In progress, Blocked, Done, Total.
- **Center-justify the five count columns; keep Department left-justified.** Backlog, In progress, Blocked, Done, and Total are center-justified in BOTH the `<th>` header and the `<td>` data cell; the Department column stays left-justified (header and cells). Current state is misaligned: count cells are right-aligned (`.count { text-align: right }` at `styles.css:285`) and count headers inherit the `.dept-table th { text-align: left }` default (`styles.css:252-253`). Implementation: add `className="count"` to the five count `<th>` headers; change `.count` to `text-align: center` (keep its `font-variant-numeric: tabular-nums`); add a `.dept-table th.count { text-align: center; }` rule so the centered header overrides the `.dept-table th` left default (specificity 0,2,1 beats 0,1,1). The Department `<th>` and `<td>` carry no `.count` class and keep the left default.
- **Layout: a new two-column grid wrapper.** Add a new grid wrapper class (a descriptive name such as `.roster-row`; the exact name is your mechanical choice) with `display: grid`, `grid-template-columns: 1fr 1fr`, `gap: 1.25rem` (matching `.main-content`'s gap at `styles.css:90`), and `align-items: start` so the shorter AI roster (3 rows) does NOT stretch to the taller Web App roster's height (the COR-T-026 org-chart-whitespace lesson: tops aligned, each card sizes to its content). Add a `@media (max-width: 768px)` rule collapsing the grid to a single column (the responsive behavior the removed `.two-col` carried). The two cards span the same total width the single roster card spanned (the full `.main-content` width).
- **Preserve the orphan warning and planned dimming in BOTH tables.** The orphan-department row warning (`dept.exists && !dept.orchestrator_command` -> `dept-orphaned` row class plus the `⚠ Department exists, orchestrator missing ⚠` title) and the `dept-planned` dimming, both from COR-T-030/031, must keep working in both tables. The Department, count, and Total columns are otherwise unchanged besides the alignment above.
- **Fold in the dead-CSS cleanup.** Removing the DOMAIN column orphans `.domain-tag`, `.domain-aiinfrastructure`, `.domain-webapp` in `styles.css` (used only in the removed cell; verified) - remove those three rules. Also remove `.badge-exists` and `.badge-missing`, left dead by COR-T-031 (verified). Do NOT remove `.badge-planned`: it is still used by `WorkspaceView.jsx`. Leave `.dept-planned`, `.dept-orphaned`, and `.count-total` intact.
- **`etl.py` and the `data.json` contract are unchanged.** The `domain` field stays emitted (the frontend partition consumes it). Do not touch `etl.py`. Same pattern as COR-T-030/031: the field stays, the column goes.

## Deliverables

1. `ai-infrastructure/project-manager/dashboard/src/views/LandingView.jsx`: the single `<DepartmentsPanel departments={data.departments} />` replaced by a two-column grid wrapper holding two `DepartmentsPanel` instances (AI Roster / Web App Roster) with domain-filtered lists; the panel order otherwise unchanged (`PulsePanel` -> two-roster grid -> `RoadmapPanel` -> `ActivityPanel`).
2. `ai-infrastructure/project-manager/dashboard/src/panels/DepartmentsPanel.jsx`: a `title` prop driving the `<h3>`; the DOMAIN column (header + cell) removed; `className="count"` added to the five count `<th>` headers; the orphan-warning, `dept-planned` dimming, and count cells otherwise preserved; a 6-column table.
3. `ai-infrastructure/project-manager/dashboard/src/styles.css`: the new roster-grid rule (`grid-template-columns: 1fr 1fr`, `gap: 1.25rem`, `align-items: start`) plus its narrow-viewport single-column collapse; `.count` changed to `text-align: center` (tabular-nums kept) and a new `.dept-table th.count { text-align: center; }` rule; the five dead rules removed (`.domain-tag`, `.domain-aiinfrastructure`, `.domain-webapp`, `.badge-exists`, `.badge-missing`); `.dept-planned`, `.dept-orphaned`, `.count-total`, and `.badge-planned` left intact.

## Files in scope

- `ai-infrastructure/project-manager/dashboard/src/views/LandingView.jsx`
- `ai-infrastructure/project-manager/dashboard/src/panels/DepartmentsPanel.jsx`
- `ai-infrastructure/project-manager/dashboard/src/styles.css`

## Files out of scope

- `ai-infrastructure/project-manager/dashboard/etl.py` (do NOT touch; the `domain` field stays emitted).
- `ai-infrastructure/project-manager/dashboard/src/views/WorkspaceView.jsx` (and its `.badge-planned` use) and every other panel (`PulsePanel`, `RoadmapPanel`, `ActivityPanel`).
- The orphan-warning logic and the `.dept-planned` rule (preserve, do not restyle).
- The `data.json` contract.

## References

- `ai-infrastructure/project-manager/tasks/in-progress/COR-T-032-split-roster-ai-and-webapp.md`: the task file; the full pinned design and verification note.
- `ai-infrastructure/project-manager/dashboard/src/views/LandingView.jsx`: the view whose single-panel render becomes the two-roster grid; current panel order at lines 19-24.
- `ai-infrastructure/project-manager/dashboard/src/panels/DepartmentsPanel.jsx`: the panel to parameterize; the DOMAIN header/cell at lines 11 and 41-45, the count cells at lines 46-50, the orphan/planned row logic at lines 21-32.
- `ai-infrastructure/project-manager/dashboard/src/styles.css`: the stylesheet to edit; `.main-content` gap at line 90, the dead badge rules at lines 140-141, the `.dept-table` rules at lines 247-272, the dead domain rules at lines 276-283, the `.count` rule at line 285.

## Related tasks and ADRs

- COR-T-031: the prior change to this panel (removed the WORKSPACE/ORCHESTRATOR columns, added the orphan warning); its output is the 7-column starting state and it left `.badge-exists`/`.badge-missing` dead.
- COR-T-030: removed the dead PHASE column; established the field-stays/column-goes pattern this task reuses for DOMAIN.
- COR-T-027: removed the previous two-column (`.two-col`) Roadmap/Org-Chart layout; this task re-introduces a two-column grid for the rosters.
- COR-T-026: fixed the org-chart card stretching to a taller sibling's height with `align-self: start`; the same lesson motivates `align-items: start` here.
- COR-T-014: built the dashboard and the roster.

## STATUS deltas

Universal hygiene only (bump `last_updated`, prepend a `recent_updates` entry in `ai-infrastructure/project-manager/STATUS.md` noting the roster was split into side-by-side AI Roster / Web App Roster tables, the DOMAIN column dropped, the count columns center-justified, and the dead domain/badge CSS removed). No phase, roadmap, or "Next step" change; no data.json contract change.

## Hard rules

- Do not touch `etl.py` or the `data.json` contract; the `domain` field stays emitted and is consumed by the `LandingView` partition.
- Do not remove `.badge-planned` (still used by `WorkspaceView.jsx`). Remove only the five rules named in the dead-CSS decision.
- Preserve the orphan-warning logic and the `.dept-planned` dimming unchanged in BOTH tables; do not restyle them.
- The `.dept-table th.count` rule must out-specify the `.dept-table th` left default so the count headers center; verify the centering renders, do not rely on declaration order alone.
- Verification (compose-only, per ADR-003): rebuild through the dashboard compose pipeline (`docker compose up -d --build` in `ai-infrastructure/project-manager/dashboard/`). Confirm: two side-by-side roster cards titled "AI Roster" (3 departments) and "Web App Roster" (5 departments) spanning the same width the single roster did; no DOMAIN column in either; each table has 6 columns; the Department column is left-justified (header and cells) and the Backlog/In progress/Blocked/Done/Total columns are center-justified in both header and cells; the planned-row dimming and orphan-warning render in both tables; the two cards are top-aligned with no large stretch whitespace under the shorter one; on a narrow viewport (max-width 768px) they collapse to a single stacked column. Confirm via grep over `src/` that no `.domain-tag`, `.domain-aiinfrastructure`, `.domain-webapp`, `.badge-exists`, or `.badge-missing` references remain, and that `.badge-planned` is retained. The user performs the final visual confirmation; confirm the structural and grep checks in your report. There is one acceptance gate: the deliverables above pass these checks.

## Worker pointer

You are the dispatched `worker-agent` (ADR-028). Universal worker conventions (run policy, git boundaries, file-edit hygiene, the six-section report shape, STATUS hygiene) live in `docs/ai-orchestration/roles/WORKER-ROLE.md`; reference it rather than re-deriving those rules. Write the closing report to `.claude/artifacts/handoffs/COR-T-032-KICKOFF-REPORT.md` per WORKER-ROLE.md, section "Report shape" (dual-channel: print the six sections to chat and write the same content to that file).
