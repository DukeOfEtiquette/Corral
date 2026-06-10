# Promote the ADR-resolution pattern into ORCHESTRATOR-ROLE.md

## Target

This is AI-infrastructure work (ADR-005): the deliverable is a shared orchestration role doc, a domain-2 artifact, not web-app code. The task (COR-T-019) adds one new subsection to `docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md` that canonicalizes the repeatable flow for resolving a pending ADR orchestrator-direct. The flow is distilled from two clean instances (COR-T-008 resolving ADR-018, COR-T-009 resolving ADR-025); this task promotes it from those instances into the role doc as durable guidance.

## Decisions resolved by the Orchestrator

The content below is pinned. Render it in the role doc's existing prose voice (short declarative prose plus a numbered list, matching sections like "Task lifecycle" and "Handoff hygiene"). Do not invent additional steps or guidance beyond what is pinned here. No em dashes anywhere (global rule, `./CLAUDE.md`): use a comma, colon, or rephrase.

- **The deliverable is one new subsection.** Add a single subsection titled "Pending-ADR resolution playbook" to `docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md`. Use a `## Pending-ADR resolution playbook` heading, at the same level as the neighbouring sections. This subsection is the ONLY content change to the file.

- **Placement is fixed.** Insert the subsection immediately AFTER the entire "Task lifecycle" section (that is, after its closing bolded "**Seam swap ahead.**" paragraph) and BEFORE the "## Handoff hygiene" section. The new `## Pending-ADR resolution playbook` heading sits between the end of "Task lifecycle" and the start of "Handoff hygiene".

- **Lead-in sentence(s).** Paraphrase the following into house voice, keeping the substance: Resolving a pending ADR is orchestrator-direct work (the `decisions/` carve-out named in the "Dispatched-worker flow"), not a dispatched-worker task. This playbook is the repeatable flow, distilled from COR-T-008 (ADR-018) and COR-T-009 (ADR-025). When a resolution spawns a separate deliverable (a doc, schema, or code touch-up), that deliverable routes through the dispatched-worker flow; the ADR edit itself stays orchestrator-direct.

