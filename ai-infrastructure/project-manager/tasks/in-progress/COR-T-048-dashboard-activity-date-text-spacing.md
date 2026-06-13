---
schema_version: 1
id: COR-T-048
title: "Dashboard: add spacing between date and text in the recent-updates / activity feed"
status: backlog
labels: []
priority: P3
created: 2026-06-13
updated: 2026-06-13
---

## Description

In the project-manager dashboard, the recent-updates / activity feed renders each entry's date immediately adjacent to its text with no separating space, e.g. `2026-06-12COR-T-046: epic/phase doctrine cascade`. Add a small gap (a CSS margin on the date span, or an explicit separator) so the date and text read as distinct.

Confirmed visible in the workspace detail view (the "Recent updates" panel rendered by `ai-infrastructure/project-manager/dashboard/src/views/WorkspaceView.jsx`); check the landing-view activity feed (`LandingView.jsx` / the activity panel reading `recent_activity`) for the same gap and fix both consistently. The fix is CSS/JSX-side in `ai-infrastructure/project-manager/dashboard/src/` (likely `WorkspaceView.jsx` / `LandingView.jsx` plus `src/styles.css`).

This is a pre-existing styling detail (the `{date, text}` data contract and the JSX are unchanged), surfaced more visibly by COR-T-047 Phase A: the git-sourced entries are short and lead with a task/ADR ID, so the missing gap reads worse than it did with the old longer hand-curated sentences. P3, cosmetic, non-blocking. **Visual deliverable** (COR-07 render gate at close). Routes through the dispatched-worker flow.

Out of scope: any change to the ETL or the `data.json` contract (COR-T-047 owns the activity-surface source); any non-spacing restyle of the feed.

## Activity log

- 2026-06-13: Created in backlog by the project-manager coordinator (orchestrator-direct). Surfaced during the COR-T-047 Phase A COR-07 render gate: the activity-feed date/text spacing nit was visible in the database workspace view. Filed as a standalone P3 cosmetic follow-up at user direction (not folded into COR-T-047 Phase B, which is the doctrine cascade + frontmatter removal). Left standalone (no `epic:`): the only fitting epic (COR-E-004 dashboard) is a done Phase-1 epic; ADR-036 permits standalone tasks.
