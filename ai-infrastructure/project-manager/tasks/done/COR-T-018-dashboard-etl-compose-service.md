---
schema_version: 1
id: COR-T-018
title: "Add a standalone ETL run target to the project-manager dashboard compose setup"
status: done
labels: [dept:agent-development]
priority: P3
created: 2026-06-10
updated: 2026-06-10
epic: COR-E-004
---

## Description

The project-manager dashboard (`ai-infrastructure/project-manager/dashboard/`) currently exposes a single compose service that builds the image and serves the SPA. There is no way to run the ETL (`etl.py`) in isolation through the supported compose path (ADR-003); regenerating `data.json` standalone requires a direct `docker run --entrypoint python3 ... etl.py` invocation against the built image, which is off the sanctioned compose seam. Surfaced as a follow-up while verifying COR-T-017.

Add a supported standalone ETL run target: either a separate `etl` service/profile in `dashboard/docker-compose.yml` that runs the ETL once and exits (writing `data.json` to the served volume), or an equivalent compose-native mechanism, so the ETL can be re-run without rebuilding or hand-rolling a `docker run`. Keep the existing serve service working; keep the `source: "markdown"` seam and the read-only `/repo` bind-mount intact (the dashboard repoints to the app at the dogfood milestone, ADR-008).

This is a dashboard/devops deliverable: it routes through the dispatched-worker flow.

## Activity log

- 2026-06-10: Created in backlog. Triaged from the COR-T-017 worker report (Follow-ups): no standalone ETL-only compose service target exists, so isolated ETL runs fall back to a direct `docker run` off the compose seam.
- 2026-06-10: Done (closed as mostly-superseded; no commits). COR-T-020 added a background `etl.py --watch` to the serve container, so data.json now auto-regenerates on every source-of-truth edit while the dashboard is up. That absorbs this task's everyday motivation (manual standalone regen). The residual distinct value, a serve-decoupled one-shot ETL via compose for CI/scripted validation, is too marginal to track for a local single-operator dashboard. Closed by Orchestrator decision with the user; reopen if a real CI/validation need surfaces.
