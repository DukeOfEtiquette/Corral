# Stamp the `backend-api` department workspace (second of two create-department runs under COR-T-023)

## Target

This is **AI-infrastructure** work (ADR-005). Stamping a department workspace is domain-2 scaffolding: you copy the department template baseline into a new workspace, substituting placeholder tokens. The `backend-api` department will later host web-app (domain-1) work, but the act of creating its empty scaffold is domain-2. No domain-1 code is written in this task.

This kickoff covers the **second of two** sequential `/create-department` runs under task COR-T-023. The first run created the `database` department and is already complete. You create ONLY the `backend-api` department here; do not touch `database` or any of its files.

The work is purely mechanical token substitution. The six template files at `ai-infrastructure/project-manager/templates/department/` are the source of truth for structure and prose. You copy each one to its output path and replace every `{{TOKEN}}` with its resolved value. No authoring, no design judgement: the templates already encode every structural decision (per ADR-030 and ADR-028/ADR-029, baked into the templates).

## Decisions resolved by the Orchestrator

- **Scope is one department, this run only.** Create the `backend-api` department workspace and its orchestrator command. The `database` department (first run) is done; do not modify it. Source: COR-T-023 is two sequential create-department runs; this is run two.
- **The deliverable is mechanical token substitution.** Copy each template file into its output location and substitute every `{{TOKEN}}` with its resolved value. The templates are the source of truth for structure and prose; do not author or redesign content. Source: ADR-030 (the scaffold contract; the recipe stamps templates, it does not invent content).
- **Token values are pinned; do not re-derive them.** Substitute exactly these values everywhere the corresponding token appears:
  - `{{DEPT_SLUG}}` = `backend-api`
  - `{{DEPT_NAME}}` = `Backend API`
  - `{{DEPT_OBS_PREFIX}}` = `API`
  - `{{DEPT_SCOPE}}` = `FastAPI service, auth, invites` (the ADR-021 web-app menu "Would own" line for `backend-api`)
  - `{{DATE}}` = `2026-06-10`
