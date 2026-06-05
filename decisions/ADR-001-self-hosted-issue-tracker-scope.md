---
schema_version: 1
adr: 1
title: "Build a self-hosted, narrow-scope issue tracker with multi-view kanban"
status: "accepted"
date: "2026-06-05"
related_adrs: [2, 3, 4, 12, 17, 18]
supersedes: []
superseded_by: null
---

# ADR-001: Build a self-hosted, narrow-scope issue tracker with multi-view kanban

## Context

The user runs orchestrator/worker LLM agents (in the `~/rogue` project) that manage development tasks through GitHub Issues plus a GitHub Projects kanban board, accessed through a GitHub MCP server. That workflow works well but is hitting GitHub API usage rate limits. The actual feature surface in use is narrow: create/read/update issues, label them, and view them on kanban boards. The bulk of GitHub's feature set (PR integration, automation keywords like `closes #N`, notifications, webhooks) is not part of the workflow.

## Alternatives considered

### Option A: Self-host a narrow clone (this project)

Build a client+server web app. The server owns an issue database; the client renders kanban board views over it. Multiple kanban views can be defined over the same database, each with its own label filter (for example, one board per department label).

**Selected because:** the use case is narrow enough to recreate, removes the external rate limit entirely, and keeps all task data local. The trade-off accepted is losing GitHub's quality-of-life automation (issue-reference keywords auto-moving status, cross-linking, etc.); that layer is explicitly out of scope for v1.

### Option B: Stay on GitHub and work around the rate limits

Caching, batching, multiple tokens, or paying for higher limits.

**Rejected because:** workarounds add complexity to every agent interaction, the ceiling remains externally controlled, and the dependency on an external service conflicts with the goal of a tool shareable on any developer machine or a central server.

### Option C: Adopt an existing self-hosted tracker (Gitea, GitLab CE, Plane, etc.)

**Rejected because:** these are far larger than the use case, bring their own auth/admin models, and would still require building a custom MCP guardrail layer around someone else's API. The narrow scope makes a purpose-built app smaller than the integration work.

## Decision

Build GHIssuesClone: a self-hosted client+server web app where the server tracks issues in its own database and the client provides kanban views. Each view is defined over the same database with per-view label filtering. GitHub-style automation keywords and other quality-of-life layers are out of scope for v1.

## Consequences

- No external rate limits; all task data is local and owned by the project.
- The GitHub features not rebuilt are genuinely lost until someone decides to add them; that loss is accepted (see future-work candidates in pending ADRs).
- The product boundary informs the schema (ADR-012), the board/status model (ADR-017), and the label taxonomy (ADR-018).
- The app must eventually replace GitHub Issues for this project's own task tracking (ADR-008).
