---
schema_version: 1
id: COR-T-045
title: "Repoint the dashboard ETL at the epic/phase files and retire the STATUS roadmap block (ADR-037 Phase B)"
status: backlog
labels: []
priority: P2
created: 2026-06-13
updated: 2026-06-13
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

- 2026-06-13: Created in backlog. The Phase B cutover of the ADR-037 cascade, split from COR-T-044 with the user so the dashboard never breaks mid-restructure (Phase A builds the new files with the old ETL still reading the old block; this task switches the ETL and removes the block). Picked up after COR-T-044 is complete and verified. Visual deliverable (COR-07 render gate at close).
