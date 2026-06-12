# Dashboard roadmap: status-colored task/ADR reference badges (COR-T-040)

## Target

This is AI-infrastructure work (ADR-005, domain 2): the project-manager coordinator dashboard tooling. You rework the ROADMAP panel of the dashboard so phase/milestone progress is conveyed by structured, deterministically-resolved task/ADR reference badges colored by live status, replacing the hand-set status pills and the prose ADR parentheticals. This reduces drift (the project's anti-drift principle): each reference's status is resolved from an authoritative source the ETL already collects, rather than re-typed by hand on the milestone. Three files are in scope: the ETL (`etl.py`), the panel (`RoadmapPanel.jsx`), and the stylesheet (`styles.css`).

The STATUS.md `roadmap:` milestone schema has already been seeded by the Orchestrator and is a READ-ONLY reference for you. You read it to know what the ETL must resolve; you never write to it.

## Decisions resolved by the Orchestrator

All decisions below are pinned. Do not re-deliberate them; implement them as stated.

- **Purpose.** Convey roadmap progress via reference badges resolved deterministically in the ETL and colored by live status, replacing hand-set status pills and prose ADR parentheticals. This is an anti-drift change: status is resolved from the authoritative source the ETL already collects, not re-typed on the milestone.

- **Display removal (Fork 1).** Remove the phase-level status badge (the DONE/CURRENT/UPCOMING pill in `.roadmap-header`, currently `badge badge-roadmap-${item.status}`) AND the milestone-level status badge (the DONE/PLANNED/IN-PROGRESS pill, currently `badge badge-milestone-${ms.status}`). Keep the phase card's left color bar (the `roadmap-${item.status}` class on the `<li>`) and the CURRENT phase's blue background untouched. The `STATUS_LABELS` and `MILESTONE_STATUS_LABELS` maps in `RoadmapPanel.jsx` are no longer used for badges; remove them (they are not needed for anything else).

- **Schema (Fork 4).** Each roadmap milestone in STATUS.md frontmatter now carries optional `tasks: []` and `adrs: []` lists (already seeded; see References). Each list entry is either a bare ID (`COR-T-014`, `DB-T-001`, `ADR-012`) or a `..` range token (`ADR-001..009`, `COR-T-001..006`). Ranges are single-prefix and numeric-span: expand `ADR-001..009` to `ADR-001` through `ADR-009`; expand `COR-T-001..006` to `COR-T-001` through `COR-T-006`. A milestone may carry both lists, one, or neither.

- **Resolution, deterministic in etl.py.** For each milestone reference: expand range tokens to individual IDs, then resolve each ID's status.
  - Task IDs resolve against the union task list from `collect_all_tasks` (which already reads every workspace tree per ADR-031, so a department ref like `DB-T-001` resolves). A task's status is the directory it sits in: `backlog` / `in-progress` / `blocked` / `done` (see `TASK_STATUSES` at `etl.py` line 98).
  - ADR IDs resolve against `collect_adrs`. An ADR's status is its frontmatter `status` field, which in this repo is only `accepted` or `pending`.
  - An ID that resolves to no record is `unresolved`.

- **Range rendering (Fork 3).** A bare ID renders as one individual badge. A `..` range token renders as ONE range badge whose color is the rollup of its members: if every member shares a status, use that status's color; if members differ, use the distinct `mixed` color. The range badge must show the range label and a member count (for example, `ADR-001-009 · 9 accepted`; exact label text is your call, but the range and the count must both be visible). A discrete list of 2-4 bare IDs renders as that many individual badges.

- **Milestone effective status (Fork 2), DERIVED.** Milestone effective status is derived, not read directly from the hand-set field:
  - If the milestone has any references, roll them up: all members `done`/`accepted` -> `done`; any member `in-progress`/`blocked` -> `in-progress`; otherwise `planned`.
  - If the milestone has NO references, fall back to its hand-set `status:` frontmatter field (the escape hatch).
  - `derive_current_phase` and `derive_next_step` currently read `ms.get("status")` directly (at `etl.py` lines ~203 and ~240). They must instead consume this derived effective status, so a milestone whose references are all done counts as done even if its hand-set `status:` has drifted.
  - The effective status is still emitted in the roadmap output for completeness, but it is NO LONGER rendered as a badge.

- **Status to color palette.** Reuse existing `styles.css` badge color VALUES where they exist; add classes only for the new states.
  - `done` / `accepted` = green (existing value bg `#1a3328`, fg `#5ec98a`; see `.badge-roadmap-done` / `.badge-milestone-done` / `.badge-adr-accepted`).
  - `in-progress` = blue (existing value bg `#1a2050`, fg `#8aacff`; see `.badge-milestone-in-progress`).
  - `blocked` = red (existing value bg `#3a1a1e`, fg `#f08090`; see `.badge-adr-superseded`). Note: the repo has no ADR `superseded` state in use; this red value is reused for the task `blocked` state only.
  - `backlog` / `planned` / `pending` = grey (existing value bg `#2a2d3e`, fg muted var; see `.badge-planned`).
  - range `mixed` = amber (existing value bg `#2e2010`, fg `#d4944a`; see `.badge-adr-pending`).
  - `unresolved` = a distinct LOUD treatment that cannot be confused with solid-red `blocked`: a dashed bright border plus a `?` or `⚠` prefix on the badge. You design the exact CSS, but it must read as a broken-reference error, visually distinct from every status color above.

- **Badge form.** Task and ADR reference badges visually echo the existing monospace ID-tag idiom (the current `.roadmap-milestone-task` / `.roadmap-milestone-id` style), now colored by status. Render a milestone's task badges and ADR badges in a stable order (tasks then ADRs is fine).

- **ETL collection ordering.** In `run_etl`, the roadmap is assembled (`etl.py` lines ~476-503) BEFORE `all_tasks` and `adrs` are collected (lines ~508 and ~512). Reference resolution needs both. Either reorder the `all_tasks` and `adrs` collection above the roadmap assembly, or resolve references in a second pass after both exist. Either is acceptable.

- **JSON contract docstring.** Update the `etl.py` module docstring (the `roadmap:` shape at lines ~39-44) to describe the new per-milestone resolved-reference output. Each reference carries at minimum: a display label, a resolved status used for coloring, a type of `task` | `adr`, and a render flavor of `single` | `range` | `unresolved`. Range references additionally carry a member count and the rollup status. Keep the docstring accurate to whatever shape you implement.

- **STATUS.md is out of scope and read-only.** The Orchestrator owns the STATUS.md `roadmap:` milestone block and has already seeded it. You MUST NOT edit STATUS.md at all (not the roadmap block, not the `recent_updates` log). Read its seeded milestones to know what the ETL must resolve; never write to it. The Orchestrator applies STATUS hygiene directly for this task (see STATUS deltas below).

## Deliverables

- **`etl.py`:** range-expansion plus reference-resolution against `collect_all_tasks` and `collect_adrs`; per-milestone resolved-reference objects in the roadmap output (label, resolved status, type, flavor; range references also carry member count and rollup status); milestone effective-status derivation with the references-rollup-then-hand-set-fallback rule; `derive_current_phase` and `derive_next_step` updated to consume the derived effective status; the module docstring `roadmap:` shape (lines ~39-44) updated to the new output.
- **`RoadmapPanel.jsx`:** remove the phase status badge and the milestone status badge (and the now-unused `STATUS_LABELS` / `MILESTONE_STATUS_LABELS` maps); render the resolved task/ADR badges (individual / range / unresolved) colored by status; keep the side color bar and the CURRENT phase background.
- **`styles.css`:** status-colored badge classes reusing the existing green/blue/red/grey VALUES; new `mixed` (amber) and `unresolved` (loud, distinct) treatments.

## Files in scope

- `ai-infrastructure/project-manager/dashboard/etl.py`
- `ai-infrastructure/project-manager/dashboard/src/panels/RoadmapPanel.jsx`
- `ai-infrastructure/project-manager/dashboard/src/styles.css`

## Files out of scope

- `ai-infrastructure/project-manager/STATUS.md` (Orchestrator-owned schema source, already seeded; READ-ONLY reference, never edit, including the `recent_updates` log).
- All other dashboard files: `ai-infrastructure/project-manager/dashboard/src/App.jsx`, `ai-infrastructure/project-manager/dashboard/src/views/LandingView.jsx`, `ai-infrastructure/project-manager/dashboard/src/views/WorkspaceView.jsx`, all other `ai-infrastructure/project-manager/dashboard/src/panels/*.jsx`, `index.html`, `Dockerfile`, `docker-compose.yml`, `entrypoint.sh`, `package.json`, `vite.config.js`.
- Everything under `app/` and every other repo path.

## References

- `ai-infrastructure/project-manager/dashboard/etl.py` - the ETL you edit. Key functions: `derive_current_phase` (line ~174), `derive_next_step` (line ~223), `derive_current_phase_title` (line ~210), `collect_all_tasks` (line ~425), `collect_tasks` (line ~256), `collect_adrs` (line ~325), `run_etl` roadmap assembly (lines ~476-503), `all_tasks` collection (line ~508), `adrs` collection (line ~512). `TASK_STATUSES = ["backlog", "in-progress", "blocked", "done"]` (line 98). Module docstring `roadmap:` shape at lines ~39-44.
- `ai-infrastructure/project-manager/dashboard/src/panels/RoadmapPanel.jsx` - the panel you edit. Currently renders `STATUS_LABELS` (phase badge), `MILESTONE_STATUS_LABELS` (milestone badge), and a plain `.roadmap-milestone-task` tag.
- `ai-infrastructure/project-manager/dashboard/src/styles.css` - existing badge palette to reuse: `.badge-roadmap-done` (green `#1a3328`/`#5ec98a`, line ~144), `.badge-milestone-in-progress` (blue `#1a2050`/`#8aacff`, line ~241), `.badge-adr-superseded` (red `#3a1a1e`/`#f08090`, line ~150), `.badge-planned` (grey `#2a2d3e`/muted, line ~139), `.badge-adr-pending` (amber `#2e2010`/`#d4944a`, line ~149); roadmap-milestone layout classes at lines ~204-242.
- `ai-infrastructure/project-manager/STATUS.md` - the seeded roadmap milestone schema (READ-ONLY reference). Milestones with references: P0-2 `adrs: [ADR-001..009]`, P0-3 `tasks: [COR-T-001..006]`, P1-1 `tasks: [COR-T-001]`, P1-4 `tasks: [COR-T-014]`, P1-6 `tasks: [COR-T-017]`, P2-0 `tasks: [COR-T-023]`, P2-1 `tasks: [DB-T-001]` `adrs: [ADR-012]`, P2-3 `adrs: [ADR-011]`, P2-4 `adrs: [ADR-014, ADR-006]`. Reference-less milestones (escape-hatch path): P0-1, P1-2, P1-3, P1-5, P2-2, and all of phases 3-8.
- ADR status vocabulary in this repo is ONLY `accepted` and `pending` (no `proposed`/`rejected`/`superseded` in use); the red `superseded` color VALUE is reused for the task `blocked` state, not for any ADR state.
- Exact verify command (use verbatim; do not invent service names): `docker compose -f ai-infrastructure/project-manager/dashboard/docker-compose.yml up --build`. The compose file defines a SINGLE service named `dashboard` (build + entrypoint ETL + http.server) serving on port 8420. There is NO `etl` service and NO `build` service; do not reference them.

## Related tasks and ADRs

- COR-T-017 - built the roadmap milestone sub-list and the `badge-milestone-*` classes / `MILESTONE_STATUS_LABELS` this task modifies. The direct predecessor of the panel you are changing.
- COR-T-029 - made the dashboard derive `current_phase` / `current_phase_title` / `next_step` from milestone statuses in `etl.py`. This task changes what those derivations read: from the hand-set `ms.status` to the new reference-derived effective status.
- COR-03 (OBSERVATIONS.md) - logged the hand-set milestone status as the dashboard's remaining drift surface. This task reduces that surface by deriving effective status from references; the Orchestrator will promote COR-03 in a follow-on ADR.
- ADR-031 - per-department task trees; the reason `collect_all_tasks` reads every workspace tree so a department reference like `DB-T-001` resolves.
- ADR-035 / COR-04 / COR-05 / COR-06 - cited-reference integrity for dispatched work. The `unresolved` badge is the deterministic in-dashboard guard against a roadmap reference that points at a nonexistent task/ADR, in the same spirit.

## STATUS deltas

No STATUS edits by you. STATUS.md is out of scope and READ-ONLY for this task (it is the seeded schema source, owned by the Orchestrator). Do NOT apply the universal STATUS hygiene write for this task: the Orchestrator applies all STATUS hygiene directly. You perform zero STATUS edits, and STATUS.md must not appear in your report's "Files touched".

## Hard rules

- **Do not edit STATUS.md** in any way (not the `roadmap:` block, not `recent_updates`, not `last_updated`). It is a read-only input. This overrides the universal wrap-up STATUS hygiene step in `EXECUTOR-ROLE.md` for this task only.
- **Reuse existing color VALUES** for `done`/`accepted` (green), `in-progress` (blue), `blocked` (red), `backlog`/`planned`/`pending` (grey), and `mixed` (amber) rather than inventing new hex values; add new CSS classes only for the new states and for the loud `unresolved` treatment.
- **Pin the verify command verbatim** as given in References. The compose file has a single service named `dashboard`; do not reference an `etl` or `build` service.

## Verification

This is a visual deliverable; the USER performs the visual confirmation (compose up, port 8420). Your job is to verify the data layer:

1. Run the pinned compose command: `docker compose -f ai-infrastructure/project-manager/dashboard/docker-compose.yml up --build`. This builds and runs the ETL through the single `dashboard` service.
2. Confirm `data.json` reflects the seeded references resolving as expected:
   - P1-1 / P1-4 / P1-6 / P2-0: each one green task badge.
   - P2-1: one green task badge (`DB-T-001` done) plus one green ADR badge (`ADR-012` accepted).
   - P2-3: one grey ADR badge (`ADR-011` pending).
   - P2-4: two green ADR badges (`ADR-014`, `ADR-006` accepted).
   - P0-2: one green range badge (`ADR-001-009`, all accepted).
   - P0-3: one green range badge (`COR-T-001-006`, all done).
   - P0-1 / P1-2 / P1-3 / P1-5 / P2-2: no reference badges (escape-hatch path, hand-set status fallback).
3. The `in-progress`, `blocked`, `mixed`-range, and `unresolved` color paths have NO live instance in the current seed (by design: STATUS.md carries no blocked/mixed/broken references). Implement all four branches fully and confirm them by reading your own code; state plainly in your report that they are implemented-but-not-live-verified. Do NOT fabricate a broken reference into STATUS.md to exercise the `unresolved` path (STATUS.md is read-only).

This is the single acceptance gate: the data layer resolves the seeded references as enumerated above, with the four no-live-instance branches implemented and code-confirmed. The user performs the visual render confirmation after you return.

## Executor pointer

You are the dispatched `executor` (ADR-028). Universal executor conventions (writing rules, run policy, git boundaries, the pinned six-section report shape) live in `docs/ai-orchestration/roles/EXECUTOR-ROLE.md`; this kickoff references them rather than re-emitting them. Write your closing report to `./.claude/artifacts/handoffs/COR-T-040-KICKOFF-REPORT.md` per `EXECUTOR-ROLE.md`, section "Report shape". Note the STATUS-deltas section above overrides the universal wrap-up STATUS hygiene step for this task: you make no STATUS edits.
