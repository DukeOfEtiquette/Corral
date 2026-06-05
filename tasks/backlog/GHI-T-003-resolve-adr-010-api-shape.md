---
schema_version: 1
id: GHI-T-003
title: "Resolve ADR-010: API shape and MCP data path"
status: backlog
labels: [dept:backend-api]
priority: P1
created: 2026-06-05
updated: 2026-06-05
---

## Description

Take `./decisions/ADR-010-api-shape-and-mcp-data-path.md` from pending to accepted. Decide REST vs GraphQL, and whether the MCP server calls the HTTP API (single enforcement seam) or the database directly. Determines build order between the MCP server and the API. Depends on GHI-T-002 (schema).

## Activity log

- 2026-06-05: Created in backlog during Phase 0 bootstrap.
