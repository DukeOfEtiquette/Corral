---
schema_version: 1
id: COR-T-023
title: "Stand up the database and backend-api departments before Phase 2 code"
status: done
labels: [dept:agent-development]
priority: P2
created: 2026-06-10
updated: 2026-06-10
---

## Description

Phase 2 (API + DB core) is the first phase that produces web-app code. Per the lazy-creation policy (ADR-021, ADR-027), a department workspace is stood up at the moment its domain's work begins, so the work has a home (its own STATUS, decisions, OBSERVATIONS, and `/<slug>-orchestrator` command) from day one. Today only the `project-manager` coordinator workspace exists; the eight blessed departments are all planned. Before any Phase 2 code lands, the relevant web-app departments must be created so the code is authored inside a real department rather than homeless.

Scope: stand up the two departments Phase 2 touches first, using the `create-department` recipe (ADR-030, the `/create-department` command and the `ai-infrastructure/project-manager/templates/department/` scaffold):

- `database` (web-app domain): home for the Postgres schema work (P2-1, ADR-012 as amended by ADR-025 epics and ADR-026 machine users).
- `backend-api` (web-app domain): home for the FastAPI endpoints, house rules, and auth/sessions work (P2-2, P2-3; ADR-013, ADR-011).

This is also the first end-to-end exercise of `create-department`, which has been built (COR-T-013) but never actually run to stamp a department; standing these up validates the recipe. Each created department gets its scoped orchestrator command and template-stamped workspace files per the scaffold contract. `mcp-server` (Phase 3) and `frontend-ui` (Phase 4) are out of scope here; they are stood up just-in-time when their phases begin.

This gates roadmap milestone P2-0; it should complete before P2-1 (schema) code work starts. It routes through the `/create-department` flow (which drives the dispatched-worker flow to stamp each workspace).

## Activity log

- 2026-06-10: Created in backlog. Surfaced from a user question during the COR-T-022 session: the department-creation sequencing (create the department before its code, per ADR-021/027 lazy creation) had no task tracking it, and the backlog was empty. Decision with the user: file this task plus a P2-0 "Create web-app departments" roadmap milestone so the before-code sequencing is structurally encoded and visible on the dashboard. Scoped to database + backend-api (the Phase 2 departments); first real create-department run.
- 2026-06-10: Picked up; moved to in-progress. Runs as two sequential `/create-department` recipe executions (database, then backend-api), each its own dispatched-worker flow, closed under this one task.
- 2026-06-10: Done. Both departments stamped via the create-department recipe (its first real end-to-end run, built in COR-T-013): `database` (DB prefix, `/database-orchestrator`) and `backend-api` (API prefix, `/backend-api-orchestrator`), each a fully-wired unit per ADR-030 (scoped orchestrator command adopting the shared role doc by reference, dispatching the universal worker-agent; no per-dept worker command, role-doc copies, or `tasks/` dir). Two dispatched-worker flows, both clean (kickoff-check / prelaunch / close-check all PASS, zero escalations, zero residual tokens verified on disk). Closed roadmap milestone P2-0. Deliverables + STATUS + both kickoff/report pairs committed as baf45d8.
