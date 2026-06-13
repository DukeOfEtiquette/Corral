# Repoint the dashboard ETL at the epic/phase files and retire the STATUS roadmap block (ADR-037 Phase B)

## Target

This is AI-infrastructure work (domain 2 per `ai-infrastructure/project-manager/decisions/ADR-005-two-domains-ai-first.md`): the project-manager dashboard's ETL pipeline. Task COR-T-045 is the visual half of the ADR-037 cascade (Phase B; COR-T-044 was Phase A). The artifact in scope is the dashboard ETL at `ai-infrastructure/project-manager/dashboard/etl.py`: you cut the roadmap data source over from the `roadmap:` block in `ai-infrastructure/project-manager/STATUS.md` frontmatter to the Phase-A epic/phase YAML files, then remove the now-dead `roadmap:` block. The governing constraint is that the `data.json` roadmap CONTRACT is preserved exactly, so the React consumer `RoadmapPanel.jsx` needs no change.

## Decisions resolved by the Orchestrator

Every decision below is pinned. Do not re-deliberate; execute as written.

- **Intent.** Cut the dashboard roadmap source from the STATUS `roadmap:` frontmatter block over to the Phase-A epic/phase files, then remove the dead `roadmap:` block. The `data.json` roadmap contract is preserved exactly so `RoadmapPanel.jsx` needs no change; the render is then verified by the Orchestrator at close.

- **Required strategy (minimal-risk, preserves the contract by construction).** Add a reader that assembles an equivalent `roadmap_raw` list FROM THE FILES, and feed it into the EXISTING roadmap-assembly loop in `run_etl` (the `for item in roadmap_raw:` loop, currently around lines 763-867 of `etl.py`) and the existing derivation functions (`derive_current_phase`, `derive_current_phase_title`, `derive_next_step`, `derive_roadmap_status`, `resolve_milestone_refs`, `derive_epic_status`, `expand_range_token`, `resolve_ref_status`). Do NOT rewrite the assembly loop or the derivation functions. Change only the SOURCE that produces `roadmap_raw`. The per-phase `roadmap_raw` shape those consumers expect is:
  ```
  {phase: int, title: str, deliverables: str, legacy: bool,
   epics: [ {id: str, dept: str, title: str,
             tasks: [task-id strings], adrs: [ADR-NNN strings]} ]}
  ```
  Produce that exact shape from the files and the contract is preserved automatically.

- **Source reader, phases.** Read `ai-infrastructure/project-manager/phases/phase-*.yml`. Each file carries `id` (the phase number), `title`, `description`, `order`, and optional `legacy`. Map to `roadmap_raw`: `phase` <- `id`, `title` <- `title`, `deliverables` <- `description`, `legacy` <- `legacy` (default false). Order the phases by the `order` field ascending.

- **Source reader, epics.** Discover every `ai-infrastructure/<workspace>/epics/` tree by generic directory discovery, NOT a hardcoded list (today `project-manager` and `database` each have one; future departments will add more). Each epic file carries `id`, `title`, `dept`, `phase`, `description`, and `adrs` (a list of integers). Group epics under their phase via the epic's `phase` field. An epic with no `phase` field would be a standalone epic; there are none in v1. If one is encountered, omit it from the phase roadmap and do not error; standalone-epic rendering is out of scope.

- **Source reader, epic tasks (bottom-up).** For each epic, gather the task IDs whose task-file frontmatter `epic:` field equals that epic's `id`, drawn from all task trees (reuse the existing `collect_all_tasks`). Emit `tasks` as a list of plain task-ID strings (for example `"COR-T-001"`), so the existing `resolve_milestone_refs` / `expand_range_token` / `resolve_ref_status` path resolves each unchanged. There are no range tokens in the bottom-up model; every task is a single id.

- **Source reader, epic ADRs.** The epic YAML `adrs` field is a list of INTEGERS (for example `[27]`). Convert each integer N to the token form the existing resolver expects: `"ADR-%03d" % N` (so `27` -> `"ADR-027"`, `9` -> `"ADR-009"`). Then `resolve_milestone_refs` resolves them as ADR refs exactly as before.

