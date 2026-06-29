# Corral

Self-hosted, narrow-scope GitHub Issues clone: an issue database with multi-view kanban boards, plus an MCP server as the only seam for LLM agents. This file is the repo-root global operating rules for AI agents working anywhere in this repo. Humans should start at `./README.md`. The project's end goal (the portable project-manager plugin destination) is recorded in `./END-GOAL.md`.

## The two domains

Per `./ai-infrastructure/project-manager/decisions/ADR-005-two-domains-ai-first.md`, this repo holds two distinct bodies of work:

1. **The web app**: FastAPI + Postgres + React + FastMCP services (none built yet; target shape in `./ai-infrastructure/project-manager/docs/architecture/OVERVIEW.md`).
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

### Secrets

Per `./ai-infrastructure/project-manager/decisions/ADR-006-admin-bootstrap-env-hash.md`: deployment credentials live in gitignored `.env` files only. Never write secrets, password hashes, or `.env` contents into any tracked file, log, or artifact. A committed `.env.example` may document variable names only.

### Documentation placement

All `.md` files go in sanctioned locations: the repo-root files (`CLAUDE.md`, `README.md`, `END-GOAL.md`, `GIT_WORKFLOW.md`), `./ai-infrastructure/project-manager/` (the AI-infrastructure workspace, its `CLAUDE.md`, `STATUS.md`, `OBSERVATIONS.md`, `decisions/`, `tasks/`, and `docs/architecture/`), `./docs/` (the shared AI-orchestration role docs and the navigation index), and sibling AI-infrastructure department workspaces created later under `./ai-infrastructure/`. Never scatter `.md` files into source directories. Navigation index: `./docs/README.md`. Exception per the ADRs on handoffs: `./.claude/` holds AI-infrastructure artifacts (slash commands, agent definitions, agent specs), git-tracked handoff artifacts (kickoffs, worker reports) in `./.claude/artifacts/handoffs/`, and gitignored scratch in `./.claude/artifacts/tmp/`; these are domain-2 working files, not documentation.

### Writing style

No em dashes in files. Use a regular hyphen, comma, colon, or rephrase. Em dashes in conversation responses are acceptable; in files they are not.

### Commit messages

Every commit subject leads with the task or ADR ID it advances (e.g. `COR-T-047:` or `ADR-039:`), followed by a specific one-line summary of what changed. This is owned-but-advisory (per ADR-035): it feeds the git-derived activity dashboard (ADR-039) and is the primary signal for `git log`-based recent-activity reads. If message quality erodes, the recorded re-open path is a commit-msg hook or checker subagent.

### Git workflow

This repo uses a mandatory worktree-per-session workflow (`./GIT_WORKFLOW.md`). It applies to every session, not only when sessions run concurrently. **Hard gate: the first file modification of any task MUST happen inside a dedicated worktree, never in the main checkout on `master`.** There is no exception for small, single-file, documentation, ADR, or coordination-surface edits, or for anything that feels "too minor to branch"; if it writes to a tracked file, it goes in a worktree. Only read-only research (reading files, `git log`, surveying state) happens in the main checkout. The instant a task turns into a change, switch to a worktree first (via `EnterWorktree` for interactive sessions, or via `git worktree add` for dispatched executor subagents, both branched from local `master` HEAD), then make every edit, commit, and compose test there, and integrate with `bin/git-integrate` from the main checkout. Un-wrapped merges into `master` are refused by the hooks in `.githooks/`. Read `./GIT_WORKFLOW.md` for the full flow before your first integration.

## Workspace orientation

| Workspace | Path | What lives there |
|---|---|---|
| AI infrastructure - coordinator | `./ai-infrastructure/project-manager/` | STATUS, OBSERVATIONS, decisions (ADRs), tasks, architecture overview; operating rules in its own `CLAUDE.md` |
| AI infrastructure - departments | `./ai-infrastructure/<dept>/` | lazily created per ADR-027 |
| Web app (future) | `app/` | Web-app services built by the lazily-created web-app departments |
| Shared infrastructure | `./.claude/`, `./docs/ai-orchestration/` | Commands, agents, specs, handoffs, and the universal role docs shared across all workspaces |
