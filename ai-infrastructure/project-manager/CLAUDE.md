# Corral - AI infrastructure: project-manager workspace

This file is the operating rules for AI agents working inside the `ai-infrastructure/project-manager/` coordinator workspace. It supplements the global rules in the repo-root `CLAUDE.md` (which remains authoritative for Agent Discipline, writing style, secrets, documentation placement, and the two-domains framing). When a rule here conflicts with the global file, surface it to the user; do not silently resolve it.

## Path conventions

After the COR-T-012 restructure, there are two path-resolution domains:

- Inside this workspace (`ai-infrastructure/project-manager/`), `./X` resolves workspace-relative. References to sibling content that moved with this workspace (`./decisions/`, `./tasks/`, `./STATUS.md`, `./OBSERVATIONS.md`, `./docs/architecture/`) use `./X` and need no change.
- References to the root-staying shared tree (`.claude/`, `docs/ai-orchestration/`, the repo-root `README.md`) use a BARE path with no `./` prefix: for example `docs/ai-orchestration/roles/WORKER-ROLE.md` or `.claude/agents/worker-agent.md`. A bare path without a `./` prefix means repo-root-relative shared infrastructure.

## Coordinator write authority

The project-manager is the coordinator workspace for all AI-infrastructure work in this repo. It owns the canonical STATUS, OBSERVATIONS, decisions (ADRs), and tasks writes. It may also create and edit files inside sibling department workspaces (`ai-infrastructure/<dept>/`) for coordination purposes: status alignment, cross-references, decision propagation, and consistency fixes. This mirrors rogue's coordinator-write grant and is documented here per ADR-027 (Consequences, "Coordinator write authority established").

## The MCP seam

Per `./decisions/ADR-004-mcp-server-as-llm-contract.md`: once the MCP server exists, LLM agents read and mutate tracker data ONLY through it. No direct database access, no raw API calls, no CLI workarounds. Until then, the interim seam is the markdown task convention in `./tasks/`.

## Tasks

The coordinator's own work items live in `./tasks/` (COR-T-NNN IDs) per `./tasks/README.md`. Per ADR-031, every department also owns its own `tasks/` tree at `ai-infrastructure/<dept>/tasks/` with its own ID prefix; the coordinator write authority (above) covers coordination writes into those trees. Do not invent parallel TODO systems (scratch lists, inline TODO sections, separate trackers). If it is work, it is a task file in the appropriate workspace's tree.

## Decisions

Binding choices get an ADR in `./decisions/` (conventions in `./decisions/README.md`). Open questions worth deciding get a `pending` ADR that reserves a number and frames the question, not an informal note. ADRs are append-only.

## Run policy

docker compose is the only supported run path once code exists (`./decisions/ADR-003-docker-compose-runtime.md`). Do not assume host-installed Python or Node; propose compose commands.

## Pointers

| File | What it is |
|---|---|
| `README.md` | Human orientation, roadmap (repo root) |
| `./STATUS.md` | Current phase, single source of truth; update at end of any session that makes progress |
| `./OBSERVATIONS.md` | Append-only pattern log, `COR-NN` IDs |
| `./decisions/` | All ADRs, accepted and pending |
| `docs/README.md` | Docs navigation (repo root) |
| `./tasks/README.md` | Task convention (canonical, markdown era; per-workspace since ADR-031) |
