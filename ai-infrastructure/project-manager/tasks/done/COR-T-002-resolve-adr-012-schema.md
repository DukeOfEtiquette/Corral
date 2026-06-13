---
schema_version: 1
id: COR-T-002
title: "Resolve ADR-012: issue, label, and view schema"
status: done
labels: [dept:database]
priority: P1
created: 2026-06-05
updated: 2026-06-05
epic: COR-E-002
---

## Description

Take `./decisions/ADR-012-issue-label-view-schema.md` from pending to accepted. Decide: status as enum column vs label family; views in DB vs client config; the issue field set (including `external_ref` for the ADR-008 import); comment/activity modeling. The API (ADR-010) and MCP tool surface (ADR-013) bind to this schema, so this decision leads.

## Activity log

- 2026-06-05: Created in backlog during Phase 0 bootstrap.
- 2026-06-05: Picked up. Decisions resolved with the user (status/priority as columns, views in DB, comments + events tables, assignee FK); kickoff drafted via the ADR-023 dispatch loop, checker PASS on iteration 1.
- 2026-06-05: Worker session executed: ADR-012 accepted, OVERVIEW.md attribution fix, STATUS deltas.
- 2026-06-05: Orchestrator review: outputs verified against kickoff; two minor findings (table miscount, unstated filter match semantics) patched directly by the Orchestrator with user approval (role deviation noted: trivial two-line fix in lieu of worker re-dispatch).
- 2026-06-05: Done: ADR-012 pending -> accepted. Commit 42dbbd1.
