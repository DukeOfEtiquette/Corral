# ADR-036 vocabulary cascade: tasks/README Vocabulary section + milestone->epic doc sweep (COR-T-042)

## Target

This is AI-infrastructure work (domain 2, ADR-005). The task propagates the ADR-036 work-item taxonomy (`./ai-infrastructure/project-manager/decisions/ADR-036-work-item-taxonomy.md`) into the operating docs so fresh sessions follow it strictly. Two parts, both pure documentation edits: (1) add a "Vocabulary" section to the canonical task convention at `./ai-infrastructure/project-manager/tasks/README.md`, and (2) sweep the work-container sense of "milestone" to "epic" in exactly three named live-doc spots. ADR-036 is the content source and the authority to cite; it is read-only here.

## Decisions resolved by the Orchestrator

- **Authority and source.** ADR-036 at `./ai-infrastructure/project-manager/decisions/ADR-036-work-item-taxonomy.md` is the binding taxonomy and the authority to cite. The Vocabulary section carries the operating *how* and points back to ADR-036 for the *why*; do not re-derive ADR-036's rationale, cross-reference it.

- **Part 1 placement and source subsections.** Add a new "Vocabulary" section to `./ai-infrastructure/project-manager/tasks/README.md`. This file is the canonical work convention for the markdown era. Place the section sensibly (for example after the "Per-workspace task trees (ADR-031)" section, or near the top); use your judgement on the exact insertion point within that file. Draw the section's content from ADR-036's "Terms", "Containment and cardinality", "Epic scope (department-scoped)", "Completion and status", and "The role of ADRs" subsections. Keep it concise and operating-focused.

- **Part 1 terms to define.** Define, drawn from ADR-036: **Roadmap** (the time-ordered view), **Phase** (a delivery band grouping epics), **Epic** (a department-scoped deliverable capability composed of tasks), **Task** (the atomic unit of work), **ADR** (a decision/governance record, referenced by epics/tasks, never work).

- **Part 1 rules to state.** State these rules: strict containment (a Phase contains only Epics; an Epic only Tasks; a Task is a leaf); the `>= 2` cardinality (Phase >= 2 Epics, Epic >= 2 Tasks) as project *conventions* describing intended shape, not schema constraints; department-scoped epics (one owning department, all tasks from that tree; cross-department work is sibling epics under a shared phase); standalone epics (no phase) and standalone tasks (no epic) floating at the top level; status rolls up task -> epic -> phase; ADRs drive no completion.

- **Part 2 is exactly three single-phrase edits.** Sweep the work-container sense of "milestone" to "epic" in EXACTLY these three live-doc spots and nowhere else:
  1. `./docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md` (~line 101, the Pending-ADR-resolution-playbook step 6): the phrase "update \"Next step\" and the roadmap milestone to drop the resolved task" becomes "...and the roadmap epic to drop the resolved task."
  2. `./README.md` (~line 52): "Live phase and milestone status:" becomes "Live phase and epic status:".
  3. `./END-GOAL.md` (~line 35): "the authoritative live status with sub-milestones" becomes "the authoritative live status with epics" (drop "sub-").

- **Do NOT touch the dogfood-event sense of "milestone" anywhere.** Every other "milestone" occurrence in the docs refers to the dogfood milestone (the import event) and is correct as written. The explicit do-not-touch list is in "Files out of scope" below. These are out of scope for the milestone term; leave them exactly as authored.

- **Scope discipline.** Part 2 is exactly three single-phrase edits. Do not broaden the sweep. If you discover a fourth work-container "milestone" not in the three named spots, do not silently edit it (it may be the event sense): record it under "Follow-ups" in the closing report and leave it untouched.

## Deliverables

- `./ai-infrastructure/project-manager/tasks/README.md`: a new "Vocabulary" section per ADR-036, defining the five terms and stating the rules named in the decisions above.
- `./docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md`: one phrase edit at ~line 101 (roadmap milestone -> roadmap epic).
- `./README.md`: one phrase edit at ~line 52 (phase and milestone status -> phase and epic status).
- `./END-GOAL.md`: one phrase edit at ~line 35 (sub-milestones -> epics).

## Files in scope

- `./ai-infrastructure/project-manager/tasks/README.md`
- `./docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md`
- `./README.md`
- `./END-GOAL.md`

## Files out of scope

