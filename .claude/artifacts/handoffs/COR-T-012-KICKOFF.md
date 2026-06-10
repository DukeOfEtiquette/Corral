# Execute the ai-infrastructure restructure (move root orchestration into ai-infrastructure/project-manager/)

## Target

This is AI-infrastructure (domain 2, ADR-005) work for task COR-T-012. You physically restructure the repo per the Decision section of `./decisions/ADR-027-ai-infrastructure-workspace-structure.md`, as amended by `./decisions/ADR-029-shared-role-docs-stay-at-repo-root.md`. You `git mv` the root orchestration content into `ai-infrastructure/project-manager/`, split the current `CLAUDE.md` into a thin repo-root file plus a workspace operating file, author a workspace README, and run a bidirectional two-domain path-reference sweep. The `.claude/` tree and `docs/ai-orchestration/` stay at the repo root as shared infrastructure. No new ADRs, no tooling, no placeholder directories. Every decision below is pinned by the Orchestrator; do not re-derive any of them.

The artifact in scope is the repo's physical layout and its path references. Read the references in the order listed before executing the move, because they describe paths in their current (pre-move) form.

## Decisions resolved by the Orchestrator

**D1 - The moves (use `git mv` to preserve history).** Move each of these from the repo root into `ai-infrastructure/project-manager/`, using `git mv` so git records renames rather than delete-plus-add:

- `CLAUDE.md` -> `ai-infrastructure/project-manager/CLAUDE.md` (then split per D3)
- `STATUS.md` -> `ai-infrastructure/project-manager/STATUS.md`
- `OBSERVATIONS.md` -> `ai-infrastructure/project-manager/OBSERVATIONS.md`
- `decisions/` (the entire directory: all ADRs and its `README.md`, as-is) -> `ai-infrastructure/project-manager/decisions/`
- `tasks/` (the entire directory: the shared COR-T pool, `.next-task-id`, `README.md`, and all backlog / in-progress / blocked / done subtrees) -> `ai-infrastructure/project-manager/tasks/`
- `docs/architecture/OVERVIEW.md` -> `ai-infrastructure/project-manager/docs/architecture/OVERVIEW.md` (this is the ONLY file moved out of `docs/`; create the nested `docs/architecture/` path under the workspace)

Source: ADR-027 Decision (Forks B and C) plus COR-T-012 decision 1. Note: COR-T-012's own task file lives inside `tasks/in-progress/` and moves with the tree; that is expected. Do NOT edit, transition, or open any task file for modification. Task transitions are Orchestrator-only (`./docs/ai-orchestration/roles/WORKER-ROLE.md`, "Universal conventions"). You move the `tasks/` tree wholesale and leave every file's content untouched.

**D2 - What stays at the repo root (do NOT move).** `.claude/` (commands, agents, specs, and `artifacts/`), `docs/ai-orchestration/` (the shared role docs `ORCHESTRATOR-ROLE.md` / `WORKER-ROLE.md`), `docs/README.md` (the docs navigation index), and `README.md` (human orientation). Source: ADR-029 plus COR-T-012 decision 2.

**D3 - CLAUDE.md split (no content dropped; every rule in the current `CLAUDE.md` lands in exactly ONE of the two files).**

- Write a NEW thin repo-root `CLAUDE.md` holding the truly-global rules: writing style (no em dashes), Secrets / no-secrets, `.md` documentation placement (with the sanctioned-location paths updated for the new structure), the "two domains" framing (ADR-005), and the Agent Discipline section. Agent Discipline's full authoritative copy STAYS here. Agent Discipline applies to every agent in the repo (orchestrators, workers, validators, all subagents, and future web-app agents), so it is truly-global and remains authoritative at the root, so the root-staying role docs keep pointing to `./CLAUDE.md` for it without a rewrite. Add brief orientation pointers into `ai-infrastructure/` (the AI-infra workspace, this restructure's product) and the future `app/` (named in PROSE ONLY; do not create the directory).
- The moved `ai-infrastructure/project-manager/CLAUDE.md` holds the AI-infrastructure operating specifics: the MCP seam, Tasks, Decisions, Run policy, Path conventions, and the Pointers table. ADD to it the coordinator-write-authority note. ADR-027 (Consequences, "Coordinator write authority established") says to document the coordinator's write authority when the workspace is stood up; this is that moment. The project-manager coordinator is the workspace that owns the STATUS / OBSERVATIONS / decisions / tasks writes and may create and edit files inside sibling department workspaces it coordinates.

