# ADR-035 implementation: kickoff citation-completeness convention + explicit step-6 deliverable-path-resolution sub-step

## Target

This is AI-infrastructure work (ADR-005). You are implementing the accepted decision in `ai-infrastructure/project-manager/decisions/ADR-035-cited-reference-integrity-dispatched-work.md` (its Decision and Consequences sections) by carrying it into two durable docs: `docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md` and `.claude/agents/specs/KICKOFF-DRAFTER-SPEC.md`. ADR-035 promotes the COR-04 / COR-05 / COR-06 observation family (dispatched executors emit unverified repository-state claims: wrong run commands, self-stale follow-ups, and fabricated cited paths baked into deliverables). The chosen enforcement is prevention-first (ADR-035 Option A): pin cited strings in the kickoff at drafting time, and make the deliverable-path-resolution check at close an explicit written step. You make zero design decisions; ADR-035 is the source of record and every choice below is already resolved.

## Decisions resolved by the Orchestrator

- **Source of record is ADR-035 (Decision + Consequences).** ADR-035 is accepted. This task only carries its decision into the durable role and spec docs. You make zero design decisions; if any wording choice feels like a design decision, it is already settled by ADR-035's text, so defer to that text.
- **What this implements.** The promotion of the COR-04/05/06 observation family. The chosen enforcement is prevention-first (ADR-035 Option A): pin cited paths/commands in the kickoff so the executor echoes a verified string, plus an explicit written close-time sub-step for deliverable-path resolution. Options B (close-checker W-rule) and C (kickoff-checker R9) were rejected/deferred by ADR-035 and are out of scope here.
- **EDIT 1 (ORCHESTRATOR-ROLE.md, section "Kickoff drafting convention").** Add a new bullet stating the citation-completeness convention: when a kickoff directs the executor to cite a repo-relative path or run a specific command, the Orchestrator carries that exact path/command in the kickoff's References / Files-in-scope (or inline in the kickoff body), so the executor echoes a verified string rather than reconstructing it from a naming convention (the COR-06 failure mode, where an executor guessed an `ADR-NNN-kebab-title` filename and shipped a broken link). State explicitly that this is an owned-but-advisory drafter convention, NOT a new kickoff-checker R-rule; a kickoff-checker R9 is ADR-035's recorded re-open path if the convention erodes. Note it is promoted from COR-04 / COR-06.
- **EDIT 2 (KICKOFF-DRAFTER-SPEC.md, section "Phase 5: Self-audit").** Add a self-audit item: every repo-relative path or command the kickoff body directs the executor to cite or run must also appear verbatim in the kickoff's References / Files-in-scope section, so the executor never reconstructs a path. Cross-reference ADR-035 by path. The "Phase 5: Self-audit" numbered list is the intended home; add it as a new numbered audit item alongside the existing R1-R8 scans.
- **EDIT 3 (ORCHESTRATOR-ROLE.md, section "Dispatched-worker flow", step 6 "Synthesize and verify against disk").** Add an explicit sub-step that the Orchestrator resolves every repo-relative path cited in the deliverable on disk before close, not merely spot-checking prose, because a fabricated path can be baked into the shipped deliverable as a link (the COR-06 failure mode). This turns the previously-emergent deliverable-path-resolution into a written step. Do NOT duplicate this into the TDD two-phase flow's step 5 (Phase 2): that step already defers to "the standard re-derivation," so step 6 is the single canonical home.
- **Wording is project-agnostic where the surrounding text is.** Both target files are generic project-manager machinery that travels with the ADR-034 plugin extraction. Match the voice and abstraction level of the surrounding text in each section; do not introduce Corral-app-specific phrasing where the neighbours are generic.
- **Path-convention style.** Inside these two root-staying shared-tree docs, follow each file's existing prefix style for the strings you add: ORCHESTRATOR-ROLE.md and KICKOFF-DRAFTER-SPEC.md reference shared-infra and ADR paths in the style their surrounding bullets already use. Match the neighbours; do not re-style existing text.

## Deliverables

