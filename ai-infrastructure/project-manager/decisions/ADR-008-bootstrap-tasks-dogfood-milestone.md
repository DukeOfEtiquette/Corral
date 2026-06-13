---
schema_version: 1
adr: 8
title: "Bootstrap task tracking in git-tracked markdown; dogfooding is an explicit milestone"
status: "accepted"
date: "2026-06-05"
related_adrs: [1, 4, 12]
supersedes: []
superseded_by: null
---

# ADR-008: Bootstrap task tracking in git-tracked markdown; dogfooding is an explicit milestone

> **Forward pointer (2026-06-13):** ADR-039 pre-stages the post-dogfood activity end-state. It derives the markdown-era STATUS activity feed (`last_updated`, `recent_updates`) from git history, which is the markdown-era analog of the app's `issue_events` audit log (ADR-012). At the dogfood migration the feed re-points its source from git to the events table without reshaping the dashboard `data.json` contract. See ADR-039.

## Context

This project needs robust task management, and task management is exactly what the project builds. The chicken-and-egg question: where do this project's own tasks live before the app can store them? Continuing on GitHub Issues would add load to the very rate limits the project exists to escape.

## Alternatives considered

### Option A: Git-tracked markdown tasks now; migrate into the app as soon as it can store issues

A simple `./tasks/` markdown convention (one file per task, status directories, frontmatter that mirrors the anticipated issue schema). When the MCP server and database can store issues, import the markdown tasks and freeze the convention.

**Selected because:** zero infrastructure on day zero, no GitHub load, and the frontmatter is deliberately shaped so migration is mechanical. Confirmed with the user on 2026-06-05. Trade-off accepted: no kanban view of project tasks until the dogfood milestone.

### Option B: Keep using GitHub Issues until the app is usable

**Rejected because:** adds to the rate-limit problem and builds more history that must be migrated later.

### Option C: Dogfood from day one (make the issue store the literal first deliverable)

**Rejected because:** the first iteration's tasks still need somewhere to live before that deliverable exists; Option A is that somewhere, and it already makes dogfooding the migration target.

## Decision

Project tasks live as markdown files under `./tasks/` per the convention in `./tasks/README.md`. Migrating those tasks into the app's own database via the MCP server is an explicit roadmap milestone (the dogfood milestone), after which the markdown tree is frozen read-only.

## Consequences

- `./tasks/README.md` is the canonical task policy for the markdown era; a fuller task-coordination doc supersedes it at the dogfood milestone.
- Task frontmatter fields map one-to-one onto the anticipated issue schema (ADR-012), and the task `id` is preserved as an external reference for idempotent import.
- The dogfood milestone is the project's first real end-to-end validation: if the app cannot absorb its own backlog, it is not done.
- Until the MCP server exists, agents touch tasks only through this markdown convention (ADR-004's interim seam).
- **ADR-036 work-item taxonomy (forward pointer).** The vocabulary that organizes the imported work (phase, epic, task, and the retirement of "milestone" as a work container) is pinned in ADR-036 (accepted). At this import, Epics become `type = epic` issues, Tasks become `type = task` issues with `parent_id`, Phases become labels, and ADRs stay external references, so the importer is a reader rather than an interpreter. The word "milestone" in this ADR's title and body is the generic event sense (the dogfood event), not the retired work-container sense. See `./ADR-036-work-item-taxonomy.md`. **ADR-038 refinement:** a Phase imports as a View entity plus a reserved `phase:*` label its epics carry, not a bare label; see `./ADR-038-phase-as-first-class-view.md`.