- **Phase cardinality check refinement.** The existing check (around lines 776-779 of `etl.py`) flags a non-legacy phase with fewer than 2 epics. After this cutover the deferred future phases (3-8) have 0 epics and would all raise spurious warnings. Change the rule to mirror the existing EPIC-level check (where 0 tasks is "forming" and not flagged, 1 task is flagged): a phase warning fires ONLY when a phase has EXACTLY 1 epic; 0 epics is "forming/future" and is NOT flagged. Keep the existing 1-epic warning message wording. Do NOT change the epic-level checks.

- **Remove the roadmap block.** Once the file reader is wired in, remove the entire `roadmap:` block (currently starting at line 3) from `ai-infrastructure/project-manager/STATUS.md` frontmatter. This is ADR-037 decision 6, the churn-coupling resolution. Keep `schema_version`, `last_updated`, `recent_updates`, and the entire markdown body. After removal `coordinator_fm.get("roadmap", [])` returns `[]`, so the file reader MUST be the source, not the now-absent frontmatter block.

- **Docstring.** Update the `etl.py` module docstring source item (a) to describe the new source (the epic/phase files) instead of the STATUS roadmap block. Keep the JSON-contract shape section accurate; it should not need to change, since the contract is preserved.

- **Dead spot-test block.** The `_spot_test_active` block in `run_etl` (around lines 749-761) is dead (`False`) and operates on `roadmap_raw`. Leave it untouched; it is out of scope.

- **Contract preservation is the gate.** The `data.json` `roadmap` array and the derived `meta` fields (`current_phase`, `current_phase_title`, `next_step`) must keep the exact shape documented in the `etl.py` docstring. `RoadmapPanel.jsx` must require NO change. If the contract cannot be preserved without a panel change, STOP and return `RETURN: ESCALATION` rather than changing the contract or the panel.

- **Expected render after the change (for your own verification).** Phase 0: legacy, no epics. Phase 1: five epics COR-E-001..005, each with its task badges and rollup. Phase 2 (current): DB-E-001 (database) with DB-T-001 and DB-T-002; the Backend API epic is gone (deferred). Phases 3-8: header plus deliverables only, no epics, and NO cardinality warning. `current_phase` = 2, `current_phase_title` = "API + DB core", `next_step` derived from the first non-done epic of phase 2.

- **Run and verify policy.** docker compose only (per `ai-infrastructure/project-manager/decisions/ADR-003-docker-compose-runtime.md`). The dashboard compose file is `ai-infrastructure/project-manager/dashboard/docker-compose.yml` (a single `dashboard` service that builds, runs the ETL, and serves on port 8420). The verification command is:
  ```
  docker compose -f ai-infrastructure/project-manager/dashboard/docker-compose.yml up --build
  ```
  Confirm the ETL runs without error and produces `data.json`. The Orchestrator performs the headless-render visual check at close (COR-07), so you are not required to render; only confirm the ETL builds clean and the contract shape is intact.

## Deliverables

- `ai-infrastructure/project-manager/dashboard/etl.py`: a new file-based roadmap reader that assembles the `roadmap_raw`-equivalent from the epic/phase files, wired into `run_etl` in place of the STATUS `roadmap:` block; the phase cardinality refinement (0 epics not flagged, 1 epic flagged); the docstring source (a) update.
- `ai-infrastructure/project-manager/STATUS.md`: the `roadmap:` block removed from frontmatter (`schema_version`, `last_updated`, `recent_updates`, and the markdown body retained).
- A stated confirmation in your report that the `data.json` roadmap/meta contract shape is unchanged and `RoadmapPanel.jsx` was NOT modified.

## Files in scope

- `ai-infrastructure/project-manager/dashboard/etl.py` (the file reader, the cardinality refinement, the docstring update).
- `ai-infrastructure/project-manager/STATUS.md` (remove the `roadmap:` block; plus the universal `recent_updates` hygiene append per the STATUS deltas section below).

