---
schema_version: 1
id: COR-T-026
title: "Dashboard layout: move roster below overview; trim org-chart whitespace"
status: backlog
labels: []
priority: P2
created: 2026-06-11
updated: 2026-06-11
---

## Description

Two presentational tweaks to the project-manager insight dashboard (`ai-infrastructure/project-manager/dashboard/`), requested after the COR-T-025 visual review. This is coordinator/agent-development AI-infrastructure work, presentational only: no change to `etl.py` or the `data.json` contract. Routes through the `/project-manager-orchestrator` dispatched-worker flow when picked up.

The landing view (`src/views/LandingView.jsx`) currently renders, top to bottom: `PulsePanel` (the overview box: project, current phase, last updated), then a `.two-col` grid holding `RoadmapPanel` and `OrgChartPanel` side by side, then `DepartmentsPanel` (the department roster, full width), then `ActivityPanel`.

1. **Move the Department Roster above the Roadmap and Org Chart.** `DepartmentsPanel` should render directly below the overview box (`PulsePanel`), above the Roadmap and Org Chart, rather than below them. Reorder the panels in `LandingView.jsx` accordingly; keep `ActivityPanel` last.

2. **Trim the Org Chart's vertical whitespace.** The Org Chart card (`OrgChartPanel`, `<pre className="org-chart">`) currently sits in the `.two-col` grid (`styles.css`, `grid-template-columns: 1fr 1fr`) alongside the much taller Roadmap, so the equal-height grid row stretches the org-chart card far below its ASCII content, leaving a large dead area (seen in the COR-T-025 review screenshot). The org-chart card should size to its content with no large empty space below the tree. Implementation is the worker's to choose (for example, aligning the card to the start of its grid row, or restructuring the row), preserving the side-by-side Roadmap/Org-Chart arrangement on wide viewports and the existing single-column collapse at the `.two-col` breakpoint.

Out of scope: any `etl.py` / `data.json` change; the `WorkspaceView`; the org-chart ASCII content itself (owned by `etl.py build_org_chart`); restyling unrelated panels.

Verification: `docker compose up` in `ai-infrastructure/project-manager/dashboard/` renders the roster directly under the overview box and above Roadmap/Org-Chart, and the Org Chart card has no large empty area below its tree, at both wide and narrow viewport widths.

## Activity log

- 2026-06-11: Created in backlog. Filed after the COR-T-025 dashboard visual review surfaced two layout asks (roster placement, org-chart whitespace). Coordinator/agent-development presentational deliverable; routes through the dispatched-worker flow. Unlabelled per the ADR-031 convention (the coordinator tree is the partition; dept:* labels are applied at the dogfood import, not hand-applied in the markdown era).
