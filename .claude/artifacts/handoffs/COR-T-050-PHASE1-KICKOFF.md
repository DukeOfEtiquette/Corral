# COR-T-050 phase 1 - derive the blocked set and render it on the dashboard

## Target

This is AI-infrastructure work (domain 2 per `ai-infrastructure/project-manager/decisions/ADR-005-two-domains-ai-first.md`): you change the dashboard's ETL and React views, which are the AI-infrastructure tooling that surfaces project state. The task is COR-T-050, and this kickoff is **phase 1 of 2 only**. Phase 1 derives the currently-blocked task set in `etl.py`, adds it to the `data.json` contract, and renders it on the dashboard (landing view plus per-workspace view). Phase 2 (a separate later dispatch, NOT this kickoff) removes the hand-authored `STATUS.md` narrative bodies and runs the doctrine cascade across role docs, commands, specs, and templates. ADR-040 decision 7 sequences this deliberately: the derived blocked surface lands and is render-verified FIRST so there is never a window where a section is neither authored nor derived. Do not do any phase-2 work in this dispatch.

## Decisions resolved by the Orchestrator

- **Phase 1 delivers the dashboard derivation only (and nothing else).** ADR-040 sequences COR-T-050: the derived blocked surface lands and is render-verified on the dashboard FIRST (this kickoff), and only then (phase 2, a separate later dispatch) are the hand-authored `STATUS.md` narrative bodies removed and the doctrine cascade run. Do NOT touch any `STATUS.md` file, any role doc, any command, any spec, any template, or any `CLAUDE.md`/README in this phase; all of those are phase 2. The "Files out of scope" section below enumerates them.

- **The blocked-set derivation in `etl.py`.** Derive the set of currently-blocked tasks across every workspace task tree. A task is blocked iff it lives in a `tasks/blocked/` directory; the directory is authoritative for status, exactly as the existing `collect_tasks` function (around line 577) already sets `status` from `status_dir` (the directory-is-authoritative comment is at line 599). The workspace-slug -> tasks mapping you need is `per_workspace_tasks`, built by `collect_all_tasks` (consumed around line 979). For each blocked task produce an entry with exactly these fields: `workspace` (the slug), `id`, `title`, and `reason`. Rationale: reusing the directory-authoritative status convention keeps the new derivation consistent with how status is already determined, per ADR-040 decision 2.

- **Reason source (pinned, per ADR-040 decision 2 "each task's recorded reason").** The block reason is recorded by convention in the task's activity log: the task lifecycle appends an activity-log line capturing the reason when a task is blocked (see `ORCHESTRATOR-ROLE.md`, "Task lifecycle", the block/unblock bullet). Source `reason` from the blocked task file's most recent activity-log line: the last `- ` bullet under the `## Activity log` heading, as a plain string. Strip the leading `- ` and any leading date prefix if it is trivially separable; otherwise keep the whole line text. If the task file has no activity log or no bullet, `reason` is the empty string `""`. This is a bounded best-effort parse: do not invent a new frontmatter field and do not change the task schema. Rationale: the activity log is the existing record of block reasons (ADR-040 consequence 3 makes the task tree load-bearing for blocked reasons on these exact terms).

- **`data.json` contract additions.** Add a top-level `blocked` key to the assembled `data` dict, near the other top-level keys (`roadmap` / `departments` / `coordinator` / `workspace_details` / `recent_activity` / `agents`, assembled around line 1268): a list of `{workspace, id, title, reason}` entries for every blocked task across all workspaces, deterministically ordered (sort by `workspace` then `id`), and the empty list `[]` when nothing is blocked. ALSO add a per-workspace `blocked` list to each `workspace_details[slug]` entry: that workspace's blocked tasks (same entry shape; `[]` when none). Preserve the ADR-039 invariant that `etl.py` never writes back into the repo and never mutates any `STATUS.md`. Rationale: ADR-040 decision 3 (materialization M2) makes `data.json` the single read surface; the no-repo-write invariant is ADR-039's, kept intact.

- **Landing-view render (required, with an affirmative empty state).** The landing view must surface the global blocked set so a surveying orchestrator can read "what is blocked" (and affirmatively see "nothing is blocked") from the dashboard instead of from a `STATUS.md` body. Render it on the landing view (`ai-infrastructure/project-manager/dashboard/src/views/LandingView.jsx`), in or beside the current-state area that `PulsePanel` occupies; `PulsePanel` already renders current phase plus next step, and the blocked set is the third piece of the same current-state picture. ALWAYS render this surface. When `data.blocked` is empty, show an explicit empty state with the exact text `No blocked work`. When non-empty, list each entry showing its `id`, `title`, `workspace`, and `reason`. Follow the existing card/panel and `styles.css` conventions; a new small panel component under `ai-infrastructure/project-manager/dashboard/src/panels/`, matching the existing panel pattern, wired into `LandingView.jsx`, is the expected shape. Rationale: ADR-040 decision 4 makes the dashboard the single read surface for current state, including the blocked set.

