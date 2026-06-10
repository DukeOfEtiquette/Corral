---
schema_version: 1
adr: 27
title: "AI-infrastructure workspace structure: project-manager coordinator and lazily-created departments"
status: "accepted"
date: "2026-06-08"
related_adrs: [1, 3, 5, 8, 9, 18, 21, 23, 24]
supersedes: []
superseded_by: null
---

# ADR-027: AI-infrastructure workspace structure: project-manager coordinator and lazily-created departments

> **Forward pointer (2026-06-09):** ADR-029 partially amends the Decision-section tree below, which placed all of `docs/` inside `project-manager/`. ADR-029 keeps the shared `docs/ai-orchestration/` role docs at the repo root (shared infrastructure, like `.claude/`) and moves only `docs/architecture/OVERVIEW.md` into `project-manager/docs/`. The four forks (A-E) and all other decisions here are unaffected. See ADR-029.

> **Forward pointer (2026-06-10):** ADR-030 partially amends Fork D below. Fork D's "paired `/<dept>-orchestrator` and `/<dept>-worker` slash-command set" becomes a single per-department `/<slug>-orchestrator` (Opus) command and NO `/<slug>-worker` command: after ADR-028 (single dispatched `worker-agent`, the `/corral-worker` command retired), department deliverable work runs through the universal dispatched `worker-agent`, which the department's own orchestrator command dispatches. The `/<slug>-orchestrator` adopts the shared `ORCHESTRATOR-ROLE.md` by reference (ADR-029, no per-workspace role-doc copy) and uses the universal checker fleet (ADR-023). Fork D's other elements (the file set, `<DEPT>-NN` observation prefix, `decisions/`, reserved `dept:<slug>` label, no `tasks/`) and Forks A-C, E are unaffected. See ADR-030 for the realized scaffold contract and the `/create-department` recipe.

> **Forward pointer (2026-06-10):** Fork E's "minimal board UI" is realized (COR-T-014) as a program-level INSIGHT dashboard (roadmap and milestone progress, a department roster with per-department detail, and a cross-workspace activity feed), NOT a per-issue kanban. The per-issue kanban is the Corral web app's own surface (ADR-001); the project-manager dashboard sits above it with planning and department-rollup views. Fork E's other aspects (a Python ETL over the `tasks/` pool and workspace `STATUS` frontmatter, the JSON data contract, compose-run per ADR-003, and the dogfood repoint per ADR-008) are unchanged.

## Context

At day zero, the repo root acts as the sole coordinator: `CLAUDE.md`, `STATUS.md`, `OBSERVATIONS.md`, `decisions/`, `docs/`, and `tasks/` all live at the root. No departments exist. ADR-009 established rogue's `~/rogue/ai-workspaces/project-manager` as Corral's exemplar and named the coordinator-plus-departments structure as the target (with ADR-021 recording the candidate list). ADR-009 Option A's parenthetical explicitly deferred it: "Skip the parts a day-zero single project does not need (multiple workspaces, frontmatter query tooling, dashboards)." That deferral was intentional MVP-maturity scoping.

With Phase 1 of the AI-infrastructure roadmap nearly complete (role docs, dispatch loop, blocking ADRs resolved), and with ADR-021 capturing a concrete candidate-department list, the moment to stand up the real directory structure has arrived. This ADR records the decided structure and the five forks resolved with the user. It amends the skip-workspaces parenthetical of ADR-009 (see Consequences). The physical file moves and tooling are follow-on work; this ADR is the spec those tasks execute against.

The rogue lineage: `~/rogue/ai-workspaces/` is an `ai-workspaces/` directory holding `project-manager/` as the coordinator workspace and sibling department workspaces. Corral renames the top-level directory `ai-infrastructure/` to make the AI-first framing explicit (ADR-005). The coordinator workspace is `ai-infrastructure/project-manager/`, and the `.claude/` shared-infrastructure convention mirrors how rogue keeps its `.claude/` at the repo root.

## Alternatives considered

### Rogue-mirror: adopt `ai-infrastructure/project-manager/` as the coordinator workspace (selected) vs. root-stays-sole-coordinator (rejected)

The selected model moves root orchestration content into `ai-infrastructure/project-manager/` and reduces the repo root to a thin orientation layer, exactly as rogue's repo root is thin while `ai-workspaces/project-manager/` holds the coordinator content.

The rejected alternative, keeping the root as the indefinite sole coordinator, was appropriate at day zero but becomes a liability as departments and the web app are added: the root accumulates content from two distinct domains (AI infrastructure and web app), path conventions become ambiguous, and the separation ADR-005 requires is not enforced by the directory structure. The skip-workspaces parenthetical in ADR-009 was explicit that this was a temporary stance.

