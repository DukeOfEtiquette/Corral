# Corral - AI infrastructure: {{DEPT_NAME}} department workspace

This file is the operating rules for AI agents working inside the `ai-infrastructure/{{DEPT_SLUG}}/` department workspace. It supplements the global rules in the repo-root `CLAUDE.md` (which remains authoritative for Agent Discipline, writing style, secrets, documentation placement, and the two-domains framing). When a rule here conflicts with the global file, surface it to the user; do not silently resolve it.

The coordinator workspace for all AI-infrastructure work is `ai-infrastructure/project-manager/`. Per ADR-027, the project-manager coordinator has write authority over this workspace for coordination purposes: status alignment, cross-references, decision propagation, and consistency fixes.

## Path conventions

There are two path-resolution domains inside this workspace:

- Inside this workspace (`ai-infrastructure/{{DEPT_SLUG}}/`), `./X` resolves workspace-relative. References to workspace-local content (`./decisions/`, `./STATUS.md`, `./OBSERVATIONS.md`) use `./X` and need no change.
- References to the root-staying shared tree (`.claude/`, `docs/ai-orchestration/`, the repo-root `CLAUDE.md` / `README.md`) and to the coordinator (`ai-infrastructure/project-manager/`) use BARE paths with no `./` prefix: for example `docs/ai-orchestration/roles/WORKER-ROLE.md` or `ai-infrastructure/project-manager/STATUS.md`.

## Operated by

This workspace is operated by the **`/{{DEPT_SLUG}}-orchestrator`** slash command. The command adopts the shared `ORCHESTRATOR-ROLE.md` (at `docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md`) by reference; there is no per-department copy of the role doc (ADR-029).

Deliverable work in this workspace executes through the universal dispatched **`worker-agent`** (at `.claude/agents/worker-agent.md`, Sonnet, foreground), dispatched by the `/{{DEPT_SLUG}}-orchestrator` command via the Task tool (ADR-028). There is no `/{{DEPT_SLUG}}-worker` command and no per-department worker-agent; the single universal worker execution path is shared across all workspaces.

The universal checker fleet (ADR-023) gates every worker run: the `worker-prelaunch-checker` and `worker-close-checker` subagents are dispatched by the orchestrator (not by the worker). A slot is reserved for an optional department-scoped checker that can layer beside the universal pair if this department's work warrants it; none is created by the scaffold recipe.

## Tasks

This workspace has NO own `tasks/` directory. All work items for this department live in the shared coordinator task pool at `ai-infrastructure/project-manager/tasks/`, tagged with the `dept:{{DEPT_SLUG}}` label (ADR-027 Fork B). Do not invent a parallel task system here.

## Decisions

Binding choices specific to this department get an ADR in `./decisions/` (conventions in `./decisions/README.md`). Cross-cutting decisions that affect the whole project belong in `ai-infrastructure/project-manager/decisions/`.

## The MCP seam

Per `ai-infrastructure/project-manager/decisions/ADR-004-mcp-server-as-llm-contract.md`: once the MCP server exists, LLM agents read and mutate tracker data ONLY through it. No direct database access, no raw API calls, no CLI workarounds. Until then, the interim seam is the markdown task convention in `ai-infrastructure/project-manager/tasks/`.

## Run policy

docker compose is the only supported run path once code exists (`ai-infrastructure/project-manager/decisions/ADR-003-docker-compose-runtime.md`). Do not assume host-installed Python or Node; propose compose commands.

## Pointers

| File | What it is |
|---|---|
| `./README.md` | Department charter for humans |
| `./STATUS.md` | Current phase and next step for this department |
| `./OBSERVATIONS.md` | Append-only pattern log, `{{DEPT_OBS_PREFIX}}-NN` IDs |
| `./decisions/` | Department-local ADRs |
| `ai-infrastructure/project-manager/tasks/` | Shared task pool (filter by `dept:{{DEPT_SLUG}}`) |
