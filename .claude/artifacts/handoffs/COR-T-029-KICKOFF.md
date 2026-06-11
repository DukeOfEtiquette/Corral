# Dashboard: derive current_phase and next_step from milestone statuses (COR-T-029)

## Target

This is AI-infrastructure work (ADR-005, domain 2): the project-manager insight dashboard ETL pipeline under `./ai-infrastructure/project-manager/dashboard/`. The artifacts in scope are the ETL script `./ai-infrastructure/project-manager/dashboard/etl.py` and the coordinator status source `./ai-infrastructure/project-manager/STATUS.md`. Today the dashboard paints each roadmap phase done/current/upcoming from a single hand-maintained `phase` field in `STATUS.md` frontmatter, and renders the NEXT STEP panel from a hand-maintained `## Next step` prose section. Both pointers drifted (the `phase` field stayed 1 after Phase 2 work began), so the live dashboard mis-rendered. This task eliminates both hand-maintained pointers by deriving `current_phase`, `current_phase_title`, and `next_step` from the per-milestone statuses that already live in the roadmap data, and removes the now-dead fields and section from `STATUS.md`.

## Decisions resolved by the Orchestrator

These are pinned. Do not re-deliberate them; implement them.

- **Goal: eliminate the hand-maintained phase pointer.** Currently `etl.py` reads `current_phase` from `STATUS.md` frontmatter `phase` (around line 280) and `current_phase_title` from frontmatter `phase_title` (around line 281), then `derive_roadmap_status(phase_num, current_phase)` (lines 142-147) paints each phase done/current/upcoming. The milestone statuses (`done` / `in-progress` / `planned`) already live in the roadmap data; derive from them instead of from the hand-maintained `phase` field.

- **`current_phase` derivation rule (pinned).** `current_phase` is the lowest phase number that is NOT fully done. A phase counts as fully done only if it has at least one milestone AND every one of its milestones has status `done`. A phase with an empty milestones list counts as NOT fully done (so it becomes current once earlier phases complete). If every phase is fully done, `current_phase` = the maximum phase number present. If the roadmap is empty, `current_phase` = 0. For the current repo state this yields `current_phase` = 2 (Phase 0 and Phase 1 are all done; Phase 2 has P2-2/P2-3/P2-4 not done).

- **`current_phase_title` derivation (pinned).** The `title` of the roadmap entry whose `phase` equals the derived `current_phase`. If no roadmap entry has that phase number, `current_phase_title` = the empty string `""`.

- **`next_step` derivation (pinned).** Stop reading the `## Next step` body section. Instead, `next_step` = the first non-`done` milestone (in roadmap order) of the derived current phase, formatted as the plain string `"<id>: <title>"`. When that milestone has a non-empty `task`, append `" (<task>)"`. If the current phase has no non-`done` milestone (the whole project is complete), `next_step` = the empty string `""`. For the current repo state this yields `"P2-2: FastAPI endpoints with house rules"` (P2-2 has no `task`, so no suffix). Keep `next_step` a plain string so the SPA's NEXT STEP panel renders it with no React change.

- **Keep `derive_roadmap_status(phase_num, current_phase)` as-is.** It already takes `current_phase` as a parameter; only the source of `current_phase` changes. Do not edit the function body.

- **Retire `extract_next_step` if it becomes unused.** After the `next_step` change, grep `etl.py` to confirm no other caller of `extract_next_step` remains before deleting it. If some other path still calls it, leave it in place.

- **`STATUS.md` cleanup (pinned, atomic with the `etl.py` change so nothing breaks mid-flight).** Remove the now-dead `phase:` and `phase_title:` frontmatter fields, and remove the entire `## Next step` body section (its content is now derived). Keep the `## Current phase` narrative section unchanged: it is human-facing context in `STATUS.md` and is NOT consumed by the dashboard. Keep the `roadmap:` frontmatter block and every milestone exactly as-is.

- **Update the ETL JSON-contract docstring.** At the top of `etl.py` (the Sources block around lines 9-12 and the `meta:` description around line 28), state that `current_phase`, `current_phase_title`, and `next_step` are DERIVED from the roadmap milestone statuses, not read from frontmatter or the `## Next step` section. Preserve the docstring's existing structure and any "do not edit" / "Never add to or edit this block" markered sub-blocks; update only the now-inaccurate derivation description.

## Deliverables

1. **`./ai-infrastructure/project-manager/dashboard/etl.py`** edited so that:
   - `current_phase` is derived from milestone statuses per the pinned rule (lowest not-fully-done phase; empty-milestones phase is not fully done; all-done falls back to max phase; empty roadmap is 0).
   - `current_phase_title` is the `title` of the roadmap entry matching the derived `current_phase` (empty string if none).
   - `next_step` is the first non-`done` milestone of the current phase, formatted `"<id>: <title>"` with `" (<task>)"` appended when `task` is non-empty (empty string if the current phase has no non-`done` milestone).
   - `extract_next_step` is removed if and only if no other caller remains after the change.
   - the JSON-contract docstring (Sources block and `meta:` description) states that these three values are derived from milestone statuses.