### Single shared `dept:`-labeled task pool (selected) vs. per-department task trees, the rogue default (rejected)

The selected model keeps a single task pool at `ai-infrastructure/project-manager/tasks/` (the current `COR-T-NNN` tree). Departments do not get their own `tasks/` directories. A department's work is tagged into the shared pool with its `dept:<slug>` label (ADR-018 taxonomy). This is a deliberate divergence from rogue, where each workspace has a separate task tree with its own ID prefix.

The rationale: Corral is building a single-pool, per-label-board-view issue tracker as its product (ADR-001). Using the same structure for its own task management dogfoods the product model from day one. One shared pool with per-`dept:` label views is exactly the workflow the app is designed to support; splitting the pool into per-department trees would contradict the product's headline feature and defer any self-referential validation until the dogfood milestone (ADR-008). The per-department-task-trees alternative is the rejected option on this dimension.

### Move all ADRs as-is, then migrate web-app ADRs to web-app departments later (selected) vs. split the ADR set now (rejected)

The selected model moves all current ADRs into `ai-infrastructure/project-manager/decisions/` during the restructure, preserving the single number sequence and all `related_adrs` cross-references intact. Web-app-domain ADRs (the product and web-app decisions) migrate out into the relevant web-app department's `decisions/` directory later, when those departments are lazily created.

Splitting the ADR set at restructure time was rejected because the current ADRs form a dense cross-reference graph: `related_adrs` links span both domains, and a split would either require a global renumber or leave dangling cross-references. Splitting later, when web-app departments are created and the cross-reference graph can be traced cleanly, avoids this churn. The rejected path would have introduced breakage for no readability gain at this stage.

## Decision

Corral adopts the rogue coordinator-plus-departments model as a real `ai-infrastructure/` directory structure. The decided target is:

```
corral/
|- CLAUDE.md            # thin: repo orientation, pointers into ai-infrastructure/ and app/ (future)
|- README.md            # human orientation
|- .claude/             # SHARED infra, stays at root: commands/, agents/, artifacts/
|- ai-infrastructure/
|  '- project-manager/  # coordinator workspace (root orchestration moves here)
|     |- CLAUDE.md  README.md  STATUS.md  OBSERVATIONS.md
|     |- decisions/     # all current ADRs move here as-is (Fork C: web-app ones migrate out later)
|     |- docs/          # ai-orchestration/roles/, architecture/OVERVIEW.md
|     |- tasks/         # the SHARED COR-T pool; dept: labels partition it (Fork B)
|     |- templates/department/   # the create-department baseline (built in a follow-on task)
|     '- dashboard/     # the PM dashboard (built in a follow-on task)
'- app/                 # (future) the web app, built by lazily-created web-app departments
```

Departments are siblings `ai-infrastructure/<dept>/` with `CLAUDE.md`, `README.md`, `STATUS.md`, `OBSERVATIONS.md`, and `decisions/`. Departments have NO own `tasks/` directory (Fork B: shared labeled pool).

The five forks are decided as follows:

**Fork A: move root orchestration into `ai-infrastructure/project-manager/`.** `CLAUDE.md` (operating rules), `STATUS.md`, `OBSERVATIONS.md`, `decisions/`, `docs/`, and `tasks/` move into the coordinator workspace. The repo root is reduced to a thin `CLAUDE.md` (orientation and pointers) and `README.md` for humans. The future web app lives under `app/` at the repo root. The physical move is a named follow-on task and is not performed by this ADR.

**`.claude/` stays at the repo root as shared infrastructure.** Slash commands (`commands/`), agent definitions (`agents/`), and handoff/scratch artifacts (`artifacts/`) remain repo-root-level and shared across all workspaces, exactly as rogue keeps `.claude/` at its repo root. They do not move into the project-manager workspace.

**Fork B: one shared `dept:`-labeled task pool.** The current `COR-T-NNN` task pool lives at `ai-infrastructure/project-manager/tasks/`. Departments are partitioned into this pool by `dept:<slug>` label (ADR-018), not by separate task directories. See the rationale above.

**Fork C: all ADRs move as-is; web-app ADRs migrate out later.** During the restructure, all current ADRs move into `ai-infrastructure/project-manager/decisions/` with no numbering changes and no split. Web-app-domain ADRs migrate out into web-app department `decisions/` directories when those departments are lazily created.

