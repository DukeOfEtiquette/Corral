---
schema_version: 1
id: COR-T-012
title: "Execute the ai-infrastructure restructure (move root orchestration into project-manager)"
status: backlog
labels: [dept:agent-development]
priority: P1
created: 2026-06-08
updated: 2026-06-08
---

## Description

Execute the physical restructure decided in `./decisions/ADR-027-ai-infrastructure-workspace-structure.md` (its Decision section is the spec). `git mv` the root orchestration content (`CLAUDE.md` operating rules, `STATUS.md`, `OBSERVATIONS.md`, `decisions/`, `docs/`, `tasks/`) into `ai-infrastructure/project-manager/`; write a thin repo-root `CLAUDE.md` (orientation plus pointers into `ai-infrastructure/` and the future `app/`) and keep `README.md` for humans; rewrite path-convention references so `./`-prefixed paths resolve workspace-relative within `project-manager/` (the moved `CLAUDE.md`, the role docs, the `/corral-orchestrator` slash command, the `worker-agent` and the other agent definitions, and the agent specs). `.claude/` stays at the repo root as shared infrastructure. No new ADRs and no tooling are authored. Gated on ADR-027 (accepted).

## Activity log

- 2026-06-08: Created in backlog. Named follow-on deliverable 1 of ADR-027 (COR-T-011); the AI-infrastructure structure's execution step.
