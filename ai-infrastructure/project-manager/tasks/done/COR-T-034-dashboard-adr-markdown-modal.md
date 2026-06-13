---
schema_version: 1
id: COR-T-034
title: "Dashboard: click an ADR title to open a markdown modal on the workspace detail view"
status: done
labels: []
priority: P2
created: 2026-06-11
updated: 2026-06-11
epic: COR-E-004
---

## Description

On the project-manager dashboard workspace detail page (`#/workspace/<department>`,
rendered by `ai-infrastructure/project-manager/dashboard/src/views/WorkspaceView.jsx`)
there is a "Decision records" table listing each ADR with a status badge
(`WorkspaceView.jsx:101-129`). Today the ADR title is plain text. Make the title
clickable so it opens a modal popup that renders the ADR's actual markdown body for
reading, then closes (backdrop click, an explicit close control, and Escape).

Reference exemplar: the rogue project-manager dashboard
(`~/rogue/ai-workspaces/project-manager/dashboard`) does this for its markdown files
via `setupMarkdownModal()` / `marked.parse()` in `static/dashboard.js`. Note the
architectures differ: rogue is vanilla JS and fetches the raw `.md` over HTTP at click
time; corral is React/Vite and serves only the built output (`/served`) over HTTP, with
the repo bind-mounted read-only at `/repo` but NOT HTTP-reachable. So the corral-native
approach is to bake each ADR's markdown body into `data.json` at ETL time
(`etl.py` `collect_adrs`, currently frontmatter-only, `etl.py:287-305`) and render it
client-side in React; do not attempt to fetch `/repo` paths over HTTP.

ADR bodies contain markdown tables, so the renderer must support GFM tables.

Scope: the dashboard only (domain-2 AI-infrastructure tooling). etl.py (ADR body
capture + data.json contract), WorkspaceView.jsx (clickable title + modal), and
styles.css (modal styling). The decisions table already in WorkspaceView is the trigger
surface; no new data sources.

## Activity log

- 2026-06-11: Created in backlog.
- 2026-06-11: Picked up; moved to in-progress. Decisions pinned: ADR body embedded in data.json via etl.py (rogue's runtime HTTP fetch is unreachable in corral's sealed `/served` container); rendered with react-markdown + remark-gfm (GFM tables); modal ported from rogue's setupMarkdownModal UX (backdrop/x/Escape close), triggered by clicking the ADR title in the decisions table.
- 2026-06-11: Executed via dispatched worker-agent (kickoff drafter/checker, prelaunch, close-check loop all PASS); verified against disk; user confirmed the modal visually. Deliverable committed as 8371aee. Moved to done.
