# Author ADR-027: AI-infrastructure workspace structure (project-manager coordinator)

## Target

This is **AI-infrastructure work (ADR-005, domain 2)**: a decision record governing how Corral's own AI orchestration is structured. The artifact in scope is one brand-new ADR, `ADR-027`, authored directly as `status: "accepted"` (it records a decision already taken with the user, not an open question to frame). The procedure differs from the COR-T-002 through COR-T-005 runs, which flipped a pre-existing `pending` ADR to `accepted`: here the ADR file does not exist yet and is created whole, following `./decisions/README.md` (the four-section body, the YAML frontmatter schema, the append-only rule). Because ADR-027 is born accepted, it carries **no** `> Pending:` blockquote callout (those mark `pending` ADRs only).

This task is **decision-level only**. It moves no files, creates no `ai-infrastructure/` directory, and builds no tooling. ADR-027 is the spec a later restructure task executes against, and the user's review gate before any file is moved. The second deliverable is universal-plus-task-specific STATUS hygiene. Nothing else in the repo is touched.

## Decisions resolved by the Orchestrator

Every item below is pinned. Encode it into ADR-027's text; do not re-open it, and do not present it to a reader as an option still on the table. (Tradeoff prose belongs in ADR-027's "Alternatives considered" section as a recorded rejected alternative, not as a live question.)

- **ADR-027 frontmatter.** Use exactly: `schema_version: 1`, `adr: 27`, `title: "AI-infrastructure workspace structure: project-manager coordinator and lazily-created departments"`, `status: "accepted"`, `date: "2026-06-08"`, `related_adrs: [1, 3, 5, 8, 9, 18, 21, 23, 24]`, `supersedes: []`, `superseded_by: null`. The `related_adrs` set is chosen because: ADR-001 is the single-issue-pool / per-label-board-view product model; ADR-003 is the compose runtime for the dashboard; ADR-005 is the two-domains framing; ADR-008 is the dogfood milestone / task-migration arc; ADR-009 is the convention ADR being amended; ADR-018 is the `dept:` label taxonomy; ADR-021 is the candidate-department menu; ADR-023 is the dispatch loop / department-scoped-checker note; ADR-024 is the amend-by-later-ADR precedent. (This rationale is to guide which ADRs you cross-reference in the body; it is not text to print verbatim in the frontmatter.)

- **Core decision: adopt the rogue coordinator-plus-departments model as a real directory structure, right-sized.** Corral's AI infrastructure is organized as self-contained workspaces under a top-level `ai-infrastructure/` directory (Corral's rename of rogue's `ai-workspaces/`). `ai-infrastructure/project-manager/` is the coordinator workspace, stood up first, before any web-app work and before any department. It tracks, dispatches, and reviews work; it does not author domain content. Departments are sibling workspaces `ai-infrastructure/<dept>/`, created lazily by the project-manager when sustained work justifies one (ADR-021's Option A leaning). The lineage is rogue's `~/rogue/ai-workspaces/project-manager/` (its coordinator/department model and its coordinator-write-authority grant); ADR-009 already established rogue as Corral's exemplar. You do NOT need to read the rogue repo to author this ADR; every fact you need is in this kickoff.

- **Fork A: move root orchestration into `ai-infrastructure/project-manager/`.** The orchestration content currently at the repo root (the `CLAUDE.md` operating rules, `STATUS.md`, `OBSERVATIONS.md`, `decisions/`, `docs/`, `tasks/`) becomes the project-manager workspace's content. The repo root is reduced to a thin orientation layer (a thin `CLAUDE.md` pointing into the structure, `README.md` for humans) and will later also hold the web app under `app/`. ADR-027 records this as the decided target; the physical move is a named follow-on task and is NOT performed here.

- **`.claude/` stays at the repo root as shared infrastructure.** Slash commands (`commands/`), agent definitions (`agents/`), and handoff/scratch artifacts (`artifacts/`) remain repo-root-level, shared across all workspaces, exactly as rogue keeps `.claude/` at its repo root. They do not move into the project-manager workspace.

- **Fork B: one shared `dept:`-labeled task pool, not per-department task trees.** Corral keeps a single task pool (the current `COR-T-NNN` tree) living at `ai-infrastructure/project-manager/tasks/`; departments do NOT get their own `tasks/` directories. A department's work is tagged into the shared pool with its `dept:<slug>` label (ADR-018 taxonomy). This deliberately diverges from rogue (where each workspace has a separate task tree with its own prefix) because it dogfoods Corral's own product model: one issue database with per-`dept:`-label board views (ADR-001). Record the rogue divergence and its rationale explicitly in the Decision and in the Alternatives section. The per-department-task-trees alternative is the rejected option on this dimension.

