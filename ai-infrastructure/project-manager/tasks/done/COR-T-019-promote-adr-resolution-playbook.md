---
schema_version: 1
id: COR-T-019
title: "Promote the ADR-resolution pattern into ORCHESTRATOR-ROLE.md"
status: done
labels: [dept:agent-development]
priority: P3
created: 2026-06-10
updated: 2026-06-10
---

## Description

Promote the recurring orchestrator-direct "resolve a pending ADR" pattern, observed cleanly across COR-T-008 (ADR-018) and COR-T-009 (ADR-025), into a short "Pending-ADR resolution playbook" subsection in `docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md`. This is the canonicalization (promoted) step of the pattern lifecycle; the matching OBSERVATIONS entry (COR-02) is logged orchestrator-direct and points at the new subsection. The playbook distills the seven-step flow both tasks followed: read the pending ADR + related_adrs both ways; do the homework and form grounded recommendations; frame only the binding decisions with the user (mechanical ones flow); set the ADR pending -> accepted; forward-pointer sweep both directions; STATUS hygiene + task-specific deltas; two-commit close. The subsection cross-references the existing "Stale-reference sweep when resolving ADRs" bullet rather than duplicating it, and is explicit that ADR resolution is orchestrator-direct (the decisions/ carve-out), distinct from the dispatched-worker flow.

The role-doc edit is a documentation deliverable, so it routes through the dispatched-worker flow per `ORCHESTRATOR-ROLE.md` (section "Dispatched-worker flow", routing rule). The OBSERVATIONS log and task transitions are orchestrator-direct.

## Activity log

- 2026-06-10: Created and picked up in the same session (orchestrator-direct task allocation). Surfaced after COR-T-009 closed: two clean orchestrator-direct ADR-resolution runs (COR-T-008, COR-T-009) following an identical shape. User chose full canonical promotion now (vs. logging-and-waiting-for-a-third instance). Decisions pinned: home is a new ORCHESTRATOR-ROLE.md subsection "Pending-ADR resolution playbook" placed after "Task lifecycle"; content is the seven-step flow; cross-reference (not duplicate) the stale-reference sweep bullet; OBSERVATIONS COR-02 logged orchestrator-direct after the worker lands the subsection.
- 2026-06-10: Done. Dispatched-worker flow ran clean: kickoff PASS (R1-R8), prelaunch PASS (W1), worker COMPLETED, close-check PASS (W2). Verified against disk: ORCHESTRATOR-ROLE.md subsection added (18 insertions, 0 deletions, no em dashes, correct placement, cross-references the stale-reference bullet without duplicating it); STATUS has one hygiene entry. OBSERVATIONS COR-02 logged orchestrator-direct (promoted -> the new subsection). Deliverable committed as e91efc8 (with the kickoff/report pair per ADR-024). Moved to done.
