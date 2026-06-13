# Build the epic/phase file structure per ADR-037 (Phase A: trees, YAML files, bottom-up linkage)

## Target

This is AI-infrastructure work (ADR-005), task COR-T-044, executed in the `project-manager` coordinator workspace with one cross-tree touch into the `database` department. It is Phase A of the ADR-037 work-item storage cascade: stand up the new `epics/` and `phases/` file trees, materialize the epic and phase definition files, and stamp bottom-up `epic:` linkage onto the existing member task files. It does NOT change how the dashboard reads the roadmap; that is Phase B (the sibling task COR-T-045).

This task is a **faithful re-representation** of the current roadmap, not a re-curation. The epic membership encoded in the `roadmap:` block of `ai-infrastructure/project-manager/STATUS.md` is the source of truth, and every assignment you make is pinned below verbatim. You do not decide where any task belongs, you do not add epics, and you do not move tasks between epics.

## Decisions resolved by the Orchestrator

Every decision below is pinned. Do not re-derive, re-curate, or extend any of them; if the repo contradicts one (for example a member task ID resolves to a file that does not exist), escalate rather than guessing.

- **Scope is a faithful re-representation, not a re-curation.** The `roadmap:` block in `ai-infrastructure/project-manager/STATUS.md` is the authoritative source for epic membership. The complete mapping is pinned in this kickoff (see "Epic files" and "Bottom-up linkage" below). Do NOT decide where un-epic'd tasks belong, do NOT add epics, do NOT move tasks between epics. Cross-check the pinned mapping against the STATUS.md `roadmap:` block as you go; if any discrepancy appears between this kickoff and that block, stop and escalate rather than resolving it yourself.

- **Two-phase split: this is Phase A only.** Do NOT touch `ai-infrastructure/project-manager/dashboard/etl.py` and do NOT modify or remove the `roadmap:` block in `ai-infrastructure/project-manager/STATUS.md`. Those belong to Phase B (COR-T-045). Leaving the roadmap block and the ETL untouched is deliberate: the dashboard keeps reading the old block and stays working through Phase A.

- **New trees to create.**
  - `ai-infrastructure/project-manager/epics/` with a `.next-epic-id` file containing `6`.
  - `ai-infrastructure/database/epics/` with a `.next-epic-id` file containing `2`.
  - `ai-infrastructure/project-manager/phases/` (no counter file; phases are keyed by their number).
  - None of these trees gets a `backlog/ in-progress/ blocked/ done/` subdivision. Epic and phase status is a derived rollup (ADR-037 decision 7), so these files are definitions, not status-bearing objects. Do NOT create `ai-infrastructure/backend-api/epics/` (its only epic is deferred; see "Provisional epics deferred").

