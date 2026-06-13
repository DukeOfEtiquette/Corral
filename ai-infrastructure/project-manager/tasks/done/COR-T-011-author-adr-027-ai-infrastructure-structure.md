---
schema_version: 1
id: COR-T-011
title: "Author ADR-027: ai-infrastructure workspace structure (project-manager coordinator)"
status: done
labels: [dept:agent-development]
priority: P1
created: 2026-06-08
updated: 2026-06-08
epic: COR-E-003
---

## Description

Author a new accepted `./decisions/ADR-027-ai-infrastructure-workspace-structure.md` that decides Corral's AI-infrastructure workspace structure: adopt the rogue coordinator-plus-departments model as a real `ai-infrastructure/<workspace>/` directory structure, with `ai-infrastructure/project-manager/` as the coordinator workspace holding the (to-be-moved) root orchestration content, and lazily-created sibling department workspaces over a single shared `dept:`-labeled task pool. Records the five forks resolved with the user (A: move root orchestration into `ai-infrastructure/project-manager/`; B: one shared labeled task pool, not per-department trees; C: web-app design ADRs migrate to web-app departments later; D: a light create-department template plus command; E: a small project-manager dashboard), amends ADR-009's "skip multiple workspaces" framing, references ADR-021's candidate list as the department menu, and names the restructure-execution, create-department-recipe, and dashboard work as follow-on tasks.

Decision-level only: no files are physically moved and no tooling is built by this task. ADR-027 is the review gate before the restructure executes in a separate task.

## Activity log

- 2026-06-08: Created and picked up (in-progress). Decomposed from the COR-T-006 / ADR-021 conversation after the user reframed the work as standing up `ai-infrastructure/project-manager/` per the rogue exemplar (`~/rogue/ai-workspaces/project-manager/`). Orchestrator producing the kickoff via the drafter+checker loop.
- 2026-06-08: Resolved. ADR-027 authored and accepted (ai-infrastructure workspace structure; Forks A-E; ADR-009 partially amended). Two em-dash stand-ins cleaned at review. Resolution committed in 50e3c87. Moved to done.
