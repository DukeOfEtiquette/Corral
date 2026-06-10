---
schema_version: 1
id: COR-T-021
title: "Thin the README roadmap to stable orientation; STATUS frontmatter owns the detail"
status: in-progress
labels: [dept:docs-curation]
priority: P3
created: 2026-06-10
updated: 2026-06-10
---

## Description

The repo-root `README.md` roadmap table (the "## Roadmap" section) duplicates phase titles and granular deliverable prose that also live in `ai-infrastructure/project-manager/STATUS.md`'s `roadmap:` frontmatter, which is the structured single source of truth the dashboard reads (and renders live since COR-T-020). The duplication is drift-prone: the README roadmap already carries a stale "(this iteration)" marker on Phase 0 even though the project is in Phase 1, and it restates deliverable lists plus inline ADR references that STATUS owns.

Resolution (information-architecture direction chosen with the user, "#1"): the README keeps only stable human orientation. Thin the README roadmap table so each phase's cell is one concise sentence of phase *intent*, drop the granular deliverable enumerations, the inline ADR citations, and the "(this iteration)" status marker, and add a one-line pointer to STATUS.md (single source of truth for live phase/milestone status) and the project-manager dashboard (the rendered live roadmap) for current status and detail. Status and milestones never live in the README; they live in STATUS frontmatter and the dashboard. No other README section changes.

This is a documentation deliverable on the repo-root human orientation file: it routes through the dispatched-worker flow.

## Activity log

- 2026-06-10: Created and picked up in the same session. Surfaced from a user question during the COR-T-020 wrap-up: the README roadmap duplicates STATUS frontmatter (phase/deliverable prose) and had drifted (stale "(this iteration)" on Phase 0). Verified the README roadmap carries no status of its own (it already defers live status to STATUS per README lines 13/42); the duplication is phase/deliverable prose. Decision pinned with the user: option #1, thin the README roadmap to stable one-line intents + a pointer to STATUS/dashboard; STATUS frontmatter remains the structured SSOT. Queued for the dispatched-worker flow.
