---
schema_version: 1
adr: 5
title: "Two domains: the web app, and the AI infrastructure that builds it; AI infrastructure first"
status: "accepted"
date: "2026-06-05"
related_adrs: [9, 16, 21]
supersedes: []
superseded_by: null
---

# ADR-005: Two domains: the web app, and the AI infrastructure that builds it; AI infrastructure first

## Context

This is an AI-first development project. The user's stated model is that there are two distinct bodies of work: (a) the web app itself, and (b) the AI infrastructure (orchestrators, workers, agents, prompts, specs) that is built and maintained in service of that web app. Example given: developing and maintaining an agent that designs tests for the web app is a separate domain from the test writing that agent will conduct. Because the AI infrastructure is what builds the web app, it must be developed first.

## Alternatives considered

### Option A: Treat AI infrastructure as a first-class domain, developed first

The repo visibly separates app artifacts from AI-infrastructure artifacts. AI-infra deliverables (role docs, agent definitions, specs, task coordination) are designed, decided, and reviewed with the same rigor as app code, and Phase 1 of the roadmap is AI infrastructure.

**Selected because:** it matches the stated intent and the proven structure in `~/rogue`, where orchestration roles, specs, and observation logs are maintained artifacts rather than incidental prompts. Trade-off accepted: visible up-front investment before any app code exists.

### Option B: Build the app directly and let AI tooling accrete informally

**Rejected because:** informal prompts decay, are unreviewable, and cannot be handed between sessions; the rogue experience shows the infrastructure pays for itself.

## Decision

The project maintains two domains. AI infrastructure (domain b) is developed before and alongside the web app (domain a). Artifacts that define agents are distinct deliverables from the artifacts those agents produce.

## Consequences

- Phase 1 of the roadmap is AI infrastructure: role docs, blocking-ADR resolution, department structure (ADR-021).
- The testing strategy ADR (ADR-016) must address both the test-designer agent (domain b) and the tests themselves (domain a). (Resolved 2026-06-12: ADR-016 accepted. The test-designer is a universal domain-b agent with a two-phase TDD flow; the tests are domain-a artifacts authored per surface. Exemplar satisfied.)
- Repo conventions for the AI-infra domain are adopted in ADR-009.
- Both domains' work items flow through the same task system (ADR-008), so neither becomes invisible.
