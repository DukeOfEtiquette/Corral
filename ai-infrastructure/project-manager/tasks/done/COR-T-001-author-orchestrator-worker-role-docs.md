---
schema_version: 1
id: COR-T-001
title: "Author orchestrator and worker role docs, right-sized from rogue"
status: done
labels: [dept:agent-development]
priority: P1
created: 2026-06-05
updated: 2026-06-05
---

## Description

Create `./docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md` and `./docs/ai-orchestration/roles/WORKER-ROLE.md` for this repo, using `~/rogue/docs/ai-orchestration/roles/` as the source material (per ADR-009). Right-size: single project, no multi-workspace routing. The role docs must reference (not duplicate) the Agent Discipline rule in `./CLAUDE.md` and define the orchestrator-to-worker kickoff/report handoff contract this project will use.

## Activity log

- 2026-06-05: Created in backlog during Phase 0 bootstrap.
- 2026-06-05: Moved to in-progress; scope widened with user approval to include the slash commands, the full drafter+checker dispatch loop (four universal subagents plus specs), and ADR-023 recording the decision.
- 2026-06-05: Done. Role docs, ADR-023, four agent definitions plus specs, and both commands authored; verification clean (em-dash scan, rogue-ism scan, cross-reference check). Commit b9550f5. Functional smoke test of the subagents deferred to first real kickoff.
