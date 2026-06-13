---
schema_version: 1
id: COR-T-050
title: "Derive the STATUS narrative body (current phase / next step / blocked); remove hand-authored body"
status: backlog
labels: []
priority: P2
created: 2026-06-13
updated: 2026-06-13
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

Routes through the dispatched-worker flow (dashboard ETL change + a documentation cascade). Likely splits into at least two dispatches mirroring the ADR-039/COR-T-047 sequencing (derive-and-verify, then remove-and-cascade); the orchestrator decides the split at kickoff time.

## Activity log

- 2026-06-13: Created in backlog. Implements ADR-040 (accepted 2026-06-13); analog of COR-T-047. Filed as the spawned implementation task at ADR-040 resolution. Unlabelled per ADR-031.
