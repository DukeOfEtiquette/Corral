# Corral

Self-hosted, narrow-scope GitHub Issues clone: an issue database with multi-view kanban boards, plus an MCP server as the only seam for LLM agents. This file is the operating rules for AI agents working in this repo. Humans should start at `./README.md`.

## The two domains

Per `./decisions/ADR-005-two-domains-ai-first.md`, this repo holds two distinct bodies of work:

1. **The web app**: FastAPI + Postgres + React + FastMCP services (none built yet; target shape in `./docs/architecture/OVERVIEW.md`).
2. **The AI infrastructure**: the orchestrators, workers, agents, specs, and task system that build and maintain the web app. An agent that designs tests is a domain-2 artifact; the tests it writes are domain-1 artifacts.

AI infrastructure is developed first. When picking up work, know which domain you are in.

## Global rules

### Agent Discipline

**IMPORTANT**: Verify before asserting. Applies to every AI agent in this repo (orchestrators, workers, validators, user-facing sessions, all subagents).

Never present a claim about repository state as fact unless you have verified it in the current session. State claims include: file existence, file location, file contents, symbol presence, command results, test status, git history, environment configuration. If the claim is load-bearing for a decision you are about to surface to the user, verify it before drafting the message.

- Before asserting state, run the cheapest tool that proves it (`ls`, `find`, `grep`, `Read`, `git log`, `git status`) and cite the result, not memory or inference.
- If verification is genuinely expensive, say so explicitly: "I have not verified X; my working assumption is..." and propose the verification step.
- Claims pulled from session memory, prior sessions, or model priors are hypotheses, not facts; re-verify before asserting.
- "I think" / "probably" does not launder an unverified claim. If it is load-bearing, verify; if not, drop it.

This is the authoritative copy for this repo; role docs (Phase 1) reference it, they do not duplicate it.

### The MCP seam

Per `./decisions/ADR-004-mcp-server-as-llm-contract.md`: once the MCP server exists, LLM agents read and mutate tracker data ONLY through it. No direct database access, no raw API calls, no CLI workarounds. Until then, the interim seam is the markdown task convention in `./tasks/`.

### Tasks

All project work items live in `./tasks/` per `./tasks/README.md`. Do not invent parallel TODO systems (scratch lists, inline TODO sections, separate trackers). If it is work, it is a task file.

### Decisions

Binding choices get an ADR in `./decisions/` (conventions in `./decisions/README.md`). Open questions worth deciding get a `pending` ADR that reserves a number and frames the question, not an informal note. ADRs are append-only.

### Secrets

Per `./decisions/ADR-006-admin-bootstrap-env-hash.md`: deployment credentials live in gitignored `.env` files only. Never write secrets, password hashes, or `.env` contents into any tracked file, log, or artifact. A committed `.env.example` may document variable names only.

### Documentation placement

All `.md` files go in sanctioned locations: the repo-root docs files (`CLAUDE.md`, `README.md`, `STATUS.md`, `OBSERVATIONS.md`), `./decisions/`, `./docs/`, and `./tasks/`. Never scatter `.md` files into source directories. Navigation index: `./docs/README.md`. Exception per ADR-023 and ADR-024: `./.claude/` holds AI-infrastructure artifacts (slash commands, agent definitions, agent specs), git-tracked handoff artifacts (kickoffs, worker reports) in `./.claude/artifacts/handoffs/`, and gitignored scratch in `./.claude/artifacts/tmp/`; these are domain-2 working files, not documentation.

### Writing style

No em dashes in files. Use a regular hyphen, comma, colon, or rephrase. Em dashes in conversation responses are acceptable; in files they are not.

### Run policy

docker compose is the only supported run path once code exists (`./decisions/ADR-003-docker-compose-runtime.md`). Do not assume host-installed Python or Node; propose compose commands.

### Path conventions

Use repo-root-relative paths with a `./` prefix (e.g. `./decisions/ADR-001-self-hosted-issue-tracker-scope.md`), not absolute paths.

## Pointers

| File | What it is |
|---|---|
| `./README.md` | Human orientation, roadmap |
| `./STATUS.md` | Current phase, single source of truth; update at end of any session that makes progress |
| `./OBSERVATIONS.md` | Append-only pattern log, `COR-NN` IDs |
| `./decisions/` | All ADRs, accepted and pending |
| `./docs/README.md` | Docs navigation |
| `./tasks/README.md` | Task convention (canonical, markdown era) |
