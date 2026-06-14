---
schema_version: 1
id: COR-T-050
title: "Derive the STATUS narrative body (current phase / next step / blocked); remove hand-authored body"
status: done
labels: []
priority: P2
created: 2026-06-13
updated: 2026-06-14
---

## Description

Implements ADR-040 (accepted 2026-06-13). The analog of COR-T-047 (which implemented ADR-039). ADR-040 decided that the `STATUS.md` narrative body (`## Current phase`, `## Next step`, `## Blocked on`) is redundant authored prose that restates already-derived facts and exists only to drift (it surfaced as the COR-T-049 incident: retired `P2-2` vocabulary + cleared `DB-T-001` gating). Derive it fully and remove the hand-authored body, completing the ADR-037 -> ADR-039 -> ADR-040 derivation line so no hand-authored content remains in `STATUS.md`.

Read ADR-040 (`ai-infrastructure/project-manager/decisions/ADR-040-status-narrative-drift-surface.md`) before scoping; it is the authority. Key pins:

- **Sources.** `## Current phase` / `## Next step` reuse the existing roadmap derivation in `etl.py` (`derive_current_phase` / `derive_current_phase_title` / `derive_next_step`); no new source. `## Blocked on` is newly derived from each workspace's `tasks/blocked/` tree (blocked task ids + each task's recorded reason).
- **Materialization (M2).** The dashboard / `data.json` is the single read surface. `etl.py` does NOT write back into the repo (ADR-039 kept `STATUS.md` untouched; preserve that). The three narrative sections are removed from every `ai-infrastructure/*/STATUS.md`; each `STATUS.md` reduces to its frontmatter (`schema_version`, plus `department` on department STATUS) and a one-line pointer to the derived surface.
- **Survey doctrine.** Orchestrators read current phase / next step / blocked from the dashboard / `data.json` (or, offline, the structured roadmap and `tasks/blocked/` trees directly). Extends ADR-039 decision 3.
- **Doctrine cascade.** Update the `STATUS.md` description (from "current phase and next step" to "pointer to the derived dashboard surface") and the survey doctrine across the role docs (`docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md` and the worker/test-designer role docs where they reference STATUS sections), the three `*-orchestrator` commands, and the department command template. The COR-T-049 STATUS-narrative cleanup and the ADR-039 hygiene-removal cascade are the precedents for the doc sweep.
- **Sequencing (load-bearing, per ADR-040 decision 7).** Land and render-verify the derived `## Blocked on` surface on the dashboard FIRST; only then remove the narrative bodies and run the doctrine cascade, so there is never a window where a section is neither authored nor derived.
- **No transitional lint** (ADR-040 decision 6): the narrative is removed, not guarded.
- **Scope expansion (folded in 2026-06-13, orchestrator homework).** Removing the hand-authored STATUS body also makes the `status_deltas` kickoff field and the **R6 kickoff rule** vestigial: they exist only to let a dispatched worker edit those sections. Phase 2 therefore also retires `status_deltas` / R6 across the dispatch toolchain: `ORCHESTRATOR-ROLE.md` (R6 convention + pending-ADR playbook step 6), `EXECUTOR-ROLE.md` and `TEST-DESIGNER-ROLE.md` (wrap-up STATUS-deltas + not-in-scope), `EXECUTOR-AGENT-SPEC.md` and `TEST-DESIGNER-AGENT-SPEC.md` (field def + STATUS-once rule), `KICKOFF-DRAFTER-SPEC.md` (field + template), `KICKOFF-CHECKER-SPEC.md` (R6 enforcement). Retiring R6 vacates a kickoff rule number (tombstone, do not renumber R1-R5/R7-R8). ADR-040 decision 7 enumerated the role-doc/command/template cascade but not this toolchain retirement; folded in here per operator decision (2026-06-13) rather than amending ADR-040.

Routes through the dispatched-worker flow (dashboard ETL change + a documentation cascade). Splits into two dispatches mirroring the ADR-039/COR-T-047 sequencing: phase 1 (derive blocked + render-verify the dashboard surface), then phase 2 (remove the four STATUS bodies + reduce to pointer + the full doctrine cascade including the R6/status_deltas retirement).

## Activity log

- 2026-06-13: Created in backlog. Implements ADR-040 (accepted 2026-06-13); analog of COR-T-047. Filed as the spawned implementation task at ADR-040 resolution. Unlabelled per ADR-031.
- 2026-06-13: Picked up (in-progress). Routing through the dispatched-worker flow with the ADR-040 sequencing (phase 1: derive + verify the blocked surface; phase 2: remove narrative bodies + doctrine cascade). Orchestrator doing homework (dashboard structure, doctrine-cascade reference sites) before resolving anticipated decisions and drafting the phase-1 kickoff.
- 2026-06-13: Homework surfaced that `status_deltas`/R6 become vestigial once the STATUS body is derived. Operator decision: fold the R6/status_deltas retirement into phase 2 (not a separate task, not an ADR-040 amendment). Scope updated above. Curated doctrine-cascade inventory (Explore sweep) held for the phase-2 kickoff.
- 2026-06-14: Done. Three dispatches, all drafter+checker PASS / prelaunch W1 PASS / close W2 PASS, each verified against disk. Phase 1 (committed `8e35e9e`): etl.py derives the cross-workspace blocked set (id/title/workspace + reason from the last activity-log bullet) into a top-level `blocked` and per-workspace `workspace_details[slug].blocked`; new BlockedPanel (landing) + conditional Blocked card (workspace view); verified live (empty / populated-via-fixture / revert) and user visual-confirmed. Phase 2a (committed `b62db1d`): removed the `## Current phase` / `## Next step` / `## Blocked on` bodies from all four STATUS.md (3 live + template), reduced to frontmatter + derived-pointer; cascaded the STATUS description + survey doctrine through the CLAUDE.md tables, READMEs, and the three commands + template; verified the dashboard still derives current_phase=2 with the bodies gone. Phase 2b (committed `ab6e811`): retired `status_deltas` and tombstoned R6 (no renumber; R7/R8 intact) across the three role docs, four specs, four agent definitions, plus an ADR-023 forward-pointer. Related: a derived-roadmap false-"done" bug surfaced during phase-1 verify (Phase 2 read done because the Backend API epic was unfiled) was fixed by filing API-E-001 (`530b671`) and captured as OBSERVATIONS COR-08 / pending ADR-041. Pre-existing follow-up (not this task): an em-dash regex literal in KICKOFF-CHECKER-SPEC.md (the em-dash detector's own pattern).
