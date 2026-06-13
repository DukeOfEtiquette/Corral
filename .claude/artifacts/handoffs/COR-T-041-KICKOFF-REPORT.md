## Deliverables completed

- **Correction 1 (rollup formula):** `derive_epic_status` in `etl.py` updated to implement ADR-036 "Completion and status" correctly. Added a fourth check after the all-backlog fallback: if any task is done/accepted but not all are, the status is `in-progress` (partial progress reads as in-progress, not planned). E2.1 (DB-T-001 done + DB-T-002 backlog) now correctly resolves to `in-progress` (1/2).

- **Correction 2 (dept badge - ETL):** `run_etl` epic assembly now reads `ep.get("dept", "")` and emits `dept` in every epic output object. Module docstring updated to include `dept` and `cross_dept_warning` in the epic shape description.

- **Correction 2 (dept badge - RoadmapPanel):** `DeptBadge` component added. Each epic header now renders `<DeptBadge>` as the left-most badge in `.roadmap-epic-badges`, before `<EpicRollupBadge>` and the ADR badges. Order: [dept] [rollup] [ADR badges] [cardinality warning] [cross-dept warning] [expand toggle].

- **Correction 2 (dept badge - CSS):** `.badge-dept` class added to `styles.css` with a neutral category-tag treatment (`#1e2835` background, `#88aac8` text, monospace font at 0.65rem). Visually distinct from status-colored rollup/task badges and matches the `.badge-role`/`.badge-domain` idiom.

- **Correction 3 (cross-dept consistency check):** Cross-department check implemented in `run_etl` epic assembly loop. For each resolved task ID in an epic, the check determines its owning workspace (the slug whose `per_workspace_tasks` list contains that task ID) and flags the epic if any task's workspace differs from the epic's `dept`. Result emitted as `cross_dept_warning` on the epic output object. RoadmapPanel renders a `dept!` warning badge (reusing `.badge-ref-unresolved` + `.roadmap-cardinality-warning` with a tooltip) when `cross_dept_warning` is set. A SPOT-TEST block (controlled by `_spot_test_active = False`) injects COR-T-001 (coordinator tree) into E2.1 (dept=database) to prove the check fires; spot-test verified, then reverted to `False`. Current data produces no cross-dept warnings.

- **Verification:** Rebuilt with `--no-cache` twice (spot-test run + final revert run). Final `data.json` confirms: E2.1 status=`in-progress` (1/2); all epics carry their `dept`; no warnings on current data; `current_phase`=2; `next_step`=`E2.1: Database schema & migrations`; Phase 0 done; Phase 1 all 5 epics done; Phase 2 current.

## Decisions made

- **Dept badge display format:** The dept slug is displayed verbatim (e.g. `database`, `project-manager`) in monospace, matching the compact format requested. `slug_to_display` was available but the raw slug is more compact and reads clearly as a category label. The badge includes a `title` tooltip showing `Department: <slug>` for accessibility.

- **Cross-dept warning badge text:** Used `dept!` (vs. `!`) to distinguish the cross-dept warning from the cardinality warning visually, since both could appear simultaneously on the same epic. Tooltip carries the full message naming the offending task(s).

- **SPOT-TEST mechanism:** Implemented as a guarded block with `_spot_test_active = False`. This lets the test be re-enabled without changing STATUS.md or data, following the COR-T-031 dormant-warning precedent. The spot-test injects COR-T-001 (project-manager tree) into E2.1 (dept=database).

## Surprises

- The spot-test output showed `task_count=3` and `done_count=2` when `_spot_test_active=True` because DB-T-001 is done and COR-T-001 (done, in coordinator tree) both count as done. The warning fired correctly. After revert: task_count=2, done_count=1, as expected.

## Follow-ups

- The SPOT-TEST block in `etl.py` uses a private flag `_spot_test_active = False`. If this pattern is used in future corrections, a triage note: consider a named constant or CLI flag for spot-testing dormant checks. Triage to orchestrator for the next dashboard iteration (COR-T candidate).

- The `_rollup_statuses` helper currently treats "any in-progress or blocked" as the winning state for range rollup. Now that `derive_epic_status` also uses partial-progress-as-in-progress, there may be a future opportunity to unify the two rollup paths. Low priority; triage to orchestrator.

## Files touched

- `./ai-infrastructure/project-manager/dashboard/etl.py`
- `./ai-infrastructure/project-manager/dashboard/src/panels/RoadmapPanel.jsx`
- `./ai-infrastructure/project-manager/dashboard/src/styles.css`
- `./.claude/artifacts/handoffs/COR-T-041-KICKOFF-REPORT.md` (this report)

Note: `./ai-infrastructure/project-manager/STATUS.md` was NOT touched per kickoff hard rules and STATUS deltas section (orchestrator applies hygiene).

## Build / verification status

**Verified by executor (automated):**
- Build: `docker compose -f ai-infrastructure/project-manager/dashboard/docker-compose.yml build --no-cache` succeeded (twice: spot-test run + final).
- Container started: `up -d` succeeded.
- `data.json` checked via `docker exec`:
  - E2.1 status = `in-progress` (was: `planned`; FIXED)
  - E2.1 done_count=1, task_count=2 (DB-T-001 done, DB-T-002 backlog)
  - All epics carry `dept` field (verified all phases)
  - No cardinality warnings on current data
  - No cross-dept warnings on current data
  - `current_phase` = 2
  - `next_step` = `E2.1: Database schema & migrations`
  - Phase 0 done; Phase 1 done (all 5 epics); Phase 2 current; Phases 3-8 upcoming
  - Cross-dept spot-test: fired correctly for COR-T-001 in E2.1 (foreign workspace detected); reverted cleanly.

**Requires user visual confirmation (not automated):**
- Dept badges render left-most in each epic header (before rollup badge)
- E2.1 rollup badge now shows blue (in-progress) with "1/2" text
- Expandable epics, ADR badges, legacy phase dimming, layout all look correct
- No regressions to other panels
