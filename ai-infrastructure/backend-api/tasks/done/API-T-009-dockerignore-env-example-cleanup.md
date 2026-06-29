---
schema_version: 1
id: API-T-009
title: "remove now-moot .env.example exclusion lines from app/api/.dockerignore and app/db/.dockerignore"
status: done
labels: []
priority: P3
created: 2026-06-29
updated: 2026-06-29
---

## Description

Housekeeping cleanup surfaced during API-T-006 (item 1). When API-T-006 consolidated the env templates into a single tracked `app/.env.example` (deleting `app/api/.env.example` and `app/db/.env.example`), the `.env.example` exclusion lines in `app/api/.dockerignore` and `app/db/.dockerignore` became no-ops: the consolidated `app/.env.example` sits above both Docker build contexts (`app/api/` and `app/db/`), so it is never in either build context, and the per-service templates those lines referenced no longer exist. The lines are harmless but stale.

Remove the `.env.example` line from `app/api/.dockerignore` and `app/db/.dockerignore`, and confirm the Docker build context is unaffected (`docker compose -f app/docker-compose.yml build` still succeeds). Trivial; routes through the dispatched-worker flow (executor), or could be folded into a larger compose/docker cleanup pass.

Note: `app/db/.dockerignore` is database-department territory; coordinate or split per-department if preferred.

References:
- `app/api/.dockerignore`, `app/db/.dockerignore` (the stale exclusion lines)
- `app/.env.example` (the consolidated template, above both build contexts)
- `ai-infrastructure/backend-api/tasks/done/API-T-006-api-devex-hardening.md` (origin: the .env.example consolidation)

## Activity log

- 2026-06-29: Filed in backlog by the Backend API Orchestrator as a triaged follow-up from API-T-006 (item 1, the .env.example consolidation). The two `.dockerignore` files retain `.env.example` exclusion lines that are now no-ops. Standalone, P3, unlabelled per ADR-031.
- 2026-06-29: Picked up and executed orchestrator-direct (not dispatched) at the user's explicit request, given the trivial inert-config scope; worktree `api-t-009-dockerignore-cleanup`. Removed the `.env.example` line from `app/api/.dockerignore` and `app/db/.dockerignore`.
- 2026-06-29: Resolved and moved to done. Both `.dockerignore` edits committed in 8c7303c; verified inert (`docker compose -f app/docker-compose.yml build api migrate` both succeed, covering the `./api` and `./db` build contexts). This done-move follows in the next commit.
