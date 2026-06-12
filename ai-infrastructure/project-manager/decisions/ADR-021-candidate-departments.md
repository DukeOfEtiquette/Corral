---
schema_version: 1
adr: 21
title: "Candidate departments: coordinator-plus-departments structure for this project"
status: "accepted"
date: "2026-06-08"
related_adrs: [1, 5, 8, 9, 18, 27]
supersedes: []
superseded_by: null
---

# ADR-021: Candidate departments: coordinator-plus-departments structure for this project

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

**Selected.** Departments are created on demand, not in advance. The menu established by this ADR is the ready list the `project-manager` coordinator stamps from when sustained work justifies it, using the create-department recipe (ADR-027 Fork D). No department workspace is created by this ADR or at this time. The `dept:*` labels already present on existing task files represent taxonomy running ahead of formal workspace creation; this is consistent with ADR-027 and intentional. The `project-manager` coordinator is the sole exception: it is instantiated by the restructure (ADR-027), not lazily created.

### Option B: Create all departments up front

Structure exists from day one, but most directories would sit empty and conventions would be guessed rather than earned.

**Rejected.** Creating eight department workspaces at this point would produce empty scaffolding before any department has real work. Conventions for a department emerge from real work, not from a template written in advance. The structural overhead would be carried with no benefit until actual department work begins. Option A's lazy model is cheaper to maintain and consistent with how rogue's departments accreted.

## Decision

This ADR blesses the nine-entry department menu and confirms the lazy-creation policy (Option A). ADR-027 is the authoritative workspace-structure ADR; ADR-021 is the menu feeding it.

**Blessed menu:**

Coordinator (instantiated by the restructure per ADR-027; not lazily created):

| Entry | Scope |
|---|---|
| project-manager | Orchestration, dispatch, review, cross-department coordination, and the shared task pool |

AI-infrastructure domain departments (lazily created, per ADR-005):

| Entry | Would own |
|---|---|
| agent-development | Orchestrator/worker role docs, agent definitions, kickoff/report specs |
| test-design | The test-designer agent and test-planning artifacts (ADR-016) |
| docs-curation | Decision hygiene, observation promotion, docs navigation |

Web-app domain departments (lazily created):

| Entry | Would own |
|---|---|
| backend-api | FastAPI service, auth, invites |
| database | Schema, migrations, seed logic |
| mcp-server | The MCP tool surface and house rules (ADR-013) |
| frontend-ui | React kanban client |
| devops | Docker images, compose topology, deployment |

**Coordinator/department distinction.** `project-manager` is the coordinator: it tracks, dispatches, and reviews; it does not author domain content. It holds write authority over the sibling department workspaces it coordinates (per ADR-027, "Coordinator write authority"). It is on the menu so coordinator-level work has a `dept:project-manager` label and its own filtered board, mirroring rogue's `workspace:project-manager`. Unlike the eight departments, it is not lazily created; it is instantiated by the restructure (ADR-027, a named follow-on task). It is not a tenth peer department.

**Label and board mapping.** Each menu entry maps to a `dept:<slug>` label (taxonomy and enforcement owned by ADR-018). At the dogfood milestone (ADR-008), each `dept:*` label gets its own filtered kanban board (ADR-001, ADR-008).

**Creation policy: lazy (Option A).** No department workspace is created by this task or at this time. The `project-manager` coordinator is the lone exception (see above). The `dept:*` labels already present on existing task files are taxonomy running ahead of formal workspace creation, which is consistent with ADR-027. The create-department recipe (ADR-027 Fork D) is how the `project-manager` stamps out a new department on demand; that recipe is a named follow-on task and is not built by this ADR.

## Consequences

- **`project-manager` coordinator role.** `project-manager` is instantiated by the restructure (COR-T-012, the ADR-027 follow-on task), not lazily created. Its write authority over sibling department workspaces is established by ADR-027. The coordinator role and its scope are defined there; this ADR adds it to the menu so coordinator-level work is labeled and visible.

- **`ai-infra` is a domain, not a department.** `ai-infra` is the ADR-005 domain name and is deliberately absent from this menu. One existing task (COR-T-007) carries an off-menu `dept:ai-infra` label. Reconciling that label is label-taxonomy hygiene owned by ADR-018 (its resolution is COR-T-008). COR-T-007 is not relabeled by this ADR; that is a COR-T-008 follow-up.

- **`dept:*` labels as taxonomy ahead of workspace creation.** Task files already carry `dept:<slug>` labels before their department workspaces exist. This is consistent with ADR-027 and intentional: the shared labeled pool (ADR-027 Fork B) is the product model Corral is building. The labels are valid now; workspace creation follows when work warrants it.

- **Create-department recipe.** How the `project-manager` stamps out a new department is defined in ADR-027 Fork D and implemented in a named follow-on task. That recipe is not provided by this ADR; this ADR provides the menu the recipe is stamped from.

- **Departments map to filtered boards at the dogfood milestone.** Each `dept:<slug>` gets its own filtered kanban board at the dogfood milestone (ADR-008), when task management migrates off the markdown `tasks/` tree and into the Corral web app. The label taxonomy and enforcement (including exactly one `dept:*` per task) are owned by ADR-018. ADR-001 established the board-per-department-label headline use case; ADR-008 fixed the dogfood milestone as when it lands.

  > Forward pointer (ADR-018, accepted 2026-06-10): the "exactly one `dept:*` per task" leaning above is amended to **at-most-one** (0 or 1). An issue may sit unlabeled; unlabeled issues appear on no department board. ADR-018 owns the resolved taxonomy; this ADR remains the authority for the valid `dept:*` slug roster.

  > Forward pointer (ADR-031, accepted 2026-06-11): the board-per-`dept:*`-label mapping above is unchanged in substance, but ADR-031 (per-department task trees, reversing ADR-027 Fork B) clarifies WHEN the `dept:<slug>` label is applied: in the markdown era a task's department is its workspace tree, not a label; the `dept:<slug>` label is applied at the dogfood import (ADR-008), derived from the tree, at which point the per-label boards become live in the app. See ADR-031.

- **ADR-027 is the authoritative structure ADR.** This ADR is the department menu; ADR-027 owns the coordinator/department model, the shared `dept:`-labeled task pool, the create-department recipe, and the coordinator write-authority grant. Readers who want the full workspace structure should read ADR-027. The two ADRs are complementary, not overlapping.

  > Forward pointer (ADR-016, accepted 2026-06-12): the `test-design` menu entry above lists "the test-designer agent" as what that department would own. ADR-016 decouples the two: the `test-designer` is authored now as a universal shared agent in `.claude/agents/` (parallel to `worker-agent`), dispatched by each web-app department orchestrator, while the `test-design` department stays a lazily-created candidate on this menu. Promotion trigger: create `test-design` when test design accretes a sustained cross-surface backlog of its own (e.g. the MCP golden-fixture corpus in Phase 3, or the cross-service end-to-end suite in Phase 4); the department then adopts the already-authored agent. This ADR remains the authority for the valid department roster; ADR-016 owns the testing strategy and the agent's home.

  > Forward pointer (ADR-032, accepted 2026-06-12): the `docs-curation` menu entry above (both the candidate table and the blessed menu) is renamed `docs`, with orchestrator command `/docs-orchestrator`, because the department owns documentation maintenance, design, and curation as production, not curation alone. The department stays lazily created. ADR-032 also generalizes the agent-feeds-department pattern (a cross-department `docs` review agent surfaces `dept:docs` issues for the `docs` department to own, mirroring `test-designer` and the test-design department). This ADR remains the authority for the valid department roster; read `docs-curation` above as `docs`.
