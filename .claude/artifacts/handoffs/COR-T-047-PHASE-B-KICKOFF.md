# COR-T-047 Phase B: retire universal STATUS hygiene across the doctrine + dispatch machinery; strip the activity frontmatter (ADR-039)

## Target

This is AI-infrastructure work (domain 2 per `./ai-infrastructure/project-manager/decisions/ADR-005-two-domains-ai-first.md`), Phase B of task COR-T-047 (`./ai-infrastructure/project-manager/tasks/in-progress/COR-T-047-derive-status-activity-surface.md`), implementing the doctrine-cascade half of `./ai-infrastructure/project-manager/decisions/ADR-039-status-derived-activity-surface.md`. Phase A (already committed) made the dashboard ETL derive each workspace's `last_updated` + `recent_updates`/`recent_activity` from git history while keeping the `data.json` contract stable, which made the `last_updated` and `recent_updates` STATUS frontmatter fields vestigial (the dashboard now ignores them). Phase B is a doctrine + spec text + frontmatter edit pass with no code: it retires the now-obsolete "universal STATUS hygiene" obligation everywhere it lives, strips the vestigial frontmatter fields from the four STATUS files, codifies the commit-message convention, and flips observation COR-03 to its terminal state.

The governing principle of ADR-039 is "history is derived, intent is authored." The activity surface (`last_updated`, `recent_updates`) is now derived from git and is never hand-edited. A STATUS file holds only hand-authored forward intent in its body sections (`## Current phase`, `## Next step` where present, `## Blocked on`). There is no longer any universal STATUS-hygiene obligation: an executor, test-designer, or orchestrator touches a workspace STATUS file only when a kickoff's `status_deltas` names a task-specific edit to one of those hand-authored sections; otherwise STATUS is not touched at all.

## Decisions resolved by the Orchestrator

All decisions below are pinned. You implement them; you do not re-decide them. They are all sourced from ADR-039 and the parent task's Phase B section.

- **A. Retire the "universal hygiene only" sentinel; the new sentinel is "none".** Everywhere the literal `status_deltas` value `"universal hygiene only"` appears, replace it with the literal `"none"`. Everywhere the kickoff-body disclaimer phrase `No task-specific STATUS deltas; universal hygiene only.` appears, replace it with `No task-specific STATUS deltas; none.` The `status_deltas` field now means: a list of task-specific edits to the hand-authored STATUS sections, OR the literal `"none"`. Rationale: with the activity surface derived, there is no universal hygiene for the sentinel to point at; the field reduces to "named hand-authored-section edits, or none".

- **B. Role docs: rewrite the "Wrap-up STATUS hygiene" sections.** In `docs/ai-orchestration/roles/EXECUTOR-ROLE.md` (section "Wrap-up STATUS hygiene", around lines 131-140) and `docs/ai-orchestration/roles/TEST-DESIGNER-ROLE.md` (the same section): remove the two universal steps (bump `last_updated`, append `recent_updates`). Rewrite the section so that the activity surface (`last_updated`, `recent_updates`) is derived from git per ADR-039 and is never hand-edited; the executor/test-designer edits the workspace STATUS file only when the kickoff's `status_deltas` names a task-specific edit to a hand-authored section; and if `status_deltas` is `"none"`, STATUS is not touched and does not appear in "Files touched". Refer to the hand-authored sections generically as "the hand-authored STATUS sections (Current phase, Next step where present, Blocked on)"; do NOT enumerate a fixed list that assumes Next step exists everywhere, because the coordinator's Next step is ETL-derived (COR-T-029) while departments' is hand-authored. Retitle the section if apt (for example "Wrap-up STATUS deltas"). Keep the workspace-targeting guidance (the kickoff names which workspace's STATUS).
  In `docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md`, make these edits:
  - Pending-ADR playbook step 6 (around line 109): drop the "bump `last_updated` and prepend a `recent_updates` entry" instruction. State that the activity surface is git-derived (no manual STATUS edit) and the resolution edits only hand-authored intent sections if they changed. Keep the existing roadmap/next-step-derived note and the epic-linkage note.
  - The R6 convention bullet "Name task-specific STATUS deltas (rule R6)" (around line 147): rewrite it. There is no universal hygiene; R6 now concerns whether the kickoff names task-specific edits to the hand-authored STATUS sections, with the literal `"none"` when there are none (replacing "universal hygiene only").
  - The `kickoff-drafter` dispatch field description for `status_deltas` (around line 159), currently "(task-specific edits or the literal 'universal hygiene only')": change the literal to `"none"`.
  - The Dispatched-worker flow step 6 verify clause that reads "Confirm the workspace STATUS file appears in the report's 'Files touched' (the executor applies STATUS hygiene once, on COMPLETED)": reframe so STATUS-in-Files-touched is conditional. It appears only when the kickoff named a `status_delta`; for a `"none"` task STATUS is correctly absent. The completion signal is `RETURN: COMPLETED` plus the verified deliverables on disk, not STATUS-touched.
  - Sweep `ORCHESTRATOR-ROLE.md` for any other "STATUS hygiene" / "bump last_updated" / "append recent_updates" phrasing and reconcile it to the no-universal-hygiene model.

