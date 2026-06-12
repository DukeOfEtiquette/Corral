---
schema_version: 1
id: COR-T-035
title: "Author the universal test-designer agent and wire the TDD two-phase flow"
status: done
labels: []
priority: P1
created: 2026-06-12
updated: 2026-06-12
---

## Description

Implement ADR-016 (testing strategy and the test-designer agent, accepted 2026-06-12). This is the AI-infrastructure deliverable that makes Corral's TDD discipline operational; it is the analog of COR-T-015, which authored the `worker-agent`. It blocks Phase 2 P2-2: backend-api cannot run API-T-001 (test-design dispatch followed by implementation dispatch) until the `test-designer` agent and the two-phase flow exist.

Domain: AI-infrastructure (domain b). Routes through the dispatched-worker flow (these are deliverables: agent definition, role doc, spec, role-doc edits, a checker rule), not orchestrator-direct.

Deliverables, all grounded in ADR-016's Decision and Consequences:

1. **Author the universal `test-designer` agent** in the shared `.claude/agents/` fleet (parallel to `worker-agent` per ADR-028 and the dispatch-loop checkers per ADR-023): the agent definition (`.claude/agents/test-designer.md` or the convention the fleet uses), a role doc under `docs/ai-orchestration/roles/` (mirroring WORKER-ROLE.md), and an agent spec under `.claude/agents/specs/`. The agent authors failing tests (red) for a surface against its contract (the relevant ADRs, the ADR-012 schema, the surface's endpoint or tool spec); it writes only test files; it never implements the surface.

2. **Wire the two-phase TDD flow** into ORCHESTRATOR-ROLE.md: for every web-app surface, the producing department's orchestrator drafts a test-design kickoff and dispatches `test-designer` (phase 1, red), then drafts an implementation kickoff naming the authored test paths as out of scope and dispatches `worker-agent` (phase 2, green). Both dispatches live in the producing orchestrator's session.

3. **Encode the test-ownership boundary** (three layers per ADR-016):
   - WORKER-ROLE.md forbids the implementation worker from creating or editing test files; the sanctioned channel for a worker that believes a test is wrong is `RETURN: ESCALATION`, which the orchestrator routes to a fresh `test-designer` dispatch (not an in-place edit).
   - The kickoff drafting convention (ORCHESTRATOR-ROLE.md, and the drafter/checker specs as needed) requires the implementation kickoff to list the surface's test paths under files out of scope.
   - A new `worker-close-checker` rule fails the close if the implementation worker's diff added or modified any test file. Add the rule ID and wording to the worker-close-checker agent and its spec (`.claude/agents/specs/`), alongside the existing W2 (Follow-ups anchoring) rule.

4. **Sweep for consistency**: update any role-doc/spec cross-references the above touch so the fleet description stays coherent (the pattern COR-T-015 followed when it added the Dispatched-worker flow and repointed the checkers).

Out of scope: creating the `test-design` department workspace (deferred to a promotion trigger per ADR-016/ADR-021); authoring any actual backend tests (that is backend-api's API-T-001, which this unblocks); the backend pytest harness and the compose one-shot `test` service (those land with API-T-001 in the `app/` tree). Backend test emphasis (API-level primary + targeted units) and execution (compose one-shot) are decided in ADR-016 and are inputs to API-T-001, not deliverables of this task.

## Activity log

- 2026-06-12: Created in backlog. Implements ADR-016 (accepted 2026-06-12). P1: blocks Phase 2 P2-2 (backend-api API-T-001 is gated on the test-designer existing). Analog of COR-T-015 (authored worker-agent). Unlabelled per ADR-031 (dept:* applied at the dogfood import, not hand-applied here).
- 2026-06-12: Picked up; moved to in-progress. Routing through the dispatched-worker flow (deliverable task); resolving anticipated design decisions with the user before drafting the kickoff.
- 2026-06-12: Done (commit d125354). Dispatched-worker flow ran clean: kickoff drafted+checked (PASS), prelaunch W1 PASS, worker-agent COMPLETED, close W2/W3 PASS, verify-against-disk clean. Resolved design decisions: test-designer is a universal Opus dispatched agent (parallel to worker-agent), full standalone TEST-DESIGNER-ROLE.md, three-layer no-touch enforcement (WORKER-ROLE no-touch bullet + implementation-kickoff files_out_of_scope + new conditional close-checker rule W3 keyed on protected_test_paths). Nine files (3 new agent/role/spec, 6 edited). One follow-up logged: the worker-close-checker Pipeline diagram top label "Worker (Sonnet)" is now narrow (it also validates test-designer Opus reports); triaged to orchestrator, under discussion.
