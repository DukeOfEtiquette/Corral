---
schema_version: 1
adr: 16
title: "Testing strategy and the test-designer agent"
status: "pending"
date: "2026-06-05"
related_adrs: [5, 13]
supersedes: []
superseded_by: null
---

# ADR-016: Testing strategy and the test-designer agent

> Pending: can wait. Design can precede code; needed when code lands.

## Context

This is the exemplar of the two-domains rule (ADR-005): an agent that designs tests is an AI-infrastructure artifact, distinct from the tests it writes (web-app artifacts). This ADR covers both: the agent's definition, inputs, and report contract; and the app-side strategy (pytest for the backend, the frontend approach, contract tests pinning the MCP tool surface from ADR-013, and how tests run in compose).

## Alternatives considered

### Open dimensions (to be structured when taken up)

- Test-designer agent: kickoff/report format, what it reads (ADRs, schema, tool surface), what it emits (test plans vs test code).
- Backend: pytest; unit vs API-level emphasis.
- Frontend: component tests vs end-to-end (e.g. Playwright) vs both.
- MCP contract tests: golden request/response fixtures per tool, tied to ADR-019 versioning.
- Execution: tests as a compose service vs containerized one-shots.

## Decision

{Pending.}

## Consequences

{Pending.}
