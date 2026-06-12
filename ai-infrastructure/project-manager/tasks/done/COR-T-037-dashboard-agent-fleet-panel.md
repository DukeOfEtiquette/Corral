---
schema_version: 1
id: COR-T-037
title: "Dashboard: add an Agent Fleet panel listing the cross-department agents"
status: done
labels: []
priority: P3
created: 2026-06-12
updated: 2026-06-12
---

## Description

Add a panel to the project-manager dashboard landing view that lists the shared cross-department agents (Tier 2 per ADR-032: the dispatched agents every orchestrator uses). The two existing Roster boxes show departments and their orchestrators; this new panel surfaces the agent fleet, which is otherwise invisible on the dashboard. Domain: AI-infrastructure (a domain-2 dashboard deliverable). Routes through the dispatched-worker flow.

Design resolved with the user:

- A new full-width "Agent Fleet" card on the landing view, placed between the roster-row (AI Roster + Web App Roster) and the Roadmap.
- `etl.py` reads `.claude/agents/*.md` frontmatter (pure reader) and emits an `agents` array into `data.json` (name, model, kind, purpose). purpose is the first sentence of each agent's frontmatter `description`.
- Classification is sourced from a new `kind:` frontmatter field added to each of the 6 agent files (user's choice over an ETL-side map): `executor` (executor, test-designer) or `dispatch` (kickoff-drafter, kickoff-checker, worker-prelaunch-checker, worker-close-checker). The kind field makes the ADR-032 taxonomy machine-readable.
- The panel groups by kind: "Executors" then "Dispatch-loop & checkers". Each agent row shows name + a model badge (opus/sonnet) + the one-line purpose.
- The ETL live-reload watch set gains `.claude/agents/` (currently unwatched) so agent edits rebuild the dashboard.

Open taxonomy note (not addressed by this task): ADR-032's Tier-2 split is "executors + validators", but `kickoff-drafter` is neither (it writes kickoffs). The dashboard's `dispatch` kind groups the drafter with the checkers pragmatically. Reconciling ADR-032's prose to name the drafter kind is a separate, optional touch-up flagged to the user.

Out of scope: the other dashboard panels and WorkspaceView.jsx; the agent `color`/`tools` frontmatter; orchestrators/departments (already on the rosters); any ADR edit; new build dependencies; append-only trees.

## Activity log

- 2026-06-12: Created and picked up (moved straight to in-progress). Design decisions resolved with the user (frontmatter `kind` field, grouped Agent Fleet panel between the rosters and the Roadmap). Allocated ID 37 (.next-task-id -> 38). Routing through the dispatched-worker flow. P3 (presentational dashboard enhancement, non-blocking). Unlabelled per ADR-031.
- 2026-06-12: Done. Deliverable executed across the original kickoff plus two corrective passes (FIX and FIX2, the latter fixing an empty Agent Fleet panel traced to `collect_agents` using yaml on non-yaml-safe agent `description` scalars); Agent Fleet panel verified serving all six cross-department agents in the container. Committed as 93343c0 (16 files: 4 dashboard files, the 6 agent `kind:` fields, and the 3 kickoff/report pairs). Moved to done.