- **The precondition is satisfied.** `backend-api` is a blessed ADR-021 web-app-domain menu entry (`ai-infrastructure/project-manager/decisions/ADR-021-candidate-departments.md`, web-app departments table). No ADR-021 menu extension is needed. Source: ADR-030 item 4 (the recipe's blessed-slug precondition).
- **Five workspace files stamp in-place; the sixth stamps out and is renamed.** The five workspace template files (`CLAUDE.md`, `README.md`, `STATUS.md`, `OBSERVATIONS.md`, `decisions/README.md`) stamp into `ai-infrastructure/backend-api/` preserving their relative paths. The sixth template, `orchestrator-command.md`, stamps OUT to `.claude/commands/backend-api-orchestrator.md` (renamed to the `<slug>-orchestrator.md` form, NOT kept as `orchestrator-command.md`, NOT placed inside the department workspace). Source: ADR-030 items 1, 3, and 4.
- **The `API-NN` observation prefix replaces `{{DEPT_OBS_PREFIX}}-NN`.** Everywhere the OBSERVATIONS template (and any other file) writes `{{DEPT_OBS_PREFIX}}-NN`, the stamped output reads `API-NN`. Source: ADR-030 item 2 (token convention) and the OBSERVATIONS template's `{{DEPT_OBS_PREFIX}}` usages.
- **Template sources are read-only inputs.** The files under `ai-infrastructure/project-manager/templates/department/` must not be edited, moved, or deleted. You read them and write substituted copies elsewhere. Source: ADR-030 item 1 (the template baseline is the recipe's source, not its target).
- **No `/backend-api-worker`, no per-department role docs, no `tasks/` directory.** Per ADR-028 (single universal dispatched worker), ADR-029 (shared role docs reused by reference), and ADR-027 Fork B (shared `dept:`-labeled task pool), the recipe creates none of these. They are already absent from the templates; you stamp exactly what the templates contain and add nothing. Source: ADR-030 item 1 ("The template does NOT contain...").

## Deliverables

Six output files, each stamped from its template with all tokens substituted:

- `ai-infrastructure/backend-api/CLAUDE.md` (stamped from `templates/department/CLAUDE.md`)
- `ai-infrastructure/backend-api/README.md` (stamped from `templates/department/README.md`)
- `ai-infrastructure/backend-api/STATUS.md` (stamped from `templates/department/STATUS.md`)
- `ai-infrastructure/backend-api/OBSERVATIONS.md` (stamped from `templates/department/OBSERVATIONS.md`, using the `API-NN` observation prefix)
- `ai-infrastructure/backend-api/decisions/README.md` (stamped from `templates/department/decisions/README.md`)
- `.claude/commands/backend-api-orchestrator.md` (stamped from `templates/department/orchestrator-command.md`, renamed to the `<slug>-orchestrator.md` form)

## Files in scope

- `ai-infrastructure/backend-api/CLAUDE.md` (new)
- `ai-infrastructure/backend-api/README.md` (new)
- `ai-infrastructure/backend-api/STATUS.md` (new)
- `ai-infrastructure/backend-api/OBSERVATIONS.md` (new)
- `ai-infrastructure/backend-api/decisions/README.md` (new)
- `.claude/commands/backend-api-orchestrator.md` (new)
- `ai-infrastructure/project-manager/STATUS.md` (universal STATUS hygiene only; see "STATUS deltas")

## Files out of scope

- The `database` department and all of its files (created in the first run; do not touch).
- The template source files under `ai-infrastructure/project-manager/templates/department/` (read-only inputs; do not edit, move, or delete).
- The other blessed departments (`mcp-server`, `frontend-ui`, `devops`, `agent-development`, `test-design`, `docs-curation`): not created here.
- The COR-T-023 task file (the Orchestrator transitions tasks; the Worker never edits the task tree).
- Any Phase 2 web-app code (FastAPI endpoints, auth, invites): only the empty department scaffold is created; no domain-1 code.

## References

- `ai-infrastructure/project-manager/decisions/ADR-030-department-scaffold-contract-create-department-recipe.md` (the scaffold contract: the file set, the token convention in item 2, and what the recipe does and does not create)
- `ai-infrastructure/project-manager/decisions/ADR-021-candidate-departments.md` (the blessed menu and the `backend-api` scope line, web-app departments table)
- `ai-infrastructure/project-manager/templates/department/CLAUDE.md` (template source to stamp into the workspace)
- `ai-infrastructure/project-manager/templates/department/README.md` (template source to stamp into the workspace)
- `ai-infrastructure/project-manager/templates/department/STATUS.md` (template source to stamp into the workspace)
- `ai-infrastructure/project-manager/templates/department/OBSERVATIONS.md` (template source; carries the `{{DEPT_OBS_PREFIX}}-NN` usages that become `API-NN`)
- `ai-infrastructure/project-manager/templates/department/decisions/README.md` (template source to stamp into the workspace)
- `ai-infrastructure/project-manager/templates/department/orchestrator-command.md` (template source for the stamped-out `.claude/commands/backend-api-orchestrator.md`)

## Related tasks and ADRs

- COR-T-023: the parent task; this is the second of its two create-department runs (`database` done, `backend-api` now).
- COR-T-013: built the create-department recipe and the templates being stamped.
- ADR-030: the scaffold contract this run executes (file set, token convention, what is and is not created).
- ADR-021: blesses the `backend-api` menu entry and supplies the scope line.
- ADR-028: single universal dispatched worker; the reason NO `/backend-api-worker` command is created.
- ADR-029: shared role docs reused by reference; the reason NO per-department role-doc copies are created.
- ADR-027: workspace structure; Fork B (shared `dept:`-labeled task pool, so NO `tasks/` directory in the department) and Fork D (the scaffold).

## STATUS deltas

Universal hygiene only, with one named edit:

- Bump `last_updated` and prepend ONE `recent_updates` entry to `ai-infrastructure/project-manager/STATUS.md` recording that the `backend-api` department workspace and its `/backend-api-orchestrator` command were created.

Do NOT touch the roadmap block or the "Next step" section. The roadmap P2-0 milestone status flip and the "Next step" rewording are deferred to task close (orchestrator-direct, after this run completes both departments).

## Hard rules

- Substitute every `{{TOKEN}}`. No output file may contain a literal `{{...}}` string. The acceptance gate verifies this with a `{{`-substring grep across the six output paths; the expected result is zero matches.
- The `orchestrator-command.md` template stamps OUT to `.claude/commands/backend-api-orchestrator.md`. Do not place it inside the department workspace, and do not keep the `orchestrator-command.md` filename.
- The template source files are read-only. Do not edit, move, or delete anything under `ai-infrastructure/project-manager/templates/department/`.
- Stamp exactly what the templates contain. Add no `/backend-api-worker` command, no per-department role docs, and no `tasks/` directory; none are in the templates and none belong in the output.

## Acceptance gate

The task is complete when all of the following hold on disk:

- All six output files exist at the paths listed under "Deliverables".
- A grep for the literal substring `{{` across the six output paths returns no matches (every token was substituted).
- `ai-infrastructure/backend-api/OBSERVATIONS.md` uses the `API-NN` observation ID prefix where the template used `{{DEPT_OBS_PREFIX}}-NN`.
- `ai-infrastructure/project-manager/STATUS.md` carries the bumped `last_updated` and the one prepended `recent_updates` entry, with the roadmap block and "Next step" section unchanged.

## Worker pointer

The worker is the dispatched `worker-agent` (ADR-028). Universal worker conventions (the writing rules and Agent Discipline in `./CLAUDE.md`, git boundaries, STATUS hygiene, the pinned six-section report shape) live in `docs/ai-orchestration/roles/WORKER-ROLE.md`; follow them rather than re-deriving them here. Write the closing report to the path derived from this kickoff per `WORKER-ROLE.md`, section "Report shape" (dual-channel).
