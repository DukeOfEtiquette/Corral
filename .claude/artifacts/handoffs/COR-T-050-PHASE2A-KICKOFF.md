# COR-T-050 phase 2a - reduce STATUS.md to frontmatter + pointer; cascade the STATUS description and survey doctrine

## Target

This is AI-infrastructure work (ADR-005, domain 2). The task is COR-T-050, phase 2a of 2. Phase 1 (the dashboard `## Blocked on` derivation and render-verification) is already done and committed; phase 2b (retiring the `status_deltas` kickoff field and the R6 kickoff rule across the role docs and agent specs) is a SEPARATE later dispatch and is NOT part of this kickoff. Phase 2a implements ADR-040 decisions 3 and 4: it removes the hand-authored STATUS narrative body from every `STATUS.md`, reduces each file to its frontmatter plus a one-line pointer, and cascades the STATUS description and survey doctrine through the `CLAUDE.md` / `README` / docs-index sites and the orchestrator-command files so the dashboard / `data.json` becomes the single read surface for current phase / next step / blocked.

The artifacts in scope are four `STATUS.md` files, seven description sites, and four orchestrator-command / template files (15 files total). The dashboard and `etl.py` are out of scope (phase 1, done); the three role docs and four agent specs are out of scope (phase 2b).

## Decisions resolved by the Orchestrator

- **What phase 2a delivers.** Per ADR-040 (`./ai-infrastructure/project-manager/decisions/ADR-040-status-narrative-drift-surface.md`, decisions 3 and 4), the hand-authored STATUS narrative body (`## Current phase`, `## Next step`, `## Blocked on`) is redundant with the derived dashboard surface: phase 1 made the blocked set derived, and current phase + next step were already derived to `data.json`. Phase 2a removes those body sections from every `STATUS.md`, reduces each file to its frontmatter plus a one-line pointer, and updates every doc site that DESCRIBES `STATUS.md` as holding the current-phase / next-step / blocked narrative or that tells a surveyor to READ those sections. The dashboard / `data.json` is the single read surface for current phase / next step / blocked. Rationale: ADR-040 is the binding decision this task implements.

- **STATUS.md reduction (4 files).** In each file below, DELETE the `## Current phase`, `## Next step`, and `## Blocked on` sections (heading plus body), KEEP the YAML frontmatter and the `# Status` H1, and replace the removed sections with the single pinned pointer paragraph (below). Per-file current sections:
  - `./ai-infrastructure/project-manager/STATUS.md` (has `## Current phase` and `## Blocked on`; no `## Next step`).
  - `./ai-infrastructure/database/STATUS.md` (has all three).
  - `./ai-infrastructure/backend-api/STATUS.md` (has all three).
  - `./ai-infrastructure/project-manager/templates/department/STATUS.md` (the department scaffold template; has all three; keep its `{{...}}` placeholder frontmatter intact).

- **Pointer paragraph text (pinned).** After the `# Status` H1 and its existing one-line description, the body becomes exactly this pointer (adjust "this workspace" / department name naturally per file): "Current phase, next step, and blocked work are derived from the roadmap (`epics/`/`phases/` files) and the `tasks/blocked/` trees and are shown on the project-manager dashboard and its `data.json` (ADR-040); they are no longer hand-authored here. Activity history is git-derived (ADR-039). This file now carries only its frontmatter and this pointer." Keep the existing `# Status` description line ("Single source of truth for current progress...") only if it stays accurate; if it claims STATUS is the single source of truth for progress, reword it so it does not contradict the pointer (the dashboard is now the source for current state). Rationale: a thin frontmatter-plus-pointer file is exactly what ADR-040 materialization M2 (decision 3) prescribes.

- **Description-site cascade (7 sites).** Each site currently describes `STATUS.md` as "current phase / next step / single source of truth." Reword each to describe it as a thin pointer whose current-phase / next-step / blocked content is derived on the dashboard (ADR-040), preserving each file's local phrasing and table format. Re-locate the exact text before editing; the line anchors below are from the orchestrator's survey and may have shifted. Sites:
  - `./ai-infrastructure/project-manager/CLAUDE.md` (Pointers table row for `./STATUS.md`, near line 37).
  - `./ai-infrastructure/database/CLAUDE.md` (Pointers table row, near line 47).
  - `./ai-infrastructure/backend-api/CLAUDE.md` (Pointers table row, near line 47).
  - `./ai-infrastructure/project-manager/templates/department/CLAUDE.md` (Pointers table row for `./STATUS.md`).
  - `./README.md` (repo root; pointer table row for the coordinator STATUS, near line 43).
  - `./ai-infrastructure/project-manager/README.md` (Pointers table row, near line 17).
  - `./docs/README.md` (doc index row for the coordinator STATUS, near line 18).
  Rationale: ADR-040 Consequence 2 names this description shift as part of the doctrine cascade.