- **C. Orchestrator commands + department template: replace the universal-hygiene bullet and reword the survey step.** In `.claude/commands/project-manager-orchestrator.md`, `.claude/commands/database-orchestrator.md`, `.claude/commands/backend-api-orchestrator.md`, and `ai-infrastructure/project-manager/templates/department/orchestrator-command.md`: replace the "Update STATUS at end of session" universal-hygiene bullet (bump `last_updated`, append a `recent_updates` entry) with: STATUS.md holds only hand-authored forward intent (`Current phase` / `Next step` / `Blocked on`); update those when intent changes; the activity history (`last_updated`, `recent_updates`) is derived from git per ADR-039 and is not hand-maintained. Also reword the survey step "Recent observations: note any ...OBSERVATIONS.md entries added since the last STATUS update" so it does not depend on the removed `last_updated` (for example "added recently" / "since the last session"), and add, per ADR-039 decision 3, that recent activity is consulted via `git log -- <workspace-path>` or the dashboard, not from STATUS frontmatter.

- **D. Agent specs: retire universal hygiene and reframe the completion signal.** In `.claude/agents/specs/EXECUTOR-AGENT-SPEC.md` and `.claude/agents/specs/TEST-DESIGNER-AGENT-SPEC.md`: rewrite every reference to "apply STATUS hygiene once", "bump last_updated, append recent_updates entry", "STATUS-once on COMPLETED", "Files touched lists ...STATUS", the `status_deltas` field type "markdown list OR 'universal hygiene only'", the ambiguous-deltas table row, and the example `status_deltas: universal hygiene only` so that: the activity surface is git-derived and never written; the agent mutates the workspace STATUS file only when `status_deltas` names a hand-authored-section edit, on COMPLETED only (the "only on COMPLETED, once" rule still applies to named deltas, to avoid premature phase flips across re-dispatches); STATUS appears in "Files touched" only when a delta was applied; the completion signal is the `RETURN` line plus the deliverables, not STATUS-touched; and the field literal `"universal hygiene only"` becomes `"none"`. In `.claude/agents/specs/KICKOFF-DRAFTER-SPEC.md`: change the `status_deltas` field literal to `"none"`; remove the explanatory note that "universal hygiene (bump last_updated, append recent_updates) is handled by the executor"; and update the R6 self-audit and the body-section template to use `No task-specific STATUS deltas; none.` In `.claude/agents/specs/KICKOFF-CHECKER-SPEC.md`: the R6 check looks for a "STATUS deltas" section OR the literal `No task-specific STATUS deltas; none.` (replacing the universal-hygiene-only disclaimer), and the FAIL recommendation text is updated correspondingly.

- **E. Strip the vestigial frontmatter from all four STATUS files.** In `ai-infrastructure/project-manager/STATUS.md`, `ai-infrastructure/database/STATUS.md`, `ai-infrastructure/backend-api/STATUS.md`, and `ai-infrastructure/project-manager/templates/department/STATUS.md`: remove the `last_updated:` and `recent_updates:` frontmatter keys entirely, including all `recent_updates` list items. Leave `schema_version` (and `department` on the department and template STATUS) and the entire hand-authored body (`## Current phase`, `## Next step` where present, `## Blocked on`) untouched. Rationale: these fields are now derived from git; the dashboard ignores the frontmatter copies (verified in Phase A).