**Fork D: department scaffold recipe (named here; built in a follow-on task).** When the project-manager creates a department `ai-infrastructure/<dept>/`, the baseline is: `CLAUDE.md` (workspace routing), `README.md` (charter), `STATUS.md` (frontmatter plus narrative), `OBSERVATIONS.md` (with a `<DEPT>-NN` observation prefix), a `decisions/` directory, a paired `/<dept>-orchestrator` (Opus) and `/<dept>-worker` (Sonnet) slash-command set under root `.claude/commands/`, and a reserved `dept:<slug>` label (ADR-018) for tagging work into the shared pool. A department has NO own `tasks/`. The create-department recipe (template directory plus `/create-department` command) is a named follow-on deliverable and is not built by this ADR.

**Fork E: project-manager dashboard (named here; built in a follow-on task).** The project-manager gets a dashboard: a Python ETL that reads the shared `tasks/` pool and workspace `STATUS` frontmatter, emits a JSON data contract, and renders a minimal board UI runnable under docker compose (ADR-003). It queries the markdown `tasks/` pool now, and repoints to the Corral web app at the dogfood milestone (ADR-008), when task management migrates off `tasks/` into the app. This mirrors how rogue's project-manager uses GitHub Issues today, which is exactly the workflow Corral's web app exists to replace: the project's self-referential mission. The dashboard build is a named follow-on deliverable and is not built by this ADR.

**Coordinator write authority.** The project-manager may create and edit files inside sibling department workspaces it coordinates (status alignment, cross-references, decision propagation, consistency fixes), mirroring rogue's coordinator-write grant.

**ADR-009 amendment.** ADR-009's skip-workspaces parenthetical ("Skip the parts a day-zero single project does not need (multiple workspaces, frontmatter query tooling, dashboards)") was MVP-maturity scoping, not a permanent architectural constraint. This ADR supersedes that framing: Corral now adopts the workspace structure and, per Fork E, a dashboard. ADR-009 is not edited (append-only convention; ADR-024 precedent for amending by a later ADR). `supersedes: []` is kept because this is a partial amendment of one parenthetical clause, not a full supersession of ADR-009's decision.

## Consequences

- **ADR-009 partial amendment.** The skip-workspaces parenthetical in ADR-009 Option A is superseded by this ADR's decision. ADR-009 itself remains `accepted` and is not edited. This follows the ADR-024 precedent: accepted ADRs are amended by a later ADR, not modified in place. Readers of ADR-009 should read ADR-027 for the workspace-structure and dashboard decisions.

- **Coordinator write authority established.** The project-manager workspace has write authority over sibling department workspaces for coordination purposes. This mirrors rogue and must be documented in the project-manager's `CLAUDE.md` when that workspace is stood up.

- **Fork C interim state.** Until web-app departments are created, all ADRs (both AI-infra and web-app domain) live together in `ai-infrastructure/project-manager/decisions/`. This is a deliberate interim state, not an oversight. The web-app-domain ADR migration is a consequence of lazy department creation and will be handled at that time.

- **Path-convention rule for the restructure.** After the move, within a workspace the `./`-prefixed path convention resolves workspace-relative: the project-manager's `CLAUDE.md`, role docs, and slash commands will reference `./tasks/`, `./decisions/`, `./docs/` meaning relative to `ai-infrastructure/project-manager/`, as rogue's per-workspace docs do. The thin repo-root `CLAUDE.md` will use repo-root-relative paths into the structure. The actual rewrite of `CLAUDE.md`, the role docs, the slash commands, and the agent specs is the restructure task's job, not this ADR's.

- **Three named follow-on tasks for the Orchestrator to queue:**
  1. **Restructure execution**: the physical `git mv` of root orchestration content into `ai-infrastructure/project-manager/`, plus the thin repo-root `CLAUDE.md` rewrite and the path-convention rewrites in role docs, slash commands, and agent specs.
  2. **Create-department recipe**: the `templates/department/` baseline plus the `/create-department` command, plus a recipe ADR to record the scaffold contract.
  3. **Project-manager dashboard**: the Fork E dashboard (Python ETL, JSON contract, board UI, compose-integrated).

  COR-T-006, which finalizes the ADR-021 candidate-department list, runs alongside and is not blocked by this ADR.

- **Dogfood arc for the dashboard.** The dashboard starts querying the markdown `tasks/` pool; at the dogfood milestone (ADR-008) it repoints to the Corral web app. This makes the dashboard a living test of the app's MCP contract (ADR-004) and a concrete artifact of the project's self-referential mission.

- **Department-scoped checkers.** Per ADR-023, department-scoped checkers can layer beside the universal `worker-prelaunch-checker` / `worker-close-checker` pair when departments land. The department scaffold (Fork D) should include a note reserving the slot for a department-scoped checker if the department's work warrants it.
