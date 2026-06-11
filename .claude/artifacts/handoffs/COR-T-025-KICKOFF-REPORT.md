## Deliverables completed

All five groups completed.

**Group 1: Template + recipe**
- Created `ai-infrastructure/project-manager/templates/department/tasks/.next-task-id` (seeded to `1`).
- Created `ai-infrastructure/project-manager/templates/department/tasks/backlog/.gitkeep`, `in-progress/.gitkeep`, `blocked/.gitkeep`, `done/.gitkeep`.
- Rewrote `ai-infrastructure/project-manager/templates/department/CLAUDE.md` "Tasks" section: removed the "NO own tasks/" shared-pool text; now states the workspace owns `./tasks/` with `{{DEPT_TASK_PREFIX}}-T-NNN` IDs. Fixed the Pointers table row to point at `./tasks/`.
- Updated `ai-infrastructure/project-manager/templates/department/orchestrator-command.md`: Phase 3 survey reads `ai-infrastructure/{{DEPT_SLUG}}/tasks/` (not the coordinator pool); Phase 4 label removed "(Filtered to dept:...)"; "Add a new task" direction allocates from `ai-infrastructure/{{DEPT_SLUG}}/tasks/.next-task-id`; "Pick up/Block/Resolve" directions use `{{DEPT_TASK_PREFIX}}-T-NNN`; Notes bullet rewritten to "Tasks are tracked in ai-infrastructure/{{DEPT_SLUG}}/tasks/".
- Updated `ai-infrastructure/project-manager/templates/department/README.md` and `STATUS.md` to sweep shared-pool language.
- Updated `.claude/commands/create-department.md`: added fourth `<TASK-PREFIX>` argument; added `{{DEPT_TASK_PREFIX}}` to token table; added `tasks/` tree to "What this command creates"; removed "No tasks/ directory" bullet from "What this command does NOT create"; reframed the `dept:<slug>` label section to note the label is applied at dogfood import, not hand-applied.

**Group 2: Two live department trees + command repoints**
- Created `ai-infrastructure/database/tasks/.next-task-id` (content: `2`).
- Created `ai-infrastructure/database/tasks/in-progress/.gitkeep`, `blocked/.gitkeep`, `done/.gitkeep` (no `.gitkeep` in `backlog/` because DB-T-001 lands there from Group 3).
- Created `ai-infrastructure/backend-api/tasks/.next-task-id` (content: `1`).
- Created `ai-infrastructure/backend-api/tasks/backlog/.gitkeep`, `in-progress/.gitkeep`, `blocked/.gitkeep`, `done/.gitkeep`.
- Repointed `.claude/commands/database-orchestrator.md`: Phase 3 survey reads `ai-infrastructure/database/tasks/`; Phase 4 task line updated; "Add a new task" allocates from `ai-infrastructure/database/tasks/.next-task-id` with `DB-T-NNN` format; Notes bullet rewritten; "Pick up/Block/Resolve" directions use `DB-T-NNN`.
- Repointed `.claude/commands/backend-api-orchestrator.md`: same pattern, uses `ai-infrastructure/backend-api/tasks/` and `API-T-NNN`.
- Updated `ai-infrastructure/database/CLAUDE.md`, `README.md`: swept shared-pool language, repointed to `./tasks/` and `DB-T-NNN`.
- Updated `ai-infrastructure/database/STATUS.md`: bumped `last_updated` to 2026-06-11, added `recent_updates` entry, repointed "Next step" to `DB-T-001` in `ai-infrastructure/database/tasks/backlog/`.
- Updated `ai-infrastructure/backend-api/CLAUDE.md`, `README.md`: swept shared-pool language, repointed to `./tasks/` and `API-T-NNN`.
- Updated `ai-infrastructure/backend-api/STATUS.md`: bumped `last_updated` to 2026-06-11, added `recent_updates` entry, repointed "Next step" to note empty backlog tree.

**Group 3: Relocate COR-T-024 to DB-T-001**
- `git mv ai-infrastructure/project-manager/tasks/backlog/COR-T-024-postgres-schema.md ai-infrastructure/database/tasks/backlog/DB-T-001-postgres-schema.md`.
- Updated frontmatter: `id: DB-T-001`, `labels: []` (stripped `dept:database`), `updated: 2026-06-11`.
- Appended activity-log line noting the relocation from COR-T-024 per ADR-031.
- Title, priority, schema_version, created, and Description body left unchanged.

**Group 4: Dashboard ETL**
- Updated `ai-infrastructure/project-manager/dashboard/etl.py`:
  - Added `collect_all_tasks()` function that reads coordinator tree plus every department's tree, returning `(all_tasks_combined, per_workspace_tasks)`.
  - Updated `run_etl()` to call `collect_all_tasks()` instead of `collect_tasks(tasks_root)`.
  - Department roster loop now uses `per_workspace_tasks.get(slug, [])` for per-department counts (no label filtering).
  - `workspace_details` coordinator section uses `per_workspace_tasks.get(COORDINATOR_SLUG, [])`.
  - `workspace_details` department loop uses `per_workspace_tasks.get(slug, [])`.
  - Module docstring updated for source (d).
  - JSON contract fields unchanged: same top-level keys, same field shapes.
