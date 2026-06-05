# Corral

A self-hosted, narrow-scope GitHub Issues clone: a server that tracks issues in its own database, and a client that renders them as kanban boards. Multiple board views can be defined over the same database, each with its own label filter, so for example every department can have its own board over the shared issue pool.

## Why

This replaces a working but rate-limited setup: LLM orchestrator/worker agents managing development tasks through GitHub Issues + a Projects kanban board via a GitHub MCP server. The feature surface actually used is small (issues, labels, kanban views), so this project rebuilds exactly that, self-hosted, with no external rate limits. GitHub's quality-of-life automation (e.g. `closes #N` moving an issue to done) is deliberately out of scope for v1. See `./decisions/ADR-001-self-hosted-issue-tracker-scope.md`.

A defining trait: this is an **AI-first project**. The AI infrastructure that builds the web app (orchestrators, workers, agents, specs) is a first-class domain alongside the app itself, and it gets built first (`./decisions/ADR-005-two-domains-ai-first.md`). Humans read this file; agents read `./CLAUDE.md`.

## Status

**Phase 1: AI infrastructure.** Orchestration roles, agents, and commands exist; no application code yet. Current progress always lives in `./STATUS.md`.

## Architecture at a glance

Four docker compose services: Postgres, a FastAPI backend, a React kanban client, and a FastMCP server that is the only path by which LLM agents touch tracker data. Full picture: `./docs/architecture/OVERVIEW.md`.

## Tech stack

- **Backend**: Python FastAPI + Postgres
- **Frontend**: React
- **LLM seam**: Python FastMCP server
- **Runtime**: Docker containers under docker compose

Rationale: `./decisions/ADR-002-tech-stack.md`.

## Getting started

> Not yet available: no code exists. This section records the intended flow.

1. Generate an admin password hash locally.
2. Copy `.env.example` to `.env`; set `ADMIN_EMAIL` and `ADMIN_PASSWORD_HASH` (`.env` is gitignored; see `./decisions/ADR-006-admin-bootstrap-env-hash.md`).
3. `docker compose up`. The server seeds the admin user on first boot.
4. Log in as admin; invite users by email from the admin page. Invites are single-use links you share manually (`./decisions/ADR-007-invite-only-tokens-no-smtp.md`).

## Repository layout

| Path | Contents |
|---|---|
| `./CLAUDE.md` | Operating rules for AI agents |
| `./STATUS.md` | Current phase (single source of truth) |
| `./OBSERVATIONS.md` | Append-only pattern log |
| `./decisions/` | ADRs: accepted decisions and queued open questions |
| `./docs/` | Architecture and (later) AI-orchestration docs |
| `./tasks/` | Project tasks, markdown convention (`./tasks/README.md`) |
| `app/` (future) | Web-app services |

## Roadmap

| Phase | Deliverable |
|---|---|
| **0. Bootstrap** (this iteration) | Docs, decision records, task convention |
| **1. AI infrastructure** | Orchestrator/worker role docs (COR-T-001); resolve blocking ADRs: schema (ADR-012), API shape (ADR-010), MCP surface (ADR-013), auth (ADR-011); department structure (ADR-021) |
| **2. MCP + DB core** | Postgres schema, FastMCP server with house rules, admin seeding. First moment the app can store an issue |
| **3. API** | FastAPI endpoints, auth/sessions, invite tokens, migrations (ADR-014) |
| **4. Kanban UI** | React multi-view board with per-view label filters (ADR-015, 017, 018), admin page |
| **5. Dogfood milestone** | Import `./tasks/` markdown into the app via the MCP server; the project tracks itself; markdown tasks frozen (`./decisions/ADR-008-bootstrap-tasks-dogfood-milestone.md`). Multi-user/agent concurrency (ADR-020) becomes live here |

## How decisions are recorded

Every binding choice is an ADR in `./decisions/`; open questions are queued there as `pending` ADRs so nothing important is decided implicitly. Conventions: `./decisions/README.md`.
