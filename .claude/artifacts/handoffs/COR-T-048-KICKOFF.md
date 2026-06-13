# COR-T-048: add spacing between date and text in the dashboard workspace recent-updates feed

## Target

This is AI-infrastructure work (domain 2 per ADR-005): the project-manager dashboard is tooling that surfaces the AI-infrastructure task and workspace state. Task COR-T-048 is a cosmetic fix to one React view. In the workspace detail view, the "Recent updates" feed renders each entry's date immediately adjacent to its text with no gap, e.g. `2026-06-12COR-T-046: ...`. The artifact in scope is a single `<li>` in `ai-infrastructure/project-manager/dashboard/src/views/WorkspaceView.jsx`. The orchestrator has fully diagnosed the cause and pinned the exact one-line fix below; you apply it, you do not investigate alternatives.

## Decisions resolved by the Orchestrator

- **The fix is a single className addition on one `<li>`.** In `ai-infrastructure/project-manager/dashboard/src/views/WorkspaceView.jsx`, the `detail.recent_updates` list is rendered by a `.map` (the `<ol className="activity-list">` block around lines 122-127). Each row is currently a bare `<li key={i}>` wrapping `<span className="activity-date">` and `<span className="activity-text">`. Change that opening tag to `<li key={i} className="activity-item">`. The two spans then run through the existing flex+gap container rule instead of butting together. This is the ONLY change in the task.
- **Reuse the existing `.activity-item` CSS rule; do not add or edit any CSS.** The rule already exists at `ai-infrastructure/project-manager/dashboard/src/styles.css` line 386 (`display: flex; gap: 0.6rem; align-items: flex-start; font-size: 0.85rem;`). Adding the class makes WorkspaceView's rows match the spacing the landing-view activity feed already renders. Source: the landing feed's `ActivityPanel` already applies `className="activity-item"` to its `<li>` (verified at `ai-infrastructure/project-manager/dashboard/src/panels/ActivityPanel.jsx` line 17) and renders with correct spacing.
- **The fix is the missing class, NOT a global CSS margin.** Rationale: the landing `ActivityPanel` already renders correctly via `.activity-item`. The only defect is that WorkspaceView's `<li>` omits that class. Adding a margin to `.activity-date` in `styles.css` would double-space the already-correct landing feed, so a `styles.css` edit is the wrong fix and is out of scope.

## Deliverables

- `ai-infrastructure/project-manager/dashboard/src/views/WorkspaceView.jsx`: the `recent_updates` row `<li>` carries `className="activity-item"` (i.e. `<li key={i} className="activity-item">`). No other change to the file.

## Files in scope

- `ai-infrastructure/project-manager/dashboard/src/views/WorkspaceView.jsx`

## Files out of scope

- `ai-infrastructure/project-manager/dashboard/src/styles.css` (the `.activity-item` flex+gap rule already exists and is correct; do not edit it)
- `ai-infrastructure/project-manager/dashboard/src/panels/ActivityPanel.jsx` (the landing activity feed already renders correctly; do not edit it)
- `ai-infrastructure/project-manager/dashboard/src/views/LandingView.jsx` (the landing view is already correct; do not edit it)
- `ai-infrastructure/project-manager/dashboard/etl.py` and the `data.json` contract / the `{date, text}` shape (owned by COR-T-047; do not change)

## References

- `ai-infrastructure/project-manager/dashboard/src/views/WorkspaceView.jsx` (the target; the `recent_updates` `.map` is the `<ol className="activity-list">` block around lines 122-127, where the `<li key={i}>` needs the class)
- `ai-infrastructure/project-manager/dashboard/src/panels/ActivityPanel.jsx` (line 17: the correct `<li key={i} className="activity-item">` pattern to match; this is the landing feed's already-correct row)
- `ai-infrastructure/project-manager/dashboard/src/styles.css` (line 386: the existing `.activity-item` flex+gap rule being reused, unchanged)
- `ai-infrastructure/project-manager/tasks/in-progress/COR-T-048-dashboard-activity-date-text-spacing.md` (the task file: scope, the visual-deliverable note, and the COR-07 render-gate context)

## Related tasks and ADRs

- COR-T-047: surfaced this nit during its Phase A COR-07 render gate. The git-sourced recent-updates entries are short and lead with a task/ADR ID, which makes the missing gap read worse than it did with the older longer hand-curated sentences. COR-T-047 owns the activity-surface source (ETL and `data.json`), which is why that surface is out of scope here.
- COR-07 (OBSERVATIONS): this is a visual deliverable; the orchestrator runs the headless-render gate at close to confirm the rendered result.

## STATUS deltas

No task-specific STATUS deltas; none. (Per ADR-039 the activity surface is git-derived and never hand-edited; this task touches no hand-authored STATUS section.)

## Hard rules

- This task is exactly one change: add `className="activity-item"` to the one `recent_updates` row `<li>` in `WorkspaceView.jsx`. Do not refactor, restyle, or touch any other line.
- Do not edit `styles.css`, `ActivityPanel.jsx`, `LandingView.jsx`, `etl.py`, or the `data.json` contract / `{date, text}` shape. These are verified correct or owned by another task; the do-not-touch list above is exhaustive.
- Verification: confirm the dashboard builds via a docker compose build (the compose-only run policy in `ai-infrastructure/project-manager/CLAUDE.md` is authoritative; do not assume host-installed Node). In your closing report, note that the orchestrator runs the COR-07 headless-render gate at close to confirm the workspace recent-updates rows now show a gap between date and text matching the landing feed; that visual confirmation is the orchestrator's gate, not yours to self-certify.

## Executor pointer

The executor is the dispatched `executor` (ADR-028). Universal executor conventions (the writing rules and Agent Discipline in `./CLAUDE.md`, the compose-only run policy, git boundaries, and the pinned six-section report shape) live in `docs/ai-orchestration/roles/EXECUTOR-ROLE.md`; follow them there rather than expecting them re-emitted here. The closing report is written to `<kickoff_dir>/<kickoff_basename>-REPORT.md` per EXECUTOR-ROLE.md, section "Report shape".
