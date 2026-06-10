# Add roadmap sub-milestones (P1-1/P1-2 granularity) to the project-manager dashboard

## Target

This is AI-infrastructure work (ADR-005), task COR-T-017. The project-manager dashboard (built under COR-T-014) renders a roadmap panel from a structured `roadmap` block in `./ai-infrastructure/project-manager/STATUS.md` via an ETL step that produces `data.json`. You are extending that pipeline end-to-end so each roadmap phase can carry a nested list of authored sub-milestones at P1-1 / P1-2 granularity: the ETL carries the new field through into the JSON contract, the RoadmapPanel renders the nested list, and the stylesheet gains the matching pill and layout classes. The artifacts in scope are the dashboard's `etl.py`, its `RoadmapPanel.jsx`, and its `styles.css`.

## Decisions resolved by the Orchestrator

- **Milestone status is authored, not derived.** Each milestone's `status` is authored in the STATUS.md roadmap block and passes through the ETL verbatim. Do NOT compute or infer milestone status from linked task state. (Resolved with the user at pickup 2026-06-10.)
- **The STATUS.md roadmap block is already authored; you consume it, you do not edit it.** The Orchestrator extended the `roadmap` block on its own coordination surface. Each phase now carries an optional `milestones:` list; each item is `{ id (e.g. "P1-1"), title, status, optional task ref }`. Verify the block is present before starting (it is your data source); read it from `./ai-infrastructure/project-manager/STATUS.md`. Do not edit the roadmap block.
- **Milestone status vocabulary is exactly `done` / `in-progress` / `planned`.** This is distinct from the phase-level status vocabulary (`done` / `current` / `upcoming`), which stays derived as it is today. Do not conflate the two vocabularies.
- **The existing per-phase `deliverables` string is kept as a phase summary line.** Render the `milestones` list nested beneath the existing `deliverables` paragraph. Do not remove or supersede `deliverables`.
- **A milestone's optional `task` ref renders as a non-linking plain-text tag.** Show it as a small plain-text tag next to the milestone title (e.g. "COR-T-014"). Do NOT hyperlink it. The dashboard's `App.jsx` routes only `#/workspace/<slug>`; ADRs are a non-anchored table and tasks have no detail page, so there is no link target. Linking was explicitly dropped after verifying the routing; it is out of scope.
- **Milestones render as an always-visible nested sub-list.** Do NOT add a collapse/expand toggle or any interactive state. This matches the static-render style of every other dashboard panel.

## Deliverables

- **ETL (`./ai-infrastructure/project-manager/dashboard/etl.py`).** In the roadmap-building loop (currently around lines 280-292), carry a `milestones` key through into each roadmap entry of the `data.json` contract. Each milestone dict carries `id`, `title`, `status` (verbatim authored pass-through), and `task` (optional; omit or set to empty string when absent). Default to an empty list when a phase has no `milestones`. Do NOT derive or compute milestone status. Update the JSON-contract docstring near the top of `etl.py` (the `roadmap:` line, around line 29) to document the new `milestones` field on each roadmap entry.
- **UI (`./ai-infrastructure/project-manager/dashboard/src/panels/RoadmapPanel.jsx`).** Under each phase's existing `roadmap-deliverables` paragraph, render a nested sub-list of that phase's milestones. Guard for phases with no milestones: render nothing extra. Each milestone row shows its `id`, its `title`, a status pill using the `done` / `in-progress` / `planned` vocabulary, and (when a `task` ref is present) a small non-linking text tag showing the ref. Reuse the existing `STATUS_LABELS` pattern for the milestone status labels.
- **CSS (`./ai-infrastructure/project-manager/dashboard/src/styles.css`).** Add milestone-specific pill/badge classes for the `done` / `in-progress` / `planned` vocabulary, plus any nested-sub-list layout styles. Follow the existing `.badge-roadmap-*` and `.roadmap-*` conventions (around lines 156-214) for the color and spacing idiom; the dark-theme variables are already defined.