- **Department scaffold (the create-department recipe, named here; built in a follow-on task per Fork D).** When the project-manager creates a department `ai-infrastructure/<dept>/`, the baseline it is stamped from is: `CLAUDE.md` (workspace routing), `README.md` (charter), `STATUS.md` (frontmatter plus narrative), `OBSERVATIONS.md` (with a `<DEPT>-NN` observation prefix), a `decisions/` directory, a paired `/<dept>-orchestrator` (Opus) plus `/<dept>-worker` (Sonnet) slash-command set under the root `.claude/commands/`, and a reserved `dept:<slug>` label (ADR-018) for tagging its work into the shared pool. A department has NO own `tasks/` (Fork B). ADR-027 records this baseline as the recipe's contract; the actual template plus `/create-department` command is a named follow-on deliverable and is NOT built here.

- **Coordinator write authority.** The project-manager may create and edit files inside the sibling department workspaces it coordinates (status alignment, cross-references, decision propagation, consistency fixes), mirroring rogue's coordinator-write grant. Record this as a consequence.

- **Fork C: web-app design ADRs migrate to web-app departments later.** In the restructure, ALL current ADRs move as-is into `ai-infrastructure/project-manager/decisions/` to avoid churn and cross-reference breakage (they are one number sequence with dense `related_adrs` links). The web-app-domain ADRs (the product/web-app decisions) migrate out into the relevant web-app department's `decisions/` later, when those departments are lazily created. Record this as the interim-then-migrate plan. Do not split the ADR set in this task, and state that the restructure task does not split it either.

- **Sub-decision: ADR-027 amends ADR-009; ADR-009 is not edited.** ADR-009 Option A's parenthetical ("Skip the parts a day-zero single project does not need (multiple workspaces, frontmatter query tooling, dashboards)") was MVP-maturity scoping, not a permanent architectural constraint. Corral now adopts the right-sized workspace structure and (Fork E) a dashboard. ADR-027 records this as an explicit amendment of ADR-009. ADR-009 is accepted and append-only (`./decisions/README.md`); it is NOT edited in place. This follows the ADR-024 precedent that an accepted ADR is amended by a later ADR. Keep `supersedes: []` (this is a partial amendment, not a full supersede).

- **ADR-021 relationship.** ADR-021 (candidate departments) stays the brainstorm menu the project-manager picks from when creating a department; it is the source of candidate names, not resolved or edited here. COR-T-006 finalizes ADR-021 separately. ADR-027 references ADR-021 as the menu and does not resolve it.

