---
schema_version: 1
id: GHI-T-001
title: "Author orchestrator and worker role docs, right-sized from rogue"
status: backlog
labels: [dept:agent-development]
priority: P1
created: 2026-06-05
updated: 2026-06-05
---

## Description

Create `./docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md` and `./docs/ai-orchestration/roles/WORKER-ROLE.md` for this repo, using `~/rogue/docs/ai-orchestration/roles/` as the source material (per ADR-009). Right-size: single project, no multi-workspace routing. The role docs must reference (not duplicate) the Agent Discipline rule in `./CLAUDE.md` and define the orchestrator-to-worker kickoff/report handoff contract this project will use.

## Activity log

- 2026-06-05: Created in backlog during Phase 0 bootstrap.
