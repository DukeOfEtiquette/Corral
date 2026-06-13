---
schema_version: 1
id: COR-T-043
title: "Dashboard: remove dead milestone-* CSS left after the COR-T-041 epic reshape"
status: in-progress
labels: []
priority: P3
created: 2026-06-13
updated: 2026-06-13
---

## Description

The COR-T-041 reshape replaced the dashboard roadmap's `phase -> milestone` rendering with `phase -> epic -> task` (new `.roadmap-epic-*` classes). The old milestone-era CSS classes were left behind in `ai-infrastructure/project-manager/dashboard/src/styles.css` and are now dead (zero references in any `.jsx`, verified by the orchestrator). This task removes them. Pure cleanup; no behavior or visual change.

The dead classes to remove (all confirmed 0 references in the dashboard `src/*.jsx` / `src/**/*.jsx`):

- `.roadmap-milestones`
- `.roadmap-milestone-item` (and the `.roadmap-milestone-item:last-child` variant)
- `.roadmap-milestone-id`
- `.roadmap-milestone-title`
- `.roadmap-milestone-task`
- `.roadmap-milestone-refs`
- `.badge-milestone-done`
- `.badge-milestone-in-progress`
- `.badge-milestone-planned`

Before removing, re-confirm each class has zero references across the dashboard JSX (grep). Do NOT remove any class still referenced. Do NOT touch the live `.roadmap-epic-*`, `.badge-ref-*`, `.badge-epic-rollup`, `.badge-dept`, or `.roadmap-*` phase classes. Out of scope: any non-CSS file, any other dead-code hunt, the `.badge-milestone-*` analog naming elsewhere.

Routes through the dispatched-worker flow (dashboard code deliverable). Surfaced as a follow-up during the COR-T-042 close.

## Activity log

- 2026-06-13: Created and picked up (in-progress) at user direction. Dead-CSS confirmed by the orchestrator (all listed classes have 0 jsx references after the COR-T-041 reshape). Routes through the dispatched-worker flow.