- ETL runs correctly (verified locally): coordinator 24 tasks (1 in-progress = COR-T-025, 23 done); database 1 backlog (DB-T-001); backend-api 0 tasks.
- `docker compose build` succeeded under `ai-infrastructure/project-manager/dashboard/`.

**Group 5: Sweep coordinator/repo shared-pool language**
- Rewrote `ai-infrastructure/project-manager/tasks/README.md`: reframed from single COR-T pool to per-workspace convention; added per-workspace-trees section explaining ADR-031; updated File format section to use `<PREFIX>-T-NNN` pattern; updated Rules section; updated migration mapping note to explain import-time label application.
- Updated `ai-infrastructure/project-manager/CLAUDE.md` "Tasks" section: scoped `./tasks/` to coordinator's own COR-T work items; added note that each department owns its own tree per ADR-031. Updated Pointers table row.
- Updated `README.md` (repo root): clarified the task tree pointer-table row.
- Updated `ai-infrastructure/project-manager/STATUS.md`: bumped `last_updated` to 2026-06-11; prepended one `recent_updates` entry summarising COR-T-025 cascade; replaced "COR-T-024 (dept:database, in backlog)" in the "Next step" narrative with "DB-T-001 in ai-infrastructure/database/tasks/backlog/".

## Decisions made

All decisions were pre-resolved by the Orchestrator and pinned in the kickoff. No new decisions made during execution. Specific implementations:
- `{{DEPT_TASK_PREFIX}}` token appears only in `templates/department/` files and `.claude/commands/create-department.md`. No token leakage into live department files (verified by grep).
- Template `STATUS.md` "Next step" repointed to generic "File the first task in `ai-infrastructure/{{DEPT_SLUG}}/tasks/backlog/`" rather than "Pick up from shared pool".
- ETL `compute_task_counts` function was kept as-is (its `label_prefix` parameter still exists for potential reuse); the call sites no longer pass `label_prefix` for per-department counts, using direct tree iteration instead.

## Surprises

