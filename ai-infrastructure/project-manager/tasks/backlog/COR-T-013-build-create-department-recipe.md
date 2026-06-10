---
schema_version: 1
id: COR-T-013
title: "Build the create-department recipe (template, command, recipe ADR)"
status: backlog
labels: [dept:agent-development]
priority: P2
created: 2026-06-08
updated: 2026-06-08
---

## Description

Build the create-department recipe per `./decisions/ADR-027-ai-infrastructure-workspace-structure.md` Fork D: a `templates/department/` baseline scaffold (`CLAUDE.md`, `README.md`, `STATUS.md`, `OBSERVATIONS.md` with a `<DEPT>-NN` observation prefix, a `decisions/` directory, paired `/<dept>-orchestrator` (Opus) and `/<dept>-worker` (Sonnet) slash-command stubs, and a reserved `dept:<slug>` label per ADR-018); a `/create-department` command that stamps the baseline out; and a recipe ADR recording the scaffold contract. Departments get no own `tasks/` directory (Fork B: shared labeled pool). Gated on the restructure (COR-T-012), which establishes the `ai-infrastructure/project-manager/` location.

## Activity log

- 2026-06-08: Created in backlog. Named follow-on deliverable 2 of ADR-027 (COR-T-011); gives the project-manager its on-demand department-creation capability.