- **Survey-doctrine cascade (4 orchestrator-command / template files).** Each `*-orchestrator` command tells the surveying orchestrator to read `STATUS.md` for current phase / next step and to update the hand-authored intent sections. Update so the survey reads current phase / next step / blocked from the dashboard / `data.json` (or, offline, derives them from the roadmap `epics/`/`phases/` files and the `tasks/blocked/` trees), and so the "update the hand-authored forward intent" instruction is REMOVED (there is no hand-authored intent to update). Sites:
  - `./.claude/commands/project-manager-orchestrator.md` (the Phase-2 "Load project context" STATUS line near line 16; the Phase-4 "Status: current phase and next step per STATUS.md" reporting line; the Notes line near line 62 "STATUS.md holds only hand-authored forward intent (Current phase / Blocked on); update those when intent changes").
  - `./.claude/commands/database-orchestrator.md` (the equivalent load-context line near line 18, the Phase-4 report line, and the Notes line near line 64).
  - `./.claude/commands/backend-api-orchestrator.md` (the equivalent lines near line 18, the Phase-4 report line, and near line 64).
  - `./ai-infrastructure/project-manager/templates/department/orchestrator-command.md` (the department command template; the equivalent load-context near line 18, Phase-4 report, and Notes near line 64 lines).
  Rationale: ADR-040 decision 4 redirects survey doctrine to the dashboard / `data.json`, extending the ADR-039 decision-3 redirect.

- **Leave ADR-039 wording intact.** These command files MAY also describe reading activity from git / the dashboard (ADR-039). Leave that ADR-039 activity-surface wording as written; only change the current-phase / next-step / blocked reads and the "update the intent sections" instruction. Rationale: ADR-039's activity-surface derivation is already shipped (COR-T-047) and is not what this task touches.

- **Preserve, do not regress.** Do not alter the STATUS frontmatter (`schema_version`, `department`), the `# Status` H1, or any ADR-039 activity-surface wording (git-derived `last_updated` / `recent_updates` stays as written). Do not touch the dogfood-event sense of "milestone" anywhere. Keep all four STATUS files structurally parallel (same pointer form). Rationale: phase 2a is a body-removal-plus-pointer change, not a frontmatter or activity-surface change.

## Deliverables

- The four `STATUS.md` files reduced to frontmatter + `# Status` H1 + the pinned pointer paragraph, with the three narrative sections removed.
- The seven description sites (3 `CLAUDE.md` + 1 template `CLAUDE.md` + repo `README` + pm `README` + `docs/README`) reworded to describe `STATUS.md` as a derived pointer.
- The four orchestrator-command / template files updated so the survey reads current state from the dashboard / `data.json` and no longer instructs updating hand-authored STATUS intent.
- The six-section closing report, including the grep results proving no narrative sections remain and that no phase-2b file was touched (see "Verification expectations").

## Files in scope

- `./ai-infrastructure/project-manager/STATUS.md`
- `./ai-infrastructure/database/STATUS.md`
- `./ai-infrastructure/backend-api/STATUS.md`
- `./ai-infrastructure/project-manager/templates/department/STATUS.md`
- `./ai-infrastructure/project-manager/CLAUDE.md`
- `./ai-infrastructure/database/CLAUDE.md`
- `./ai-infrastructure/backend-api/CLAUDE.md`
- `./ai-infrastructure/project-manager/templates/department/CLAUDE.md`
- `./README.md`
- `./ai-infrastructure/project-manager/README.md`
- `./docs/README.md`
- `./.claude/commands/project-manager-orchestrator.md`
- `./.claude/commands/database-orchestrator.md`
- `./.claude/commands/backend-api-orchestrator.md`
- `./ai-infrastructure/project-manager/templates/department/orchestrator-command.md`

## Files out of scope

- `./docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md` (phase 2b: `status_deltas` / R6).
- `./docs/ai-orchestration/roles/EXECUTOR-ROLE.md` (phase 2b).
- `./docs/ai-orchestration/roles/TEST-DESIGNER-ROLE.md` (phase 2b).
- `./.claude/agents/specs/EXECUTOR-AGENT-SPEC.md` (phase 2b: `status_deltas` field + STATUS-once rule).
- `./.claude/agents/specs/TEST-DESIGNER-AGENT-SPEC.md` (phase 2b).
- `./.claude/agents/specs/KICKOFF-DRAFTER-SPEC.md` (phase 2b: `status_deltas` field + template).
- `./.claude/agents/specs/KICKOFF-CHECKER-SPEC.md` (phase 2b: R6 enforcement).
- `./ai-infrastructure/project-manager/dashboard/` and `./ai-infrastructure/project-manager/dashboard/etl.py` (phase 1, done).

