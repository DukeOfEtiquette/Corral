---
schema_version: 1
id: COR-T-012
title: "Execute the ai-infrastructure restructure (move root orchestration into project-manager)"
status: backlog
labels: [dept:agent-development]
priority: P1
created: 2026-06-08
updated: 2026-06-09
---

## Description

Execute the physical restructure decided in `./decisions/ADR-027-ai-infrastructure-workspace-structure.md` (its Decision section is the spec), **as amended by `./decisions/ADR-029-shared-role-docs-stay-at-repo-root.md`**. `git mv` the root orchestration content into `ai-infrastructure/project-manager/`, write the two `CLAUDE.md` files plus a workspace README, and do the two-domain path-reference sweep. `.claude/` stays at the repo root as shared infrastructure. No new ADRs and no tooling are authored. Gated on ADR-027 and ADR-029 (both accepted).

## Resolved decisions (the anticipated decisions are resolved; pin these in the kickoff)

These were resolved on 2026-06-09 ahead of drafting the kickoff. The kickoff encodes them; the Worker does not re-derive them.

1. **What moves into `ai-infrastructure/project-manager/`:** `CLAUDE.md` (operating rules, split per item 3), `STATUS.md`, `OBSERVATIONS.md`, `decisions/` (all ADRs as-is, ADR-027 Fork C), `tasks/` (the shared `COR-T` pool, Fork B), and **only** `docs/architecture/OVERVIEW.md` -> `project-manager/docs/architecture/OVERVIEW.md`.
2. **What stays at the repo root (ADR-029):** `docs/ai-orchestration/` (the shared role docs `ORCHESTRATOR-ROLE.md` / `WORKER-ROLE.md` are universal infrastructure, like `.claude/`) and `docs/README.md` (the docs nav index; update its pointer to the moved OVERVIEW). The `.claude/` tree (commands, agents, specs, artifacts) stays at root. The repo-root `README.md` stays for humans.
3. **`CLAUDE.md` split:** write a thin repo-root `CLAUDE.md` that keeps the truly-global rules (writing style / no em dashes, no secrets, `.md` placement, the two-domains framing per ADR-005, the Agent Discipline pointer) plus orientation pointers into `ai-infrastructure/` and the future `app/`. Move the AI-infrastructure operating specifics (MCP seam, tasks, decisions, run policy, path conventions) into `ai-infrastructure/project-manager/CLAUDE.md`, and add to it the **coordinator-write-authority note** (ADR-027 says to document it when the workspace is stood up; this is that moment).
4. **Path-reference convention (the two-domain rule, ADR-027 path-convention consequence + ADR-029):** after the move there are two resolution domains. (a) **Inside moved workspace files** (`project-manager/CLAUDE.md`, the moved ADRs, `project-manager/docs/architecture/OVERVIEW.md`): `./X` resolves workspace-relative, so their existing `./decisions/`, `./tasks/`, `./STATUS.md` references need NO change (they moved together); a reference to the non-moved shared tree uses a bare `.claude/...` or `docs/ai-orchestration/...` (no `./` prefix) meaning repo-root. (b) **Inside root-staying files** (the thin root `CLAUDE.md`, every root `.claude/` agent/command/spec, and the root role docs): `./X` resolves repo-root-relative, so references to moved content must be rewritten to `./ai-infrastructure/project-manager/...` (e.g. `./decisions/ADR-NNN` -> `./ai-infrastructure/project-manager/decisions/ADR-NNN`, `./STATUS.md` -> `./ai-infrastructure/project-manager/STATUS.md`). The shared role docs stay at `./docs/ai-orchestration/roles/...`, so the `worker-agent` and other root `.claude/` files keep that bootstrap path unchanged.

   NOTE: this supersedes the original task framing that said to "rewrite refs to resolve workspace-relative within `project-manager/`"; that was written 2026-06-08 before ADR-029 kept the role docs and `.claude/` at root, and is wrong for root-staying files.
5. **No empty placeholders:** do NOT create `app/`, `templates/department/`, or `dashboard/` (git does not track empty dirs; they are built by COR-T-013 / COR-T-014). The thin root `CLAUDE.md` names `app/` as future in prose only.
6. **Author `ai-infrastructure/project-manager/README.md`:** a short workspace charter (the coordinator workspace's purpose), per the ADR-027 tree.
7. **No new `workspace:` frontmatter field** on moved files (rogue has one; ADR-027 does not require it; avoid schema churn).

## Files in scope

- Moves (`git mv`): `CLAUDE.md` (then rewrite), `STATUS.md`, `OBSERVATIONS.md`, `decisions/`, `tasks/`, `docs/architecture/OVERVIEW.md`.
- New: thin repo-root `CLAUDE.md`, `ai-infrastructure/project-manager/README.md`.
- Path-reference rewrite (root-staying, repo-root-relative): `docs/README.md`, every `./.claude/commands/*.md`, `./.claude/agents/*.md`, `./.claude/agents/specs/*.md`, and the root role docs `./docs/ai-orchestration/roles/*.md` where they reference moved content.

## Out of scope

- `.claude/` does not move. The shared role docs (`docs/ai-orchestration/`) do not move. No new ADRs, no tooling, no placeholders, no frontmatter-schema changes, no web-app-ADR split (deferred to lazy web-app department creation, ADR-027 Fork C).

## Related tasks and ADRs

- ADR-027 (workspace structure; the restructure spec) and ADR-029 (amends it: shared role docs stay at root).
- ADR-005 (two domains; the separation this restructure enforces).
- ADR-024 (handoff artifacts in `.claude/`, which stays at root).
- ADR-028 (the dispatched `worker-agent` whose root bootstrap path ADR-029 preserves).
- COR-T-013, COR-T-014 (the follow-on tasks that create `templates/department/` and `dashboard/`).

## Activity log

- 2026-06-08: Created in backlog. Named follow-on deliverable 1 of ADR-027 (COR-T-011); the AI-infrastructure structure's execution step.
- 2026-06-09: Anticipated decisions resolved (ADR-029 authored; remaining mechanical decisions pinned in "Resolved decisions" above). Corrected the stale path-rewrite framing in the original description. Task stays in backlog, ready for an orchestrator to pick up and route through the dispatched-worker flow.
