---
schema_version: 1
id: GHI-T-002
title: "Resolve ADR-012: issue, label, and view schema"
status: backlog
labels: [dept:database]
priority: P1
created: 2026-06-05
updated: 2026-06-05
---

## Description

Take `./decisions/ADR-012-issue-label-view-schema.md` from pending to accepted. Decide: status as enum column vs label family; views in DB vs client config; the issue field set (including `external_ref` for the ADR-008 import); comment/activity modeling. The API (ADR-010) and MCP tool surface (ADR-013) bind to this schema, so this decision leads.

## Activity log

- 2026-06-05: Created in backlog during Phase 0 bootstrap.
