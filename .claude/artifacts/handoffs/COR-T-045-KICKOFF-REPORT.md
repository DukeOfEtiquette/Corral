## Deliverables completed

All three deliverables shipped:

1. **`ai-infrastructure/project-manager/dashboard/etl.py`**: Added `collect_roadmap_from_files(repo_root)` and the helper `_collect_tasks_by_epic(repo_root)`. These replace the old `coordinator_fm.get("roadmap", [])` source in `run_etl`. The reader discovers phase YAML files from `ai-infrastructure/project-manager/phases/phase-*.yml` (ordered by the `order` field), discovers epic YAML files generically from every `ai-infrastructure/<workspace>/epics/*.yml` tree (no hardcoded list), groups epics by their `phase:` field, and collects tasks bottom-up by scanning all task files for the `epic:` frontmatter field. ADR integer lists are converted to `"ADR-%03d" % N` token strings so the existing `resolve_milestone_refs` path handles them unchanged. The cardinality check was changed from `len(raw_epics) < 2` to `len(raw_epics) == 1` (0 epics = forming/future, not flagged; 1 epic = smell, flagged). The docstring source (a) was updated to describe the new YAML-file source. `WATCH_PATTERNS` gained a `.yml` pattern for the ai-infrastructure tree.

2. **`ai-infrastructure/project-manager/STATUS.md`**: The entire `roadmap:` frontmatter block (phases 0-8 with their epics) was removed. `schema_version`, `last_updated`, `recent_updates`, and the markdown body are retained. One `recent_updates` entry appended; `last_updated` bumped to today (2026-06-12).

3. **Contract preservation confirmed**: The ETL was run locally against the repo and produced `data.json`. The `roadmap` array shape and `meta` fields (`current_phase`, `current_phase_title`, `next_step`) match the documented contract exactly. `RoadmapPanel.jsx` was NOT modified.

## Decisions made

- The `all_tasks` parameter was removed from `collect_roadmap_from_files` after the cleanup pass, since `collect_tasks` does not expose the `epic:` frontmatter field and the bottom-up scan uses a separate `_collect_tasks_by_epic` helper that re-reads frontmatter. The call site in `run_etl` was updated accordingly.
- `WATCH_PATTERNS` was extended to include `ai-infrastructure/.*\.yml$` so that changes to epic and phase YAML files trigger a watch-mode rebuild. This is a natural correctness extension of the roadmap source change and is within the scope of etl.py.
- The cardinality check correctly fires for Phase 2 (currently 1 epic, DB-E-001 only; the old E2.2 Backend API epic was never promoted to a new epic file under ADR-037). This is the expected behavior per the new rule.

## Surprises

- Phase 2 has only 1 epic (DB-E-001) after the cutover. The old STATUS.md had E2.2 Backend API as a provisional epic with 0 tasks; that entry was never filed as a new `*.yml` epic file by COR-T-044. The kickoff explicitly states "the Backend API epic is gone (deferred)" so this is expected. The `== 1` cardinality check correctly flags Phase 2; Phases 3-8 with 0 epics are not flagged.
- COR-T-041..COR-T-045 do not carry `epic:` frontmatter fields (they are standalone tasks not backfilled into any epic by COR-T-044). This matches the COR-T-044 scope which only backfilled tasks through COR-T-040.

## Follow-ups

- COR-T candidate (triage to orchestrator): COR-E-004 (project-manager dashboard) currently shows 15 tasks but COR-T-041..COR-T-045 are dashboard-related tasks with no `epic:` linkage. A follow-on task could backfill these into COR-E-004 or a new COR-E-006 epic, growing the dashboard epic's task count and resolving the orphan.
- COR-T candidate (triage to orchestrator): Phase 2 has 1 epic (DB-E-001). When the Backend API epic is formally scoped as a new `DB-E` or `API-E` file, Phase 2's cardinality warning will resolve. This is expected; no action needed now.

## Files touched

- `./ai-infrastructure/project-manager/dashboard/etl.py` (new `collect_roadmap_from_files`, new `_collect_tasks_by_epic`, updated `run_etl` call site, updated cardinality check, updated docstring source (a), updated `WATCH_PATTERNS`)
- `./ai-infrastructure/project-manager/STATUS.md` (`roadmap:` block removed, `recent_updates` entry appended, `last_updated` bumped)
- `./.claude/artifacts/handoffs/COR-T-045-KICKOFF-REPORT.md` (this report)

## Build / verification status

- Python syntax check: `python3 -m py_compile etl.py` returned SYNTAX OK.
- Local ETL run (host Python, not compose): `etl.run_etl(repo_root, served_dir)` succeeded, producing `data.json` (303,814 bytes). Output verified:
  - Phase 0 (Bootstrap): legacy=True, 0 epics, warning=None
  - Phase 1 (AI infrastructure): 5 epics (COR-E-001..005), status=done, warning=None
  - Phase 2 (API + DB core): 1 epic (DB-E-001, 2 tasks DB-T-001+DB-T-002), status=current, warning fires (1 epic, expected)
  - Phases 3-8: 0 epics, status=upcoming, warning=None (the cardinality refinement confirmed)
  - `current_phase` = 2, `current_phase_title` = "API + DB core", `next_step` = "DB-E-001: Database schema & migrations"
- `RoadmapPanel.jsx` was NOT modified; the data.json roadmap/meta contract shape is preserved.
- Full compose build (`docker compose -f ai-infrastructure/project-manager/dashboard/docker-compose.yml up --build`) is reserved for the Orchestrator's close-phase visual check (COR-07 practice per the kickoff).
