---
schema_version: 1
id: COR-T-005
title: "Resolve ADR-011: auth and session mechanism"
status: backlog
labels: [dept:backend-api]
priority: P1
created: 2026-06-05
updated: 2026-06-05
---

## Description

Take `./decisions/ADR-011-auth-session-mechanism.md` from pending to accepted. Decide sessions vs JWT, library vs hand-rolled, the admin-credential hash algorithm (finalizes ADR-006's mechanics), invite-token mechanics (ADR-007), and how the MCP server authenticates to the API if ADR-010 lands on the API path.

## Activity log

- 2026-06-05: Created in backlog during Phase 0 bootstrap.
