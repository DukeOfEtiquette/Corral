---
schema_version: 1
id: COR-T-052
title: "Make the dashboard tables responsive on mobile (rosters + Agent Fleet overflow at phone widths)"
status: done
labels: []
priority: P3
created: 2026-06-14
updated: 2026-06-14
---

## Description

Surfaced 2026-06-14 during a COR-T-051 mobile render gate (the first time the dashboard was render-checked at a phone width). At ~390px the wide tables clip their right-hand columns off-screen:

- `DepartmentsPanel` (the AI Roster and Web App Roster tables): the `Blocked` / `Done` / `Total` columns run off the right edge.
- `AgentsPanel` (the Agent Fleet table): the `Purpose` column is clipped.
- `WorkspaceView` likely has the same issue with its ADR / task tables (verify).

A partial `@media (max-width: 768px)` block and some `overflow-x: auto` already exist in `ai-infrastructure/project-manager/dashboard/src/styles.css`, but they do not cover these tables. Make the dashboard usable on mobile without regressing desktop: wrap the wide tables in horizontal-scroll containers and/or switch to a stacked/card layout at narrow breakpoints (the approach is an anticipated decision for the orchestrator to resolve at kickoff time, after reading the current `@media` block and table CSS).

Standalone task (no `epic:` linkage): the Phase-1 dashboard epic `COR-E-004` is done; attaching a new task would wrongly un-complete it. This is a one-off post-Phase-1 dashboard fix.

Routes through the dispatched-worker flow (dashboard CSS/JSX). Visual surface, so it gets a render gate at BOTH desktop and mobile widths per the standing visual-check convention (the reason this was caught).

## Activity log

- 2026-06-14: Created in backlog. Surfaced by the COR-T-051 mobile render gate (dashboard tables overflow at phone widths). Unlabelled per ADR-031.
- 2026-06-14: Picked up (in-progress). Routing through the dispatched-worker flow. Orchestrator doing homework (the current @media block + table CSS) to resolve the responsive approach before drafting the kickoff. Render gate at desktop + mobile per the standing visual-check convention.
- 2026-06-14: Done (committed `05490d5`). One dispatch (drafter+checker PASS, prelaunch W1 PASS, close W2 PASS). Executor wrapped the three wide tables (.dept-table, .agent-table, .adrs-table) in .table-scroll (overflow-x: auto) containers with a 480px table min-width. Verify-against-disk via a Playwright scroll assertion (scrollWidth vs clientWidth) at 390px caught that the executor's fix only half-worked: the Agent Fleet tables scrolled but the roster tables overflowed the PAGE (their cards are grid items in .roster-row with default min-width:auto). Orchestrator-applied corrective fix `.roster-row > .card { min-width: 0 }`; re-verified all four tables scrollable=true at 390px and scrollable=false (fit) at 1500px, desktop unchanged. The Playwright scroll check (not the static screenshot) is what surfaced the defect, validating the desktop-and-mobile visual-check convention. Two report follow-ups (both COR-T candidates, anchored, not filed): an @media audit for other overflow surfaces, and a render-gate note.
