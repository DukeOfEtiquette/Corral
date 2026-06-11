# COR-T-025 - Implement per-department task trees (ADR-031 cascade)

## Target

This is **ai-infrastructure** work (ADR-005): a coordinator / agent-development deliverable that executes the implementation cascade specified by `ai-infrastructure/project-manager/decisions/ADR-031-per-department-task-trees.md`. ADR-031 reverses ADR-027 Fork B's single shared task pool and adopts per-department task trees (rogue-faithful): every workspace (the `project-manager` coordinator and each department) owns its own `tasks/` tree with its own ID prefix and `.next-task-id` counter; a task's department is implied by the tree it lives in, and the `dept:<slug>` label is applied at the dogfood import (ADR-008), not hand-applied in the markdown era. Your job is to land the full cascade across the template, the two live department workspaces, the relocated task, the dashboard ETL, and the coordinator/repo prose. The ADR is the spec you execute against; you do not re-decide anything it settled.

## Decisions resolved by the Orchestrator

- **Task-ID prefix is a new template token AND a new operator argument.** Introduce a `{{DEPT_TASK_PREFIX}}` template token, sourced from a new fourth `/create-department` operator argument `<TASK-PREFIX>`, parallel to the existing `<OBS-PREFIX>` (operator-supplied, deliberately not auto-derived from the slug). The token VALUE is the bare department code (for example `DB`, `API`); template text writes full task IDs as `{{DEPT_TASK_PREFIX}}-T-NNN`. Observation prefix and task prefix remain independent operator inputs. (Both live departments happen to use the same code for both: database = `DB`, backend-api = `API`.)
- **`.next-task-id` format and seeding.** `.next-task-id` holds the next unallocated NNN as a plain integer (per `ai-infrastructure/project-manager/tasks/README.md`). The template scaffold seeds `tasks/.next-task-id` to `1`. The live `database/tasks/.next-task-id` is seeded to `2` (because DB-T-001 is already consumed by the relocated task). The live `backend-api/tasks/.next-task-id` is seeded to `1` (empty tree).
- **Coordinator `.next-task-id` stays `26`; do NOT edit it.** ID 24 (freed when COR-T-024 relocates to DB-T-001) becomes a permanent gap. IDs are never reused (`tasks/README.md`). This resolves a tension: ADR-031 Consequences says the coordinator id "reverts accordingly," but COR-T-025 already consumed id 25, so a literal revert would conflict with the never-reuse rule. The never-reuse convention wins; the gap is fine.
- **COR-T-024 -> DB-T-001 relocation specifics.** `git mv ai-infrastructure/project-manager/tasks/backlog/COR-T-024-postgres-schema.md` to `ai-infrastructure/database/tasks/backlog/DB-T-001-postgres-schema.md`. Set frontmatter `id: DB-T-001`. STRIP the `dept:database` label (set `labels: []`): under ADR-031 the tree is the partition and the `dept:<slug>` label is applied at the dogfood import (ADR-008), not hand-applied in the markdown era, so a department-tree task carries no hand-applied dept label. Keep title, priority, schema_version, created, and the Description body unchanged; bump `updated` to 2026-06-11; append one dated activity-log line noting the relocation/rename from COR-T-024 per ADR-031.
- **Empty state dirs are made git-trackable with `.gitkeep`.** Git does not track empty directories. Each empty task state directory (`backlog/`, `in-progress/`, `blocked/`, `done/`) gets a `.gitkeep` file, alongside the `.next-task-id` file. This applies to the template scaffold (all four state dirs) and the two live department trees: database's `backlog/` instead holds `DB-T-001-...md` so it needs no `.gitkeep`; database's other three state dirs and all four of backend-api's state dirs get `.gitkeep`.
- **STATUS.md history is not rewritten.** Update only live forward-looking prose in `ai-infrastructure/project-manager/STATUS.md` (the "Next step" reference to COR-T-024 -> DB-T-001). Historical `recent_updates` entries that describe the now-reversed shared pool (including the ADR-031 filing entry) are settled history and are left verbatim, exactly as `done/` tasks are left alone.
- **etl.py reads every workspace tree.** Update `ai-infrastructure/project-manager/dashboard/etl.py` to read every workspace's `tasks/` tree (coordinator `ai-infrastructure/project-manager/tasks/` plus each existing department `ai-infrastructure/<dept>/tasks/`), attributing each task to its workspace by the tree it lives in rather than by a `dept:` label filter. Preserve the `data.json` contract exactly (same field names and shapes: overall task counts and per-department `task_counts`); per-department counts now come from that department's own tree; overall counts are the union across all trees. The `collect_tasks` / `compute_task_counts` / `DEPARTMENTS_ROSTER` functions are the relevant seams. Verify the dashboard builds under docker compose (ADR-003).
- **ADRs are not edited.** ADR-031/027/030/021 already carry the accepted decision and their forward-pointer notes (added in commit ca0afe9). The `decisions/` tree is out of scope; do not touch any ADR.