- **Workspace-view render (required, conditional card).** In `ai-infrastructure/project-manager/dashboard/src/views/WorkspaceView.jsx` (the `WorkspaceDetailFull` component), add a "Blocked" card that renders that workspace's `detail.blocked` list, following the existing conditional-card convention used there for `recent_updates` / `observations` / `adrs` (render the card only when the list is non-empty). Each row shows `id`, `title`, and `reason`. Rationale: the per-workspace surface mirrors the per-workspace `blocked` list added to `workspace_details`, using the established conditional-card pattern.

- **Styling.** Add any needed styles to `ai-infrastructure/project-manager/dashboard/src/styles.css` following the existing class conventions (for example `card`, `muted`, the activity-list pattern). Keep it consistent with the existing visual language; no redesign. Rationale: the kickoff scopes a small additive surface, not a restyle.

- **Verification approach (pinned; respect ADR-003 compose-only and the do-not-fabricate rule).** All workspace `tasks/blocked/` trees are currently EMPTY (only `.gitkeep`), so the real current state exercises the empty path (`blocked == []`, landing shows `No blocked work`). To exercise the POPULATED path, create a TEMPORARY throwaway blocked task fixture at `ai-infrastructure/project-manager/tasks/blocked/COR-T-999-blocked-fixture.md` with minimal valid task frontmatter (id `COR-T-999`, a title, `status: blocked`) and a one-line `## Activity log` bullet stating a reason; confirm the derivation includes it; then DELETE the fixture before completing, so the tree returns to empty and no fixture is committed. Verify the data shape by reading the code path you wrote. If (and only if) a runtime is actually available to you, you may run the ETL and cite real output, but do NOT fabricate a run or invent a compose service/command name. If you cannot run it, say so explicitly and report what you verified by inspection. The live visual render at the dashboard is confirmed by the Orchestrator via compose after this dispatch closes (a user-gated visual check); you do not need to run the dashboard or a browser. Rationale: the `tasks/blocked/` trees being empty means inspection plus a throwaway fixture is the only honest way to exercise both paths without fabricating a run, consistent with ADR-003 (compose-only) and the do-not-fabricate discipline in `./CLAUDE.md`.

  Note on the fixture and the task-tree boundary: `EXECUTOR-ROLE.md` ("Do not touch `./ai-infrastructure/project-manager/tasks/`") forbids you from transitioning tracked tasks. This fixture is an explicit, kickoff-authorized exception scoped to verification only: it is a throwaway non-task file you create and then delete within this dispatch, it is never committed, and it never reaches the done/in-progress lifecycle. Creating and deleting this one fixture file is in scope; do not move, edit, or create any other file under any `tasks/` tree.

## Deliverables

- `ai-infrastructure/project-manager/dashboard/etl.py`: a blocked-set derivation across all workspace `tasks/blocked/` trees; a top-level `blocked` list and a per-workspace `workspace_details[slug]["blocked"]` list added to `data.json`, each entry `{workspace, id, title, reason}`, deterministically ordered (sort by `workspace` then `id`), `[]` when empty; the ETL-never-writes-`STATUS.md` invariant preserved.
- A landing-view blocked surface: a new panel component under `ai-infrastructure/project-manager/dashboard/src/panels/`, wired into `ai-infrastructure/project-manager/dashboard/src/views/LandingView.jsx`, that always renders, with the `No blocked work` empty state and a per-entry list (`id`, `title`, `workspace`, `reason`) when populated.
- A workspace-view "Blocked" conditional card in `ai-infrastructure/project-manager/dashboard/src/views/WorkspaceView.jsx` (`WorkspaceDetailFull`) rendering `detail.blocked` (each row: `id`, `title`, `reason`), shown only when the list is non-empty.
- Any needed `ai-infrastructure/project-manager/dashboard/src/styles.css` additions following existing conventions.
- The pinned six-section closing report, stating exactly what was verified by inspection versus actually run (no fabricated runs).

## Files in scope

- `ai-infrastructure/project-manager/dashboard/etl.py`
- `ai-infrastructure/project-manager/dashboard/src/views/LandingView.jsx`
- `ai-infrastructure/project-manager/dashboard/src/views/WorkspaceView.jsx`
- `ai-infrastructure/project-manager/dashboard/src/panels/PulsePanel.jsx` (read for the panel pattern; edit only if wiring the new panel beside it requires it)
- `ai-infrastructure/project-manager/dashboard/src/styles.css`
- A new panel component file under `ai-infrastructure/project-manager/dashboard/src/panels/` for the blocked surface (you choose the filename, matching the existing panel naming pattern)
- `ai-infrastructure/project-manager/tasks/blocked/COR-T-999-blocked-fixture.md` (temporary verification fixture only; create then DELETE before completing; never commit)

## Files out of scope

