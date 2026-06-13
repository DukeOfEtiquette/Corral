# Epic/phase doctrine cascade: operationalize ADR-037/038 in role docs, commands, and scaffold docs

## Target

This is **AI-infrastructure** work (domain 2 per `./ai-infrastructure/project-manager/decisions/ADR-005-two-domains-ai-first.md`). Task `COR-T-046` (file `./ai-infrastructure/project-manager/tasks/in-progress/COR-T-046-epic-phase-doctrine-cascade.md`) closes the operational-doctrine gaps left by the ADR-037/038 epic/phase cascade.

ADR-037/038 made Epics and Phases first-class work items: per-workspace `epics/` YAML trees, a coordinator-owned `phases/` tree, bottom-up `epic:`/`phase:` linkage, department-prefixed IDs from each `epics/.next-epic-id`, and a roadmap that is now a derived view computed by the dashboard ETL. COR-T-044/045 delivered the DATA layer and `./ai-infrastructure/project-manager/tasks/README.md` (section "Epics and phases") documents the CONVENTION. This task is the doctrine analog of COR-T-042 (the ADR-036 vocabulary cascade): it propagates the new model into the role docs, orchestrator commands, department-template scaffold, and per-workspace `CLAUDE.md` files, plus a small `epic:` linkage backfill on three done tasks.

The decisions below are all pinned by the Orchestrator. Implement them; do not re-decide them. Every change is doctrine/text editing or task-frontmatter editing; no code, no epic/phase YAML edits.

## Decisions resolved by the Orchestrator

**Decision 1 -- Fix three named stale STATUS-hygiene references, then sweep for siblings.** The manual STATUS roadmap block (retired by ADR-037; roadmap is now derived) and the manual `## Next step` STATUS section (removed by COR-T-029; `next_step` is now derived in `etl.py`) no longer exist, but the doctrine still tells agents to hand-edit them. Apply these three edits:

- `docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md`, "Pending-ADR resolution playbook" step 6 (~line 101). It currently reads: bump `last_updated`, prepend a `recent_updates` entry, **and update "Next step" and the roadmap epic to drop the resolved task**. Remove the stale `and update "Next step" and the roadmap epic to drop the resolved task` clause. Step 6 should state that STATUS hygiene is bumping `last_updated` and prepending a `recent_updates` entry; note that the roadmap and next-step are now derived (no manual STATUS edit), and that a resolved task KEEPS its `epic:` linkage (the ETL rolls it up as done).
- `docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md`, "Kickoff drafting convention" bullet "Name task-specific STATUS deltas (rule R6)" (~line 139). The example list reads `phase changes, "Next step" rewording, "Blocked on" updates`. Drop `"Next step" rewording` (the `## Next step` section no longer exists). Keep "phase changes" and "Blocked on" updates (those narrative sections remain).
- `docs/ai-orchestration/roles/EXECUTOR-ROLE.md` (~line 138). Same example list `phase changes, "Next step" rewording, "Blocked on" updates`; apply the same fix, dropping `"Next step" rewording`.

After those three, grep both role docs for any remaining instruction to hand-edit a STATUS "roadmap" block or "Next step" section and correct it the same way. DO NOT touch the line-85 "dogfood milestone" reference in `docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md`; that is the event sense of "milestone" and is correct as-is.

**Decision 2 -- Add an epic/phase lifecycle subsection to ORCHESTRATOR-ROLE.md.** In the "Task lifecycle" section of `docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md`, add a concise new subsection (for example, "Epic and phase lifecycle") that CROSS-REFERENCES `./ai-infrastructure/project-manager/tasks/README.md` section "Epics and phases" rather than duplicating the YAML schemas. It must cover: (a) creating an Epic file and allocating its id from the owning workspace's `epics/.next-epic-id` (read, use, write back the increment), lazily creating the `epics/` tree on the workspace's first epic per the README's "Lazy creation" rule; (b) creating and ordering a Phase file in the coordinator-owned `phases/` tree; (c) setting the `epic:` field on a newly filed task that belongs to an epic, and the `phase:` field on an epic that belongs to a phase (bottom-up linkage). Additionally, in the existing "Add a new task" lifecycle bullet (~line 82), add a short note that the Orchestrator decides the task's `epic:` linkage at filing time (set `epic: <id>` if it belongs to an epic; standalone otherwise).

**Decision 3 -- Add an epics/phases survey step to the orchestrator commands and the department template.** The orchestrator survey commands and the department template currently survey only `tasks/` trees. Add:

