---
schema_version: 1
id: COR-T-053
title: "Sweep stale 'pending' ADR cross-references in accepted ADRs (decision-hygiene drift)"
status: backlog
labels: []
priority: P3
created: 2026-06-15
updated: 2026-06-15
---

## Description

Filed by the Backend API Orchestrator into the coordinator tree (cross-workspace): this is decision-hygiene work on the coordinator's `decisions/` ADRs, not backend-api work, so it lives here as a `COR-T` task. Surfaced during backend-api API-T-001 planning on 2026-06-15.

**The drift.** An ADR's prose that refers to a sibling ADR as "(pending)" goes stale the moment that sibling is accepted, because ADRs are append-only: their decision text is never edited in place (the ADR-024 amend-by-later-note precedent). A reader who trusts the cross-reference instead of the referenced ADR's own `status:` field can act on a wrong premise.

**Concrete instance (the trigger).** `ADR-013-mcp-tool-surface-house-rules.md` (dated 2026-06-07) refers to ADR-018 (department label taxonomy) and ADR-021 (candidate departments) as "pending." Both were accepted shortly after (ADR-021 on 2026-06-08, ADR-018 on 2026-06-10). On 2026-06-15 the stale "ADR-018 (pending)" reference produced a wrong "must resolve ADR-018 first" premise while scoping API-T-001; it was caught by checking ADR-018's own `status:` (accepted), but only after it had shaped a plan. Other instances likely exist across the ADR set.

**Goal (eventual cleanup; recorded now for later).** Sweep the accepted ADRs for "(pending)" cross-references to ADRs that have since been accepted, and reconcile each, respecting the append-only rule: do NOT edit decision text in place; add a dated forward-pointer note (the ADR-024 precedent, the same mechanism ADR-021 already uses, e.g. its "Forward pointer (ADR-018, accepted 2026-06-10)" note). Add the pointer where a stale "(pending)" is load-bearing or misleading.

**Detection is mechanical.** `grep -rn "pending" ai-infrastructure/project-manager/decisions/` cross-referenced against each named ADR's actual `status:` field surfaces the gap (the same derive-from-the-source-of-truth check the dashboard relies on).

**Possible extension (not the core ask; decide at kickoff).** Prevention: the ORCHESTRATOR-ROLE "Stale-reference sweep when resolving ADRs" bullet already sweeps the ADR being resolved, but not retroactively the ADRs that referenced it as pending. A step in the Pending-ADR resolution playbook (add forward-pointers to all referencing ADRs at acceptance time) or a checker would prevent recurrence. Scope this in or defer it when the task is picked up.

Routes through the dispatched-worker flow when picked up (a decisions/docs deliverable). Eventually this is `docs`-department work (decision hygiene, ADR-021/032); for now it is coordinator-owned. Standalone task (no epic).

References:
- `ai-infrastructure/project-manager/decisions/ADR-013-mcp-tool-surface-house-rules.md` (carries the stale "pending" refs to ADR-018/021)
- `ai-infrastructure/project-manager/decisions/ADR-018-department-label-taxonomy.md` and `ai-infrastructure/project-manager/decisions/ADR-021-candidate-departments.md` (the accepted ADRs referenced as pending; ADR-021 already models the fix with its forward-pointer notes)
- `docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md` (the "Stale-reference sweep when resolving ADRs" bullet + the Pending-ADR resolution playbook)
- ADR-024 (by ID): the amend-by-later-note / forward-pointer precedent the cleanup should follow (resolve its exact path at kickoff).

## Activity log

- 2026-06-15: Created in backlog by the Backend API Orchestrator (cross-workspace into the coordinator tree, at user direction). Surfaced during API-T-001 planning when ADR-013's stale "ADR-018 (pending)" cross-reference produced a wrong premise, caught by verifying ADR-018's own accepted status. Filed P3 (eventual cleanup) and standalone (decision-hygiene work fits no current epic). Unlabelled per ADR-031.
