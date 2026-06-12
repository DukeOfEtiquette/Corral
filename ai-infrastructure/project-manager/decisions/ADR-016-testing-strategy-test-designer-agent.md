---
schema_version: 1
adr: 16
title: "Testing strategy and the test-designer agent"
status: "accepted"
date: "2026-06-12"
related_adrs: [3, 5, 10, 13, 19, 21, 28]
supersedes: []
superseded_by: null
---

# ADR-016: Testing strategy and the test-designer agent

## Context

This is the exemplar of the two-domains rule (ADR-005): an agent that designs tests is an AI-infrastructure artifact, distinct from the tests it writes (web-app artifacts). This ADR covers both: the agent's definition and flow; and the app-side strategy (pytest for the backend, the frontend approach, contract tests pinning the MCP tool surface from ADR-013, and how tests run in compose).

Resolved 2026-06-12 (was pending). Two user declarations reshaped the resolution away from the original open-dimension list:

1. Corral is a test-driven-development (TDD) project. Tests for a surface are authored before that surface's implementation exists; implementation proceeds red-to-green against them.
2. Test design and implementation are performed by separate agents. A dedicated test-designer agent authors tests with clean context; the implementation worker makes them pass but may not touch them. The separation keeps test design uncontaminated by implementation thinking and prevents an implementer from weakening a test to make it pass.

## Alternatives considered

### Test-designer home: universal shared agent vs dedicated department

**Option A (selected):** author the test-designer as a universal dispatched agent in the shared `.claude/agents/` fleet, parallel to `worker-agent` (ADR-028) and the dispatch-loop checkers (ADR-023). Each web-app department orchestrator dispatches it, contextualized per surface by the test-design kickoff. The `test-design` department on the ADR-021 menu stays lazily uncreated.

**Option B (rejected for now):** stand up the `test-design` department workspace now (its own STATUS, tasks tree, orchestrator command) to own the agent.

Reasoning: the entire AI-infra fleet is universal capabilities dispatched by whichever orchestrator needs them (`worker-agent`, `kickoff-drafter`, the checkers); none has a department, so a test-design department would make the test-designer the odd one out. TDD couples test design tightly to a single surface's red-to-green build loop inside a single orchestrator session, so a separate department would put a coordination seam through the middle of that loop. "Each department contextualizes the agent for its needs" is exactly the universal-agent dispatch model (the same way `worker-agent` is contextualized by its kickoff and explicit reads). A department earns existence when it has a sustained backlog of its own (ADR-021 lazy rule); test design is currently a step in other departments' flows, not standalone production. Universal-now is cheaply promoted into a department later; department-now is hard to walk back.

### Backend strategy: unit-primary vs API-level-primary

**Option A (selected):** pytest with API-level/integration tests primary, exercised through the FastAPI app (ASGI transport) against a real Postgres, plus targeted unit tests for non-trivial logic (argon2id hashing, invite-token mechanics).

**Option B (rejected):** unit-primary, mocking the DB and dependencies, with few full-stack tests.

Reasoning: ADR-010 and ADR-013 make the HTTP API layer the single house-rule enforcement seam, so the API level is where the enforced contract (priority required at create, free status transitions, label-family invariants) is actually verified. Unit-primary would mock away exactly the seam the house rules live in.

### Test execution: long-running service vs one-shot

**Option A (selected):** a containerized one-shot `test` compose service running pytest against an ephemeral Postgres, mirroring the `migrate` one-shot that DB-T-001 established in `app/docker-compose.yml`.

**Option B (rejected):** a long-running test service.

Reasoning: ADR-003 makes compose the only run path; the one-shot pattern already exists in the topology; a long-running service buys nothing for a run-to-completion test pass.

### Frontend and MCP contract tests (deferred as decisions, not left open)

- **Frontend tests** (component vs end-to-end): deferred to Phase 4 / `frontend-ui`, decided when that surface and department exist. The TDD two-phase flow and the locked-tests rule apply when it lands.
- **MCP contract tests** (golden per-tool request/response fixtures): deferred to Phase 3 / `mcp-server`, decided alongside ADR-019 (MCP contract versioning, pending), to which they are tied. The same TDD model applies.

