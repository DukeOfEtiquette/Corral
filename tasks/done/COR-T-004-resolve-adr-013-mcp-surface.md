---
schema_version: 1
id: COR-T-004
title: "Resolve ADR-013: MCP tool surface and house rules"
status: done
labels: [dept:mcp-server]
priority: P1
created: 2026-06-05
updated: 2026-06-05
---

## Description

Take `./decisions/ADR-013-mcp-tool-surface-house-rules.md` from pending to accepted. Decide the v1 tool set (mirror ghtask vs leaner) and the server-enforced invariants (label families, status transitions, label creation rights). Include the importer tool needed for the ADR-008 dogfood milestone. Depends on COR-T-002 (schema) and COR-T-003 (data path).

## Activity log

- 2026-06-05: Created in backlog during Phase 0 bootstrap.
- 2026-06-07: Picked up by the Orchestrator; kickoff drafted and dispatched (drafter+checker loop PASS iteration 1), Worker session executed.
- 2026-06-07: Done. ADR-013 accepted (nine-tool MCP surface, free transitions, priority required, label-governance mechanism deferred to ADR-018/ADR-021); ADR-025 queued pending (native epics); OVERVIEW and STATUS updated. Worker output reviewed PASS against file state. Commit 8a90dce.