- **F. Add a "### Commit messages" subsection to the repo-root `./CLAUDE.md`.** Place it in the "## Global rules" section, immediately after "### Writing style". Content: every commit subject leads with the task or ADR ID it advances (for example `COR-T-047: ...` or `ADR-039: ...`) plus a specific one-line summary; this is owned-but-advisory because it feeds the ADR-039 git-derived activity dashboard, so a vague subject degrades the feed; enforcement (a `commit-msg` hook or a checker) is the recorded re-open path if feed quality erodes. Rationale and precedent: this mirrors the ADR-035 citation-completeness owned-but-advisory pattern (`./ai-infrastructure/project-manager/decisions/ADR-035-cited-reference-integrity-dispatched-work.md`, Consequences: "owned-but-advisory ... Re-open trigger ...").

- **G. Flip OBSERVATIONS COR-03 to its terminal state.** In `ai-infrastructure/project-manager/OBSERVATIONS.md`, edit COR-03's `- state:` line (line 40) to record that the last hand-maintained STATUS surface (`last_updated` + `recent_updates`) is now derived via ADR-039 / COR-T-047, so the drift-relocation chain COR-03 tracked terminates here. Follow the OBSERVATIONS append-only convention: edit only the state/promotion-pointer line; do not rewrite the entry body (context/pattern lines stay as written).

## Deliverables

- B: the three role docs rewritten per decision B (`EXECUTOR-ROLE.md`, `TEST-DESIGNER-ROLE.md`, `ORCHESTRATOR-ROLE.md`).
- C: the three orchestrator commands and the department template rewritten per decision C.
- D: the four agent specs rewritten per decision D.
- E: the four STATUS files with `last_updated` + `recent_updates` frontmatter stripped per decision E.
- F: the new "### Commit messages" subsection in `./CLAUDE.md` per decision F.
- G: the COR-03 state line flipped per decision G.
- The sentinel retirement (decision A) applied consistently across every file above.

## Files in scope

- `docs/ai-orchestration/roles/EXECUTOR-ROLE.md`
- `docs/ai-orchestration/roles/TEST-DESIGNER-ROLE.md`
- `docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md`
- `.claude/commands/project-manager-orchestrator.md`
- `.claude/commands/database-orchestrator.md`
- `.claude/commands/backend-api-orchestrator.md`
- `ai-infrastructure/project-manager/templates/department/orchestrator-command.md`
- `.claude/agents/specs/EXECUTOR-AGENT-SPEC.md`
- `.claude/agents/specs/TEST-DESIGNER-AGENT-SPEC.md`
- `.claude/agents/specs/KICKOFF-DRAFTER-SPEC.md`
- `.claude/agents/specs/KICKOFF-CHECKER-SPEC.md`
- `ai-infrastructure/project-manager/STATUS.md`
- `ai-infrastructure/database/STATUS.md`
- `ai-infrastructure/backend-api/STATUS.md`
- `ai-infrastructure/project-manager/templates/department/STATUS.md`
- `./CLAUDE.md`
- `ai-infrastructure/project-manager/OBSERVATIONS.md`

## Files out of scope

- `ai-infrastructure/project-manager/dashboard/etl.py` and all dashboard code/JSX. Phase A owns the ETL; the `data.json` contract is unchanged. If you notice the now-dead `coordinator_fm` parse in `etl.py`, leave it; it is a harmless trivial cleanup outside this task.
- `ai-infrastructure/project-manager/decisions/ADR-039-status-derived-activity-surface.md`. Accepted; do not edit.
- The hand-authored STATUS body sections (`## Current phase` / `## Next step` / `## Blocked on`) in any STATUS file. Only the `last_updated` + `recent_updates` frontmatter keys are removed.
- `.claude/agents/specs/WORKER-CLOSE-CHECKER-SPEC.md` and `.claude/agents/specs/WORKER-PRELAUNCH-CHECKER-SPEC.md`. The close/prelaunch checkers enforce W1/W2/W3, not STATUS hygiene; no change needed. You may read them if useful to confirm, but do not edit them.

