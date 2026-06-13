# Dashboard reshape: render the phase -> epic -> task roadmap (COR-T-041)

## Target

This is AI-infrastructure work (ADR-005, domain 2): the project-manager coordinator dashboard tooling. The coordinator `roadmap:` block in `./ai-infrastructure/project-manager/STATUS.md` has already been restructured (orchestrator-direct) from `phase -> milestone` to `phase -> epic -> task` per ADR-036. The dashboard's `etl.py` still reads the old `milestones` schema, so the live roadmap is currently degraded. This task repoints the dashboard at the new structure: the ETL consumes `roadmap[].epics[]`, derives epic and phase status from task rollups, and the React RoadmapPanel renders the phase -> epic hierarchy with expandable tasks. The artifacts in scope are the three dashboard files listed under "Files in scope". ADR-036 is the binding model; ADR-025 is the underlying epic schema. STATUS.md is the read-only schema source and is out of scope.

## Decisions resolved by the Orchestrator

- **Purpose is a repoint, not a redesign.** The STATUS `roadmap:` block is already restructured to `phase -> epic -> task`. Your job is to make the dashboard consume and render that new structure, replacing the dead `milestones` code path. The live roadmap is currently degraded until you do.

- **New STATUS schema the ETL reads (READ-ONLY; do not edit STATUS.md).** Each `roadmap[]` phase is `{phase, title, deliverables, legacy (optional bool, true only on Phase 0), epics: []}`. Each epic is `{id (e.g. "E1.2"), title, tasks: [task-id or .. range tokens], adrs: [ADR-id or .. range tokens]}`. There is NO per-milestone or per-epic `status` field anymore; status is derived. In the live STATUS.md: phase 1 has epics E1.1..E1.5; E1.2 has `tasks: [COR-T-002, COR-T-003, COR-T-004, COR-T-005, COR-T-008, COR-T-009, COR-T-010]` and `adrs: [ADR-010, ADR-011, ADR-012, ADR-013, ADR-018, ADR-025, ADR-026]`; phase 2 E2.1 has `tasks: [DB-T-001, DB-T-002]` and `adrs: [ADR-012, ADR-014, ADR-025, ADR-026]`; E2.2 has `tasks: []`; phase 0 has `legacy: true` and `epics: []`; future phases (3-8) have 2 epics each with empty `tasks: []`. Read the live `roadmap:` block in `./ai-infrastructure/project-manager/STATUS.md` for the authoritative current data; the examples here are illustrative.

- **Reuse the COR-T-040 resolution machinery.** The existing helpers in `etl.py` (`expand_range_token`, `resolve_ref_status`, `resolve_milestone_refs`, `_rollup_statuses`, `derive_effective_status`) already expand `..` range tokens and resolve task ids against `collect_all_tasks` (status = directory) and ADR ids against `collect_adrs` (status = frontmatter). Adapt these to resolve an epic's `tasks` and `adrs` lists rather than a milestone's. Keep the task/adr split: tasks are work, ADRs are governing references.

- **Epic status rollup is TASK-refs-only (ADR-036).** An epic's status derives from its resolved TASK refs only; ADRs never drive status. All tasks done -> 'done'; any task in-progress or blocked -> 'in-progress'; an epic with 0 tasks -> 'planned'; otherwise (all backlog) -> 'planned'. This mirrors the existing `derive_effective_status` task-only rule (the `task_refs = [r for r in refs if r.get("type") == "task"]` filter, etl.py ~line 459).

- **Phase status and current_phase repoint to epics.** A phase is fully done iff `legacy: true`, OR it has >=1 epic and every epic's rolled-up status is 'done'. `derive_current_phase` returns the lowest phase that is not fully done (currently reads milestones at etl.py ~line 219; repoint to epics). `derive_next_step` returns the first non-done epic of the current phase formatted as '<epic id>: <epic title>' (currently reads milestones at ~line 269; repoint to epics). `derive_roadmap_status` (done/current/upcoming from current_phase, ~line 178) is unchanged. Expected on current data: Phase 0 legacy -> done; Phase 1 all epics done -> done; Phase 2 E2.1 in-progress (DB-T-001 done + DB-T-002 backlog) and E2.2 planned (0 tasks) -> phase 2 not done -> current_phase = 2; next_step = 'E2.1: Database schema & migrations'.

- **ETL roadmap-assembly output shape (in `run_etl`, currently ~lines 476-503).** Emit per phase `{phase, title, deliverables, legacy, status (derived via derive_roadmap_status), epics: [...], warning}`. Emit per epic `{id, title, status (rolled-up), task_count, done_count, tasks: [resolved task refs], adrs: [resolved adr refs], warning}`. Each resolved ref keeps the COR-T-040 shape (label, resolved_status, type, flavor; range refs add member_count/rollup_status). Update the etl module docstring (the roadmap shape, currently ~lines 39-44) to this new structure.

