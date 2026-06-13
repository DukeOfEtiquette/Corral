---
schema_version: 1
id: COR-T-045
title: "Repoint the dashboard ETL at the epic/phase files and retire the STATUS roadmap block (ADR-037 Phase B)"
status: done
labels: []
priority: P2
created: 2026-06-12
updated: 2026-06-12
---

## Description

Phase B of the ADR-037 work-item storage cascade, the cutover. Depends on COR-T-044 (Phase A), which builds the epic/phase file structure and the bottom-up linkage while leaving the dashboard ETL and the STATUS.md roadmap block untouched. This task switches the dashboard's source and removes the old representation, so it must run after Phase A is complete and verified. Routes through the dispatched-worker flow. This is a **visual deliverable**: it carries a headless-render + user visual gate at close per COR-07.

In scope:

1. **Rewrite the dashboard ETL reader.** `ai-infrastructure/project-manager/dashboard/etl.py` currently reads the roadmap from the STATUS.md `roadmap:` block (`derive_current_phase`, `derive_roadmap_status`, `derive_epic_status`, `resolve_milestone_refs`, and the roadmap data contract). Rewrite it to reconstruct the roadmap from the Phase-A files: walk the `epics/` trees, group epics by their `phase:` field, attach tasks by their `epic:` field, read phase order from the `phases/` files, and roll status up per ADR-036. Provisional (not-yet-materialized) epics simply do not appear; future phases render from their phase file.

2. **Retire the STATUS roadmap block.** Remove the `roadmap:` block from STATUS.md frontmatter once the ETL reads the files (ADR-037 decision 6, the churn-coupling resolution). STATUS keeps the current-phase narrative and `recent_updates`.

3. **Keep the data contract stable, verify the render.** The roadmap shape emitted to `data.json` should stay stable so `RoadmapPanel.jsx` needs minimal or no change (the derivation changes its source, not its output); confirm this and adjust the panel only if the contract must shift. Headless-render the running dashboard and confirm the roadmap renders correctly from the new source before the user gate.

Out of scope: any change to the Phase-A file structure or linkage (COR-T-044, accepted as the input); any re-curation of epic membership; the deferred provisional epics; the ADR-038 app-schema realization (deferred to the dogfood-import build).

References: `./decisions/ADR-037-work-item-storage-representation.md`, `./decisions/ADR-038-phase-as-first-class-view.md`, `./decisions/ADR-036-work-item-taxonomy.md`, `ai-infrastructure/project-manager/dashboard/etl.py`, the COR-T-044 outputs (the `epics/`/`phases/` trees).

## Activity log

- 2026-06-12: Created in backlog. The Phase B cutover of the ADR-037 cascade, split from COR-T-044 with the user so the dashboard never breaks mid-restructure (Phase A builds the new files with the old ETL still reading the old block; this task switches the ETL and removes the block). Picked up after COR-T-044 is complete and verified. Visual deliverable (COR-07 render gate at close).
- 2026-06-12: Picked up; moved to in-progress. COR-T-044 (Phase A) is done (committed 7c6c8f7 + 3299ea4): the epics/ + phases/ files and bottom-up linkage are in place. Orchestrator homework on etl.py + RoadmapPanel.jsx surfaced two pinned refinements for the kickoff: (1) epic `adrs` are integers in the YAML, map them to ADR-NNN tokens for the existing resolver; (2) the phase cardinality check must treat 0-epic phases as "forming" (not flagged), only flagging 1-epic phases, so the deferred future phases do not show spurious warnings. Next: draft+check kickoff and dispatch executor with the COR-07 render gate at close.
- 2026-06-12: Done. Kickoff drafted+checked (PASS), prelaunch PASS, executor dispatched (Sonnet). Delivered the file-based roadmap reader (collect_roadmap_from_files + _collect_tasks_by_epic) wired into run_etl, the phase cardinality refinement (0 epics not flagged, 1 flagged), and removal of the STATUS roadmap block. Verified via compose (the sanctioned path) + headless render (COR-07): data.json contract intact, RoadmapPanel.jsx untouched, roadmap renders correctly. At close the executor had set last_updated to 2026-06-12, the correct session date (a subsequent reset to 2026-06-13 was itself erroneous and has since been normalized back to 2026-06-12 repo-wide). Phase 2 shows the expected 1-epic warning (Backend API deferred); user confirmed the render and accepted the warning as-is. Deliverable committed 1bacdd5. Completes the ADR-037/038 cascade.