## References

- `ai-infrastructure/project-manager/decisions/ADR-039-status-derived-activity-surface.md`: the governing decision. Decisions 1-7, especially decision 3 (survey doctrine), decision 5 (commit-message convention), and decision 6 (the doctrine cascade this task implements).
- `ai-infrastructure/project-manager/decisions/ADR-035-cited-reference-integrity-dispatched-work.md`: the owned-but-advisory convention precedent for the commit-message rule in decision F (see its Consequences "owned-but-advisory ... Re-open trigger").
- `ai-infrastructure/project-manager/OBSERVATIONS.md`: the COR-03 entry to flip in decision G (the `- state:` line).
- `ai-infrastructure/project-manager/tasks/in-progress/COR-T-047-derive-status-activity-surface.md`: the parent task; its Phase B section enumerates the same steps and the out-of-scope fences.

## Related tasks and ADRs

- ADR-039: the decision this task completes. Phase B is the doctrine cascade plus frontmatter-removal half.
- COR-T-047 Phase A (committed): the derive-ETL that made the frontmatter vestigial; this is the second dispatch under the same task.
- COR-T-029: derived the coordinator's Next step. This is why Next step is coordinator-derived but department-hand-authored, so do not assume Next step exists in every STATUS (decision B's generic-reference guidance).
- COR-T-046: the prior doctrine cascade (an analog). It fixed the "Next step rewording" stale example in ORCHESTRATOR/EXECUTOR but left TEST-DESIGNER-ROLE's copy, which this rewrite supersedes anyway.
- ADR-035: the owned-but-advisory convention precedent for the commit-message rule (decision F).

## STATUS deltas

No task-specific STATUS deltas; none.

## Hard rules

- No code edits. This is a doctrine + spec text + frontmatter pass. Do not touch `etl.py`, the dashboard JSX, or the `data.json` contract.
- Do not edit any STATUS body section (`## Current phase` / `## Next step` / `## Blocked on`). In the four STATUS files, only the `last_updated` and `recent_updates` frontmatter keys are removed; `schema_version` (and `department` where present) stay.
- Do not edit ADR-039 (accepted) or the two checker specs listed out of scope.
- In OBSERVATIONS, edit only the COR-03 `- state:` line (append-only convention); do not rewrite the entry body.
- When generically naming the hand-authored STATUS sections, write "Current phase, Next step where present, Blocked on"; do not assert that Next step exists in every workspace's STATUS.
- After the edits, verify (and report in the closing report's "Build / verification status"):
  - `grep` the in-scope role docs, the three commands, the template, and the four specs and confirm zero remaining `universal hygiene only` literals and zero remaining instructions to "bump last_updated" / "append a recent_updates entry" as a universal step. The only surviving mentions of `last_updated` / `recent_updates` should describe them as git-derived per ADR-039.
  - Confirm the four STATUS files no longer carry `last_updated` / `recent_updates` frontmatter keys but retain `schema_version` (and `department` where present) and their full body.
  - Confirm `./CLAUDE.md` has the new "### Commit messages" subsection placed after "### Writing style".
  - Confirm the OBSERVATIONS COR-03 `- state:` line is flipped.
  - Confirm via `git diff` that there is no edit to `etl.py`, the JSX, ADR-039, or any STATUS body section.
- Note in the report that the Orchestrator will run a final dashboard render at close to confirm the frontmatter strip did not affect the git-derived render; you are not asked to run it (compose run policy, ADR-003).

## Executor pointer

The executor is the dispatched `executor` (ADR-028). Universal executor conventions (the writing rules and Agent Discipline in `./CLAUDE.md`, the compose-only run policy, git boundaries, and the pinned six-section report shape) live in `docs/ai-orchestration/roles/EXECUTOR-ROLE.md` and are referenced, not re-emitted here. The closing report is written to `./.claude/artifacts/handoffs/COR-T-047-PHASE-B-KICKOFF-REPORT.md` per `EXECUTOR-ROLE.md`, section "Report shape".