- **Phase files: pure YAML, one per phase, in `phases/`, filenames `phase-0.yml` through `phase-8.yml`.** Schema per file: `schema_version: 1`, `id: <n>` (the phase number), `title: "<title>"`, `description: "<concise line>"`, `order: <n>` (equal to the phase number; ADR-038's first-class ordering), and `legacy: true` on `phase-0` ONLY (omit `legacy` for phases 1 through 8). Content is taken verbatim from the current STATUS.md roadmap entries:
  - `phase-0`: title "Bootstrap", `legacy: true`, description "Repo init, ADR-001..009 accepted, the task convention seeded; predates the task system (ADR-008), exempt from epic/task decomposition per ADR-036."
  - `phase-1`: title "AI infrastructure", description "Orchestration role docs and the dispatch loop, the foundational ADRs, the department structure, and the dashboard."
  - `phase-2`: title "API + DB core", description "Postgres schema and migrations, FastAPI endpoints, auth/sessions, invite tokens, admin seeding."
  - `phase-3`: title "MCP server", description "FastMCP server as an authenticated API client; the agent seam goes live."
  - `phase-4`: title "Kanban UI", description "React multi-view board with per-view label filters, admin page."
  - `phase-5`: title "Dogfood milestone", description "Import the markdown tasks into the app via the MCP server; the project tracks itself; markdown tasks frozen."
  - `phase-6`: title "Remote deployment & concurrency", description "Deploy Corral to a remote server; prove multiple concurrent agent sessions work with no errors."
  - `phase-7`: title "Repoint ai-infrastructure at the remote", description "Switch this project's dashboard and task seam from local markdown to the remote Corral deploy."
  - `phase-8`: title "Extract the project-manager plugin", description "Generalize project-manager into a portable Claude Code plugin; dogfood Corral with it."

- **Epic files: pure YAML, one per epic.** Schema per file: `schema_version: 1`, `id: <PREFIX>-E-NNN`, `title: "<title>"`, `dept: <slug>`, `phase: <n>`, `description: "<concise one-line summary; you may base it on the title>"`, `adrs: [<numbers>]` (governing ADR numbers, informational, drawn from the roadmap entry). Epics do NOT list their tasks; linkage is bottom-up. Filenames are `<id>-<kebab-slug>.yml`. Materialize exactly these six epics (the only roadmap epics that currently have tasks), at the exact paths given:
  - `ai-infrastructure/project-manager/epics/COR-E-001-orchestration-system.yml`: title "Orchestration system: roles, dispatch loop, agents", `dept: project-manager`, `phase: 1`, `adrs: [23, 24, 28, 16, 32, 35]`.
  - `ai-infrastructure/project-manager/epics/COR-E-002-data-model-api-mcp-decisions.yml`: title "Data model, API & MCP decisions", `dept: project-manager`, `phase: 1`, `adrs: [10, 11, 12, 13, 18, 25, 26]`.
  - `ai-infrastructure/project-manager/epics/COR-E-003-department-workspace-structure.yml`: title "Department & workspace structure", `dept: project-manager`, `phase: 1`, `adrs: [21, 27, 30, 31]`.
  - `ai-infrastructure/project-manager/epics/COR-E-004-project-manager-dashboard.yml`: title "project-manager dashboard", `dept: project-manager`, `phase: 1`, `adrs: [27]`.
  - `ai-infrastructure/project-manager/epics/COR-E-005-project-orientation-docs.yml`: title "Project orientation docs", `dept: project-manager`, `phase: 1`, `adrs: [34]`.
  - `ai-infrastructure/database/epics/DB-E-001-database-schema-migrations.yml`: title "Database schema & migrations", `dept: database`, `phase: 2`, `adrs: [12, 14, 25, 26]`.

- **Bottom-up linkage: add an `epic: <id>` frontmatter field to exactly the task files named below, and nothing else.** Do not change their `status`, `updated`, `title`, `labels`, or activity log; this is a representational backfill, not a task event. Locate each file by its ID before editing (most are done tasks under `done/`). Membership per epic:
  - **COR-E-001**: COR-T-001, COR-T-007, COR-T-015, COR-T-016, COR-T-019, COR-T-035, COR-T-036, COR-T-039
  - **COR-E-002**: COR-T-002, COR-T-003, COR-T-004, COR-T-005, COR-T-008, COR-T-009, COR-T-010
  - **COR-E-003**: COR-T-006, COR-T-011, COR-T-012, COR-T-013, COR-T-023, COR-T-025
  - **COR-E-004**: COR-T-014, COR-T-017, COR-T-018, COR-T-020, COR-T-022, COR-T-026, COR-T-027, COR-T-029, COR-T-030, COR-T-031, COR-T-032, COR-T-033, COR-T-034, COR-T-037, COR-T-040
  - **COR-E-005**: COR-T-021, COR-T-038
  - **DB-E-001**: DB-T-001, DB-T-002

  The coordinator (`COR-T-*`) tasks live under `ai-infrastructure/project-manager/tasks/` (mostly `done/`). `DB-T-001` is under `ai-infrastructure/database/tasks/done/` and `DB-T-002` is under `ai-infrastructure/database/tasks/backlog/`. The `epic:` value is the epic ID (for example `epic: COR-E-001`).

- **Un-epic'd tasks are left alone.** Do NOT add an `epic:` field to COR-T-028, COR-T-041, COR-T-042, COR-T-043, COR-T-044, or COR-T-045. The current roadmap does not place them in any epic, so they remain standalone. Touch none of their frontmatter.

- **Provisional epics deferred.** Do NOT materialize the zero-task provisional epics (Phase 2's Backend API E2.2, and all epics of Phases 3 through 8). They are filed lazily when their work or department begins (ADR-021/ADR-031 lazy creation, the `>= 2`-task convention). Only the six epics named above get files in this phase.

- **tasks/README.md update.** Add an epic/phase convention to `ai-infrastructure/project-manager/tasks/README.md`: a new subsection describing the `epics/` tree (per workspace, each with its own `.next-epic-id`), the coordinator-owned `phases/` tree, the pure-YAML file format with the schemas above, the bottom-up linkage fields (`epic:` on tasks, `phase:` on epics), the department-prefixed epic ID scheme and numeric phase keys, and that these trees carry no status subdivision (status is a derived rollup). Cross-reference ADR-037 and ADR-038. Lightly refresh the existing Vocabulary section to note that Epics and Phases are now first-class files. Use bare repo-root-relative paths or workspace-relative `./` paths per the path convention in `ai-infrastructure/project-manager/CLAUDE.md` (this file resolves `./decisions/`, `./tasks/` workspace-relative).

## Deliverables

- `ai-infrastructure/project-manager/epics/` exists, containing the five epic YAML files (`COR-E-001` through `COR-E-005` at the exact filenames above) and a `.next-epic-id` file whose sole content is `6`.
- `ai-infrastructure/database/epics/` exists, containing the `DB-E-001-database-schema-migrations.yml` file and a `.next-epic-id` file whose sole content is `2`.
- `ai-infrastructure/project-manager/phases/` exists, containing nine phase YAML files (`phase-0.yml` through `phase-8.yml`), with `legacy: true` present only on `phase-0`.
- Each of the member task files listed under "Bottom-up linkage" carries an `epic: <id>` frontmatter field naming its epic, and nothing else in those files is changed.
- `ai-infrastructure/project-manager/tasks/README.md` updated with the epic/phase convention subsection and a refreshed Vocabulary note, cross-referencing ADR-037 and ADR-038.

## Files in scope

- `ai-infrastructure/project-manager/epics/` (new tree: five epic `.yml` files plus `.next-epic-id`)
- `ai-infrastructure/database/epics/` (new tree: one epic `.yml` file plus `.next-epic-id`)
- `ai-infrastructure/project-manager/phases/` (new tree: nine phase `.yml` files)
- The member task files listed under "Bottom-up linkage" (add only the `epic:` field to each)
- `ai-infrastructure/project-manager/tasks/README.md`
- `ai-infrastructure/project-manager/STATUS.md` (universal hygiene only: bump `last_updated`, append one `recent_updates` entry; the `roadmap:` block must stay byte-for-byte unchanged)

## Files out of scope

- `ai-infrastructure/project-manager/dashboard/etl.py` (Phase B, COR-T-045)
- The `roadmap:` block in `ai-infrastructure/project-manager/STATUS.md` (Phase B removes it; do NOT touch the block here; appending a `recent_updates` entry per universal hygiene is allowed, but the `roadmap:` block must be left byte-for-byte unchanged)
- `ai-infrastructure/project-manager/dashboard/RoadmapPanel.jsx` and all dashboard rendering (Phase B)
- `ai-infrastructure/backend-api/` (no `epics/` tree this phase; E2.2 deferred)
- The task files COR-T-028, COR-T-041, COR-T-042, COR-T-043, COR-T-044, COR-T-045 (leave their frontmatter untouched)
- Any new epics beyond the six named; any re-assignment of tasks between epics

## References

- `ai-infrastructure/project-manager/decisions/ADR-037-work-item-storage-representation.md`: the representation this task implements (file format, the `epics/` and `phases/` trees, bottom-up `epic:`/`phase:` linkage, no-status-directory rule). Read end-to-end first.
- `ai-infrastructure/project-manager/decisions/ADR-038-phase-as-first-class-view.md`: phase-as-View; the import target the phase files anticipate (and the source of the first-class `order` field on phases).
- `ai-infrastructure/project-manager/decisions/ADR-036-work-item-taxonomy.md`: containment, rollup, and cardinality semantics the trees encode.
- `ai-infrastructure/project-manager/decisions/ADR-031-per-department-task-trees.md`: per-workspace trees; this task adds an `epics/` sibling to each relevant workspace.
- `ai-infrastructure/project-manager/STATUS.md`: its `roadmap:` block is the source the pinned mapping is drawn from. Read-only here; cross-check the pinned mapping against it, but do not edit the block.
- `ai-infrastructure/project-manager/tasks/README.md`: gets the new epic/phase convention subsection and the refreshed Vocabulary note.
- `ai-infrastructure/project-manager/CLAUDE.md`: the two-domain path convention (workspace-relative `./` inside this workspace; bare paths for repo-root shared infra) the README edits must follow.

## Related tasks and ADRs

- ADR-037: the accepted storage-representation decision this task implements.
- ADR-038: the accepted phase-as-View decision; the phase files anticipate its View import target (and supply the `order` field).
- ADR-036: the work-item taxonomy (strict containment, status rollup, the `>= 2` conventions).
- ADR-031: per-workspace task trees; this task adds an `epics/` sibling tree to each relevant workspace.
- COR-T-045: Phase B (the ETL cutover and `roadmap:` block removal); this task must NOT do any of Phase B's work.
- COR-T-041: the prior ADR-036 roadmap restructure, for context on the current roadmap shape being decomposed.

## STATUS deltas

Universal hygiene only: bump `last_updated` to today and append one `recent_updates` entry naming this task (COR-T-044) and what it delivered (the `epics/` and `phases/` trees, the six epic files, the nine phase files, the bottom-up `epic:` backfill, and the tasks/README convention update). Do NOT modify the `roadmap:` block or any other STATUS frontmatter field; Phase B owns the roadmap-block removal.

## Hard rules

- The `roadmap:` block in `ai-infrastructure/project-manager/STATUS.md` must remain byte-for-byte unchanged. Your only permitted STATUS edits are bumping `last_updated` and appending one `recent_updates` entry.
- The pinned mapping in this kickoff is authoritative and is itself drawn from the STATUS.md `roadmap:` block. If a member task ID resolves to a missing file, or the `roadmap:` block disagrees with this kickoff, stop and escalate; do not improvise a resolution.
- Epic and phase files are pure YAML (`.yml`), not markdown. Tasks and ADRs stay markdown; this leaf-versus-container file-type split is deliberate (ADR-037 decision 1).
- For the `epic:` backfill, add only the `epic:` frontmatter field. Do not touch `status`, `updated`, `title`, `labels`, the activity log, or any body text of those task files.
- No `epics/` tree for `backend-api` and no status subdivision (`backlog/`, `in-progress/`, etc.) inside any `epics/` or `phases/` tree.

## Executor pointer

The executor is the dispatched `executor` (ADR-028). Universal executor conventions (verify-before-asserting, the repo writing rules including no em dashes in files, file-edit hygiene, the no-touch rule for `ai-infrastructure/project-manager/tasks/` transitions, and wrap-up STATUS hygiene) live in `docs/ai-orchestration/roles/EXECUTOR-ROLE.md`; apply them without re-statement here. Note that the `epic:` backfill on existing task files is sanctioned by this kickoff and is an in-scope edit (it is a frontmatter-field addition, not a task transition), so it does not conflict with the do-not-touch-tasks convention. Write the closing report to `./.claude/artifacts/handoffs/COR-T-044-KICKOFF-REPORT.md` per EXECUTOR-ROLE.md, section "Report shape".
