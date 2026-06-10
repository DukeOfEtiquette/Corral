---
schema_version: 1
id: COR-T-014
title: "Build the project-manager dashboard (small, querying the shared task pool)"
status: backlog
labels: [dept:agent-development]
priority: P2
created: 2026-06-08
updated: 2026-06-08
---

## Description

Build the project-manager dashboard per `./decisions/ADR-027-ai-infrastructure-workspace-structure.md` Fork E, scoped small: a Python ETL that reads the shared `tasks/` pool and workspace `STATUS` frontmatter, emits a JSON data contract, and renders a minimal board UI, runnable under docker compose (ADR-003). It queries the markdown `tasks/` pool now and is designed to repoint to the Corral web app at the dogfood milestone (ADR-008), when task management migrates off `tasks/`. Gated on the restructure (COR-T-012), which establishes the shared pool location at `ai-infrastructure/project-manager/tasks/`.

## Activity log

- 2026-06-08: Created in backlog. Named follow-on deliverable 3 of ADR-027 (COR-T-011); the PM's at-a-glance board over the shared pool, and the first concrete dogfood-arc artifact.
