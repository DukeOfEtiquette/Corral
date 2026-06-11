# Stamp the `database` department workspace (first of two create-department runs under COR-T-023)

## Target

This is an **AI-infrastructure** task (domain 2, per ADR-005). Stamping a department workspace is AI-infrastructure scaffolding work: you are creating the empty scaffold that a department will later use to drive web-app (domain 1) work. The act of creating the scaffold is domain 2; no domain-1 web-app code is produced here.

The artifact in scope is the new `database` department workspace at `ai-infrastructure/database/`, plus its stamped-out orchestrator command at `.claude/commands/database-orchestrator.md`. The work is purely mechanical token substitution: copy each template file from `ai-infrastructure/project-manager/templates/department/` into its output location, substituting every `{{TOKEN}}` with the resolved value pinned below. The templates are the source of truth for structure and prose; you author nothing and design nothing.

This is the FIRST of two sequential `/create-department` runs under task COR-T-023. This kickoff covers ONLY the `database` department. The `backend-api` department is a separate, later kickoff and is entirely out of scope here.

## Decisions resolved by the Orchestrator

- **Scope of this run: `database` only.** This kickoff stamps exactly one department, `database`. Do not create, touch, or anticipate the `backend-api` department; it is a separate later kickoff.
- **The work is decision-free token substitution.** Copy each template file verbatim into its output location, replacing every `{{TOKEN}}` with its resolved value. No authoring, design judgement, or prose changes. The templates define the structure and content; you only substitute tokens.
- **Token values (pinned; do not re-derive):**
  - `{{DEPT_SLUG}}` = `database`
  - `{{DEPT_NAME}}` = `Database`
  - `{{DEPT_OBS_PREFIX}}` = `DB`
  - `{{DEPT_SCOPE}}` = `Schema, migrations, seed logic` (the ADR-021 web-app menu "Would own" line for `database`)
  - `{{DATE}}` = `2026-06-10`
- **Precondition satisfied: `database` is a blessed ADR-021 menu entry.** No ADR-021 menu extension is needed; the blessed-menu-slug precondition for `/create-department` (ADR-030 item 4) is already met.
- **File mapping (six output files).** The five workspace template files stamp into `ai-infrastructure/database/` preserving their relative paths. The sixth template, `orchestrator-command.md`, stamps OUT to `.claude/commands/database-orchestrator.md`: it is renamed to the `<slug>-orchestrator.md` form (NOT kept as `orchestrator-command.md`) and placed under `.claude/commands/` (NOT inside the department workspace). This split is the ADR-030 contract (items 1 and 3).
- **The `DB-NN` observation prefix replaces `{{DEPT_OBS_PREFIX}}-NN`.** Wherever the `OBSERVATIONS.md` template uses `{{DEPT_OBS_PREFIX}}-NN` (or `{{DEPT_OBS_PREFIX}}` alone), the stamped output reads `DB-NN` (or `DB`). The same applies to the `{{DEPT_OBS_PREFIX}}` token wherever it appears in `CLAUDE.md` and the orchestrator command.
- **What the recipe does NOT create (already baked into the templates per ADR-028/ADR-029/ADR-027 Fork B).** No `/database-worker` command, no per-department role-doc copies, and no `tasks/` directory inside the workspace. The department uses the shared coordinator task pool tagged `dept:database`. You do not add any of these; you stamp exactly what the templates contain, nothing more.
- **Templates are READ-ONLY inputs.** The template source files at `ai-infrastructure/project-manager/templates/department/` must not be edited, moved, or deleted. You read them and write substituted copies to the output locations.

## Deliverables

- `ai-infrastructure/database/CLAUDE.md` (stamped from `templates/department/CLAUDE.md`)
- `ai-infrastructure/database/README.md` (stamped from `templates/department/README.md`)
- `ai-infrastructure/database/STATUS.md` (stamped from `templates/department/STATUS.md`)
- `ai-infrastructure/database/OBSERVATIONS.md` (stamped from `templates/department/OBSERVATIONS.md`, using the `DB-NN` observation prefix)
- `ai-infrastructure/database/decisions/README.md` (stamped from `templates/department/decisions/README.md`)
- `.claude/commands/database-orchestrator.md` (stamped from `templates/department/orchestrator-command.md`, renamed to the `<slug>-orchestrator.md` form)

Each deliverable is a new file containing zero literal `{{...}}` token strings.

## Files in scope

- `ai-infrastructure/database/CLAUDE.md` (new)
- `ai-infrastructure/database/README.md` (new)
- `ai-infrastructure/database/STATUS.md` (new)
- `ai-infrastructure/database/OBSERVATIONS.md` (new)
- `ai-infrastructure/database/decisions/README.md` (new)
- `.claude/commands/database-orchestrator.md` (new)
- `ai-infrastructure/project-manager/STATUS.md` (universal STATUS hygiene write only; see "STATUS deltas")

