---
schema_version: 1
id: COR-T-033
title: "Dashboard: add the project-manager coordinator to the AI Roster"
status: done
labels: []
priority: P3
created: 2026-06-11
updated: 2026-06-11
---

## Description

Add the project-manager coordinator as a row in the dashboard's AI Roster (the left table of the COR-T-032 split). The coordinator is an ai-infrastructure workspace but is not part of `data.departments` (which is specifically the ADR-021 department roster), so the AI Roster previously listed only the three ai-infrastructure departments.

Executed orchestrator-direct (no dispatched-worker flow) per explicit user instruction, as an exception to the standard deliverable routing. Recorded as a task for traceability.

The fix is frontend-only and does not touch `etl.py` or the data.json contract: `LandingView.jsx` assembles a coordinator roster row from `data.coordinator` (slug) and `data.workspace_details['project-manager'].task_counts` (with `domain: 'ai-infrastructure'`, `exists: true`, `orchestrator_command: true`) and prepends it to the ai-infrastructure-filtered list. The coordinator row links to `#/workspace/project-manager` like the department rows, shows its own tasks-tree counts (backlog 1, done 30, total 31 at execution time), and does not trip the orphan warning (its orchestrator command exists).

## Activity log

- 2026-06-11: Created and executed orchestrator-direct (no worker) per explicit user instruction, then closed. Patched LandingView.jsx to prepend a project-manager coordinator row to the AI Roster, sourced from the existing coordinator/workspace_details data (etl.py and data.json untouched). Rebuilt via docker compose --build and verified the AI Roster lists project-manager + the three ai-infrastructure departments; serve health HTTP 200; visually confirmed by the user. Committed in 27d8cb0 (deliverable + STATUS hygiene). Unlabelled per ADR-031.