- **The seven steps.** Render as a numbered list. Paraphrase each into house voice; preserve the substance exactly. Do not add, drop, split, or merge steps.

  1. Read the pending ADR and its related_adrs in both directions. The ADR frames the question and the alternatives; the related ADRs, and any docs that cite it, are where leanings, deferrals, and forward-pointers live.

  2. Do the homework before surfacing anything to the user. Read every affected ADR end-to-end (the schema it amends, the surface it extends, the board and versioning neighbours) and form a recommendation for each binding dimension, grounded in the established philosophy of the existing decisions rather than presented as a bare option list.

  3. Frame only the binding decisions with the user; let the mechanical ones flow. Genuinely architectural dimensions (the data model, the tool surface) are the user's call; dimensions that follow mechanically from a chosen option (cardinality from a single FK, a deferral to a later phase) are stated, not asked. Never frame a question whose live answer path is "let a later step or agent decide."

  4. Take the ADR from pending to accepted: fill Decision and Consequences declaratively, bump date, expand related_adrs, and remove the "> Pending:" callout.

  5. Run the forward-pointer sweep in both directions, per the existing "Stale-reference sweep when resolving ADRs" bullet under "Kickoff drafting convention" (cross-reference that bullet by name; do NOT restate or duplicate its content). For each accepted ADR the decision amends, add a forward-pointer note while the amendment itself lives in the later ADR (the ADR-024 precedent: amend by a later ADR, never edit an accepted ADR's decision in place); mark resolved any "deferred to ADR-NNN (pending)" language in neighbours; and leave conditional leanings that did not fire accurate as written (do not edit what is still true). Contradicted leanings are decisions: surface them to the user. Stale cross-references are deliverables: fix them or triage them as follow-ups.

  6. Apply STATUS hygiene plus the task-specific deltas: bump last_updated, prepend a recent_updates entry, and update "Next step" and the roadmap milestone to drop the resolved task.

  7. Close with two commits: commit 1 is the ADR acceptance plus forward-pointer notes plus STATUS (task still in-progress); commit 2 is the task move to done, whose done activity-log line cites commit 1's short hash. The split sidesteps the chicken-and-egg of recording the deliverable's hash in the done line.

- **Touch nothing else.** Do not edit, move, or reword any other section of `ORCHESTRATOR-ROLE.md`, including the existing "Stale-reference sweep when resolving ADRs" bullet (it stays exactly where it is; the playbook only references it by name).

## Deliverables

- One new "Pending-ADR resolution playbook" subsection in `docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md`, placed and styled exactly as pinned above (lead-in prose plus the seven-step numbered list, in the role doc's voice, no em dashes).
- Universal STATUS hygiene only (see "STATUS deltas").

## Files in scope

- `docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md` (add the one subsection between "Task lifecycle" and "Handoff hygiene")
- `ai-infrastructure/project-manager/STATUS.md` (universal hygiene only)

## Files out of scope

- `ai-infrastructure/project-manager/OBSERVATIONS.md` (the matching COR-02 observation is logged orchestrator-direct, NOT by you)
- the `ai-infrastructure/project-manager/tasks/` tree (task transitions are orchestrator-only)
- every ADR under `ai-infrastructure/project-manager/decisions/` (no ADR is edited by this task)
- the command files under `.claude/commands/` and the agent specs under `.claude/agents/`
- `docs/ai-orchestration/roles/WORKER-ROLE.md`

## References

- `docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md`: the target. Read "Task lifecycle" (the insertion point is right after it, immediately following its closing bolded "**Seam swap ahead.**" paragraph), "Kickoff drafting convention" (contains the "Stale-reference sweep when resolving ADRs" bullet the playbook cross-references by name), and "Dispatched-worker flow" (the orchestrator-direct `decisions/` carve-out language) to match voice and place the subsection correctly.
- `ai-infrastructure/project-manager/OBSERVATIONS.md`: the COR-01 entry is the precedent that orchestrator-process patterns promote into ORCHESTRATOR-ROLE.md. Read-only context; do not edit.
- `ai-infrastructure/project-manager/tasks/done/COR-T-008-resolve-adr-018-label-taxonomy.md`: instance 1 the playbook distills. Read-only.
- `ai-infrastructure/project-manager/tasks/done/COR-T-009-resolve-adr-025-native-epics.md`: instance 2 the playbook distills. Read-only.

## Related tasks and ADRs

- COR-T-008: first clean instance (ADR-018 resolution) the playbook distills.
- COR-T-009: second clean instance (ADR-025 resolution) the playbook distills.
- COR-01 (OBSERVATIONS): the precedent that orchestrator-process patterns promote into ORCHESTRATOR-ROLE.md.
- ADR-024: the amend-by-later-ADR precedent cited in the playbook's step 5.

## STATUS deltas

No task-specific STATUS deltas; universal hygiene only. Apply the universal hygiene in `ai-infrastructure/project-manager/STATUS.md` (bump `last_updated`, append a `recent_updates` entry) per `WORKER-ROLE.md`, section "Wrap-up STATUS hygiene".

## Hard rules

- The subsection is the only content change to `ORCHESTRATOR-ROLE.md`. Match the existing prose voice; do not paraphrase the seven steps into a different register or add guidance beyond what the decisions pin.
- Render step 5 as a cross-reference to the existing "Stale-reference sweep when resolving ADRs" bullet by name; do NOT restate or duplicate that bullet's content.
- No em dashes anywhere in the file (`./CLAUDE.md`, global writing rule). Use a comma, colon, or rephrase.

## Worker pointer

You are the dispatched `worker-agent` (ADR-028). Universal worker conventions live in `docs/ai-orchestration/roles/WORKER-ROLE.md`. Write your closing report to `./.claude/artifacts/handoffs/COR-T-019-KICKOFF-REPORT.md` per `WORKER-ROLE.md`, section "Report shape".