- Every `ai-infrastructure/*/STATUS.md` (phase 2 removes the narrative bodies; untouched here)
- `docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md`, `docs/ai-orchestration/roles/EXECUTOR-ROLE.md`, `docs/ai-orchestration/roles/TEST-DESIGNER-ROLE.md` (phase 2)
- `.claude/commands/*-orchestrator.md` and the department command template (phase 2)
- `.claude/agents/specs/*.md` (the `status_deltas` / R6 retirement is phase 2)
- Every `ai-infrastructure/*/CLAUDE.md`, every `README.md`, `docs/README.md` (phase 2)
- The `PulsePanel` current-phase / next-step rendering (must not regress: do not remove or alter it; do not alter the roadmap, departments, agents, or activity surfaces)
- Any file under any `tasks/` tree other than the single temporary fixture named in "Files in scope"

## References

- `ai-infrastructure/project-manager/decisions/ADR-040-status-narrative-drift-surface.md` - the decision this implements; decision 2 pins the blocked source, decision 3 (M2) makes `data.json` the single surface and keeps the no-repo-write invariant, decision 4 makes the dashboard the read surface for blocked, consequence 3 makes the task tree load-bearing for reasons.
- `ai-infrastructure/project-manager/tasks/in-progress/COR-T-050-derive-status-narrative-body.md` - the task file; its "Sequencing" pin (decision 7) and the phase-1/phase-2 split.
- `ai-infrastructure/project-manager/dashboard/etl.py` - `collect_tasks` (around line 577, directory-authoritative status at line 599), `collect_all_tasks` / `per_workspace_tasks` (around line 979), the `data` dict assembly (around line 1268).
- `ai-infrastructure/project-manager/dashboard/src/views/LandingView.jsx` - where the global blocked surface is wired in, beside the `PulsePanel` current-state area.
- `ai-infrastructure/project-manager/dashboard/src/views/WorkspaceView.jsx` - the `WorkspaceDetailFull` component and its conditional-card convention (`recent_updates` / `observations` / `adrs`).
- `ai-infrastructure/project-manager/dashboard/src/panels/PulsePanel.jsx` - the existing panel pattern to match for the new blocked panel.
- `ai-infrastructure/project-manager/dashboard/src/styles.css` - the existing class conventions (`card`, `muted`, the activity-list pattern) to follow.

Path-convention note: inside the `ai-infrastructure/project-manager/` workspace and for shared infra under `.claude/` and `docs/`, references use bare repo-root-relative paths (no `./` prefix), per `ai-infrastructure/project-manager/CLAUDE.md` ("Path conventions"). The dashboard files above follow that convention. The two global-rules files referenced by absolute convention (`./CLAUDE.md`, the role docs) are repo-root-relative.

## Related tasks and ADRs

- ADR-040 - the decision this implements; phase 1 is its blocked-surface derivation (decision 2 pins the blocked source, decision 3 makes the dashboard the single read surface).
- ADR-039 / COR-T-047 - the precedent; `etl.py` derives but never writes `STATUS.md`. Preserve that invariant.
- ADR-003 - docker compose is the only supported run path; constrains how verification can run.
- COR-T-037 / COR-T-040 - prior dashboard panel and derivation tasks; the established panel/ETL pattern to follow.

## STATUS deltas

No task-specific STATUS deltas; none. (The `STATUS.md` body is explicitly out of scope in phase 1 and is the subject of phase 2; the activity surface is git-derived per ADR-039 and is never hand-edited.)

## Hard rules

- **Do not regress `PulsePanel`.** The current-phase and next-step rendering stays exactly as it is; it is already derived and is not part of this change. Do not alter the roadmap, departments, agents, or activity surfaces.
- **`etl.py` never writes back into the repo.** Preserve the ADR-039 invariant: no `STATUS.md` mutation, no repo writes from the ETL. The only file your ETL change writes is `data.json` in the served directory, exactly as today.
- **Delete the verification fixture before completing.** `ai-infrastructure/project-manager/tasks/blocked/COR-T-999-blocked-fixture.md` is throwaway: create it to exercise the populated path, confirm the derivation, then delete it so the tree returns to empty. It must not be committed and must not appear in the final working tree.
- **Do not fabricate a run.** If no runtime is available to you, say so explicitly and report what you verified by inspection of the code path you wrote. Do not invent a compose service or command name. ADR-003 makes compose the only supported run path.
- **Deterministic ordering.** Both the top-level `blocked` list and each per-workspace `blocked` list are sorted by `workspace` then `id`; the empty case is the literal `[]`.
- **Exact empty-state text.** The landing-view empty state is the literal string `No blocked work`.

## Executor pointer

The executor is the dispatched `executor` (ADR-028). Universal executor conventions (the six-section report shape, the dual-channel write, the repo writing rules, the compose-only run policy, git boundaries) live in `docs/ai-orchestration/roles/EXECUTOR-ROLE.md`; this kickoff references them rather than re-emitting them. The closing report is written to the derived dual-channel path per `EXECUTOR-ROLE.md`, section "Report shape".