- `docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md`: a new citation-completeness bullet added to the "Kickoff drafting convention" section (EDIT 1), stating the convention, marking it owned-but-advisory and NOT a kickoff-checker R-rule (with R9 named as the recorded re-open path), and noting promotion from COR-04 / COR-06.
- `docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md`: an explicit deliverable-path-resolution sub-step added to the "Dispatched-worker flow" step 6 (EDIT 3), requiring the Orchestrator to resolve every repo-relative path cited in the deliverable on disk before close.
- `.claude/agents/specs/KICKOFF-DRAFTER-SPEC.md`: a new citation-completeness self-audit item in the "Phase 5: Self-audit" numbered list (EDIT 2), cross-referencing ADR-035 by path.

## Files in scope

- `docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md` (EDIT 1 and EDIT 3)
- `.claude/agents/specs/KICKOFF-DRAFTER-SPEC.md` (EDIT 2)

## Files out of scope

- `.claude/agents/kickoff-checker.md` (no R9; ADR-035 defers it to Option C)
- `.claude/agents/specs/KICKOFF-CHECKER-SPEC.md` (no R9; ADR-035 defers it)
- `.claude/agents/worker-close-checker.md` (no W-rule; ADR-035 rejects it as redundant with step 6, Option B)
- `.claude/agents/specs/WORKER-CLOSE-CHECKER-SPEC.md` (no W-rule; ADR-035 rejects it)
- `ai-infrastructure/project-manager/decisions/ADR-023-dispatch-loop-day-zero.md` (forward-pointer already added orchestrator-direct)
- `ai-infrastructure/project-manager/decisions/ADR-028-worker-as-dispatched-subagent.md` (forward-pointer already added orchestrator-direct)
- `ai-infrastructure/project-manager/OBSERVATIONS.md` (COR-04/05/06 promotion already applied orchestrator-direct)
- The TDD two-phase flow's step 5 in ORCHESTRATOR-ROLE.md (EDIT 3 goes only into the Dispatched-worker flow step 6; do not duplicate it into the TDD step 5, which already defers to the standard re-derivation)

## References

- `ai-infrastructure/project-manager/decisions/ADR-035-cited-reference-integrity-dispatched-work.md` (source of record: its Decision and Consequences sections define all three edits; this is the authoritative text every edit must faithfully reflect)
- `docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md` (target of EDIT 1 and EDIT 3; the "Kickoff drafting convention" section and the "Dispatched-worker flow" step 6)
- `.claude/agents/specs/KICKOFF-DRAFTER-SPEC.md` (target of EDIT 2; the "Phase 5: Self-audit" section)
- `ai-infrastructure/project-manager/OBSERVATIONS.md` (COR-04, COR-05, COR-06: the promoted family providing the failure-mode context, including the `ADR-NNN-kebab-title` reconstruction described in COR-06)

## Related tasks and ADRs

- ADR-035: the source decision this task implements (Decision + Consequences).
- ADR-023: the dispatch-loop and kickoff-drafting convention / R-rule set that EDIT 1 extends.
- ADR-028: the verify-against-disk step 6 that EDIT 3 makes explicit.
- ADR-016: the worker-close-checker W-rule mechanism ADR-035 rejected (context for why no W-rule is added here).
- ADR-034: the plugin-extraction boundary; both targets are generic machinery that travels with it, which is why wording stays project-agnostic.

## STATUS deltas

No task-specific STATUS deltas; universal hygiene only.

## Hard rules

- Make exactly the three edits named (EDIT 1, EDIT 2, EDIT 3) in exactly the two in-scope files. Do not touch any out-of-scope file.
- Do not add a kickoff-checker R9 or a worker-close-checker W-rule. ADR-035 explicitly defers R9 (Option C) and rejects the W-rule (Option B); EDIT 1 must name R9 as the recorded re-open path, not introduce it.
- Do not duplicate EDIT 3 into the TDD two-phase flow's step 5. The Dispatched-worker flow step 6 is the single canonical home.
- Faithfully reflect ADR-035's Decision and Consequences text; do not extend, narrow, or reinterpret the decision.
- Match the surrounding text's voice, abstraction level, and path-prefix style in each edited section; keep wording project-agnostic where the neighbours are generic.

## Executor pointer

You are the dispatched `executor` (ADR-028). Universal executor conventions live in `docs/ai-orchestration/roles/EXECUTOR-ROLE.md`. Write your closing report to the dual-channel path derived per EXECUTOR-ROLE.md, section "Report shape".