## Deliverables

Land the full ADR-031 implementation cascade, in five groups. All five are required for completion.

**Group 1: Template + recipe.**
- Add a `tasks/` tree to `ai-infrastructure/project-manager/templates/department/`: `tasks/.next-task-id` seeded to `1`; `tasks/backlog/.gitkeep`, `tasks/in-progress/.gitkeep`, `tasks/blocked/.gitkeep`, `tasks/done/.gitkeep`.
- Rewrite the template `CLAUDE.md` "Tasks" section (currently states the workspace has NO own `tasks/` directory) to state the department owns a `./tasks/` tree allocating `{{DEPT_TASK_PREFIX}}-T-NNN` IDs from its own `./tasks/.next-task-id`, and fix the Pointers table row that currently points at the shared coordinator pool.
- Re-point the template `orchestrator-command.md`: Phase 3 survey reads the department's OWN `./tasks/` tree (not the coordinator pool filtered by `dept:` label); Phase 4 drop the "(Filtered to dept:...)" note; the "Add a new task" direction allocates from `./tasks/.next-task-id` and drafts in `./tasks/backlog/` with a `{{DEPT_TASK_PREFIX}}-T-NNN` id; the final Notes bullet about the shared-pool filter is rewritten; the generic `COR-T-NNN` placeholders in the typical-directions list become `{{DEPT_TASK_PREFIX}}-T-NNN`; the "Tasks live in markdown" note paths are repointed.
- Sweep shared-pool language from the template `README.md` and `STATUS.md`.
- Update `.claude/commands/create-department.md`: add the fourth `<TASK-PREFIX>` input and a `{{DEPT_TASK_PREFIX}}` token-table row; add the `tasks/` tree to "What this command creates"; remove the "No `tasks/` directory" bullet from "What this command does NOT create"; reframe the "dept:<slug> label reservation" section so the label is applied at the dogfood import (derived from the tree) rather than tagging pool tasks in the markdown era; update the example invocation to include the task prefix.