- **Fork E: the project-manager dashboard (named here; built in a follow-on task).** The project-manager gets a dashboard, scoped small first: a Python ETL that reads the shared `tasks/` pool and workspace `STATUS` frontmatter, emits a JSON data contract, and renders a minimal board UI; runnable under docker compose (ADR-003). It queries the markdown `tasks/` pool now, and repoints to the Corral web app at the dogfood milestone (ADR-008), when task management migrates off `tasks/` into the app. Record this arc explicitly: it mirrors how rogue's project-manager uses GitHub Issues today, which is exactly the workflow Corral's web app exists to replace (the project's self-referential mission). The dashboard build is a named follow-on deliverable and is NOT built here.

- **Path-convention rule for the restructure (record so the follow-on restructure task executes against it).** After the move, within a workspace the `./`-prefixed repo-relative path convention (the `./CLAUDE.md` writing/path rules) resolves workspace-relative: the project-manager's `CLAUDE.md`, role docs, and slash commands reference `./tasks/`, `./decisions/`, `./docs/` meaning relative to `ai-infrastructure/project-manager/`, as rogue's per-workspace docs do. The thin repo-root `CLAUDE.md` uses repo-root-relative paths into the structure. ADR-027 states this rule; the actual rewrite of `CLAUDE.md`, the role docs, the slash commands, and the agent specs is the follow-on restructure task's job, NOT this task's.

- **Follow-on deliverables named, not built.** In Consequences, name three follow-on tasks the Orchestrator will queue after ADR-027 is accepted: (1) execute the restructure (the physical `git mv` of root orchestration into `ai-infrastructure/project-manager/` plus the path-convention rewrites and the thin root layer); (2) the create-department recipe (the `templates/department/` baseline plus the `/create-department` command, plus a recipe ADR); (3) the project-manager dashboard (Fork E). Reference these descriptively by the work they do, NOT by unallocated `COR-T` IDs (the IDs are not yet assigned). Also note that COR-T-006 finalizes the ADR-021 candidate list alongside.

- **Exact target tree to record in the Decision section.** Encode this directory tree as the decided target so the restructure task has an unambiguous spec:

  ```
  corral/
  |- CLAUDE.md            # thin: repo orientation, pointers into ai-infrastructure/ and app/ (future)
  |- README.md            # human orientation
  |- .claude/             # SHARED infra, stays at root: commands/, agents/, artifacts/
  |- ai-infrastructure/
  |  '- project-manager/  # coordinator workspace (this is where root orchestration moves)
  |     |- CLAUDE.md  README.md  STATUS.md  OBSERVATIONS.md
  |     |- decisions/     # all current ADRs move here as-is (Fork C: web-app ones migrate out later)
  |     |- docs/          # ai-orchestration/roles/, architecture/OVERVIEW.md
  |     |- tasks/         # the SHARED COR-T pool; dept: labels partition it (Fork B)
  |     |- templates/department/   # the create-department baseline (built in a follow-on task)
  |     '- dashboard/     # the PM dashboard (built in a follow-on task)
  '- app/                 # (future) the web app, built by lazily-created web-app departments
  ```

  Departments are siblings `ai-infrastructure/<dept>/` with `CLAUDE.md / README / STATUS / OBSERVATIONS / decisions/` and NO own `tasks/`.

## Deliverables

1. **`./decisions/ADR-027-ai-infrastructure-workspace-structure.md`**, created whole, `status: "accepted"`, with:
   - The frontmatter pinned above (verbatim values).
   - **Context**: why the structure is decided now, the rogue lineage (ADR-009 exemplar), the day-zero state (repo root acting as the sole coordinator), and the ADR-009 skip-workspaces parenthetical being revisited.
   - **Alternatives considered**: an honest set, each with the selected option and the rejected counterpart stated:
     - the rogue-mirror with `ai-infrastructure/project-manager/` (selected) vs root-stays-sole-coordinator (rejected);
     - the single shared `dept:`-labeled task pool (selected) vs per-department task trees, the rogue default (rejected, with the dogfood rationale);
     - move-all-ADRs-then-migrate-web-app-ADRs-later (selected) vs split-the-ADR-set-now (rejected, with the churn / cross-reference-breakage rationale).
   - **Decision**: stated declaratively. Encode the exact target tree above, and Forks A through E as decided forks of the structure.
   - **Consequences**: cover the ADR-009 amendment (and that ADR-009 is not edited, per the ADR-024 precedent), the coordinator write authority, the Fork C interim-then-migrate plan, the path-convention rule, the three named follow-on deliverables (descriptive, no unallocated IDs), and the dogfood/dashboard arc.
2. **`./STATUS.md`** updated per the "STATUS deltas" section below (universal hygiene plus the task-specific edits).

## Files in scope

- `./decisions/ADR-027-ai-infrastructure-workspace-structure.md` (create new, `status: "accepted"`).
- `./STATUS.md` (task-specific delta plus universal hygiene).

## Files out of scope

- **No file moves.** This task does NOT move `CLAUDE.md`, `STATUS.md`, `OBSERVATIONS.md`, `decisions/`, `docs/`, or `tasks/` into `ai-infrastructure/project-manager/`, and does NOT create the `ai-infrastructure/` directory. That is the follow-on restructure task. ADR-027 only records the target.
- **No tooling.** Do NOT create `templates/department/`, a `/create-department` command, or any `dashboard/` code. Those are named follow-on deliverables.
- **Every other ADR.** ADR-009 is amended in ADR-027's prose but NOT edited (append-only). ADR-021 is referenced but NOT resolved or edited. ADR-001 / ADR-003 / ADR-005 / ADR-008 / ADR-018 / ADR-023 / ADR-024 are cited, not edited. Do NOT create or edit any ADR other than the new ADR-027.
- **The `./tasks/` tree**, including `./tasks/in-progress/COR-T-011-author-adr-027-ai-infrastructure-structure.md`. Task transitions and new-task creation are Orchestrator-only; read the task file for context, but never move, edit, or create anything under `./tasks/`. Reference the three follow-on tasks descriptively in ADR-027, not by ID.
- **`./CLAUDE.md`, the role docs, the slash commands, the agent specs, `./README.md`, `./docs/architecture/OVERVIEW.md`.** ADR-027 describes how the restructure task will change these, but this task edits none of them.
- **`./.claude/` contents.** Not touched (beyond writing this task's own report via the dual-channel convention).

## References

Read these in order before authoring:

- `./decisions/README.md`: ADR conventions: the frontmatter schema, status values, the four-section body, the append-only rule, and how a new accepted ADR is authored.
- `./decisions/ADR-009-adopt-rogue-orchestration-conventions.md`: the convention ADR being amended; read its Option A parenthetical ("skip multiple workspaces ... dashboards") and its Decision so the amendment is framed accurately.
- `./decisions/ADR-021-candidate-departments.md`: the candidate-department menu and the lazy-creation (Option A) leaning ADR-027 builds on.
- `./decisions/ADR-005-two-domains-ai-first.md`: the two-domains framing (this ADR is domain-2 work governing how domain 2 is structured).
- `./decisions/ADR-008-bootstrap-tasks-dogfood-milestone.md`: the dogfood milestone where the markdown task pool migrates into the Corral web app; the arc the dashboard follows.
- `./decisions/ADR-001-self-hosted-issue-tracker-scope.md`: the single-pool, per-label-board-view product model that justifies Fork B (shared labeled pool).
- `./decisions/ADR-024-git-tracked-handoff-artifacts.md`: the precedent that an accepted ADR is amended by a later ADR, not edited in place (cited for the ADR-009 amendment).
- `./decisions/ADR-023-dispatch-loop-day-zero.md`: notes that department-scoped checkers can layer when departments land; supports the department-scaffold framing.
- `./decisions/ADR-003-docker-compose-runtime.md`: the compose-only run policy the dashboard honors.
- `./CLAUDE.md`: read-only context for what root orchestration content exists and will move (do not edit it).

## Related tasks and ADRs

- COR-T-011 (`./tasks/in-progress/COR-T-011-author-adr-027-ai-infrastructure-structure.md`): this task's tracking file; read for context, do not edit.
- COR-T-006 (`./tasks/in-progress/COR-T-006-resolve-adr-021-departments.md`): finalizes the ADR-021 candidate list that feeds ADR-027's department menu; runs alongside, resolved separately.
- ADR-009: the convention ADR amended by ADR-027 (rogue exemplar; the skip-workspaces parenthetical is the framing being amended).
- ADR-021: the candidate-department menu ADR-027 references but does not resolve.
- ADR-005: the two-domains framing (ADR-027 is domain-2 work governing domain-2 structure).
- ADR-001: the single-issue-pool, per-label-board-view product model that justifies Fork B.
- ADR-008: the dogfood milestone the dashboard arc (Fork E) follows.
- ADR-024: the amend-by-later-ADR precedent for the ADR-009 amendment.
- ADR-018: the `dept:` label taxonomy used to partition the shared task pool and reserve a department label.
- ADR-023: the dispatch loop; department-scoped checkers layer when departments land, supporting the scaffold framing.
- ADR-003: the compose-only run policy the dashboard honors.

## STATUS deltas

Beyond universal STATUS hygiene (bump `last_updated` to `2026-06-08` and append a `recent_updates` entry, per `./docs/ai-orchestration/roles/WORKER-ROLE.md`), apply these task-specific edits to `./STATUS.md`:

- Add a `recent_updates` entry recording that ADR-027 was accepted: Corral adopts the rogue coordinator-plus-departments model as a real `ai-infrastructure/<workspace>/` structure with `ai-infrastructure/project-manager/` as the coordinator (root orchestration to move there), a single shared `dept:`-labeled task pool, lazily-created departments, an amendment of ADR-009's skip-workspaces framing, and named follow-on work (restructure execution, create-department recipe, project-manager dashboard).
- Rewrite the "Next step" paragraph so it states that the foundational AI-infrastructure structure is now decided (ADR-027) and the next backbone step is executing the restructure (move root orchestration into `ai-infrastructure/project-manager/`), followed by the create-department recipe and the project-manager dashboard; the ADR-021 candidate-list finalization (COR-T-006) rides alongside. Keep these references descriptive (no specific unallocated task IDs).
- The "Blocked on" section stays "Nothing." (no change required beyond confirming it).

## Hard rules

- ADR-027 is authored directly as `status: "accepted"`. It carries **no** `> Pending:` blockquote callout (that marker is for `pending` ADRs only).
- ADR-027 is a brand-new file created whole. It is not a flip of a pre-existing `pending` ADR; there is no prior body to edit.
- ADRs are append-only (`./decisions/README.md`). The ADR-009 amendment lives entirely inside ADR-027's prose; ADR-009 is not touched.
- This task records decisions only. It moves no files, creates no `ai-infrastructure/` directory, and builds no `templates/`, `/create-department` command, or `dashboard/` code.

## Worker pointer

The Worker session is `/corral-worker`. Universal Worker conventions (the writing rules and Agent Discipline in `./CLAUDE.md`, the docker-compose-only run policy, the git boundaries, the pinned six-section report shape, and the wrap-up STATUS hygiene) live in `./docs/ai-orchestration/roles/WORKER-ROLE.md`; follow them rather than re-deriving them here. Write the closing report to `./.claude/artifacts/handoffs/COR-T-011-KICKOFF-REPORT.md` per `WORKER-ROLE.md`, section "Report shape".
