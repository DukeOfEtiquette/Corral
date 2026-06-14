# COR-T-052 - make the dashboard tables responsive on mobile (horizontal-scroll wrappers)

## Target

This is AI-infrastructure work (ADR-005): a presentation-only fix to the project-manager dashboard (a React + CSS surface under `ai-infrastructure/project-manager/dashboard/`). At phone widths (~390px) the dashboard's wide tables clip their right-hand columns off-screen. The task wraps each wide table in a horizontal-scroll container and adds the supporting CSS so the tables become fully reachable on narrow viewports, with the desktop appearance unchanged. The artifacts in scope are three panel/view JSX files and the shared `styles.css`.

## Decisions resolved by the Orchestrator

- **The problem (pinned diagnosis).** At ~390px the wide tables clip their right-hand columns off-screen: the AI Roster and Web App Roster tables (`DepartmentsPanel`, `.dept-table`) lose `Blocked` / `Done` / `Total`; the Agent Fleet table (`AgentsPanel`, `.agent-table`) loses `Purpose`; and the `WorkspaceView` Decision-records table (`.adrs-table`) overflows the same way. The tables are `width: 100%` with `white-space: nowrap` headers, so on a narrow viewport they squish and clip rather than scroll. The existing `@media (max-width: 768px)` block in `ai-infrastructure/project-manager/dashboard/src/styles.css` (around line 324) only restacks `.roster-row` to a single column; it does not handle table overflow.

- **Approach (pinned): horizontal-scroll wrappers, NOT a stacked-card rewrite.** Wrap each wide table in a scroll container (a `<div>` with `overflow-x: auto`, for example a `table-scroll` class) and ensure each table keeps a sensible `min-width` so that on a narrow viewport the table maintains readable column widths and the wrapper scrolls horizontally, instead of the columns squishing and clipping. This is the standard responsive-table pattern, preserves the table semantics and the desktop appearance exactly, and is low-risk. Do NOT convert the tables to a stacked or card layout, and do NOT change the columns or the data.

- **Where to apply (pinned).** The wide tables are in three files: the roster table in `ai-infrastructure/project-manager/dashboard/src/panels/DepartmentsPanel.jsx` (`.dept-table`); the Agent Fleet table in `ai-infrastructure/project-manager/dashboard/src/panels/AgentsPanel.jsx` (`.agent-table`, rendered once per `AgentGroup`); and the Decision-records table in `ai-infrastructure/project-manager/dashboard/src/views/WorkspaceView.jsx` (`.adrs-table`). Add the scroll wrapper around each `<table>` and add the supporting CSS in `ai-infrastructure/project-manager/dashboard/src/styles.css`. Per-column `min-width` rules already exist for `.agent-table` (the `nth-child` width rules around line 690); the effective table min-width (the sum of column widths) is what should drive the horizontal scroll.

- **Per-column nuance (pinned, execution-tuning within the scroll approach).** Tables of short or numeric cells (the rosters, the ADR num/status/date columns) scroll cleanly under a `min-width`. For the long-text column (the Agent Fleet `Purpose`, class `.agent-purpose`), let that column wrap within a reasonable table `min-width` rather than forcing an extreme single-line width; follow the existing column-width conventions already in `styles.css`. This is tuning inside the pinned scroll-wrapper approach, not a separate design choice.

- **Desktop must be unchanged (pinned).** At desktop widths the wrapper introduces no visible change: each table fits within its card and no scrollbar appears. The COR-T-051 row hover and warning styling (`.dept-orphaned`, `.dept-no-epic`, `.dept-planned`, and their `:hover` variants) must render identically. Confirm the desktop render is visually identical to before.

- **Verification (pinned, both viewports).** This is a visual surface, so the acceptance gate is a render check at BOTH a desktop width (~1500px) and a mobile width (~390px): on mobile, every table is fully reachable (the wrapper scrolls horizontally, no columns clipped off-screen); on desktop, the layout is visually unchanged. The Orchestrator runs this render gate at both widths after you return (the standing desktop-and-mobile visual-check convention; this issue was caught precisely because that gate was applied). In your report, state plainly what you verified by inspection (reading the rendered DOM or CSS) versus by run, and do not claim a render you did not perform. The compose-only run policy (ADR-003) governs any run-based verification.

