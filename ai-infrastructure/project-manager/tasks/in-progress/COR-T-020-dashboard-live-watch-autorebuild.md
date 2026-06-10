---
schema_version: 1
id: COR-T-020
title: "Live auto-rebuilding dashboard: watch sources and refresh the page"
status: in-progress
labels: [dept:agent-development]
priority: P2
created: 2026-06-10
updated: 2026-06-10
---

## Description

The project-manager dashboard (`ai-infrastructure/project-manager/dashboard/`) regenerates `data.json` only once, at container start (the `etl.py && http.server` entrypoint), and the SPA (`src/App.jsx`) fetches `data.json` once on mount with no polling. So a source-of-truth edit (STATUS, tasks, decisions, OBSERVATIONS) does not reach the dashboard until a manual container rebuild plus a manual browser refresh. Make the dashboard live: watch the markdown sources, auto-regenerate `data.json` on change, and have the open page reflect it without a manual refresh.

Design pinned with the user, grounded in the rogue exemplar (`~/rogue/ai-workspaces/project-manager/dashboard`, which does this via `build.py --watch` + a 5s client poller):

- **Server watch**: add a `--watch` mode to `etl.py` (argparse flag) using the `watchdog` library's `PollingObserver` (bind-mount safe on any Docker host, unlike rogue's native-FS inotify `Observer`). On `--watch`: build once, then watch the ETL's source tree under `REPO_ROOT`, debounced ~350ms, filtering to content-change events only and to the files the ETL actually reads (replicating rogue's watchdog-feedback-loop guard). Re-run the existing build (writing `data.json` to `SERVED_DIR`) on each debounced change. The default (no flag) one-shot behavior is unchanged.
- **Process model**: single container. The entrypoint runs `etl.py` once, launches `etl.py --watch` in the background, then runs `http.server` in the foreground. Watcher failure is non-fatal (log, keep serving). This improves on rogue's flagged two-process wart. `docker-compose.yml` topology is unchanged.
- **Client**: `App.jsx` polls `./data.json` (`cache: 'no-store'`) every 5s, compares `meta.generated_at`, and soft-re-renders via `setData` on change (preferred over rogue's full `location.reload()`: no flash, preserves the hash route). Transient poll errors do not blow away the current view.
- **Deps**: add `watchdog` to the serve-stage `pip install` in the `Dockerfile` (currently `PyYAML==6.0.2` only).

This is a dashboard/devops deliverable: it routes through the dispatched-worker flow. Markdown-era convenience; superseded when the dashboard repoints to the app at the dogfood milestone (ADR-008). Keeps the `source: "markdown"` seam and the read-only `/repo` bind-mount intact (ADR-003 compose-only).

## Activity log

- 2026-06-10: Created and picked up in the same session. User asked for a watch that auto-rebuilds the page on source-of-truth updates and pointed at the rogue dashboard exemplar for the `--watch`/serve pattern. Homework done: read rogue's `build.py` run_watch (watchdog Observer, 350ms debounce, content-change-event filter) and `dashboard.js` poller (5s, compare generated_at, reload). Decisions pinned with the user: watchdog PollingObserver (bind-mount robust); single container with background `etl.py --watch`; client 5s poll with soft React re-render. Queued for the dispatched-worker flow.