- `.claude/commands/project-manager-orchestrator.md`: in Phase 3 ("Survey state") add a step that lists the coordinator `epics/` tree (each epic's id, title, phase, and rolled-up task count) AND the coordinator-owned `phases/` tree; add a matching line to the Phase 4 ("Report findings") shape. Also add an `epic:` linkage note to the "Add a new task" typical-direction bullet (~line 48), mirroring Decision 2.
- `.claude/commands/database-orchestrator.md` and `.claude/commands/backend-api-orchestrator.md`: add an epics survey step for that department's OWN `epics/` tree only (phases are coordinator-owned and are not surveyed by departments). The tree may not exist yet (lazy creation), so the step must no-op gracefully.
- `ai-infrastructure/project-manager/templates/department/orchestrator-command.md`: the same department-level epics survey step, using the existing `{{DEPT_SLUG}}` token.

**Decision 4 -- Document the `epics/` tree in the three CLAUDE.md files.** Each of the three files has a "## Tasks" section and a "## Pointers" table that document the `./tasks/` tree but not the `epics/` tree. Add a short Epics note (a "## Epics" section or a sentence in the Tasks area) and a Pointers-table row for the `epics/` tree, written to be accurate WHETHER OR NOT the `epics/` tree exists yet (lazy creation; created on the workspace's first epic). Files:

- `ai-infrastructure/project-manager/templates/department/CLAUDE.md`: use the `{{DEPT_TASK_PREFIX}}` / `{{DEPT_SLUG}}` tokens to match its existing style.
- `ai-infrastructure/database/CLAUDE.md`: its `epics/` tree exists on disk now (the most out-of-sync of the three).
- `ai-infrastructure/backend-api/CLAUDE.md`: no epics yet; phrase for the lazy/not-yet case.

**Decision 5 -- Add an ADR-030 forward-pointer note.** In `ai-infrastructure/project-manager/decisions/ADR-030-department-scaffold-contract-create-department-recipe.md`, add a forward-pointer note that ADR-037 extends the per-workspace tree model with a lazily-created `epics/` sibling tree (and the coordinator-owned `phases/` tree). This is an ADDITIVE forward-pointer note in ADR-030 ONLY. Do NOT edit ADR-037's decision body; ADR-037 remains the amending ADR, per the ADR-024 amend-by-later-ADR precedent.

**Decision 6 -- Backfill `epic: COR-E-004` on three done dashboard tasks.** Add `epic: COR-E-004` to the YAML frontmatter of these three DONE tasks:

- `ai-infrastructure/project-manager/tasks/done/COR-T-041-dashboard-epic-reshape.md`
- `ai-infrastructure/project-manager/tasks/done/COR-T-043-dashboard-dead-milestone-css.md`
- `ai-infrastructure/project-manager/tasks/done/COR-T-045-roadmap-etl-cutover.md`

Place the `epic:` field in frontmatter consistent with how `epic:` appears on other linked task files (for example, DB-T-002 carries it after `updated:`). Leave `COR-T-042` and `COR-T-044` standalone (NO `epic:` field) -- this is pinned, not your choice. All three target tasks are done and `COR-E-004` is already all-done, so the rollup stays done; no epic or phase reopens. This edits task FRONTMATTER ONLY; do not touch any epic/phase YAML file.

**Explicit non-gaps (do NOT "fix" these; named so you do not regress them).**

- The department template and the `/create-department` recipe (`.claude/commands/create-department.md`) correctly do NOT stamp an `epics/` tree or a `.next-epic-id`. Epics are LAZY. Do not add an eager epics scaffold and do not edit the recipe.
- `backend-api` correctly has no `epics/` tree (no epics yet). Do not create one.
- ADR-038's app-side realization (the `phase:*` label family, view-ordering DDL, API enforcement) is deferred to the dogfood-import build (Phase 5/7), and this deferral leaves nothing in this task blocked or conditional: it does NOT affect any deliverable here because every surface this task edits -- the role docs, the orchestrator commands, the department template, the `CLAUDE.md` files, the ADR-030 forward-pointer note, and the three task-frontmatter `epic:` backfills -- is markdown/doctrine only and touches no DDL, no `phase:*` label, and no API-enforcement code. So there is no action for you here: do nothing about ADR-038's deferred app-side scope (do not add a `phase:*` label, view-ordering DDL, or any enforcement; do not reference the deferred scope as if it were live).

## Deliverables

- `docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md`: the stale-reference fixes (Decision 1, the step-6 and R6-example edits plus the sibling sweep) AND the new epic/phase lifecycle subsection and the "Add a new task" `epic:` note (Decision 2).
- `docs/ai-orchestration/roles/EXECUTOR-ROLE.md`: the stale-reference fix (Decision 1, drop `"Next step" rewording` from the ~line-138 example list).
- `.claude/commands/project-manager-orchestrator.md`: the coordinator epics + phases survey step (Phase 3 and Phase 4) and the "Add a new task" `epic:` note (Decision 3).
- `.claude/commands/database-orchestrator.md`: the department-own `epics/` survey step, graceful no-op when absent (Decision 3).
- `.claude/commands/backend-api-orchestrator.md`: the same department-own `epics/` survey step, graceful no-op when absent (Decision 3).
- `ai-infrastructure/project-manager/templates/department/orchestrator-command.md`: the department-level epics survey step using `{{DEPT_SLUG}}` (Decision 3).
- `ai-infrastructure/project-manager/templates/department/CLAUDE.md`: Epics documentation using the `{{DEPT_TASK_PREFIX}}` / `{{DEPT_SLUG}}` tokens (Decision 4).
- `ai-infrastructure/database/CLAUDE.md`: Epics documentation, tree-exists phrasing (Decision 4).
- `ai-infrastructure/backend-api/CLAUDE.md`: Epics documentation, lazy/not-yet phrasing (Decision 4).
- `ai-infrastructure/project-manager/decisions/ADR-030-department-scaffold-contract-create-department-recipe.md`: the additive forward-pointer note (Decision 5).
- `ai-infrastructure/project-manager/tasks/done/COR-T-041-dashboard-epic-reshape.md`, `ai-infrastructure/project-manager/tasks/done/COR-T-043-dashboard-dead-milestone-css.md`, `ai-infrastructure/project-manager/tasks/done/COR-T-045-roadmap-etl-cutover.md`: each gains `epic: COR-E-004` in frontmatter (Decision 6).

## Files in scope

- `docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md`
- `docs/ai-orchestration/roles/EXECUTOR-ROLE.md`
- `.claude/commands/project-manager-orchestrator.md`
- `.claude/commands/database-orchestrator.md`
- `.claude/commands/backend-api-orchestrator.md`
- `ai-infrastructure/project-manager/templates/department/orchestrator-command.md`
- `ai-infrastructure/project-manager/templates/department/CLAUDE.md`
- `ai-infrastructure/database/CLAUDE.md`
- `ai-infrastructure/backend-api/CLAUDE.md`
- `ai-infrastructure/project-manager/decisions/ADR-030-department-scaffold-contract-create-department-recipe.md`
- `ai-infrastructure/project-manager/tasks/done/COR-T-041-dashboard-epic-reshape.md`
- `ai-infrastructure/project-manager/tasks/done/COR-T-043-dashboard-dead-milestone-css.md`
- `ai-infrastructure/project-manager/tasks/done/COR-T-045-roadmap-etl-cutover.md`

## Files out of scope

- `ai-infrastructure/project-manager/dashboard/etl.py` (data layer; done in COR-T-045).
- All files under `ai-infrastructure/*/epics/` and `ai-infrastructure/project-manager/phases/` (the epic/phase YAML files). Do not modify any epic or phase file.
- `ai-infrastructure/project-manager/tasks/README.md` (the cross-reference TARGET for Decision 2; read it, do not edit it).
- `.claude/commands/create-department.md` (lazy creation; correctly stamps no epics tree; no edit).
- `ai-infrastructure/project-manager/decisions/ADR-037-work-item-storage-representation.md` and `ai-infrastructure/project-manager/decisions/ADR-038-phase-as-first-class-view.md` (do not edit their decision bodies; ADR-030 gets the only forward-pointer note).
- `ai-infrastructure/project-manager/tasks/done/COR-T-042-*` and `ai-infrastructure/project-manager/tasks/done/COR-T-044-*` (pinned standalone; no `epic:` field).
- `ai-infrastructure/project-manager/STATUS.md` roadmap and next-step content (derived; not hand-edited).

## References

- `ai-infrastructure/project-manager/tasks/README.md`, section "Epics and phases" -- the cross-reference target for Decision 2 (the storage convention, the `.next-epic-id` counter, the "Lazy creation" rule, and the `epic:`/`phase:` linkage fields). Cross-reference it from the role doc; do not duplicate its schemas.
- `ai-infrastructure/project-manager/decisions/ADR-037-work-item-storage-representation.md` -- the storage decomposition (per-workspace `epics/` trees, coordinator-owned `phases/` tree, derived roadmap).
- `ai-infrastructure/project-manager/decisions/ADR-038-phase-as-first-class-view.md` -- phase as a first-class view (app-side realization is out of scope here).
- `ai-infrastructure/project-manager/decisions/ADR-036-work-item-taxonomy.md` -- the work-item taxonomy these docs must reflect (the `>= 2`-task epic convention).
- `ai-infrastructure/project-manager/decisions/ADR-030-department-scaffold-contract-create-department-recipe.md` -- the scaffold contract that the `epics/` tree extends (Decision 5 edits this file).
- `ai-infrastructure/project-manager/decisions/ADR-031-per-department-task-trees.md` -- the per-workspace tree model the `epics/` tree is a sibling of.
- The linkage epic is `COR-E-004` (file `ai-infrastructure/project-manager/epics/COR-E-004-project-manager-dashboard.yml`); read it for the id but do not edit it (Decision 6 backfills `epic: COR-E-004` on the task files, not the epic file).

Path-convention note: per `ai-infrastructure/project-manager/CLAUDE.md`, references inside the coordinator workspace use the `./` prefix, while references to the root-staying shared tree (`.claude/`, `docs/ai-orchestration/`) use a BARE path with no `./` prefix. Match the surrounding file's existing convention when you add cross-references.

## Related tasks and ADRs

- COR-T-044, COR-T-045 -- the data-layer cascade this task completes (storage decomposition + roadmap ETL cutover).
- COR-T-042 -- the structural analog (the ADR-036 vocabulary cascade); this task is its doctrine counterpart.
- COR-T-029 -- removed the manual `## Next step` STATUS section, which is why the "Next step" doctrine references (Decision 1) are stale.
- ADR-037, ADR-038, ADR-036 -- the work-item model these docs must now reflect.
- ADR-030, ADR-031 -- the scaffold contract and per-workspace tree model that the `epics/` tree extends.

## STATUS deltas

No task-specific STATUS deltas; universal hygiene only. (The roadmap and next-step are derived, not hand-edited; do not touch `ai-infrastructure/project-manager/STATUS.md` roadmap/next-step content.)

## Hard rules

- **Doctrine and frontmatter edits only.** Every change is text editing in role docs, commands, templates, `CLAUDE.md` files, and ADR-030, plus `epic:` frontmatter on three done task files. No code. No epic/phase YAML edits.
- **Preserve template token style.** In the template files (`ai-infrastructure/project-manager/templates/department/orchestrator-command.md` and `.../CLAUDE.md`), keep `{{DEPT_SLUG}}` / `{{DEPT_TASK_PREFIX}}` tokens literal; do not accidentally expand them. In the non-template files, do not introduce literal `{{...}}` tokens.
- **Cross-reference, do not duplicate.** The epic/phase lifecycle subsection (Decision 2) points at `./ai-infrastructure/project-manager/tasks/README.md` section "Epics and phases"; it does not re-emit the YAML schemas.
- **Respect the explicit non-gaps.** Do not add an eager epics scaffold to the template or recipe; do not create a `backend-api/epics/` tree; do not touch ADR-038's deferred app-side scope.
- **Do not transition or move COR-T-046.** Task transitions are Orchestrator-only (`docs/ai-orchestration/roles/EXECUTOR-ROLE.md`, "Universal conventions"). The backfill edits in Decision 6 are content edits to done task FILES, which the kickoff explicitly puts in scope; they are not task-state transitions.

**Verification expectations (specific to this task).** Before assembling the report, verify on disk:

1. Grep `docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md` and `docs/ai-orchestration/roles/EXECUTOR-ROLE.md` for any remaining stale "Next step" / "roadmap epic" / "roadmap block" hand-edit instruction; confirm zero remain, EXCEPT the line-85 dogfood-milestone event reference in ORCHESTRATOR-ROLE.md (which is correct and must be left intact).
2. Confirm `COR-T-041`, `COR-T-043`, and `COR-T-045` done task files now carry `epic: COR-E-004`, and that `COR-T-042` and `COR-T-044` still carry NO `epic:` field.
3. Confirm no file under `ai-infrastructure/*/epics/`, no file under `ai-infrastructure/project-manager/phases/`, and `ai-infrastructure/project-manager/dashboard/etl.py` were modified (`git diff --name-only` should list none of them).
4. Confirm template token style is preserved: no literal `{{...}}` token left unintended in non-template files, and no tokens accidentally expanded inside the template files.

## Executor pointer

The executor is the dispatched `executor` (ADR-028). Universal executor conventions live in `docs/ai-orchestration/roles/EXECUTOR-ROLE.md`. Write the closing report to `./.claude/artifacts/handoffs/COR-T-046-KICKOFF-REPORT.md` per EXECUTOR-ROLE.md, section "Report shape" (the dual-channel print-to-chat-and-write-to-file requirement).