2. **`./ai-infrastructure/project-manager/STATUS.md`** edited so that:
   - the `phase:` and `phase_title:` frontmatter fields are removed.
   - the `## Next step` body section is removed in full.
   - everything else is preserved: the `roadmap:` block and every milestone, the `## Current phase` narrative section, `recent_updates`, and `last_updated` (the latter is bumped per universal STATUS hygiene).

## Files in scope

- `./ai-infrastructure/project-manager/dashboard/etl.py`
- `./ai-infrastructure/project-manager/STATUS.md`

## Files out of scope

- The React SPA and all panels under `./ai-infrastructure/project-manager/dashboard/src/`, including the NEXT STEP panel component. `next_step` stays a plain string, so no React change is needed or wanted.
- Any department STATUS file (`./ai-infrastructure/<dept>/STATUS.md`). Only the coordinator STATUS feeds the dashboard `meta`.
- The `## Current phase` narrative section of `./ai-infrastructure/project-manager/STATUS.md`. Leave it as written.
- The `roadmap:` frontmatter block and any milestone entry in `STATUS.md`. The derivation consumes them read-only; do not edit them.
- `Dockerfile`, `docker-compose.yml`, `entrypoint.sh`, `requirements.txt` in the dashboard directory. No run-path change is needed.

## References

Read these in order. They are the only context you need; do not survey the repo beyond them.

- `./ai-infrastructure/project-manager/tasks/in-progress/COR-T-029-dashboard-derive-current-phase-and-next-step.md` (the task file; the root-cause description and the activity log). Read-only; do not move, edit, or create task files.
- `./ai-infrastructure/project-manager/dashboard/etl.py` (the pipeline you are editing; see `derive_roadmap_status` lines 142-147, the `meta`/`current_phase` assembly around lines 280-283 and the `meta` dict around lines 468-471, the roadmap-building loop around lines 285-316, and `extract_next_step` lines 150-164).
- `./ai-infrastructure/project-manager/STATUS.md` (the source you are editing; the `phase`/`phase_title` frontmatter fields lines 3-4, the `roadmap:` block lines 5-97, and the `## Next step` section lines 155-157).

## Related tasks and ADRs

- COR-T-014: built the dashboard and defined the `data.json` contract this task amends.
- COR-T-017: added the per-phase `milestones` array to the ETL and the data contract; this task's derivation consumes exactly that data.
- COR-T-020: made the dashboard live (`etl.py --watch` auto-rebuild); relevant because verification runs through the live compose pipeline.
- ADR-008: the dashboard reads markdown now and repoints to the app at the dogfood milestone, so the `data.json` contract is interim and amending it is low-risk.

## STATUS deltas

Beyond universal hygiene (bump `last_updated` to today's date, prepend a `recent_updates` entry), this task itself removes the `phase:` / `phase_title:` frontmatter fields and the `## Next step` section from `STATUS.md` as part of the deliverable (deliverable 2 above), so those edits land in the same STATUS edit pass.

- The `recent_updates` entry should record that the dashboard now derives `current_phase`, `current_phase_title`, and `next_step` from the roadmap milestone statuses, and that the manual `phase` / `phase_title` frontmatter fields and the `## Next step` section were removed.
- Do NOT rewrite the `## Current phase` narrative section; it was just refreshed for Phase 2.
- Do NOT re-add a `phase` / `phase_title` frontmatter field or a `## Next step` section.

## Hard rules

- The `etl.py` derivation change and the `STATUS.md` field/section removals must be consistent with each other: once `etl.py` stops reading `phase`, `phase_title`, and `## Next step`, those sources are dead and must be removed from `STATUS.md`; do not leave one half done.
- Treat the `roadmap:` block and its milestones as read-only input. The derivation reads them; it never edits them.
- Match existing indentation and style in `etl.py`; do not introduce unrelated cleanup or refactoring in the same pass (file-edit hygiene per `WORKER-ROLE.md`).

## Verification expectations

Run verification through the dashboard compose pipeline (compose-only per ADR-003; do not assume host Python). Rebuild `data.json` and confirm the derived `meta`:

- `meta.current_phase` = 2
- `meta.current_phase_title` = "API + DB core: schema, endpoints, auth, migrations" (the Phase 2 roadmap title)
- `meta.next_step` = "P2-2: FastAPI endpoints with house rules"
- the roadmap phase statuses are Phase 0 `done`, Phase 1 `done`, Phase 2 `current`, Phases 3-5 `upcoming`

Then confirm `STATUS.md` structural state:

- `STATUS.md` no longer contains a `phase:` or `phase_title:` frontmatter field.
- `STATUS.md` no longer contains a `## Next step` section.
- the `roadmap:` block and the `## Current phase` section are intact.

Report these derived `data.json` values and the `STATUS.md` structural checks in your closing report. The user performs any final visual confirmation of the live dashboard; you confirm the derived `data.json` values and the `STATUS.md` checks.

## Worker pointer

You are the dispatched `worker-agent` (ADR-028). Universal worker conventions (the run policy, git boundaries, file-edit hygiene, STATUS hygiene, the pinned report shape) live in `./docs/ai-orchestration/roles/WORKER-ROLE.md`; follow them rather than re-deriving them here. Write your closing report to the dual-channel path derived from this kickoff per `WORKER-ROLE.md`, section "Report shape".