## Files out of scope

- `ai-infrastructure/project-manager/dashboard/src/panels/RoadmapPanel.jsx` (must NOT change; return `RETURN: ESCALATION` if it would need to).
- The epic/phase YAML files under `ai-infrastructure/project-manager/phases/`, `ai-infrastructure/project-manager/epics/`, `ai-infrastructure/database/epics/`, and the task `epic:` linkage (COR-T-044 output, the read-only input to this task).
- Every other ETL source (departments, agents, ADRs, observations, task counts) and every other dashboard panel or view.
- The `_spot_test_active` dead block in `run_etl` (leave as-is).

## References

- `ai-infrastructure/project-manager/dashboard/etl.py` (the module docstring's JSON-contract section and the roadmap-assembly loop are the spec to preserve; read both; the loop is around lines 763-867, the cardinality check around lines 776-779, the dead spot-test block around lines 749-761).
- `ai-infrastructure/project-manager/dashboard/src/panels/RoadmapPanel.jsx` (the consumer; read to confirm no change is needed).
- `ai-infrastructure/project-manager/decisions/ADR-037-work-item-storage-representation.md` (decisions 5 derived-roadmap and 6 roadmap-leaves-STATUS; the governing spec).
- `ai-infrastructure/project-manager/decisions/ADR-038-phase-as-first-class-view.md` (the phase-as-View target; informational context for the phase files).
- `ai-infrastructure/project-manager/decisions/ADR-036-work-item-taxonomy.md` (the status rollup and cardinality semantics the reader applies).
- `ai-infrastructure/project-manager/phases/`, `ai-infrastructure/project-manager/epics/`, and `ai-infrastructure/database/epics/` (the new roadmap source produced by COR-T-044).

## Related tasks and ADRs

- COR-T-044: Phase A, the input; it built the epic/phase files and the bottom-up `epic:` linkage this task reads.
- ADR-037: decisions 5 (the roadmap becomes a derived view) and 6 (the roadmap block leaves STATUS.md); the governing spec.
- ADR-038: phase-as-View, the eventual import target; informational context for the phase files.
- ADR-036: the status rollup and cardinality conventions the reader applies.
- COR-T-040 and COR-T-041: the prior dashboard roadmap badge and reshape work, for context on the contract being preserved.

## STATUS deltas

Task-specific: remove the `roadmap:` block from `ai-infrastructure/project-manager/STATUS.md` frontmatter. This is a deliverable change per ADR-037 decision 6, not mere hygiene; it is the same edit listed under Deliverables and Files in scope. Beyond removing the `roadmap:` block and the universal `recent_updates` append, do not change STATUS frontmatter. Universal hygiene (bump `last_updated`, append one `recent_updates` entry) is yours per `docs/ai-orchestration/roles/EXECUTOR-ROLE.md` and is not re-enumerated here.

## Hard rules

- Do NOT rewrite the roadmap-assembly loop or any of the named derivation functions. Change only the source that produces `roadmap_raw`.
- Do NOT modify `RoadmapPanel.jsx`. If preserving the contract would require a panel change, STOP and return `RETURN: ESCALATION`; do not change the contract or the panel.
- Do NOT touch the `_spot_test_active` dead block.
- Discover epic trees generically; do not hardcode `project-manager` and `database`.
- Verification is docker compose only (ADR-003), via the command pinned in the run-and-verify decision above.

## Executor pointer

The executor is the dispatched `executor` (ADR-028). Universal executor conventions (the pinned six-section report shape, the dual-channel report write, the universal STATUS hygiene, the no-edit-outside-scope and verify-before-asserting rules) live in `docs/ai-orchestration/roles/EXECUTOR-ROLE.md`. The closing report is written to `./.claude/artifacts/handoffs/COR-T-045-KICKOFF-REPORT.md` per EXECUTOR-ROLE.md, section "Report shape".