## Deliverables

- `ai-infrastructure/project-manager/dashboard/src/panels/DepartmentsPanel.jsx`: the `.dept-table` `<table>` wrapped in a horizontal-scroll container.
- `ai-infrastructure/project-manager/dashboard/src/panels/AgentsPanel.jsx`: the `.agent-table` `<table>` (inside `AgentGroup`) wrapped in a horizontal-scroll container.
- `ai-infrastructure/project-manager/dashboard/src/views/WorkspaceView.jsx`: the `.adrs-table` `<table>` wrapped in a horizontal-scroll container.
- `ai-infrastructure/project-manager/dashboard/src/styles.css`: the scroll-container CSS plus any table `min-width` needed to drive the horizontal scroll on narrow viewports, with the desktop appearance unchanged.
- The pinned six-section closing report, stating for each table what was verified by inspection versus by run.

## Files in scope

- `ai-infrastructure/project-manager/dashboard/src/panels/DepartmentsPanel.jsx`
- `ai-infrastructure/project-manager/dashboard/src/panels/AgentsPanel.jsx`
- `ai-infrastructure/project-manager/dashboard/src/views/WorkspaceView.jsx`
- `ai-infrastructure/project-manager/dashboard/src/styles.css`

## Files out of scope

- `ai-infrastructure/project-manager/dashboard/etl.py` and the data layer (this is a presentation-only change).
- The roster, agent, or ADR data, columns, or panel structure (only wrap the existing tables; do not restructure them or change which columns render).
- The COR-T-051 warning and hover row styling semantics (`.dept-orphaned`, `.dept-no-epic`, `.dept-planned` and their `:hover` rules must render identically).
- Any `STATUS.md`, role doc, or non-dashboard file.

## References

- `ai-infrastructure/project-manager/tasks/in-progress/COR-T-052-dashboard-mobile-responsive-tables.md` - the task file: the surfaced problem, the standalone-task rationale, and the both-widths render-gate expectation.
- `ai-infrastructure/project-manager/dashboard/src/panels/DepartmentsPanel.jsx` - the `.dept-table` roster table to wrap.
- `ai-infrastructure/project-manager/dashboard/src/panels/AgentsPanel.jsx` - the `.agent-table` Agent Fleet table to wrap (rendered per `AgentGroup`).
- `ai-infrastructure/project-manager/dashboard/src/views/WorkspaceView.jsx` - the `.adrs-table` Decision-records table to wrap.
- `ai-infrastructure/project-manager/dashboard/src/styles.css` - the existing `@media (max-width: 768px)` block (around line 324), the table styles (`.dept-table` ~line 331, `.adrs-table` ~line 372, `.agent-table` ~line 681 with its `nth-child` column widths ~line 690): the CSS you extend with the scroll-container rules.

## Related tasks and ADRs

- COR-T-051 - its mobile render gate surfaced this issue; its `.dept-table` warning and hover row styling must not regress.
- COR-E-004 - the Phase-1 dashboard epic (done); this is a standalone post-Phase-1 fix, deliberately NOT linked to that epic (linking it would un-complete the epic).
- ADR-003 - the compose-only run policy; it constrains how any run-based verification is performed.

## Hard rules

- Wrap the existing tables; do not restructure them, change their columns, or convert them to a stacked or card layout (the scroll-wrapper approach is pinned above).
- Do not regress the COR-T-051 warning and hover row styling; it must render identically at desktop width.
- Keep the desktop render visually identical: no scrollbar should appear and no layout should shift at desktop widths.
- Stay within the four files in scope. Out-of-scope discoveries go under "Follow-ups" in the report, anchored to a target (a COR-T candidate tag or a triage-to-orchestrator flag).

## Executor pointer

The executor is the dispatched `executor` (ADR-028). Universal executor conventions (the repo writing rules and Agent Discipline in `./CLAUDE.md`, the compose-only run policy, git boundaries, and the pinned six-section report shape) live in `./docs/ai-orchestration/roles/EXECUTOR-ROLE.md` and are referenced, not restated here. Write the closing report to the dual-channel path derived per `EXECUTOR-ROLE.md`, section "Report shape" (`<kickoff-dir>/<KICKOFF-BASENAME>-REPORT.md`).