## Files out of scope

- The `backend-api` department and all of its files. It is a separate, later kickoff under COR-T-023.
- The template source files under `ai-infrastructure/project-manager/templates/department/`. They are READ-ONLY inputs; do not edit, move, or delete them.
- The other blessed departments (`mcp-server`, `frontend-ui`, `devops`, `agent-development`, `test-design`, `docs-curation`). None are created here.
- The COR-T-023 task file. The Orchestrator transitions tasks; the Worker never edits the task tree (`ai-infrastructure/project-manager/tasks/`).
- Any Phase 2 web-app code (Postgres schema, FastAPI endpoints, seed logic). Only the empty department scaffold is created here; no domain-1 code.

## References

- `ai-infrastructure/project-manager/decisions/ADR-030-department-scaffold-contract-create-department-recipe.md` - the scaffold contract: the file set (item 1), the token convention (item 2), the orchestrator-command stamp-out (item 3), and what the recipe does and does not create.
- `ai-infrastructure/project-manager/decisions/ADR-021-candidate-departments.md` - the blessed menu and the `database` scope line that `{{DEPT_SCOPE}}` resolves to.
- `ai-infrastructure/project-manager/templates/department/CLAUDE.md` - template source; stamp to `ai-infrastructure/database/CLAUDE.md`.
- `ai-infrastructure/project-manager/templates/department/README.md` - template source; stamp to `ai-infrastructure/database/README.md`.
- `ai-infrastructure/project-manager/templates/department/STATUS.md` - template source; stamp to `ai-infrastructure/database/STATUS.md`.
- `ai-infrastructure/project-manager/templates/department/OBSERVATIONS.md` - template source; stamp to `ai-infrastructure/database/OBSERVATIONS.md` (using the `DB-NN` prefix).
- `ai-infrastructure/project-manager/templates/department/decisions/README.md` - template source; stamp to `ai-infrastructure/database/decisions/README.md`.
- `ai-infrastructure/project-manager/templates/department/orchestrator-command.md` - template source; stamp to `.claude/commands/database-orchestrator.md`.

## Related tasks and ADRs

- COR-T-023 - the parent task; this is the first of its two create-department runs (`database` now, `backend-api` next).
- COR-T-013 - built the create-department recipe and the templates you are stamping; this kickoff is the first real exercise of it.
- ADR-030 - the department scaffold contract you stamp to (file set, token convention, stamp-out mapping).
- ADR-021 - the blessed department menu; supplies the `database` scope line.
- ADR-028 - single universal dispatched worker; the reason NO `/database-worker` command is created.
- ADR-029 - shared role docs reused by reference; the reason NO per-department role-doc copies are created.
- ADR-027 - workspace structure; Fork B (shared `dept:`-labeled task pool, so NO `tasks/` directory in the department) and Fork D (the scaffold).

## STATUS deltas

Universal hygiene only. Apply the two universal STATUS steps to `ai-infrastructure/project-manager/STATUS.md` per `./docs/ai-orchestration/roles/WORKER-ROLE.md` (section "Wrap-up STATUS hygiene"):

1. Bump `last_updated` in the frontmatter to `2026-06-10`.
2. Prepend ONE `recent_updates` entry recording that the `database` department workspace and its `/database-orchestrator` command were created.

Do NOT touch the roadmap block or the "Next step" section. The roadmap P2-0 milestone status flip and the "Next step" rewording are deferred to task close (orchestrator-direct, after BOTH departments exist); they are not part of this run.

## Hard rules

- **Token completeness gate.** Every one of the six output files must contain ZERO literal `{{...}}` token strings. Verify with a grep for `{{` across the six output paths; the expected result is no matches. This is the single acceptance gate for the stamping work.
- **Templates stay untouched.** The six template source files under `ai-infrastructure/project-manager/templates/department/` are read-only. Do not edit, move, or delete them.
- **Stamp exactly what the templates contain.** Do not add a `tasks/` directory, a `/database-worker` command, or any role-doc copy. If a template's content surprises you, stamp it faithfully and note the surprise in your report rather than editing it.
- **Output-path discipline.** The five workspace files keep their relative paths under `ai-infrastructure/database/` (note `decisions/README.md` requires creating the `ai-infrastructure/database/decisions/` directory). The orchestrator command is the only file that stamps OUT of the workspace, to `.claude/commands/database-orchestrator.md`.

## Worker pointer

You are the dispatched `worker-agent` (ADR-028). Universal worker conventions (the report shape, file-edit hygiene, the run policy, git boundaries, and the writing rules) live in `./docs/ai-orchestration/roles/WORKER-ROLE.md`; follow them rather than expecting them restated here. Write your closing report to the derived path next to this kickoff per `./docs/ai-orchestration/roles/WORKER-ROLE.md` (section "Report shape", dual-channel).
