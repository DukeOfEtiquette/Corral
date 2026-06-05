---
schema_version: 1
adr: 13
title: "MCP tool surface and server-enforced house rules"
status: "pending"
date: "2026-06-05"
related_adrs: [4, 10, 12, 19]
supersedes: []
superseded_by: null
---

# ADR-013: MCP tool surface and server-enforced house rules

> Pending: blocks the first development iteration (Phase 1). Frames the question; decision not yet taken.

## Context

ADR-004 commits to an MCP server as the sole LLM seam. This ADR decides what that server exposes and enforces. The proven reference is rogue's `ghtask` surface: `task_list`, `task_get`, `task_create`, `task_claim`, `task_move`, `task_comment`, `task_label`, `task_link`, with server-side house rules (required label families, exactly-one-status, priority labels, auto-created sanctioned labels).

## Alternatives considered

### Option A: Mirror the ghtask tool set, renamed for this domain

`issue_list/get/create/claim/move/comment/label/link` plus `view_list`. Familiar to the existing agent fleet; proven ergonomics.

### Option B: Leaner v1 surface

Only `issue_list/get/create/move/comment`; add claim/label/link when an agent workflow actually needs them.

### Open house-rule dimensions

Which invariants are server-enforced: required label families (e.g. exactly one `dept:*`?), priority required or optional, who may create labels (relates to ADR-018), valid status transitions (relates to ADR-017), and an importer/migration tool for the ADR-008 dogfood milestone.

## Decision

{Pending.}

## Consequences

{Pending.}
