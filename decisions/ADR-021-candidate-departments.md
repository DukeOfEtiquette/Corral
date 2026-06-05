---
schema_version: 1
adr: 21
title: "Candidate departments: coordinator-plus-departments structure for this project"
status: "pending"
date: "2026-06-05"
related_adrs: [5, 9, 18]
supersedes: []
superseded_by: null
---

# ADR-021: Candidate departments: coordinator-plus-departments structure for this project

> Pending: resolve in Phase 1. Frames the candidate list per the user's request; which departments exist, and when each is created, is not yet decided.

## Context

Per ADR-009, this project mirrors the structure of `~/rogue/ai-workspaces/project-manager`: a coordinator that sequences and gates work across departments, where each department owns its own production. At day zero the repo root acts as the coordinator and no departments exist yet. The user asked for a recorded list of candidate departments to decide on and create in the future.

There is a deliberate symmetry: once the app exists and the dogfood milestone lands (ADR-008), each department maps to a `dept:*` label (ADR-018) and gets its own filtered kanban board. The project's organizational structure and the app's headline feature are the same shape.

## Candidate departments

AI-infrastructure domain (per ADR-005):

| Candidate | Would own |
|---|---|
| agent-development | Orchestrator/worker role docs, agent definitions, kickoff/report specs |
| test-design | The test-designer agent and test-planning artifacts (ADR-016) |
| docs-curation | Decision hygiene, observation promotion, docs navigation |

Web-app domain:

| Candidate | Would own |
|---|---|
| backend-api | FastAPI service, auth, invites |
| database | Schema, migrations, seed logic |
| mcp-server | The MCP tool surface and house rules (ADR-013) |
| frontend-ui | React kanban client |
| devops | Docker images, compose topology, deployment |

## Alternatives considered

### Option A: Create departments lazily, on first real workload

Repo root stays the coordinator; a department is created (directory, conventions, label) only when sustained work justifies it.

**Leaning selected:** matches the rogue history, where departments accreted as need emerged.

### Option B: Create all departments up front

Structure exists from day one, but most directories would sit empty and conventions would be guessed rather than earned.

## Decision

{Pending. To be resolved as task COR-T-006.}

## Consequences

{Pending.}
