---
schema_version: 1
id: COR-T-006
title: "Resolve ADR-021: decide the initial departments"
status: done
labels: [dept:docs-curation]
priority: P2
created: 2026-06-05
updated: 2026-06-08
epic: COR-E-003
---

## Description

Take `./decisions/ADR-021-candidate-departments.md` from pending to accepted. Review the candidate list with the user, decide which departments exist at Phase 1 (lazy creation is the leaning), and define what creating a department entails (directory? conventions doc? `dept:*` label reservation per ADR-018?).

## Activity log

- 2026-06-05: Created in backlog during Phase 0 bootstrap.
- 2026-06-08: Picked up; moved to in-progress. Orchestrator resolving anticipated decisions before kickoff.
- 2026-06-08: Reframed mid-flight: the conversation surfaced the ai-infrastructure/project-manager standup (ADR-027, COR-T-011), which superseded the original "what creating a department entails" question. ADR-021 narrowed to blessing the nine-entry candidate menu (project-manager coordinator + 3 AI-infra + 5 web-app departments), lazy creation, and an ADR-027 reference. Resolved; ADR-021 accepted. Committed in b35ef1e. Moved to done.
