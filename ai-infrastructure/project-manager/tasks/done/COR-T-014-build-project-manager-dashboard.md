---
schema_version: 1
id: COR-T-014
title: "Build the project-manager dashboard (program-level insight over the shared pool and workspaces)"
status: done
labels: [dept:agent-development]
priority: P2
created: 2026-06-08
updated: 2026-06-10
---

## Description

Build the project-manager dashboard per `./decisions/ADR-027-ai-infrastructure-workspace-structure.md` Fork E (as clarified by its 2026-06-10 forward-pointer): a program-level INSIGHT dashboard for the coordinator, NOT a per-issue kanban (the kanban is the Corral web app's own surface, ADR-001). It surfaces the plan/roadmap and milestone progress, the department roster with per-department insight (handling not-yet-created departments gracefully), and cross-workspace activity. A Python ETL reads the shared `tasks/` pool, each workspace `STATUS.md` frontmatter (including the new `roadmap` block), and the ADR-021 department list, emits a JSON data contract, and a React/Vite static UI renders it, runnable under docker compose (ADR-003). It reads the markdown sources now and repoints to the Corral app at the dogfood milestone (ADR-008). Gated on the restructure (COR-T-012, done).

Resolved decisions (pinned with the user 2026-06-10, after the first kanban build was scrapped as the wrong concept):

- Concept: program insight (roadmap/milestones, department roster + per-department detail, cross-workspace activity feed, org chart), not a per-issue board. Inspiration (verified, adapted, not copied): `~/rogue/ai-workspaces/project-manager/dashboard`.
- UI: React built with Vite into a static bundle; two-page model (landing overview + per-workspace detail), hash-routed so it serves correctly from a static file server.
- Serving: static-generate + `python -m http.server`; standalone one-service `dashboard/docker-compose.yml`; host port 8420; read-only bind-mount of `ai-infrastructure/`; `data.json` gitignored.
- Plan source: a structured `roadmap` block in project-manager `STATUS.md` frontmatter (phase/title/deliverables); the ETL derives done/current/upcoming from the top-level `phase` field.
- Department roster: the ADR-021 blessed list encoded as an ETL constant (pointer to ADR-021 as authority); not-yet-created departments render as "planned"; existence, `/<slug>-orchestrator` presence, STATUS phase/last_updated, and `dept:`-label task counts shown per department.
- Decoupling unchanged: ADR-015/017/018 stay pending and are not decided by the dashboard.
- No `.md` files inside `dashboard/` (documentation-placement rule).

## Activity log

- 2026-06-08: Created in backlog. Named follow-on deliverable 3 of ADR-027 (COR-T-011); the PM's at-a-glance board over the shared pool, and the first concrete dogfood-arc artifact.
- 2026-06-10: Picked up; moved to in-progress. Orchestrator begins decision-resolution homework (Fork E design: serving model, UI tech, board scope, compose placement) ahead of the dispatched-worker flow.
- 2026-06-10: Redirected by the user. The first build (a per-issue kanban: status columns and task cards) was the wrong concept and was scrapped (uncommitted). The project-manager dashboard is program-level INSIGHT (roadmap, departments, activity); the per-issue kanban belongs to the Corral app. Studied and verified `~/rogue/ai-workspaces/project-manager/dashboard` as inspiration, re-resolved the design with the user (React/Vite two-page, structured roadmap in STATUS frontmatter, landing + per-workspace detail), authored the STATUS `roadmap` block and an ADR-027 Fork E clarifying forward-pointer, and reverted the premature STATUS "executed" edit. Re-drafting the kickoff next.
- 2026-06-10: Done. Built via the dispatched-worker flow (kickoff drafted+checked PASS, prelaunch PASS W1, worker COMPLETED, close PASS W2); a follow-up corrective worker applied the dark theme (styles.css only, JSX untouched). Orchestrator ran the container under docker compose, captured screenshots, re-derived the rendered data against disk (department rollups correct; the two `dept:ai-infra` tasks correctly orphan, COR-T-008 territory), and the user confirmed the visual. Deliverables and coordination artifacts (`dashboard/`, the STATUS roadmap block + Next-step, the ADR-027 Fork E forward-pointer, the kickoff/report pair) committed as 716869e. Noted non-blocking polish follow-ups: `index.html` color-scheme meta and `.roadmap-upcoming` opacity (dark-theme report), a project-wide task total plus an "unmapped" bucket for the `dept:ai-infra` tasks, and a Dockerfile `CMD` exec. Moved to done; this task-resolution move committed separately.