Source: COR-T-012 decision 3, with the Agent Discipline placement pinned by the Orchestrator (decision 3's "Agent Discipline pointer" reads as: the authoritative section stays at root).

**D4 - Two-domain path-reference sweep (BIDIRECTIONAL).** After the move there are two path-resolution domains. Sweep both.

- (a) **Inside moved workspace files** (`project-manager/CLAUDE.md`, the moved ADRs under `project-manager/decisions/`, `project-manager/docs/architecture/OVERVIEW.md`, the moved `STATUS.md` / `OBSERVATIONS.md`, `project-manager/tasks/README.md`): `./X` now resolves workspace-relative. Their existing references to OTHER moved content (`./decisions/...`, `./tasks/...`, `./STATUS.md`, `./OBSERVATIONS.md`) need NO change (they moved together). A reference to the NON-moved shared tree must be rewritten to a BARE path with no `./` prefix, meaning repo-root: `./.claude/...` -> `.claude/...`, `./docs/ai-orchestration/...` -> `docs/ai-orchestration/...`, `./README.md` -> `README.md`, `./docs/README.md` -> `docs/README.md`. Concretely: the moved `STATUS.md` references the role docs and the root README; several moved ADRs (for example ADR-009, ADR-023, ADR-028) reference `.claude/` agents/specs and the role docs; rewrite those to bare paths. Rewriting a path reference inside an append-only ADR is a mechanical path fix authorized by decision 4(a), not a decision change; append-only is respected.
- (b) **Inside root-staying files** (the new thin root `CLAUDE.md`, `README.md`, `docs/README.md`, every `./.claude/commands/*.md`, `./.claude/agents/*.md`, `./.claude/agents/specs/*.md`, and the root role docs `./docs/ai-orchestration/roles/*.md`): `./X` resolves repo-root-relative, so references to MOVED content must be rewritten to `./ai-infrastructure/project-manager/...` (for example `./decisions/ADR-NNN` -> `./ai-infrastructure/project-manager/decisions/ADR-NNN`, `./STATUS.md` -> `./ai-infrastructure/project-manager/STATUS.md`, `./docs/architecture/OVERVIEW.md` -> `./ai-infrastructure/project-manager/docs/architecture/OVERVIEW.md`). References to root-staying content stay unchanged: the role docs remain at `./docs/ai-orchestration/roles/...` (so the `worker-agent` bootstrap path is UNCHANGED), `.claude/` references stay, `.env` / `.env.example` references stay.
- **`./CLAUDE.md` references are split-routed** (a consequence of D3). In a root-staying file, a `./CLAUDE.md` reference that cites a rule which MOVED to the PM file (Run policy, MCP seam, Tasks, Decisions, Path conventions) is rewritten to `./ai-infrastructure/project-manager/CLAUDE.md`; one that cites a rule which STAYED at root (writing style, Agent Discipline, `.md` placement, Secrets, two-domains framing) keeps `./CLAUDE.md`. Read the specific citation to route each one; do not blanket-rewrite `./CLAUDE.md` references.
- The PM `CLAUDE.md` "Path conventions" section must DOCUMENT this two-domain rule: workspace-relative `./` inside the workspace; a bare path (no `./`) means the repo-root shared tree.

Source: COR-T-012 decision 4 plus the Orchestrator's split-routing and bidirectional-sweep operationalization.

**D5 - `README.md` is in scope (user-confirmed 2026-06-09), mechanical rewrite only.** `README.md` stays at the repo root and has references to moved content. Rewrite its references to moved content (`./decisions/...`, `./STATUS.md`, `./OBSERVATIONS.md`, `./tasks/...`, `./docs/architecture/OVERVIEW.md`) to `./ai-infrastructure/project-manager/...`. LEAVE unchanged its references to root-staying files: `./CLAUDE.md` (the thin root file still exists; the human-facing "agents read ./CLAUDE.md" pointer and the pointer-table `./CLAUDE.md` row stay valid) and `.env` / `.env.example`. Make no structural or prose changes beyond the path rewrites.

**D6 - No empty placeholder directories.** Do NOT create `app/`, `templates/department/`, or `dashboard/` (git does not track empty directories; these are built by COR-T-013 / COR-T-014). The thin root `CLAUDE.md` names `app/` as future in prose only.

**D7 - Author `ai-infrastructure/project-manager/README.md`.** A short workspace charter stating the coordinator workspace's purpose: the project-manager coordinator that holds STATUS / OBSERVATIONS / decisions / tasks and orchestrates AI-infra work, per the ADR-027 tree. Keep it brief.

**D8 - No new `workspace:` frontmatter field** on any moved file. ADR-027 does not require it; avoid schema churn.

**D9 - Existing handoff artifacts are out of scope.** Do NOT rewrite path references inside `.claude/artifacts/handoffs/*` (the historical kickoff / report pairs for done tasks COR-T-002 through COR-T-006 and COR-T-011). They stay at root as historical records; rewriting them would be revisionist. They are not navigation.

## Deliverables

1. The moved tree under `ai-infrastructure/project-manager/` (`CLAUDE.md`, `STATUS.md`, `OBSERVATIONS.md`, `decisions/`, `tasks/`, `docs/architecture/OVERVIEW.md`), via `git mv` with history preserved.
2. A new thin repo-root `CLAUDE.md` (truly-global rules plus orientation pointers).
3. `ai-infrastructure/project-manager/CLAUDE.md` (AI-infra operating specifics plus the coordinator-write-authority note), produced by splitting the moved `CLAUDE.md`.
4. `ai-infrastructure/project-manager/README.md` (workspace charter).
5. The completed bidirectional two-domain path-reference sweep across moved files and root-staying files per D4 and D5.

## Files in scope

- Moves (`git mv`): `CLAUDE.md`, `STATUS.md`, `OBSERVATIONS.md`, `decisions/`, `tasks/`, `docs/architecture/OVERVIEW.md`.
- New files: the thin repo-root `CLAUDE.md`, `ai-infrastructure/project-manager/README.md`.
- Path-reference rewrites (root-staying side, D4b plus D5): `README.md`, `docs/README.md`, `./.claude/commands/*.md`, `./.claude/agents/*.md`, `./.claude/agents/specs/*.md`, `./docs/ai-orchestration/roles/*.md`.
- Path-reference rewrites (moved side, D4a): inside the moved files where they reference root-staying shared content (`project-manager/CLAUDE.md`, the moved `STATUS.md` / `OBSERVATIONS.md`, the moved ADRs, `project-manager/docs/architecture/OVERVIEW.md`, `project-manager/tasks/README.md`).

## Files out of scope

- `.claude/` does NOT move (commands, agents, specs, and `artifacts/` all stay at the repo root).
- `docs/ai-orchestration/` does NOT move (shared role docs stay at root, ADR-029).
- `.claude/artifacts/handoffs/*` historical kickoff / report pairs: not rewritten (D9).
- Task file content: the `tasks/` tree is moved wholesale, but NO task file is edited or transitioned (Orchestrator-only).
- No new ADRs, no tooling or scripts, no placeholder directories (`app/`, `templates/department/`, `dashboard/`), no frontmatter-schema changes.
- No web-app-ADR split is in scope: there is nothing for this task to split, because no web-app ADRs exist yet and no path reference in scope points to a web-app-ADR file, so the bidirectional sweep has no web-app-ADR target to touch. The web-app departments and their ADRs are created lazily later under ADR-027 Fork C; that future creation is not this task's concern and requires no action here. Verifying the absence (no web-app-ADR file appears among the moved or root-staying files you sweep) is the full extent of this item's bearing on the task.

## References

Read these in order. The paths are current (pre-move) because you read them before executing the move.

- `./decisions/ADR-027-ai-infrastructure-workspace-structure.md` - the restructure spec; its Decision section governs the move.
- `./decisions/ADR-029-shared-role-docs-stay-at-repo-root.md` - amends ADR-027; the role docs and `.claude/` stay at root.
- `./decisions/ADR-005-two-domains-ai-first.md` - the two-domains separation this restructure enforces.
- `./tasks/in-progress/COR-T-012-execute-ai-infrastructure-restructure.md` - the task file; its "Resolved decisions" section is the source these pins came from.

## Related tasks and ADRs

- ADR-027 - the workspace-structure spec; the restructure this task executes.
- ADR-029 - amends ADR-027: shared role docs and `.claude/` stay at the repo root.
- ADR-005 - the two-domain separation the restructure enforces.
- ADR-024 - handoff artifacts live in `.claude/`, which stays at root (informs D9 and the report path).
- ADR-028 - the dispatched `worker-agent` whose root `docs/ai-orchestration/roles/WORKER-ROLE.md` bootstrap path ADR-029 deliberately preserves (so D4b leaves that path unchanged).
- COR-T-013 - the follow-on that creates `templates/department/` and `/create-department`; why D6 forbids creating that placeholder now.
- COR-T-014 - the follow-on that creates `dashboard/`; same reason.

## STATUS deltas

Apply universal STATUS hygiene to the MOVED `ai-infrastructure/project-manager/STATUS.md` (bump `last_updated`, append a `recent_updates` entry describing the restructure execution), per `./docs/ai-orchestration/roles/WORKER-ROLE.md`, "Wrap-up STATUS hygiene". Task-specific deltas beyond that:

1. Update the "Next step" paragraph to reflect that the ai-infrastructure restructure has been executed and the new `ai-infrastructure/project-manager/` workspace layout is in place, with COR-T-013 and COR-T-014 as the remaining ADR-027 follow-ons.
2. Apply the D4(a) bare-path rewrite to STATUS.md's own references to root-staying content: the `./docs/ai-orchestration/roles/...` and `./README.md` references become bare `docs/ai-orchestration/roles/...` and `README.md`.

Do NOT mark COR-T-012 done in STATUS (the Orchestrator closes it at the commit gate). The `recent_updates` entry states the restructure was executed, factually.

## Hard rules

- **`git mv` only for the moves.** Every move in D1 uses `git mv` so git records a rename. Do not delete-and-recreate; that loses history.
- **Content preservation across the CLAUDE.md split (D3).** Every rule in the current `CLAUDE.md` must land in exactly one of the two files. Nothing is dropped and nothing is duplicated across the two. Agent Discipline lands in the thin root file.
- **Append-only ADRs are respected.** The only edits to moved ADRs are the mechanical bare-path rewrites authorized by D4(a). Do not alter any ADR's decision content.
- **No task-file edits.** The `tasks/` tree moves wholesale; no file inside it is opened for modification, transitioned, or re-slugged.
- **Route each `./CLAUDE.md` reference by its citation (D4).** Do not blanket-rewrite. A reference is rewritten to the PM file only when it cites a rule that moved to the PM file; otherwise it stays as `./CLAUDE.md`.

## Verification expectations (for the closing report's single acceptance gate)

- `git mv` was used for all moves (git records renames, not delete-plus-add); history is preserved.
- The full moved tree exists under `ai-infrastructure/project-manager/`, and the repo root no longer contains `STATUS.md`, `OBSERVATIONS.md`, `decisions/`, `tasks/`, or `docs/architecture/` (the root retains the new thin `CLAUDE.md`, `README.md`, `docs/ai-orchestration/`, `docs/README.md`, and `.claude/`).
- The CLAUDE.md split dropped no content: every rule from the original `CLAUDE.md` is present in exactly one of the two files, and Agent Discipline is in the root file.
- No root-staying file contains a `./`-prefixed reference to moved content that now resolves to a non-existent path; every rewritten reference resolves to an existing file. Verify representative references resolve, including a split-routed `./CLAUDE.md` example (one rewritten to the PM file and one left at root).
- No moved file references the shared root tree via a `./docs/ai-orchestration/...`, `./.claude/...`, or `./README.md` path (those are now bare).
- No placeholder directories were created, no web-app-ADR file was touched (none exists to touch), and `.claude/artifacts/handoffs/*` are unchanged.

## Worker pointer

You are the dispatched `worker-agent` (ADR-028). Universal worker conventions live in `./docs/ai-orchestration/roles/WORKER-ROLE.md`; read it for the report shape, the dual-channel write, and the universal conventions. The closing report is written to `./.claude/artifacts/handoffs/COR-T-012-KICKOFF-REPORT.md` per WORKER-ROLE.md, "Report shape" (dual-channel: print to chat and write to file). Note: the report path is under `.claude/`, which does not move, so this path is stable across the restructure.
