# Dashboard: remove dead milestone-* CSS left after the COR-T-041 epic reshape (COR-T-043)

## Target

This is AI-infrastructure work (domain 2 per ADR-005): a cleanup edit to the project-manager dashboard's stylesheet. COR-T-041 reshaped the dashboard roadmap from a `phase -> milestone` rendering to a `phase -> epic -> task` rendering, switching the live markup to the `.roadmap-epic-*` classes. The milestone-era CSS classes left behind are now dead (zero references in any dashboard `.jsx`). This task removes those dead rules from `ai-infrastructure/project-manager/dashboard/src/styles.css`. It is a pure cleanup with no intended behavior or visual change: the removed classes are unused, so the rendered dashboard must be identical before and after.

## Decisions resolved by the Orchestrator

- **Purpose is pure cleanup, no behavior or visual change.** The COR-T-041 reshape replaced the roadmap's milestone rendering with epic rendering (live `.roadmap-epic-*` classes). The milestone-era CSS classes are now dead (zero references in any dashboard `.jsx`, confirmed by the Orchestrator). Remove them from `ai-infrastructure/project-manager/dashboard/src/styles.css`. The render must be identical after the change.
- **Remove exactly these dead CSS rules.** Each was verified at 0 references across the dashboard JSX. Remove the full rule block (selector + braces + body) for each: `.roadmap-milestones`, `.roadmap-milestone-item`, `.roadmap-milestone-item:last-child`, `.roadmap-milestone-id`, `.roadmap-milestone-title`, `.roadmap-milestone-task`, `.roadmap-milestone-refs`, `.badge-milestone-done`, `.badge-milestone-in-progress`, `.badge-milestone-planned`. Also remove any section comment that introduced only these now-removed rules and is left orphaned (a comment that no longer heads any surviving rule).
- **Re-confirm zero references before removing each class.** Grep each class name across the dashboard JSX first (`ai-infrastructure/project-manager/dashboard/src/*.jsx` and `ai-infrastructure/project-manager/dashboard/src/**/*.jsx`). Remove a class only if it has zero JSX references. Rationale: the removal is safe only because the classes are unused; re-confirming on disk guards against drift since the Orchestrator's survey.
- **If any listed class is still referenced, do not remove it.** Keep it in place and report the unexpected reference under Surprises. Do not force the removal.
- **Locate the rules by selector, not by line number.** The dead rules currently sit in the roadmap CSS region (the `.roadmap-milestones` block begins near line 206, the `.badge-milestone-*` rules near line 248-250, and `.roadmap-milestone-refs` near line 270), but re-locate each by its selector text before editing; line numbers drift.
- **Do not touch the live classes.** Leave every one of these in place: `.roadmap-epic-*` (`.roadmap-epic-item`, `-header`, `-id`, `-title`, `-badges`, `-tasks`, `-toggle`), `.badge-ref-*`, `.badge-epic-rollup`, `.badge-dept`, `.roadmap-cardinality-warning`, the phase-level roadmap classes (`.roadmap-item`, `.roadmap-done`, `.roadmap-current`, `.roadmap-upcoming`, `.roadmap-legacy`, `.roadmap-list`, `.roadmap-header`, `.roadmap-phase`, `.roadmap-title`, `.roadmap-deliverables`), and every non-roadmap class. Only the ten milestone-era selectors named above are removed.
- **Verification is build-only for the executor; visual confirmation is external.** Rebuild via compose with `--no-cache` (the COR-T-040/041 lesson) and confirm the build succeeds and the container comes up. State plainly in the report that you verified the build and that the final visual confirmation that the roadmap still renders with no change is performed externally (the Orchestrator headless-renders before the user's gate, the COR-07 practice). Because the removed classes were unused, the render must be identical; you are not expected to self-certify the visual surface.

## Deliverables

- `ai-infrastructure/project-manager/dashboard/src/styles.css`: the ten dead milestone-era rule blocks listed above removed (each re-confirmed at zero JSX references), plus any orphaned section comment that headed only those rules. Nothing else in the file changed.

## Files in scope

- `ai-infrastructure/project-manager/dashboard/src/styles.css`

## Files out of scope

- All other dashboard files: `etl.py`, every `.jsx`, `index.html`, the `Dockerfile`, `docker-compose.yml`, `package.json`, `vite.config.js`. Grep the `.jsx` files to re-confirm references, but do not modify them.
- Everything outside `ai-infrastructure/project-manager/dashboard/`.
- The live classes named in the "Do not touch the live classes" decision above: `.roadmap-epic-*`, `.badge-ref-*`, `.badge-epic-rollup`, `.badge-dept`, `.roadmap-cardinality-warning`, and the phase-level roadmap classes. Keep all of them.

## References

- `ai-infrastructure/project-manager/dashboard/src/styles.css` - the only file edited. The dead milestone rules are in the roadmap CSS region (`.roadmap-milestones` near line 206 through `.badge-milestone-planned` near line 250, and `.roadmap-milestone-refs` near line 270). Re-locate each rule by selector text before editing, not by line number.
- `ai-infrastructure/project-manager/dashboard/src/panels/RoadmapPanel.jsx` - the live roadmap panel. Grep it (and the sibling panels under `ai-infrastructure/project-manager/dashboard/src/panels/`) to confirm the milestone classes are unreferenced and the epic classes are what render.
- Verify command (run verbatim; single `dashboard` service on port 8420; no `etl` or `build` service, the COR-04 failure mode): `docker compose -f ai-infrastructure/project-manager/dashboard/docker-compose.yml build --no-cache && docker compose -f ai-infrastructure/project-manager/dashboard/docker-compose.yml up -d`

## Related tasks and ADRs

- COR-T-041 - the reshape that replaced milestone rendering with epic rendering and orphaned these milestone-era classes.
- COR-T-040 - introduced the `.badge-ref-*` classes (live; keep them).
- COR-07 (OBSERVATIONS) - visual deliverables have a verification blind spot; relevant because this touches a visual surface, though the change is intended as a visual no-op.

## STATUS deltas

No task-specific STATUS deltas; universal hygiene only. Apply the universal hygiene to `ai-infrastructure/project-manager/STATUS.md` per `docs/ai-orchestration/roles/EXECUTOR-ROLE.md` (bump `last_updated`, prepend a `recent_updates` entry). Do not edit the roadmap block.

## Hard rules

- Re-confirm zero JSX references for each listed class before removing it; remove only classes with zero references. A class that is unexpectedly still referenced stays in place and is reported under Surprises.
- Remove only the ten milestone-era selectors named above (and any section comment orphaned by their removal). Do not remove, rename, or reorder any other rule.
- Edit `styles.css` only. Grep the `.jsx` files to confirm references, but make no edits to them or to any other dashboard file.
- Run the verify command verbatim as given in References. Verification is build-only for you; the visual confirmation is external (the COR-07 practice).

## Executor pointer

The executor is the dispatched `executor` (ADR-028). Universal executor conventions (writing rules, the compose-only run policy, git boundaries, the pinned six-section report shape, STATUS hygiene) live in `docs/ai-orchestration/roles/EXECUTOR-ROLE.md`; follow them rather than re-deriving them here. Write the closing report to this kickoff's directory as `COR-T-043-KICKOFF-REPORT.md` per `docs/ai-orchestration/roles/EXECUTOR-ROLE.md`, section "Report shape".
