# COR-T-050 phase 2b: retire status_deltas and the R6 kickoff rule across the dispatch toolchain

## Target

This is AI-infrastructure work (domain 2 per ADR-005): you are editing the dispatch-toolchain documents themselves (role docs, agent specs, agent definitions), not web-app code. The task is COR-T-050 phase 2b, the final dispatch of COR-T-050 and the last hop of the ADR-037 -> ADR-039 -> ADR-040 derivation line. ADR-040 (accepted, phases 1 and 2a already done) made the `STATUS.md` current-state surface fully derived and removed the hand-authored `## Current phase` / `## Next step` / `## Blocked on` body sections. The `status_deltas` kickoff field and the R6 kickoff rule existed solely to let a dispatched worker edit those now-removed sections. With no hand-authored STATUS body left, both are vestigial. This phase retires `status_deltas` entirely and tombstones R6 across the 11 operational files of the dispatch toolchain.

## Decisions resolved by the Orchestrator

- **Why this phase exists.** ADR-040 (phases 1 and 2a, done) derived the STATUS current-state surface and removed the hand-authored `## Current phase` / `## Next step` / `## Blocked on` body sections. The `status_deltas` kickoff field and the R6 kickoff rule existed only to let a dispatched worker edit those now-removed sections. With no hand-authored STATUS body remaining, both are vestigial and must be retired across the dispatch toolchain. This was folded into COR-T-050 per operator decision (2026-06-13), not via an ADR-040 amendment.
- **Retire `status_deltas` entirely.** Remove the `status_deltas` input field and every instruction to apply it, from all of: the executor and test-designer agent input schemas and definitions, the kickoff-drafter inputs and template, and the orchestrator role's dispatch flow and kickoff convention. After this phase, no kickoff carries a `status_deltas` field and no agent reads or applies one.
- **Retire R6 by TOMBSTONE, not by renumbering.** The kickoff rules are R1-R8. Do NOT renumber R7 or R8 to fill the gap; renumbering would invalidate every R7/R8 reference across the repo. Where R6 is defined or enforced, replace its content with a short tombstone note stating that R6 is retired by ADR-040 / COR-T-050 (the STATUS body is derived, so there is no status_deltas section to require), and keep the R1-R5 and R7-R8 numbers exactly as they are. Every surviving reference to R7 and R8 must remain valid and unchanged.
- **Executors and test-designers never touch STATUS now.** In `EXECUTOR-ROLE.md` and `TEST-DESIGNER-ROLE.md`, update the "Wrap-up STATUS deltas" sections and the "Not in scope" lines: remove the status_deltas apply behavior, and state that the worker never reads or edits any STATUS file (current-state is derived on the dashboard per ADR-040; activity history is git-derived per ADR-039). Remove the corresponding "STATUS-once" rule from `EXECUTOR-AGENT-SPEC.md` and `TEST-DESIGNER-AGENT-SPEC.md`. Leave all ADR-039 activity-surface wording intact wherever it appears: the git-derived `last_updated` / `recent_updates` statements stay.
- **Orchestrator role doc edits (locate exact wording before editing).** In `ORCHESTRATOR-ROLE.md`: (a) the kickoff drafting convention's R6 bullet ("Name task-specific STATUS deltas (rule R6)...") becomes the R6 tombstone note; (b) the drafter+checker dispatch-loop field list and the Dispatched-worker-flow field list that pass `status_deltas` drop that field; (c) the Pending-ADR resolution playbook step that says to "apply any task-specific STATUS deltas to the hand-authored intent sections (Current phase, Next step where present, Blocked on)" is rewritten to state that current phase / next step / blocked are derived (ADR-040) and there is no STATUS edit to apply.
- **Tombstone wording is yours to phrase, content is pinned.** Each tombstone names ADR-040 and COR-T-050 as the retirement source and states the reason (the STATUS body is derived; there is no status_deltas section to require or apply). A tombstone that names `status_deltas` or `R6` while declaring them retired is correct and expected; that is the difference between a live field/rule and a retired one. Do not invent new behavior, new fields, or new rules.
- **Edit ALL 11 operational files, edit ONLY these.** The exact inventory is in "Files in scope" below. Re-locate the exact text in each file before editing (wording may have shifted since this kickoff was drafted; verify against the file, not against this kickoff's paraphrase). Do not edit any file outside the inventory.

## Deliverables

- The 11 operational files edited so that `status_deltas` is fully retired: the field removed from the executor / test-designer / kickoff-drafter input schemas and definitions and from the orchestrator dispatch-flow field lists; the apply-behavior removed from the role docs and specs.
- R6 tombstoned in place wherever it is defined or enforced: retired with a note naming ADR-040 / COR-T-050, with R1-R5 and R7-R8 numbering preserved exactly and every surviving R7/R8 reference unchanged.
- The closing six-section report (per `EXECUTOR-ROLE.md`, section "Report shape"), including the grep verification results proving: (a) no live `status_deltas` field or apply-instruction remains in the 11 files (a tombstone note that names status_deltas while declaring it retired is acceptable and expected); (b) R6 is tombstoned, with the string "R6" surviving only in retirement/tombstone notes and in the untouched R7/R8 neighbours' numbering; (c) R7 and R8 are unchanged; (d) `git diff --name-only` shows ONLY the 11 in-scope files plus the report; (e) no accepted ADR, done task, or phase-1/2a file was touched.

## Files in scope

Edit all 11; re-locate the exact text in each before editing.

Role docs:
- ./docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md
- ./docs/ai-orchestration/roles/EXECUTOR-ROLE.md
- ./docs/ai-orchestration/roles/TEST-DESIGNER-ROLE.md

Specs:
- ./.claude/agents/specs/EXECUTOR-AGENT-SPEC.md
- ./.claude/agents/specs/TEST-DESIGNER-AGENT-SPEC.md
- ./.claude/agents/specs/KICKOFF-DRAFTER-SPEC.md
- ./.claude/agents/specs/KICKOFF-CHECKER-SPEC.md

Agent definitions:
- ./.claude/agents/executor.md
- ./.claude/agents/test-designer.md
- ./.claude/agents/kickoff-drafter.md
- ./.claude/agents/kickoff-checker.md

## Files out of scope

Do NOT touch any of these:
- ./ai-infrastructure/project-manager/decisions/ADR-023-dispatch-loop-day-zero.md (accepted ADR; it references R6/status_deltas; the Orchestrator adds the R6-retirement forward-pointer coordinator-direct, separately from this dispatch).
- ./ai-infrastructure/project-manager/decisions/ADR-039-status-derived-activity-surface.md (accepted ADR; its R6 mention is accurate history and stays).
- ./ai-infrastructure/project-manager/decisions/ADR-040-status-narrative-drift-surface.md (accepted ADR; the decision record, not an edit target).
- Any file under ./ai-infrastructure/project-manager/tasks/done/ (historical records).
- ./ai-infrastructure/database/OBSERVATIONS.md (historical log).
- ./ai-infrastructure/project-manager/tasks/in-progress/COR-T-050-derive-status-narrative-body.md (the task file; the Orchestrator transitions tasks, not the executor).
- All STATUS.md files, all CLAUDE.md files, all README files, and all *-orchestrator command files (the phase-2a doctrine cascade, already done).
- ./ai-infrastructure/project-manager/dashboard/ and its etl.py (the phase-1 derivation, already done).

## References

- ./ai-infrastructure/project-manager/decisions/ADR-040-status-narrative-drift-surface.md (the governing decision; full implementation requires retiring the status_deltas/R6 mechanism, the toolchain half of the cascade).
- ./ai-infrastructure/project-manager/tasks/in-progress/COR-T-050-derive-status-narrative-body.md (read-only; the task scope, including the 2026-06-13 scope-expansion bullet folding this retirement into phase 2b).
- ./docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md (one of the edit targets; the R6 convention bullet, the two dispatch-loop field lists, and the Pending-ADR playbook step 6 are the sites to rewrite).
- ./.claude/agents/specs/KICKOFF-CHECKER-SPEC.md (one of the edit targets; Phase 5 enforces R6 and the report-schema examples cite R6).
- ./.claude/agents/specs/EXECUTOR-AGENT-SPEC.md (one of the edit targets; the `status_deltas` input row, the STATUS-once style rule, and the Phase 5 apply-step are the sites to rewrite).

## Related tasks and ADRs

- ADR-040 (./ai-infrastructure/project-manager/decisions/ADR-040-status-narrative-drift-surface.md): the governing decision; its full implementation requires retiring the status_deltas/R6 mechanism (the toolchain half of the cascade this phase completes).
- ADR-023 (./ai-infrastructure/project-manager/decisions/ADR-023-dispatch-loop-day-zero.md): defined the dispatch loop and the R1-R8 kickoff rules / W1-W3 worker rules; R6 (STATUS-deltas present) is the rule being retired here. The Orchestrator adds the forward-pointer to ADR-023 coordinator-direct; do not edit it.
- ADR-039 (./ai-infrastructure/project-manager/decisions/ADR-039-status-derived-activity-surface.md): derived the activity surface and already removed the STATUS-hygiene half of the old R6; this phase removes the remaining status_deltas half. Leave ADR-039 activity wording intact wherever it appears.
- COR-T-050 phase 2a (this task; ./ai-infrastructure/project-manager/tasks/in-progress/COR-T-050-derive-status-narrative-body.md): removed the STATUS bodies that status_deltas/R6 targeted; this phase finishes the job by retiring the now-orphaned field and rule.

## STATUS deltas

No task-specific STATUS deltas; none. This task touches no STATUS file: current-state is derived per ADR-040 and activity history is git-derived per ADR-039. (This is the final kickoff that carries a STATUS deltas section at all, since this phase retires the `status_deltas` field and the R6 rule that required it.)

## Hard rules

- **Tombstone R6; never renumber.** R1-R5 and R7-R8 keep their exact numbers. Renumbering would silently break every R7/R8 reference across the repo. After editing, R7 and R8 read exactly as before (only neighbouring R6 content changes to a retirement note).
- **Edit only the 11 files in scope.** No accepted ADR, no done task, no STATUS/CLAUDE/README/command file, no dashboard or etl.py file is touched. `git diff --name-only` at the end shows exactly the 11 in-scope files plus the report file, and nothing else.
- **Preserve all ADR-039 activity-surface wording.** The git-derived `last_updated` / `recent_updates` statements are correct and stay. Only the `status_deltas` (hand-authored STATUS body edit) behavior is removed.
- **Verify each edit site against the file, not against this kickoff.** This kickoff paraphrases the target wording; the file is authoritative. Re-locate the exact text in each file before editing (grep for `status_deltas`, `R6`, "STATUS deltas", "STATUS-once" in each file to find every site).
- **Verification grep is a deliverable, not optional.** The report carries the grep output proving status_deltas is retired (live field/apply-instruction gone, tombstone-naming permitted), R6 is tombstoned with R7/R8 intact, and only the 11 files changed.

## Executor pointer

The executor is the dispatched `executor` (ADR-028). Universal executor conventions live in `./docs/ai-orchestration/roles/EXECUTOR-ROLE.md`. Note that `EXECUTOR-ROLE.md` is itself one of the 11 files you edit this dispatch; adopt the role from its current on-disk content, then apply the pinned edit to its "Wrap-up STATUS deltas" and "Not in scope" sections as part of the deliverables. The closing report is written to `./.claude/artifacts/handoffs/COR-T-050-PHASE2B-KICKOFF-REPORT.md` per `EXECUTOR-ROLE.md`, section "Report shape".