These hold the dogfood-EVENT sense of "milestone" (the import event) and are correct as written; do not edit them for the milestone term:

- `./README.md:61` ("5. Dogfood milestone" phase-5 title)
- `./docs/README.md:33`
- `./END-GOAL.md:25` and `./END-GOAL.md:29`
- `./.claude/commands/project-manager-orchestrator.md:59`
- `./.claude/commands/backend-api-orchestrator.md:62`
- `./.claude/commands/database-orchestrator.md:62`
- `./.claude/commands/create-department.md:104`
- `./ai-infrastructure/project-manager/tasks/README.md:3` and `:7` (the "dogfood milestone" event references in the existing prose; you are ADDING a Vocabulary section to this file, not editing those two lines)
- `./.claude/agents/specs/KICKOFF-CHECKER-SPEC.md:158`
- `./.claude/agents/specs/KICKOFF-DRAFTER-SPEC.md:282`
- `./docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md:85` (the "Seam swap ahead" dogfood-milestone sentence; your only edit to this file is at ~line 101)

Also do NOT edit:

- `./ai-infrastructure/project-manager/decisions/ADR-036-work-item-taxonomy.md` (the source; read-only)
- `./ai-infrastructure/database/tasks/done/DB-T-001-postgres-schema.md` (historical done task)
- `./ai-infrastructure/project-manager/dashboard/` (the dashboard, including the `.roadmap-milestone-*` / `.badge-milestone-*` CSS class names in its `styles.css`; that is a separate dead-CSS cleanup, out of scope here)
- `./ai-infrastructure/project-manager/STATUS.md` roadmap block (already restructured)

## References

- `./ai-infrastructure/project-manager/decisions/ADR-036-work-item-taxonomy.md` - the binding taxonomy; the Vocabulary section is drawn from its "Terms", "Containment and cardinality", "Epic scope (department-scoped)", "Completion and status", and "The role of ADRs" subsections. Cite this as the authority.
- `./ai-infrastructure/project-manager/tasks/README.md` - the file to extend (Part 1); also holds the event-sense "milestone" at lines 3 and 7, which stay untouched.
- `./docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md` - Part 2 edit at ~line 101; do NOT touch ~line 85 (dogfood-event sense).
- `./README.md` - Part 2 edit at ~line 52; do NOT touch ~line 61 (Dogfood milestone phase-5 title).
- `./END-GOAL.md` - Part 2 edit at ~line 35; do NOT touch ~lines 25 and 29 (dogfood-event sense).

## Related tasks and ADRs

- ADR-036 - the work-item taxonomy this cascade documents and propagates; the authority to cite.
- COR-T-041 - the dashboard reshape that rendered the taxonomy; this task is the doc half of the same ADR-036 restructure.
- COR-T-040 - the predecessor that introduced the task/ADR reference badges.

## STATUS deltas

No task-specific STATUS deltas; universal hygiene only. `./ai-infrastructure/project-manager/STATUS.md` is settled (the restructure is committed and its roadmap block is out of scope). Perform the universal STATUS hygiene per `./docs/ai-orchestration/roles/EXECUTOR-ROLE.md` (bump `last_updated`, prepend a `recent_updates` entry naming this task and the cascade); do not edit the roadmap block.

## Hard rules

- The "Vocabulary" section is operating-focused and concise: cross-reference ADR-036 for rationale rather than re-deriving it.
- The `>= 2` cardinality minimums are stated as project conventions describing intended shape, not as schema constraints (ADR-036 is explicit on this distinction).
- Part 2 is exactly three single-phrase edits at the three named spots. Any additional work-container "milestone" you discover goes under "Follow-ups" with a "triage to orchestrator" flag; do not edit it.
- Use Edit (not Write) for the three Part-2 phrase edits and for inserting the Vocabulary section into the existing `./ai-infrastructure/project-manager/tasks/README.md`; read before edit and match indentation exactly.

## Executor pointer

The executor is the dispatched `executor` (ADR-028). Universal executor conventions (the writing rules and Agent Discipline in `./CLAUDE.md`, file-edit hygiene, the no-out-of-scope-edits rule, and STATUS hygiene) live in `./docs/ai-orchestration/roles/EXECUTOR-ROLE.md`. The closing report is written to `./.claude/artifacts/handoffs/COR-T-042-KICKOFF-REPORT.md` per EXECUTOR-ROLE.md, section "Report shape".