- **Density: epic rollup, expandable (the user's binding choice).** RoadmapPanel renders `phase -> epic`. Each epic header shows: epic id + title, a single ROLLUP badge (count + rolled-up status color), and its governing ADR badges (always shown, informational). Clicking an epic expands its individual TASK badges (colored by task status); collapsed by default. Reuse the COR-T-040 badge components and CSS (`SingleBadge`, `refBadgeClass`, `.badge-ref-*`). Model the epic rollup badge on the existing `RangeBadge` (a single status-colored badge): text = "<n> done" when all tasks done, "<done>/<task_count>" when partially done, "planned" when 0 tasks; colored by the epic's rolled-up status (done -> green, in-progress -> blue, blocked -> red, planned -> grey). Use React state (for example a Set of expanded epic ids) for the expand/collapse toggle.

- **Phase 0 legacy rendering.** Render the legacy phase dimmed/closed as a done bootstrap phase with no epics and no expand affordance (it carries `legacy: true` and `epics: []`). Exempt it from the cardinality check.

- **Future/forming epics (0 tasks).** The rollup badge reads 'planned' (grey); ADR badges still render; expanding reveals no tasks. This is not a warning.

- **Cardinality consistency check (ADR-036).** Flag (a) an epic with exactly 1 task (the "should be a standalone task" smell) and (b) a non-legacy phase with fewer than 2 epics, by emitting a `warning` field in the ETL output and rendering a subtle warning indicator (reuse the loud/dashed `.badge-ref-unresolved` treatment idiom, or a small warning glyph plus a native title tooltip). A 0-task epic is forming, NOT flagged. This check is DORMANT on current data (no 1-task epics; every non-legacy phase has >=2 epics): implement it, spot-test it by temporarily inducing a violation, confirm it renders, then revert so STATUS.md is untouched. This follows the COR-T-031 dormant-warning precedent (`./ai-infrastructure/project-manager/tasks/done/COR-T-031-roster-trim-columns-orphan-warning.md`).

- **Unresolvable refs.** Keep the COR-T-040 `unresolved` handling for any task/ADR id that resolves to no record (the loud guard badge).

- **STATUS.md is out of scope and READ-ONLY.** It is the schema source the ETL reads; you perform NO STATUS edits, including `recent_updates`. The orchestrator applies STATUS hygiene for this task. Your "Files touched" must NOT include STATUS.md.

- **Verification.** Rebuild via compose (a `--no-cache` build is required for the JS/CSS build stage to pick up changes; the COR-T-040 lesson) and confirm `data.json` reflects: Phase 0 legacy done; Phase 1 done (all 5 epics done); Phase 2 current with E2.1 in-progress + E2.2 planned; current_phase=2; next_step 'E2.1: ...'; future phases planned; no cardinality warnings on current data. Final visual confirmation (expandable epics, rollup badges, ADR badges, legacy phase, divider/layout) is the USER's gate; state that plainly in your report.

## Deliverables

- `ai-infrastructure/project-manager/dashboard/etl.py`: read `roadmap[].epics[]`; resolve epic `tasks` and `adrs` (reusing the range-expansion/resolution helpers); roll up epic status from tasks and phase status from epics; repoint `derive_current_phase` and `derive_next_step`; handle `legacy`; emit the new per-phase/per-epic output including counts and the cardinality `warning`; update the module docstring.
- `ai-infrastructure/project-manager/dashboard/src/panels/RoadmapPanel.jsx`: render phase -> epic (rollup badge + ADR badges + expand toggle) -> expandable task badges; legacy phase dimmed; warning indicator. Reuse the COR-T-040 badge components.
- `ai-infrastructure/project-manager/dashboard/src/styles.css`: epic-level classes (epic header, rollup badge if distinct, expand affordance), legacy-phase dimming, cardinality warning indicator. Reuse existing `.badge-ref-*` values.

## Files in scope

- `ai-infrastructure/project-manager/dashboard/etl.py`
- `ai-infrastructure/project-manager/dashboard/src/panels/RoadmapPanel.jsx`
- `ai-infrastructure/project-manager/dashboard/src/styles.css`

## Files out of scope

- `ai-infrastructure/project-manager/STATUS.md` (READ-ONLY schema source, already restructured; never edit, including `recent_updates`). It is the ETL's input, not a deliverable.
- `ai-infrastructure/project-manager/dashboard/src/views/LandingView.jsx` (RoadmapPanel's prop signature `{roadmap}` is unchanged, so its caller needs no edit)
- `ai-infrastructure/project-manager/dashboard/src/views/WorkspaceView.jsx` and all other panels
- Everything else under the dashboard and the repo

## References

- `ai-infrastructure/project-manager/dashboard/etl.py` - the ETL to repoint. Key functions: `derive_roadmap_status` (~178, unchanged), `derive_current_phase` (~186, reads milestones at ~219), `derive_next_step` (~248, reads milestones at ~269), `derive_effective_status` (the task-only rollup, the `type == 'task'` filter ~459), `resolve_milestone_refs` / `expand_range_token` / `resolve_ref_status` / `_rollup_statuses` (the COR-T-040 helpers), `collect_all_tasks` (~425, reads every workspace tree including database so DB-T-002 resolves as backlog), `collect_adrs` (~325), `run_etl` roadmap assembly (~476-503), the module docstring roadmap shape (~39-44). `TASK_STATUSES = backlog/in-progress/blocked/done` (~98).
- `ai-infrastructure/project-manager/dashboard/src/panels/RoadmapPanel.jsx` - the current panel and the reusable badge components: `refBadgeClass`, `SingleBadge`, `RangeBadge`, `UnresolvedBadge`, `RefBadge`. Note: badge data is passed via the `badge` prop, NOT `ref` (which is a React reserved prop); keep using `badge`.
- `ai-infrastructure/project-manager/dashboard/src/styles.css` - existing `.badge-ref-done/-in-progress/-blocked/-planned/-mixed/-unresolved` (~244+), `.roadmap-milestone-*` (~204-242), `.roadmap-item` / `.roadmap-*` phase classes (~192-202), `.roadmap-milestone-refs` flex container.
- `ai-infrastructure/project-manager/STATUS.md` - the live `roadmap:` block is the new epics schema (READ-ONLY reference; the ETL's schema source).
- ADR status vocabulary in this repo is only `accepted` and `pending`.
- `ai-infrastructure/project-manager/decisions/ADR-036-work-item-taxonomy.md` - the work-item taxonomy this renders.
- `ai-infrastructure/project-manager/decisions/ADR-025-native-epics.md` - the app's native epic/task model the taxonomy maps onto.
- `ai-infrastructure/project-manager/tasks/done/COR-T-040-dashboard-roadmap-ref-badges.md` - the predecessor task whose badge components and resolution helpers you reuse and lift to the epic layer.
- `ai-infrastructure/project-manager/tasks/done/COR-T-031-roster-trim-columns-orphan-warning.md` - the dormant-warning precedent (implement, spot-test by inducing a violation, revert).
- Exact verify command (run verbatim; the dashboard compose file defines a SINGLE service `dashboard` on port 8420; there is NO `etl` or `build` service): `docker compose -f ai-infrastructure/project-manager/dashboard/docker-compose.yml build --no-cache && docker compose -f ai-infrastructure/project-manager/dashboard/docker-compose.yml up -d`

## Related tasks and ADRs

- ADR-036 (`ai-infrastructure/project-manager/decisions/ADR-036-work-item-taxonomy.md`) - the work-item taxonomy this renders (Phase >=2 Epics >=2 Tasks; standalones float; status rolls up task -> epic -> phase; ADRs are governing references, never drive completion). The binding spec.
- ADR-025 (`ai-infrastructure/project-manager/decisions/ADR-025-native-epics.md`) - the app's native epic/task model (type=epic|task, parent_id) the taxonomy maps onto.
- COR-T-040 - the immediate predecessor: built the task/ADR ref badges, the resolution helpers, and the task-only effective-status rule this task reuses and lifts to the epic layer.
- COR-03 (OBSERVATIONS) - promoted by ADR-036; epic/phase status is now a task rollup, not hand-set.
- COR-T-031 - precedent for a dormant dashboard warning (orphan-department row): implement, spot-test by inducing a violation, revert.

## STATUS deltas

No task-specific STATUS deltas; universal hygiene only. STATUS.md is out of scope and read-only for this task (it is already restructured, and it is the ETL's schema source). You perform NO STATUS edits, including the universal `last_updated` bump and `recent_updates` append; the orchestrator applies STATUS hygiene for this task. Your "Files touched" must NOT include `./ai-infrastructure/project-manager/STATUS.md`.

## Hard rules

- **Do not edit STATUS.md.** It is the ETL's read-only schema source and is already restructured. No edits, including `recent_updates`. This overrides the usual Executor wrap-up STATUS hygiene for this task (the orchestrator applies hygiene). If STATUS.md appears in your changeset, you have violated scope.
- **Revert the cardinality spot-test.** The cardinality check is dormant on current data. To prove it works, temporarily induce a violation, confirm it renders, then revert so STATUS.md and the ETL output match the live data. The end state has zero cardinality warnings.
- **Compose verification needs `--no-cache`.** The JS/CSS build stage will not pick up your changes without it (the COR-T-040 lesson). Use the exact command in the References section.
- **Reuse, do not reinvent, the COR-T-040 badge components and resolution helpers.** Lift them to the epic layer; do not author parallel implementations.
- **Final visual confirmation is the user's gate.** You verify `data.json` content and that the build succeeds; the rendered look (expandable epics, rollup badges, ADR badges, dimmed legacy phase, layout) is confirmed by the user, not by you. State this plainly in "Build / verification status".

## Executor pointer

The executor is the dispatched `executor` (ADR-028). Universal executor conventions (the run policy, git boundaries, file-edit hygiene, the pinned six-section report shape, and the verify-before-asserting discipline) live in `./docs/ai-orchestration/roles/EXECUTOR-ROLE.md`; this kickoff carries only the per-task content. The closing report is written to `./.claude/artifacts/handoffs/COR-T-041-KICKOFF-REPORT.md` per EXECUTOR-ROLE.md, section "Report shape".