## Files in scope

- `./ai-infrastructure/project-manager/dashboard/etl.py`
- `./ai-infrastructure/project-manager/dashboard/src/panels/RoadmapPanel.jsx`
- `./ai-infrastructure/project-manager/dashboard/src/styles.css`

## Files out of scope

- `./ai-infrastructure/project-manager/STATUS.md` (the roadmap block is already authored by the Orchestrator; do not edit it. The one allowed touch is universal STATUS hygiene, the `recent_updates` / `last_updated` frontmatter bump per WORKER-ROLE.md, which is a separate frontmatter area from the roadmap block.)
- `./ai-infrastructure/project-manager/dashboard/src/App.jsx` (no routing changes; linking is out of scope)
- `./ai-infrastructure/project-manager/dashboard/src/views/*` and all other panels (RoadmapPanel is the only panel touched)
- Any derivation or computed-status logic (explicitly rejected; milestone status is authored pass-through)

## References

- `./ai-infrastructure/project-manager/dashboard/etl.py` (the ETL whose roadmap loop and contract docstring change; read the roadmap loop around lines 280-292 and the docstring around lines 26-37)
- `./ai-infrastructure/project-manager/dashboard/src/panels/RoadmapPanel.jsx` (the panel to extend; reuse its existing `STATUS_LABELS` pattern and `roadmap-deliverables` structure)
- `./ai-infrastructure/project-manager/dashboard/src/styles.css` (the roadmap styles around lines 156-214 to mirror for the new milestone classes)
- `./ai-infrastructure/project-manager/STATUS.md` (the data source: the authored `roadmap.milestones` block to consume; verify it is present before starting)

## Related tasks and ADRs

- COR-T-014: built the dashboard and the structured `roadmap` block this task extends; the authoritative prior art for the ETL contract and the panel conventions.
- ADR-008: the dashboard reads markdown sources now and repoints to the app at the dogfood milestone; keep the `source: "markdown"` seam intact and do not couple milestone rendering to the app.
- ADR-027: established the project-manager dashboard as an ADR-027 Fork E follow-on.

## STATUS deltas

No task-specific STATUS deltas; universal hygiene only.

## Hard rules

- Run policy is docker compose only (ADR-003). The dashboard has its own `docker-compose.yml` in the `./ai-infrastructure/project-manager/dashboard/` directory; run the ETL through compose, not host-installed Python or Node.
- The roadmap status vocabularies are distinct: milestone statuses are `done` / `in-progress` / `planned`; phase statuses are `done` / `current` / `upcoming`. Do not introduce milestone status values outside the milestone vocabulary, and do not change phase-status handling.
- Do not hyperlink the milestone `task` tag, and do not add any interactive (collapse/expand) state to the milestone sub-list.

## Verification expectations

- Run the ETL through the dashboard's compose path and confirm `data.json`'s roadmap entries now each carry a `milestones` array: phases that have authored milestones carry their `id` / `title` / `status` (and `task` where present), and phases without milestones carry an empty list. Do NOT trust the authored block to be complete; confirm against the produced `data.json`.
- The rendered RoadmapPanel is a visual surface, and the Orchestrator performs the runtime and visual confirmation. State in your report exactly how to bring the dashboard up (the compose command and any service that must be running) and what to look for: each phase shows its milestones as an always-visible nested sub-list with correct status pills and the non-linking task tag where present, and the existing `deliverables` line is retained as the phase summary.

## Worker pointer

You are the dispatched `worker-agent` (ADR-028). Universal worker conventions (file-edit hygiene, the docker-compose run policy, staging without committing, and the pinned six-section report) live in `./docs/ai-orchestration/roles/WORKER-ROLE.md`. Write your closing report to `./.claude/artifacts/handoffs/COR-T-017-KICKOFF-REPORT.md` per WORKER-ROLE.md, section "Report shape".