## References

- `./ai-infrastructure/project-manager/decisions/ADR-040-status-narrative-drift-surface.md` - the decision this task implements; decisions 3 (materialization M2: thin frontmatter-plus-pointer file; dashboard is the single surface) and 4 (survey doctrine redirects to the dashboard / `data.json`) are the authority.
- `./ai-infrastructure/project-manager/decisions/ADR-039-status-derived-activity-surface.md` - the precedent that derived the activity surface and redirected activity reads to git / the dashboard; its activity-surface wording (`last_updated` / `recent_updates`, git-derived) stays intact.
- `./ai-infrastructure/project-manager/tasks/in-progress/COR-T-050-derive-status-narrative-body.md` - the task file; confirms the phase-1 / phase-2a / phase-2b split and the sequencing constraint.
- `./ai-infrastructure/database/STATUS.md` - an in-scope file and a worked example of all three narrative sections to remove.
- `./ai-infrastructure/project-manager/STATUS.md` - an in-scope file; the coordinator STATUS (has `## Current phase` and `## Blocked on`, no `## Next step`).

## Related tasks and ADRs

- ADR-040 - the decision this implements (decisions 3 and 4: the dashboard is the single read surface; survey doctrine redirects).
- ADR-039 / COR-T-047 - the precedent that derived the activity surface and redirected activity reads to git / the dashboard; this extends the same survey-doctrine redirect to current phase / next step / blocked. Leave its activity-surface wording intact.
- COR-T-049 - the prior STATUS-narrative vocabulary sweep (same files); this supersedes that hand-authored narrative entirely by removing it.
- ADR-030 - the create-department recipe; the department template `STATUS.md` and orchestrator-command template are updated so newly stamped departments inherit the pointer form.

## STATUS deltas

This task's deliverable IS the `STATUS.md` reduction: all four `STATUS.md` files appear in "Files in scope" and will appear in "Files touched". The `## Current phase` / `## Next step` / `## Blocked on` sections are removed and replaced with the pinned derived-pointer paragraph per ADR-040. There are no incidental forward-intent edits beyond the deliverable itself; do not add, reword, or "freshen" any narrative content while removing it.

## Hard rules

- **Sequencing safety.** Phase 1 (the derived `## Blocked on` dashboard surface) is already landed and verified, so removing the narrative bodies now leaves no window where a section is neither authored nor derived. Do not re-derive or re-verify the dashboard surface; it is out of scope.
- **Re-locate before editing.** The line anchors in the description-site and survey-doctrine cascades are from the orchestrator's survey and may have shifted. Locate the exact target text in each file before editing; match indentation and table format exactly. Do not edit a row you cannot positively identify as the STATUS-description or STATUS-read row.
- **Pointer parallelism.** Keep all four `STATUS.md` files structurally parallel: same `# Status` H1, same single pointer paragraph form (adjusted only for the workspace / department name).
- **No phase-2b drift.** Do not touch the three role docs or the four agent specs listed in "Files out of scope". The `status_deltas` field and the R6 rule are phase 2b. If you find STATUS-description or survey-doctrine wording in a file NOT listed in "Files in scope", do not edit it; record it under "Follow-ups".
- **Verification expectations.** After editing, run `grep -rn '^## \(Current phase\|Next step\|Blocked on\)' ai-infrastructure` and confirm it returns nothing (no `STATUS.md` under `ai-infrastructure/`, including the template, still contains those sections). Confirm each of the four `STATUS.md` files still has valid frontmatter and the pointer paragraph. Confirm no phase-2b file was touched: `git diff --name-only` should show only the 15 in-scope files (the four `STATUS.md` files, the seven description sites, and the four command / template files) and the kickoff report pair. Include the grep output and the `git diff --name-only` output verbatim in the closing report's "Build / verification status" section.

## Executor pointer

The executor is the dispatched `executor` (ADR-028). Universal executor conventions (read-before-edit, no em dashes in files, repo-root-relative `./` paths, stage-do-not-commit, the no-edits-outside-scope rule) live in `./docs/ai-orchestration/roles/EXECUTOR-ROLE.md` and are not re-emitted here. The closing report is written to `./.claude/artifacts/handoffs/COR-T-050-PHASE2A-KICKOFF-REPORT.md` per EXECUTOR-ROLE.md, section "Report shape".
