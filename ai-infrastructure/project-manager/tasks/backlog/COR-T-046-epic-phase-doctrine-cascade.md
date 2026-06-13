---
schema_version: 1
id: COR-T-046
title: "Epic/phase doctrine cascade: operationalize ADR-037/038 in role docs, commands, and scaffold docs"
status: backlog
labels: []
priority: P2
created: 2026-06-12
updated: 2026-06-12
---

## Description

ADR-037/038 made Epics and Phases first-class work items (per-workspace `epics/` YAML trees, a coordinator-owned `phases/` tree, bottom-up `epic:`/`phase:` linkage, department-prefixed IDs allocated from `.next-epic-id`, and the roadmap as a derived view computed by the dashboard ETL). COR-T-044 (storage decomposition) and COR-T-045 (ETL cutover) implemented the **data layer**, and the `tasks/README.md` "Epics and phases" section documents the **convention**. But the **operational doctrine** (the role docs, the orchestrator survey commands, and the per-workspace `CLAUDE.md` files) was never updated, so an orchestrator reading the role docs has no flow for creating, allocating, surveying, or linking epics and phases, and one instruction is now actively stale. This task is the doctrine-and-docs analog of COR-T-042 (the vocabulary cascade), routed through the dispatched-worker flow.

Surfaced by a post-cascade audit (this session). The five gaps to close, each verified on disk:

1. **Stale instruction (correctness fix).** `docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md` line ~101 (Pending-ADR resolution playbook, step 6) says "update 'Next step' and the roadmap epic to drop the resolved task." Post-ADR-037 the roadmap is **derived**: there is no roadmap block in STATUS.md to edit, and a resolved task **keeps** its `epic:` linkage (the ETL rolls it up as done). Correct this to describe the derived-roadmap reality (STATUS hygiene no longer touches a roadmap block; epic membership is unchanged on resolve). While here, sweep the whole role doc for any other reference to a hand-edited STATUS roadmap block.

2. **No epic/phase lifecycle in the role doc.** `ORCHESTRATOR-ROLE.md` "Task lifecycle" documents allocating `.next-task-id` and drafting task files, but has no parallel guidance for: creating an Epic file, allocating an epic ID from a workspace's `.next-epic-id` (read/use/write-back, lazy-creating the `epics/` tree on first epic per `tasks/README.md`), creating/ordering a Phase file, and setting the `epic:` field on a newly filed task that belongs to an epic. Add a concise subsection that **cross-references** the `tasks/README.md` "Epics and phases" convention rather than duplicating the schemas. The "Add a new task" lifecycle step should note the `epic:` linkage decision.

3. **Survey blindness.** The orchestrator survey commands (`.claude/commands/project-manager-orchestrator.md`, `database-orchestrator.md`, `backend-api-orchestrator.md`) and the department command template (`ai-infrastructure/project-manager/templates/department/orchestrator-command.md`) survey only the `tasks/` trees. Add an epics/phases survey step (list the workspace `epics/` tree and, for the coordinator, the `phases/` tree) so a state survey reports epic/phase structure, not just tasks.

4. **CLAUDE.md doc gap.** The department template `CLAUDE.md` and both live department `CLAUDE.md` files (`ai-infrastructure/database/CLAUDE.md`, `ai-infrastructure/backend-api/CLAUDE.md`) document the `tasks/` tree but not the (lazily-created) `epics/` tree. Add an Epics note + Pointers-table row paralleling the Tasks treatment, written so it is accurate whether or not the `epics/` tree exists yet (lazy creation). The database `CLAUDE.md` is the most out of sync (its `epics/` tree exists on disk, undocumented).

5. **Bidirectional-link hygiene.** `ADR-030-department-scaffold-contract-create-department-recipe.md` has no forward-pointer to ADR-037, even though ADR-037 extends the per-workspace tree model that the scaffold contract enumerates. Add a forward-pointer note to ADR-030 (ADR-037 itself stays the amending ADR; do not edit ADR-037's decision). ADR-031 already carries its pointer.

6. **Backfill missing `epic:` linkage on the restructure tasks.** COR-T-040 through 045 (the ADR-036/037/038 restructure) were filed/executed around the linkage backfill, and five ended up with no `epic:` field (only COR-T-040 carries `epic: COR-E-004`). Pin the linkage (an orchestrator decision, resolved here, NOT executor judgement): add `epic: COR-E-004` to the three dashboard deliverables -- COR-T-041 (dashboard epic reshape), COR-T-043 (dead milestone CSS), and COR-T-045 (roadmap ETL cutover); leave COR-T-042 (vocabulary cascade) and COR-T-044 (storage decomposition) **standalone** (no `epic:`) as cross-cutting work-item-model doctrine that fits no single Phase-1 epic (ADR-036 permits standalone tasks). All three linked tasks are done and COR-E-004 is already all-done, so the rollup stays done -- no epic or phase is reopened. These files live in `ai-infrastructure/project-manager/tasks/done/`. (This edits task frontmatter only; it does not touch any epic/phase YAML file.)

### Explicitly NOT gaps (do not "fix" these)

- The department **template and `/create-department` recipe correctly do NOT stamp an `epics/` tree or `.next-epic-id`** -- epics are created **lazily** (only when a workspace's first epic is ready to file, `tasks/README.md` "Lazy creation"). Only `tasks/` is eager. Do not add an eager `epics/` scaffold.
- **backend-api correctly has no `epics/` tree** (it has no epics yet). Do not create one.
- **ADR-038's app-side realization** (the `phase:*` reserved label family, view `position`/ordering DDL, API enforcement) is intentionally **deferred to the dogfood-import build (Phase 5/7)** and recorded as an ADR-038 consequence. Out of scope here; this task is markdown-era doctrine only.

Out of scope: any change to the storage decomposition, the epic/phase YAML files, or the ETL (all done and verified in COR-T-044/045); creating any new epic/phase file; the deferred ADR-038 schema realization.

## Activity log

- 2026-06-12: Created in backlog by the project-manager coordinator (orchestrator-direct, coordinator task tree). Surfaced by a post-ADR-037/038 audit: COR-T-044/045 delivered the data layer (storage decomposition + ETL) and `tasks/README.md` carries the convention, but the operational doctrine (role docs, survey commands, department `CLAUDE.md` files) was never updated and `ORCHESTRATOR-ROLE.md` line ~101 carries a now-stale roadmap-edit instruction. Five gaps enumerated above, each verified on disk; the lazy-creation non-gaps and the deferred ADR-038 realization are explicitly fenced off. Left standalone (no `epic:` linkage) deliberately: the only fitting epic (COR-E-001) is a done Phase-1 epic, and linking a new backlog task would reopen its rollup and Phase 1; ADR-036 permits standalone tasks. P2 (one latent correctness fix plus completeness; non-blocking). Routes through the dispatched-worker flow as a documentation cascade (analog of COR-T-042) when picked up.
- 2026-06-12: Added item 6 at user direction -- backfill the missing `epic:` linkage on the restructure tasks (COR-T-041/043/045 -> COR-E-004; COR-T-042/044 left standalone), with the per-task linkage pinned here as an orchestrator decision so the kickoff carries it resolved.