## Decision

Corral is a TDD project. For every web-app surface, tests are authored before implementation by a dedicated test-designer agent, and implementation proceeds red-to-green by a separate worker that may not modify tests.

| Dimension | Decision |
|---|---|
| Project discipline | TDD: tests precede the surface |
| Designer/implementer split | A universal `test-designer` agent designs tests; `worker-agent` implements to green and may not touch tests |
| No-touch enforcement | Role + kickoff out-of-scope + a new `worker-close-checker` rule failing the close if the impl worker's diff touched a test file; worker escalates instead of editing |
| Test-designer home | Universal shared agent now; `test-design` department deferred to a promotion trigger |
| Backend strategy | pytest, API-level primary + targeted units |
| Execution | Compose one-shot `test` service (mirrors the `migrate` one-shot) |
| Frontend / MCP contract tests | Deferred to Phase 4 / Phase 3; follow the same TDD two-phase + locked-tests model when they land |

### Two-phase per-surface flow

1. The producing department's orchestrator drafts a test-design kickoff and dispatches the universal `test-designer` agent, which authors the failing tests for the surface against its contract (the relevant ADRs, the ADR-012 schema, the surface's endpoint or tool spec). It writes only test files.
2. The orchestrator drafts an implementation kickoff naming the now-authored test paths under files out of scope, and dispatches `worker-agent` (ADR-028), which implements until all tests pass. The worker may not create or edit test files. If it believes a test is wrong it returns `RETURN: ESCALATION` rather than editing; the orchestrator routes the correction to a fresh `test-designer` dispatch.

### Test-ownership boundary (enforcement)

Three layers: (a) WORKER-ROLE forbids the implementation worker from creating or editing test files; (b) the implementation kickoff lists the surface's test paths under files out of scope; (c) a new `worker-close-checker` rule fails the close if the implementation worker's diff added or modified any test file. The escalate-don't-edit path is the sanctioned channel for a worker that believes a test is wrong.

## Consequences

- **Test-designer authored as universal shared infra ahead of any department.** This decouples the test-designer agent from the `test-design` department that ADR-021 listed as its owner: the agent is shared `.claude/` infrastructure now (like `worker-agent`), and `test-design` remains a lazily-created candidate on the ADR-021 menu. Promotion trigger: create the `test-design` department when test design accretes a sustained cross-surface backlog of its own (for example the MCP golden-fixture corpus in Phase 3, or the cross-service end-to-end suite in Phase 4); the department then adopts the already-authored agent. Forward-pointer note added to ADR-021.

- **ADR-005 exemplar satisfied.** ADR-005 requires this ADR to address both the test-designer agent (domain b) and the tests themselves (domain a). It does: the agent is a universal domain-2 artifact with a defined two-phase flow; the tests are domain-1 artifacts authored per surface.

- **Backend tests follow the enforcement seam.** API-level-primary testing verifies the house rules where ADR-010 and ADR-013 enforce them (the HTTP API layer), not against mocks that would bypass that seam.

- **MCP contract tests gated on ADR-019.** The Phase 3 golden-fixture contract tests are decided alongside the still-pending ADR-019 versioning policy. Forward-pointer note added to ADR-019.

- **Implementation chain blocks Phase 2 (P2-2).** Authoring the universal test-designer agent (role doc + agent definition + spec), wiring the two-phase TDD flow and the test-ownership boundary into ORCHESTRATOR-ROLE / WORKER-ROLE / the kickoff drafting convention, and adding the `worker-close-checker` no-touch rule are queued as COR-T-035 (the analog of COR-T-015, which authored `worker-agent`). P2-2 (backend-api API-T-001) is gated on COR-T-035: backend-api files API-T-001 as a test-design dispatch followed by an implementation dispatch once the test-designer exists.

- **New close-checker rule.** The `worker-close-checker` gains a rule beyond the current W2 (Follow-ups anchoring): an implementation worker's diff must touch no test files. Authoring it (rule ID and spec wording) is part of COR-T-035.