**Group 2: Two live department trees + command repoints.**
- Create `ai-infrastructure/database/tasks/`: `.next-task-id` = `2`; state dirs per the `.gitkeep` decision (database's `backlog/` receives DB-T-001 in Group 3, so no `.gitkeep` there; `in-progress/`, `blocked/`, `done/` each get a `.gitkeep`).
- Create `ai-infrastructure/backend-api/tasks/`: `.next-task-id` = `1`; four state dirs (`backlog/`, `in-progress/`, `blocked/`, `done/`), each with a `.gitkeep`.
- Re-point `.claude/commands/database-orchestrator.md` and `.claude/commands/backend-api-orchestrator.md` Phase 3 surveys (and the parallel "Add a new task" / Notes lines) to each department's OWN `./tasks/` tree with its concrete prefix (`DB-T`, `API-T`). These are stamped instances, so write the concrete prefixes, NOT the `{{DEPT_TASK_PREFIX}}` token.
- Sweep shared-pool language from `ai-infrastructure/database/CLAUDE.md`, `ai-infrastructure/database/README.md`, `ai-infrastructure/database/STATUS.md`, `ai-infrastructure/backend-api/CLAUDE.md`, `ai-infrastructure/backend-api/README.md`, and `ai-infrastructure/backend-api/STATUS.md` (repoint each to the department's own tree; database/STATUS.md "Next step" points at DB-T-001 in its own backlog; backend-api/STATUS.md notes an empty backlog tree).

**Group 3: Relocate COR-T-024 to DB-T-001** per the "COR-T-024 -> DB-T-001 relocation specifics" decision above (`git mv`, set `id: DB-T-001`, strip the label to `labels: []`, bump `updated`, append the dated relocation activity-log line, keep everything else verbatim).

**Group 4: Dashboard ETL** per the "etl.py reads every workspace tree" decision above; verify the dashboard builds under docker compose and the emitted `data.json` renders all three trees with correct per-tree counts and an unchanged JSON contract.

**Group 5: Sweep coordinator/repo shared-pool language.**
- Reframe `ai-infrastructure/project-manager/tasks/README.md` from "the single COR-T pool" to the per-workspace convention (each workspace owns a `tasks/` tree with its own prefix and `.next-task-id`; the tree is the department partition; the `dept:<slug>` label is applied at import).
- Reframe the "Tasks" section of `ai-infrastructure/project-manager/CLAUDE.md` (the line stating "All project work items live in `./tasks/`") so it scopes `./tasks/` to the COORDINATOR's own work items and notes each department owns its own tree (the existing coordinator-write-authority section already grants cross-workspace edits).
- Lightly clarify the repo-root `README.md` pointer-table row if it implies a single project-wide pool.
- Update `ai-infrastructure/project-manager/STATUS.md` "Next step" per the STATUS deltas section below.

## Files in scope

You may modify exactly these paths. Several are NEW files (created), several are repointed prose, and one is a `git mv`.

Group 1 (template + recipe):
- `ai-infrastructure/project-manager/templates/department/tasks/.next-task-id` (NEW, content: `1`)
- `ai-infrastructure/project-manager/templates/department/tasks/backlog/.gitkeep` (NEW)
- `ai-infrastructure/project-manager/templates/department/tasks/in-progress/.gitkeep` (NEW)
- `ai-infrastructure/project-manager/templates/department/tasks/blocked/.gitkeep` (NEW)
- `ai-infrastructure/project-manager/templates/department/tasks/done/.gitkeep` (NEW)
- `ai-infrastructure/project-manager/templates/department/CLAUDE.md`
- `ai-infrastructure/project-manager/templates/department/orchestrator-command.md`
- `ai-infrastructure/project-manager/templates/department/README.md`
- `ai-infrastructure/project-manager/templates/department/STATUS.md`
- `.claude/commands/create-department.md`

Group 2 (live trees + command repoints):
- `ai-infrastructure/database/tasks/.next-task-id` (NEW, content: `2`)
- `ai-infrastructure/database/tasks/in-progress/.gitkeep`, `ai-infrastructure/database/tasks/blocked/.gitkeep`, `ai-infrastructure/database/tasks/done/.gitkeep` (NEW; database `backlog/` gets DB-T-001 from Group 3, no `.gitkeep` there)
- `ai-infrastructure/backend-api/tasks/.next-task-id` (NEW, content: `1`)
- `ai-infrastructure/backend-api/tasks/backlog/.gitkeep`, `ai-infrastructure/backend-api/tasks/in-progress/.gitkeep`, `ai-infrastructure/backend-api/tasks/blocked/.gitkeep`, `ai-infrastructure/backend-api/tasks/done/.gitkeep` (NEW)
- `.claude/commands/database-orchestrator.md`
- `.claude/commands/backend-api-orchestrator.md`
- `ai-infrastructure/database/CLAUDE.md`
- `ai-infrastructure/database/README.md`
- `ai-infrastructure/database/STATUS.md`
- `ai-infrastructure/backend-api/CLAUDE.md`
- `ai-infrastructure/backend-api/README.md`
- `ai-infrastructure/backend-api/STATUS.md`

Group 3 (relocation):
- `ai-infrastructure/project-manager/tasks/backlog/COR-T-024-postgres-schema.md` -> `git mv` to `ai-infrastructure/database/tasks/backlog/DB-T-001-postgres-schema.md`

Group 4 (ETL):
- `ai-infrastructure/project-manager/dashboard/etl.py`

Group 5 (coordinator/repo prose):
- `ai-infrastructure/project-manager/tasks/README.md`
- `ai-infrastructure/project-manager/CLAUDE.md`
- `README.md` (repo root; light pointer-row clarification only)
- `ai-infrastructure/project-manager/STATUS.md` (Next step delta + universal hygiene)

## Files out of scope

Do NOT modify these:
- The entire `ai-infrastructure/project-manager/decisions/` tree (ADR-031/027/030/021 and all other ADRs): they already carry the decision and forward-pointer notes (commit ca0afe9). Do not edit any ADR.
- The dogfood-era import behaviour (ADR-008) and the moment-of-label-application logic: future work, not implemented here.
- The Corral web app's label/board implementation (Phase 4) and any web-app code under `app/` or elsewhere.
- Settled `tasks/done/` history across all trees, and the historical `recent_updates` entries in any STATUS.md: leave verbatim.
- The coordinator's own COR-T task files' `dept:` labels (for example COR-T-025's `dept:agent-development`): do NOT retroactively strip them. Only the relocated DB-T-001's label is stripped, as part of its in-scope relocation.
- Coordinator `ai-infrastructure/project-manager/tasks/.next-task-id`: stays `26`, not edited.

## References

Read these in this order; they ground the cascade:
- `ai-infrastructure/project-manager/decisions/ADR-031-per-department-task-trees.md` - the spec this task executes against (read the Decision and Consequences end-to-end).
- `ai-infrastructure/project-manager/tasks/README.md` - the task convention being reframed per-workspace; also the `.next-task-id` integer-format source.
- `ai-infrastructure/project-manager/templates/department/` - template source: `CLAUDE.md`, `README.md`, `STATUS.md`, `OBSERVATIONS.md`, `orchestrator-command.md`, `decisions/README.md`.
- `.claude/commands/create-department.md` - the recipe gaining the fourth argument and the `tasks/` tree.
- `.claude/commands/database-orchestrator.md` and `.claude/commands/backend-api-orchestrator.md` - the two live commands to repoint.
- `ai-infrastructure/project-manager/dashboard/etl.py` - the ETL to update; `collect_tasks` / `compute_task_counts` / `DEPARTMENTS_ROSTER` are the relevant seams.
- `ai-infrastructure/project-manager/decisions/ADR-027-ai-infrastructure-workspace-structure.md` - Fork B, the reversed decision; context only, do not edit.
- `ai-infrastructure/project-manager/decisions/ADR-030-department-scaffold-contract-create-department-recipe.md` - scaffold contract; context only, do not edit.
- `ai-infrastructure/project-manager/decisions/ADR-003-docker-compose-runtime.md` - compose-only run policy for the etl verify.

## Related tasks and ADRs

- ADR-031: the spec this task executes against (per-department task trees).
- ADR-027 (Fork B): the single-shared-pool decision being reversed; explains why the cascade exists.
- ADR-030: the scaffold contract amended to include a `tasks/` tree; forward-pointer already added.
- ADR-021: board-mapping timing clarified (dept label applied at import); forward-pointer already added.
- ADR-008: the dogfood import where the `dept:<slug>` label is applied from the tree; out of scope, but the reason markdown-era tasks carry no hand-applied dept label.
- ADR-001: the single-pool/per-label-board app model preserved and relocated to the app layer.
- ADR-003: compose-only run policy governing the etl.py verification.
- COR-T-023: stood up the database and backend-api departments; its smoke tests surfaced the missing-task-home problem.
- COR-T-024 -> DB-T-001: the task being relocated into the database tree.
- COR-T-014 / COR-T-017 / COR-T-020 / COR-T-022: built and extended dashboard/etl.py; context for the ETL change.

## STATUS deltas

Task-specific: in `ai-infrastructure/project-manager/STATUS.md` "Next step", replace the reference to "COR-T-024 (`dept:database`, in backlog), ready to be picked up through the `/database-orchestrator`" with a reference to DB-T-001 living in `ai-infrastructure/database/tasks/backlog/`, surveyed via `/database-orchestrator`'s own task tree. Leave all historical `recent_updates` entries verbatim (do not rewrite the shared-pool descriptions in past entries).

The department STATUS.md "Next step" edits (`ai-infrastructure/database/STATUS.md`, `ai-infrastructure/backend-api/STATUS.md`) are separate deliverables listed under Group 2 / Files in scope, not part of this coordinator-STATUS delta.

Universal STATUS hygiene per `docs/ai-orchestration/roles/WORKER-ROLE.md` applies as always: bump `last_updated` to 2026-06-11, and prepend one `recent_updates` entry summarising the COR-T-025 cascade.

## Hard rules

These are task-specific guards beyond the universal conventions (the universal writing rules, the docker-compose-only run policy, git boundaries, and the report shape live in `./CLAUDE.md`, `ai-infrastructure/project-manager/CLAUDE.md`, and `docs/ai-orchestration/roles/WORKER-ROLE.md`; reference them, they are not restated here).

- **Tokens live ONLY in the template and the recipe.** No literal `{{DEPT_TASK_PREFIX}}` or any other unsubstituted `{{...}}` token may leak into the live `ai-infrastructure/database/` or `ai-infrastructure/backend-api/` files. Those are stamped instances; write concrete prefixes (`DB-T`, `API-T`) there. The `{{DEPT_TASK_PREFIX}}` token appears only under `ai-infrastructure/project-manager/templates/department/` and `.claude/commands/create-department.md`.
- **Use `git mv` for the relocation.** Group 3 moves COR-T-024 with `git mv` (preserve history), not a delete-plus-create.
- **Do not rewrite settled history.** Historical STATUS `recent_updates` entries, settled `tasks/done/` files, and the coordinator's own COR-T `dept:` labels are left verbatim. Only DB-T-001's label is stripped, as part of its in-scope relocation.
- **Preserve the `data.json` contract exactly.** The ETL change must keep the same field names and shapes; only the data source (many trees instead of one label-filtered pool) changes.
- **Path conventions inside the coordinator workspace.** Per `ai-infrastructure/project-manager/CLAUDE.md`, references inside the `ai-infrastructure/project-manager/` workspace use workspace-relative `./X`; references to the root-staying shared tree (`.claude/`, `docs/ai-orchestration/`, repo-root `README.md`) use a bare repo-root-relative path. Honour the convention already in force in each file you edit.

## Verification expectations

Confirm and report each of these in the closing "Build / verification status" section:
- A fresh `/database-orchestrator` survey reads `ai-infrastructure/database/tasks/` and finds DB-T-001 (not the coordinator pool); a fresh `/backend-api-orchestrator` survey reads `ai-infrastructure/backend-api/tasks/` and finds an empty backlog.
- The dashboard ETL builds under docker compose and the emitted `data.json` renders all three trees (coordinator + database + backend-api) with correct per-tree counts; the JSON contract (field names and shapes) is unchanged.
- No literal `{{DEPT_TASK_PREFIX}}` or any other unsubstituted `{{...}}` token leaks into the live `database/` or `backend-api/` files (tokens remain ONLY in `templates/department/` and the create-department recipe).
- A `git grep` over the swept live docs / commands / templates finds no remaining "shared ... task pool" / "NO own tasks" / dept-label-filter-the-pool phrasing outside settled `tasks/done/` history, historical STATUS `recent_updates` entries, and the ADRs' own records.

## Worker pointer

You are the dispatched `worker-agent` (ADR-028). Universal worker conventions live in `docs/ai-orchestration/roles/WORKER-ROLE.md`. Write your closing report to `./.claude/artifacts/handoffs/COR-T-025-KICKOFF-REPORT.md` per `WORKER-ROLE.md`, section "Report shape" (six sections, dual-channel: print to chat and write to file).
