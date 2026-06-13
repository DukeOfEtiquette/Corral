---
schema_version: 1
id: COR-T-039
title: "ADR-035 implementation: kickoff citation-completeness convention + explicit step-6 deliverable-path-resolution sub-step"
status: done
labels: []
priority: P2
created: 2026-06-12
updated: 2026-06-12
epic: COR-E-001
---

## Description

Implementation cascade for ADR-035 (cited-reference integrity for dispatched work), which promoted the COR-04/05/06 observation family. ADR-035 pins the decision; this task carries it into the durable role and spec docs. This is the ADR-016 -> COR-T-035 / ADR-028 -> COR-T-015 precedent: the ADR is accepted orchestrator-direct, the doc edits route through the dispatched-worker flow because role docs and specs are deliverables.

Three edits, all in generic project-manager machinery (so they travel with the ADR-034 plugin extraction):

1. **Kickoff citation-completeness convention** in the "Kickoff drafting convention" section of `docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md`: add a bullet stating that when a kickoff directs the executor to cite a repo-relative path or run a specific command, the exact path/command is carried in the kickoff's `references` / `explicit_reads` (or inline in the kickoff body), so the executor echoes a verified string rather than reconstructing it from a naming convention. Frame it as an owned-but-advisory drafter convention, explicitly NOT a new kickoff-checker R-rule (a kickoff-checker R9 is ADR-035's recorded re-open path, not adopted now).

2. **Drafter spec edit** in `.claude/agents/specs/KICKOFF-DRAFTER-SPEC.md`: reflect the same citation-completeness convention so the `kickoff-drafter` applies it when authoring `references` / `explicit_reads`.

3. **Explicit step-6 sub-step** in `docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md` Dispatched-worker flow step 6 (and the TDD flow's step-5 echo if consistency warrants): add an explicit instruction that the orchestrator resolves every repo-relative path cited in the deliverable on disk before close, making COR-06's previously-emergent behaviour a written step.

Out of scope: adding any kickoff-checker R-rule (R9) or worker-close-checker W-rule (both recorded as deferred/rejected in ADR-035); editing the accepted ADRs' decisions (forward-pointer notes already added orchestrator-direct at ADR-035 acceptance time); the OBSERVATIONS promotion (already applied orchestrator-direct).

Source of record: `./decisions/ADR-035-cited-reference-integrity-dispatched-work.md` (Decision and Consequences) and OBSERVATIONS COR-04/05/06.

## Activity log

- 2026-06-12: Created in backlog. Filed as the ADR-035 implementation cascade at ADR-035 acceptance time (orchestrator-direct ADR; the doc edits are deliverables that route through the dispatched-worker flow). P2. Allocated ID 39 (.next-task-id -> 40). Unlabelled per ADR-031 (dept:* applied at the dogfood import, not hand-applied here).
- 2026-06-12: Picked up and moved to in-progress. All decisions pinned by ADR-035 (zero anticipated decisions for the executor); routing through the dispatched-worker flow (draft+check kickoff, prelaunch, dispatch executor, close).
- 2026-06-12: Done (commit f328786). Dispatched-worker flow ran clean: kickoff drafted+checked (PASS, 0 findings), prelaunch W1 PASS, executor COMPLETED, close W2 PASS (W3 inert). Three edits landed: ORCHESTRATOR-ROLE.md citation-completeness bullet (EDIT 1) + step-6 deliverable-path-resolution sub-step (EDIT 3), and KICKOFF-DRAFTER-SPEC.md Phase 5 self-audit item (EDIT 2). Verified against disk: all three present and faithful to ADR-035; scope clean (no checker/ADR/OBSERVATIONS files touched); no R9 or W-rule introduced; TDD step 5 untouched; no em dashes. First close verified under ADR-035's own new step-6 rule: the deliverable cites three repo-relative paths, all resolve on disk, prefix style matches each file's existing convention. Deliverable + kickoff/report pair (ADR-024) + STATUS hygiene committed as f328786; this task-resolution move committed separately.
