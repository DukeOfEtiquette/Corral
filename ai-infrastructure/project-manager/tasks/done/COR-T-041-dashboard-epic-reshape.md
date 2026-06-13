---
schema_version: 1
id: COR-T-041
title: "Dashboard reshape: render the phase -> epic -> task roadmap (ADR-036)"
status: done
labels: []
priority: P2
created: 2026-06-13
updated: 2026-06-13
---

## Description

Reshape the project-manager dashboard to consume the ADR-036 roadmap structure. The coordinator `STATUS.md` `roadmap:` block has been restructured (orchestrator-direct) from `phase -> milestone` to `phase -> epic -> task`: each phase carries `epics: []`, each epic carries `tasks: []` (work) and `adrs: []` (governing references), and the hand-set status is gone (status rolls up from tasks). Phase 0 carries `legacy: true` and empty epics. The current dashboard `etl.py` still reads the old `milestones` schema, so the live roadmap is degraded until this lands. This is the dashboard half of the ADR-036 restructure; it routes through the dispatched-worker flow (dashboard code is a deliverable).

Pinned design (resolved with the user 2026-06-13):

- **Density (the binding decision): epic rollup, expandable.** The roadmap renders `phase -> epic`; each epic shows a rollup badge (count + rolled-up status color, reusing the COR-T-040 range-badge style) plus its governing ADR badges (informational). Clicking an epic expands its individual task badges (the COR-T-040 task badge components, colored by task status); collapsed by default.
- **Status rolls up, derived, no hand-set pills.** Epic status = rollup of its TASK refs only (all done -> done; any in-progress/blocked -> in-progress/blocked; 0 tasks -> planned). ADR refs are informational, never drive status (ADR-036). Phase status derives from its epics (all done -> done; legacy -> done); current_phase = lowest phase not fully done.
- **Phase 0 legacy:** rendered dimmed/closed as a done bootstrap phase with no epics; exempt from cardinality.
- **Future/forming epics (0 tasks):** rollup shows "planned" (grey), ADR badges shown, expand reveals no tasks. Not a warning.
- **Cardinality consistency check:** flag an epic with exactly 1 task (the "should be a standalone task" smell) and a non-legacy phase with <2 epics, via a subtle warning indicator (reuse the unresolved/warning treatment). 0-task epics are forming, not flagged. The check is dormant on current data (no 1-task epics; every non-legacy phase has >=2 epics); spot-test and revert, per the COR-T-031 precedent.

## Activity log

- 2026-06-13: Created and picked up (in-progress). Follows the ADR-036 STATUS.md restructure (orchestrator-direct). Density decision (epic rollup, expandable) resolved with the user; routes through the dispatched-worker flow. The vocabulary cascade (tasks/README Vocabulary section + milestone->epic doc sweep) is a separate follow-on (COR-T-042, not yet filed).
- 2026-06-13: Done. Dispatched executor reshaped the dashboard to phase->epic->task; a corrective dispatch then fixed the rollup formula (E2.1 partial-progress now reads in-progress), added the left-most department badge per epic, and wired the cross-department consistency check. User-confirmed visually (dept badges left-most, E2.1 blue, legacy phase dimmed). Deliverable committed in 37ac5f4 (alongside the STATUS phase->epic->task restructure, the ADR-036 epic-scope + rollup amendment, and DB-T-002). Both consistency checks dormant on current data, spot-tested and reverted. Kickoff/report pair committed in 37ac5f4 (ADR-024).
