# COR-T-051 - guard derived phase-completeness (eager forming-epic recipe step + dashboard no-epic check)

## Target

This is **AI-infrastructure** work (ADR-005, domain 2). The task implements ADR-041 (accepted 2026-06-14, Option D), which promotes observation COR-08. The fully-derived roadmap (ADR-037) reads a phase as done when all its *filed* epics are done, so a department with anticipated work but no epic file makes its phase read prematurely complete. You build a two-layer guard: a warn-only dashboard consistency check that catches existing gaps, and a create-department recipe step plus a convention note that prevent future gaps. All three deliverables ship in this one dispatch. ADR-041 is the authority; read it first (path in References).

## Decisions resolved by the Orchestrator

The orchestrator resolved every design choice below. Execute them as pinned; do not re-open or re-deliberate them.

### Deliverable 1: dashboard no-epic consistency check (`etl.py`)

- **Where.** In `ai-infrastructure/project-manager/dashboard/etl.py`, in the `departments` assembly loop at lines 1256-1273, where each `DEPARTMENTS_ROSTER` entry becomes a department dict carrying `slug`/`domain`/`exists`/`orchestrator_command`/`label`/`status`/`task_counts`. Add a per-department epic count and a new `no_epic_warning` field to that dict.
- **Epic count source (pinned).** Compute the per-department epic count by counting the epic YAML files in that department's own epics tree: the `*.yml` files in `ai-infrastructure/<slug>/epics/`, excluding the `.next-epic-id` counter file. The directory may not exist for a given department, in which case the count is `0`. Do NOT derive the count from `collect_roadmap_from_files` (defined at `etl.py` line 858): per its docstring that function omits standalone (phase-less) epics, so it would undercount and fire a false no-epic warning for a department whose only epic is standalone. Counting the department's epic files directly counts ALL of its epics, which is exactly what "department has zero epics" requires.
- **Warning value.** Set `no_epic_warning` to a short string (for example `"Department exists but has no epic; its work is unrepresented in the roadmap (ADR-041)."`) when `exists` is `true` AND the epic count is `0`; otherwise set it to `null`. This mirrors the existing warning family: `phase_warning`, `epic_warning`, and `cross_dept_warning` are all string-or-null. Follow that string-or-null shape exactly.
- **Warn-only (load-bearing).** This is advisory per the ADR-035 / ADR-039 owned-but-advisory model (ADR-041 decision 2). Do NOT change, gate, or suppress any derived phase status, epic status, department status, `current_phase`, or `next_step`. The check only adds the new field; the derived statuses must be byte-for-byte unchanged for the current repo state.

### Deliverable 1 render (`DepartmentsPanel.jsx` + `styles.css`)

- **Follow the `isOrphaned` precedent.** `ai-infrastructure/project-manager/dashboard/src/panels/DepartmentsPanel.jsx` already renders an advisory warning for the orphaned case: `isOrphaned = dept.exists && !dept.orchestrator_command` (line 20) drives a row class (`dept-orphaned`, lines 21-25) and a `title` tooltip (line 30). Add a parallel indicator for the no-epic case: a row class (for example `dept-no-epic`) and/or a `title` tooltip carrying `dept.no_epic_warning`, rendered consistently with how `isOrphaned` is rendered in that file.
- **CSS.** Add any needed style for the new row class to `ai-infrastructure/project-manager/dashboard/src/styles.css`, following the existing `dept-orphaned` (lines 354-355) and `dept-planned` (line 353) conventions under the `.dept-table` block.
- **Visual surface.** This is a visual deliverable; the orchestrator render-verifies it at close (the dashboard is already running for that gate). You do not need to launch a browser.

### Deliverable 2: create-department recipe forming-epic step (`.claude/commands/create-department.md`)

Amend the recipe so a newly stamped department carries a forming epic from day one (ADR-041 decision 1, which amends ADR-030). Make these four edits:

- **(a) Fifth input.** Add a fifth argument `<phase>` (the integer roadmap phase the department's forming epic belongs to) to the "Inputs" section, and extend the example invocation accordingly.
- **(b) Token.** Add a `{{DEPT_PHASE}}` row to the "Token substitution" table, valued from the `<phase>` argument.
- **(c) Created artifacts.** Add an entry under "What this command creates" for the `epics/` tree: `ai-infrastructure/<slug>/epics/.next-epic-id` seeded to `2`, and a forming epic file `ai-infrastructure/<slug>/epics/<TASK-PREFIX>-E-001-<slug>.yml`.
- **(d) Execution-flow step.** Add the corresponding step to the "Execution flow" that stamps the forming epic, and update the recipe's verification/confirmation text (currently the "seven target files" check in Step 6) to include the `epics/` tree and the forming epic.
- **Forming epic content.** The forming epic file follows the existing epic format. Use `ai-infrastructure/backend-api/epics/API-E-001-backend-api.yml` and `ai-infrastructure/database/epics/DB-E-001-database-schema-migrations.yml` as the format exemplars. The fields are: `schema_version: 1`, `id: <TASK-PREFIX>-E-001`, `title: "<Display Name>"`, `dept: <slug>`, `phase: <phase>`, and a one-line `description:` describing the forming epic. The epic ID prefix is the department's task prefix (database -> `DB-E`, backend-api -> `API-E`). Zero tasks is correct: a forming epic with no tasks is `planned` per ADR-036.
- **No template FILE.** Do NOT add an epic template file under `ai-infrastructure/project-manager/templates/department/`. The forming epic is generated inline from the inputs (its phase, title, and description vary per department), unlike the fixed template files the recipe stamps.

### Deliverable 3: convention note (`tasks/README.md`)

- **Where.** In `ai-infrastructure/project-manager/tasks/README.md`, amend the "Lazy creation" subsection under "Epics and phases" (lines 88-90). It currently says to create an `epics/` tree only when the workspace's first epic is ready and not to create placeholder trees.
- **What to add.** Reflect ADR-041: a department files at least one forming epic for its active or next phase when it is stood up, so no active phase reads done while a member department is unrepresented; the `epics/` tree is created then. Reconcile with the no-empty-placeholders rule by noting that a forming epic carries real content (its `dept`, `phase`, `title`, and `description`), so it is not an empty placeholder.
- **Cross-references.** Keep the existing cross-references to ADR-021, ADR-031, and ADR-036 accurate, and add ADR-041.

## Deliverables

- `ai-infrastructure/project-manager/dashboard/etl.py`: per-department epic count (counted from `ai-infrastructure/<slug>/epics/*.yml`) plus a `no_epic_warning` (string-or-null) field on each department entry; warn-only, no derived-status change.
- `ai-infrastructure/project-manager/dashboard/src/panels/DepartmentsPanel.jsx` (and `ai-infrastructure/project-manager/dashboard/src/styles.css`): the no-epic warning rendered following the `isOrphaned` precedent.
- `.claude/commands/create-department.md`: the `<phase>` input, the `{{DEPT_PHASE}}` token, the `epics/` tree plus forming-epic creation step, and the verification-text update.
- `ai-infrastructure/project-manager/tasks/README.md`: the "Lazy creation" subsection amended for the eager-forming-epic convention (ADR-041).
- The six-section closing report (per EXECUTOR-ROLE.md "Report shape"), stating explicitly what was verified by code inspection versus by run.

## Files in scope

- `ai-infrastructure/project-manager/dashboard/etl.py`
- `ai-infrastructure/project-manager/dashboard/src/panels/DepartmentsPanel.jsx`
- `ai-infrastructure/project-manager/dashboard/src/styles.css`
- `.claude/commands/create-department.md`
- `ai-infrastructure/project-manager/tasks/README.md`

## Files out of scope

- `ai-infrastructure/project-manager/dashboard/src/panels/BlockedPanel.jsx` and the blocked surface (COR-T-050, done; do not touch).
- Any `STATUS.md`, and the department STATUS or CLAUDE templates (COR-T-049/050, done). The only template-area change is the create-department command file itself; do NOT touch `ai-infrastructure/project-manager/templates/department/`.
- The roadmap / `current_phase` / `next_step` derivation in `etl.py`: it must stay byte-for-byte unchanged for the current repo state; this change is additive and advisory only.
- `ai-infrastructure/project-manager/templates/department/`: no epic template file is added; the forming epic is generated inline by the recipe.

## References

- `ai-infrastructure/project-manager/decisions/ADR-041-guard-derived-phase-completeness.md`: the authority for this task (Option D: discipline plus advisory check). Decision 1 is the recipe/convention discipline; decision 2 is the etl check; decision 3 keeps ADR-036's rollup semantics unchanged. Read first.
- `ai-infrastructure/project-manager/tasks/in-progress/COR-T-051-guard-derived-phase-completeness.md`: this task file (read-only context; do not edit or move it).
- `ai-infrastructure/project-manager/dashboard/etl.py`: the `departments` assembly loop is at lines 1256-1273 (Deliverable 1 target). `collect_roadmap_from_files` is at line 858; it is named here only to identify the source you must NOT use for the epic count (its docstring confirms it omits standalone epics).
- `ai-infrastructure/project-manager/dashboard/src/panels/DepartmentsPanel.jsx`: the `isOrphaned` precedent to follow is at lines 20-30.
- `ai-infrastructure/project-manager/dashboard/src/styles.css`: the `.dept-table` block with `dept-planned` (line 353) and `dept-orphaned` (lines 354-355) conventions to follow.
- `ai-infrastructure/backend-api/epics/API-E-001-backend-api.yml`: forming-epic format exemplar (a `phase: 2` forming epic).
- `ai-infrastructure/database/epics/DB-E-001-database-schema-migrations.yml`: epic format exemplar.
- `.claude/commands/create-department.md`: the recipe to amend (Inputs, Token substitution table, "What this command creates", Execution flow).
- `ai-infrastructure/project-manager/tasks/README.md`: the "Epics and phases" section, "Lazy creation" subsection at lines 88-90 (Deliverable 3 target).

## Related tasks and ADRs

- ADR-041: the decision implemented here (Option D: eager-forming-epic discipline plus advisory check). Decision 1 = recipe/convention discipline; decision 2 = the etl check; decision 3 = ADR-036 rollup semantics unchanged.
- ADR-036: the consistency-check family the new check joins; its rollup semantics are unchanged here (do not amend them).
- ADR-030: the create-department recipe contract being extended with the forming-epic step (see its 2026-06-14 forward-pointer).
- ADR-035 / ADR-039: the owned-but-advisory enforcement model the check follows (warn-only).
- COR-T-050: filed the `API-E-001` epic that fixed the surfaced instance; this task guards against recurrence and must not regress its blocked-surface / STATUS work.

## Hard rules

- **Warn-only, no status change.** The new check is additive and advisory. The derived `current_phase` (currently 2), `next_step`, roadmap phase/epic/department statuses, and the blocked surface must be byte-for-byte unchanged for the current repo state. If any of those would change, you have over-reached the scope; stop and escalate.
- **Count epic files directly, not via `collect_roadmap_from_files`.** The pinned epic-count source is the per-department `epics/*.yml` file count (excluding `.next-epic-id`). Using `collect_roadmap_from_files` would undercount standalone epics and fire a false warning; do not use it as the count source.
- **No epic template file.** Deliverable 2 generates the forming epic inline from the recipe inputs; it does NOT add a file under `ai-infrastructure/project-manager/templates/department/`.
- **Mind the path conventions.** Inside `ai-infrastructure/project-manager/`, workspace-local references use the `./` prefix; references to the root-staying shared tree (`.claude/`, `docs/ai-orchestration/`) use bare paths with no `./` prefix (per `ai-infrastructure/project-manager/CLAUDE.md`). Match the surrounding file's convention when you edit each target.

## Verification expectations

Report exactly what was verified by code inspection versus by run, with no fabricated runs (ADR-003 compose-only; the COR-04 fabricated-run failure mode). Specifically:

- **Clean pass for current state.** Confirm that for the current repo, both existing departments (`database`, `backend-api`) now have at least one epic, so `no_epic_warning` is `null` for every department and no warning renders (the ADR-041 instance was already fixed by filing `API-E-001`).
- **Derived statuses unchanged.** Confirm the derived `current_phase` (2), `next_step`, roadmap statuses, and the blocked surface are unchanged by this change. The check must be purely additive.
- **Warning-fires path.** Verify the warning-fires behaviour by code inspection, or by a temporary scenario that you immediately revert. Do NOT leave any test epic removed or any temporary edit on disk.
- **Render gate.** The dashboard is already running for the orchestrator's render gate; you do not need to run a browser. Note in your report that the render is the orchestrator's gate to confirm visually.

## Executor pointer

You are the dispatched `executor` (ADR-028). Universal executor conventions (the six-section report shape, the dual-channel report write, the compose-only run policy, git boundaries, and the repo writing rules) live in `docs/ai-orchestration/roles/EXECUTOR-ROLE.md` and the repo-root `CLAUDE.md`; follow them without restating them. Write your closing report to `.claude/artifacts/handoffs/COR-T-051-KICKOFF-REPORT.md` per EXECUTOR-ROLE.md, section "Report shape".
