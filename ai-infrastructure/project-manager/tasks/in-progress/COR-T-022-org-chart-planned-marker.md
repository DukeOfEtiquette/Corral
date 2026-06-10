---
schema_version: 1
id: COR-T-022
title: "Mark planned departments in the dashboard org chart"
status: in-progress
labels: [dept:agent-development]
priority: P3
created: 2026-06-10
updated: 2026-06-10
---

## Description

The project-manager dashboard org chart (`build_org_chart` in `ai-infrastructure/project-manager/dashboard/etl.py`) renders every entry of the hardcoded ADR-021 `DEPARTMENTS_ROSTER` with no created-vs-planned distinction, so blessed-but-not-yet-instantiated departments (agent-development, test-design, docs-curation, and the five web-app departments) appear in the chart as if they exist. This contradicts the Departments table panel, which already badges each department `exists` vs `planned`. The org chart should tell the same truth.

Resolution: in `build_org_chart`, append a " (planned)" suffix to each department that is not created (its `exists` flag is false), and render created departments and the coordinator root with no suffix. Wire it by passing the computed `departments` list (which carries the `exists` flag derived from `dept_exists`) into `build_org_chart` instead of `DEPARTMENTS_ROSTER`. The "(planned)" wording matches the Departments panel badge. The ASCII tree structure and domain grouping are otherwise unchanged, and the marker is text inside the org_chart string (no JSX or CSS change; OrgChartPanel renders the string verbatim). The data.json contract stays a string; only its content gains markers.

This is a dashboard code deliverable: it routes through the dispatched-worker flow. Note: because `etl.py` is baked into the image, this change takes effect only after a `docker compose up --build`; the COR-T-020 live watch re-runs the existing in-container etl.py on markdown changes and will not pick up an etl.py code change without a rebuild.

## Activity log

- 2026-06-10: Created and picked up in the same session. Surfaced from a user observation: the dashboard org chart listed agent-development/test-design/docs-curation as if they existed, while only project-manager is instantiated (lazy creation, ADR-021/027). Verified build_org_chart renders DEPARTMENTS_ROSTER with no marker while the Departments panel badges exists/planned, so the two panels contradict each other. Decision pinned with the user (#1): mark planned departments in the org chart with a "(planned)" suffix driven by the actual exists flag. Queued for the dispatched-worker flow.
