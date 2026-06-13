---
schema_version: 1
id: COR-T-047
title: "Derive the STATUS activity surface (ADR-039): git-sourced last_updated + recent_updates, retire universal STATUS hygiene"
status: backlog
labels: []
priority: P2
created: 2026-06-13
updated: 2026-06-13
---

## Description

Implement ADR-039 (`./decisions/ADR-039-status-derived-activity-surface.md`). The decision: `last_updated` and `recent_updates` become DERIVED from git history (the activity surface, history); `## Current phase` / `## Next step` / `## Blocked on` stay HAND-AUTHORED (forward intent). This removes the `last_updated`/`recent_updates` drift class (the COR-03 terminal derivation) and structurally closes the cross-workspace-write drift gap (ADR-027) that a `/database-orchestrator` survey surfaced on the stale `database/STATUS.md`.

All design decisions are pinned in ADR-039; this task implements them, it does not re-decide. Routes through the dispatched-worker flow. **Visual deliverable** (the dashboard roadmap/activity panels): carries a headless-render + user visual gate at close per COR-07.

**Sequence the work in two phases so there is never a window where the activity surface is neither hand-maintained nor derived** (ADR-039 decision 6):

### Phase A: build the derivation (ETL + container), contract stable

1. **ETL.** Rewrite `ai-infrastructure/project-manager/dashboard/etl.py` so the per-workspace `last_updated` derives from `git log -1 -- <workspace-path>` and the per-workspace `recent_updates` / the aggregate `recent_activity` derive from `git log -- <workspace-path>` (replacing `parse_recent_updates` reading frontmatter and the `coordinator_fm.get("last_updated")` / per-dept `fm.get("last_updated")` reads). Keep the `data.json` contract shape stable (the `recent_updates`, `recent_activity`, `last_updated` fields already exist) so `RoadmapPanel.jsx` / the activity panel need minimal or no change (ADR-037 precedent). Decide entry count/formatting (commit date + subject; map the task/ADR ID out of the subject for display).
2. **Container.** Add git to the dashboard serve image (`Dockerfile`, `python:3.12-slim`) so `etl.py` can read history; the compose mount already includes `/repo/.git` read-only. Handle git's `safe.directory` ownership check under the read-only mount (e.g. `git config --global --add safe.directory /repo` in `entrypoint.sh`). dulwich (pure-Python) is the fallback if the git-binary route is problematic in-container.
3. **Verify.** Compose build + headless render (COR-07): confirm the roadmap and the activity feed render from the git source, `data.json` contract intact, panels unchanged. At this point STATUS.md frontmatter still carries `last_updated`/`recent_updates` but the dashboard ignores them; no drift window.

### Phase B: doctrine cascade + frontmatter removal

4. **Remove the universal STATUS-hygiene obligation** from `docs/ai-orchestration/roles/EXECUTOR-ROLE.md`, `docs/ai-orchestration/roles/TEST-DESIGNER-ROLE.md`, `docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md` (the lifecycle text and the R6 "Name task-specific STATUS deltas" convention), the three orchestrator commands (`.claude/commands/{project-manager,database,backend-api}-orchestrator.md`), and the department command template (`ai-infrastructure/project-manager/templates/department/orchestrator-command.md`). Rewrite the survey doctrine so a surveying orchestrator consults `git log -- <workspace>` (or the dashboard) for recent activity instead of reading `recent_updates` from frontmatter (ADR-039 decision 3).
5. **Remove the `last_updated` and `recent_updates` frontmatter fields** from every workspace `STATUS.md` (coordinator + departments + the department template), leaving `schema_version` (+ `department`) and the hand-authored `## Current phase` / `## Next step` / `## Blocked on` body. Update the STATUS schema wherever it is documented.
6. **Codify the commit-message convention (owned-but-advisory, ADR-039 decision 5):** every commit subject leads with the task/ADR ID plus a specific summary. Record it as a convention (advisory, with a `commit-msg` hook or checker as the recorded re-open path); place it where commit conventions belong (a CLAUDE.md operating-rules note or the docs index, decided during kickoff drafting).
7. **OBSERVATIONS:** flip COR-03 to its terminal state (the last hand-maintained STATUS surface is now derived), per ADR-039 Consequences.

Out of scope: the ADR-039 decision itself (accepted); any change to the `data.json` contract shape (source-only); the `## Current phase` / `## Next step` / `## Blocked on` hand-authored sections (kept); the post-dogfood `issue_events` source swap (ADR-008, a later phase).

## Activity log

- 2026-06-13: Created in backlog by the project-manager coordinator (orchestrator-direct) on acceptance of ADR-039. The implementation cascade for deriving the STATUS activity surface; two-phase sequencing pinned (derive-ETL + container render-verified first, then the doctrine cascade + frontmatter removal) so the activity surface is never simultaneously un-maintained and un-derived. Left standalone (no `epic:`) deliberately: the only fitting epic (COR-E-004 dashboard) is a done Phase-1 epic and linking a new task would reopen its rollup; ADR-036 permits standalone tasks. P2; visual deliverable (COR-07 render gate at close). Routes through the dispatched-worker flow; analog of the COR-T-044/045 two-phase split.
