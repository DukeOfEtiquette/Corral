---
schema_version: 1
id: COR-T-003
title: "Resolve ADR-010: API shape and MCP data path"
status: done
labels: [dept:backend-api]
priority: P1
created: 2026-06-05
updated: 2026-06-05
epic: COR-E-002
---

## Description

Take `./decisions/ADR-010-api-shape-and-mcp-data-path.md` from pending to accepted. Decide REST vs GraphQL, and whether the MCP server calls the HTTP API (single enforcement seam) or the database directly. Determines build order between the MCP server and the API. Depends on COR-T-002 (schema).

## Activity log

- 2026-06-05: Created in backlog during Phase 0 bootstrap.
- 2026-06-05: Picked up. Decisions resolved with the user (REST, MCP via HTTP API, README roadmap phases 2/3 swapped to fix the build-order inversion); kickoff drafted via the ADR-023 dispatch loop, checker PASS on iteration 1.
- 2026-06-05: Worker session executed: ADR-010 accepted, README roadmap swap, OVERVIEW.md mcp bullet, STATUS deltas.
- 2026-06-05: Orchestrator review: outputs verified against kickoff; findings (related_adrs missing two cited ADRs, leaked kickoff phrasing, stale ADR-004 cross-reference flagged by the Worker) patched directly by the Orchestrator with user approval (role deviation noted, same precedent as COR-T-002). Third COR-01 occurrence promoted to a role-doc homework step (commit 7a4eb86).
- 2026-06-05: Done: ADR-010 pending -> accepted. Commit 59661d6.