- `ai-infrastructure/project-manager/tasks/backlog/COR-T-025-implement-per-department-task-trees.md` was already staged as moved to `in-progress/` before this session began (visible in `git status`). This is the expected in-progress state for the task being executed. No action needed; the task file was not touched (per kickoff rules, task transitions are the Orchestrator's job).

## Follow-ups

- COR-T candidate: The `compute_task_counts` function in `etl.py` retains an unused `label_prefix` parameter that is no longer called for per-department counts. It may be useful at the dogfood import layer (ADR-008) or for future coordinator-only counts. If the label-filter path is no longer needed, a cleanup pass could remove the parameter. Triage to orchestrator.
- COR-T candidate: The `WATCH_PATTERNS` list in `etl.py` still only covers `ai-infrastructure/` and `.claude/commands/`. Now that department tasks live under `ai-infrastructure/`, they are already covered by the existing `ai-infrastructure/` pattern - no immediate gap, but worth confirming during the next ETL review pass. Triage to orchestrator.
- COR-T candidate: The `count_observations` function in `etl.py` uses a `COR-NN` pattern regex. Department observations use prefixes like `DB-NN` and `API-NN`. The function is only called on the coordinator's `OBSERVATIONS.md` in the current code, so there is no bug, but if per-department observation counts are added to the ETL later, the function will need a generalised pattern. Triage to orchestrator.

## Files touched

Group 1 (template + recipe):
- `/home/adam/src/corral/ai-infrastructure/project-manager/templates/department/tasks/.next-task-id` (NEW)
- `/home/adam/src/corral/ai-infrastructure/project-manager/templates/department/tasks/backlog/.gitkeep` (NEW)
- `/home/adam/src/corral/ai-infrastructure/project-manager/templates/department/tasks/in-progress/.gitkeep` (NEW)
- `/home/adam/src/corral/ai-infrastructure/project-manager/templates/department/tasks/blocked/.gitkeep` (NEW)
- `/home/adam/src/corral/ai-infrastructure/project-manager/templates/department/tasks/done/.gitkeep` (NEW)
- `/home/adam/src/corral/ai-infrastructure/project-manager/templates/department/CLAUDE.md` (edited)
- `/home/adam/src/corral/ai-infrastructure/project-manager/templates/department/orchestrator-command.md` (edited)
- `/home/adam/src/corral/ai-infrastructure/project-manager/templates/department/README.md` (edited)
- `/home/adam/src/corral/ai-infrastructure/project-manager/templates/department/STATUS.md` (edited)
- `/home/adam/src/corral/.claude/commands/create-department.md` (edited)

Group 2 (live trees + command repoints):
- `/home/adam/src/corral/ai-infrastructure/database/tasks/.next-task-id` (NEW)
- `/home/adam/src/corral/ai-infrastructure/database/tasks/in-progress/.gitkeep` (NEW)
- `/home/adam/src/corral/ai-infrastructure/database/tasks/blocked/.gitkeep` (NEW)
- `/home/adam/src/corral/ai-infrastructure/database/tasks/done/.gitkeep` (NEW)
- `/home/adam/src/corral/ai-infrastructure/backend-api/tasks/.next-task-id` (NEW)
- `/home/adam/src/corral/ai-infrastructure/backend-api/tasks/backlog/.gitkeep` (NEW)
- `/home/adam/src/corral/ai-infrastructure/backend-api/tasks/in-progress/.gitkeep` (NEW)
- `/home/adam/src/corral/ai-infrastructure/backend-api/tasks/blocked/.gitkeep` (NEW)
- `/home/adam/src/corral/ai-infrastructure/backend-api/tasks/done/.gitkeep` (NEW)
- `/home/adam/src/corral/.claude/commands/database-orchestrator.md` (edited)
- `/home/adam/src/corral/.claude/commands/backend-api-orchestrator.md` (edited)
- `/home/adam/src/corral/ai-infrastructure/database/CLAUDE.md` (edited)
- `/home/adam/src/corral/ai-infrastructure/database/README.md` (edited)
- `/home/adam/src/corral/ai-infrastructure/database/STATUS.md` (edited)
- `/home/adam/src/corral/ai-infrastructure/backend-api/CLAUDE.md` (edited)
- `/home/adam/src/corral/ai-infrastructure/backend-api/README.md` (edited)
- `/home/adam/src/corral/ai-infrastructure/backend-api/STATUS.md` (edited)

Group 3 (relocation):
- `/home/adam/src/corral/ai-infrastructure/project-manager/tasks/backlog/COR-T-024-postgres-schema.md` -> git mv to `/home/adam/src/corral/ai-infrastructure/database/tasks/backlog/DB-T-001-postgres-schema.md` (edited frontmatter + activity log)

Group 4 (ETL):
- `/home/adam/src/corral/ai-infrastructure/project-manager/dashboard/etl.py` (edited)

Group 5 (coordinator/repo prose):
- `/home/adam/src/corral/ai-infrastructure/project-manager/tasks/README.md` (edited)
- `/home/adam/src/corral/ai-infrastructure/project-manager/CLAUDE.md` (edited)
- `/home/adam/src/corral/README.md` (edited)
- `/home/adam/src/corral/ai-infrastructure/project-manager/STATUS.md` (edited)

Report file (dual-channel):
- `/home/adam/src/corral/.claude/artifacts/handoffs/COR-T-025-KICKOFF-REPORT.md` (this file)

## Build / verification status

**ETL syntax:** `python3 -c "import ast; ast.parse(...)"` confirmed `etl.py` parses without error.

**ETL functional run (local):** ETL ran against the live repo and produced correct output:
- Coordinator: 24 tasks total (0 backlog, 1 in-progress = COR-T-025, 0 blocked, 23 done). Correct: COR-T-024 is gone from coordinator pool; it is now DB-T-001 in the database tree.
- Database: 1 task total (1 backlog = DB-T-001, rest zero). Correct.
- Backend-api: 0 tasks total. Correct (empty tree).
- JSON contract fields unchanged: `['meta', 'roadmap', 'org_chart', 'departments', 'coordinator', 'workspace_details', 'recent_activity']`.

**Docker compose build:** `docker compose build` under `ai-infrastructure/project-manager/dashboard/` completed successfully (Image `dashboard-dashboard` built).

**Token leakage check:** `grep -rn "{{...}}"` over `ai-infrastructure/database/` and `ai-infrastructure/backend-api/` returned zero matches. Tokens remain only in `templates/department/` and `.claude/commands/create-department.md`.

**Shared-pool language sweep:** `grep -rn "shared.*task pool|NO own.*tasks|filtering for.*dept:"` over all live non-ADR non-done files returned only one match: the ADR-027 citation in `create-department.md`'s References section (an ADR title reference, not a live instruction).

**Em/en dash check:** No em dashes (U+2014) or en dashes (U+2013) found in any edited file.

**`/database-orchestrator` survey readiness:** The command now reads `ai-infrastructure/database/tasks/backlog/`, `in-progress/`, `blocked/`. DB-T-001 is in `backlog/`. A fresh survey will find it directly without filtering any shared pool.

**`/backend-api-orchestrator` survey readiness:** The command now reads `ai-infrastructure/backend-api/tasks/`. All state directories exist (with `.gitkeep`). A survey will find an empty backlog, correctly.

**Verification the user should perform after review:**
- Run `docker compose up` in `ai-infrastructure/project-manager/dashboard/` and confirm the rendered dashboard shows correct task counts per department.
- Optionally run `/database-orchestrator` and `/backend-api-orchestrator` smoke tests to confirm they survey the correct trees.
