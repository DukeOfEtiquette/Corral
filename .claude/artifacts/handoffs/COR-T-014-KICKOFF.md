# Build the project-manager dashboard (ADR-027 Fork E): a program-level insight dashboard (Python ETL + JSON contract + React board), compose-run

## Target

This is AI-infrastructure work (domain 2 per `./ai-infrastructure/project-manager/decisions/ADR-005-two-domains-ai-first.md`): tooling that observes the AI-infrastructure program, not the Corral web app itself. The task is COR-T-014, realizing ADR-027 Fork E (as clarified by its 2026-06-10 forward-pointer). You are building the project-manager coordinator's dashboard: a program-level INSIGHT surface over the roadmap, the department roster, and cross-workspace activity. The artifact in scope is a greenfield directory tree under `ai-infrastructure/project-manager/dashboard/`: a Python ETL, a React/Vite static app, a multi-stage Dockerfile, and a standalone one-service compose file.

This is NOT a per-issue kanban. A prior build of this directory was a per-issue kanban with status columns and task cards; it was the wrong concept and was deleted. The per-issue kanban is the Corral web app's own surface (`./ai-infrastructure/project-manager/decisions/ADR-001-self-hosted-issue-tracker-scope.md`). The dashboard you build sits ABOVE that: planning, roadmap, milestone progress, a department roster (including departments that do not exist yet), an org chart, and an activity feed. The decisions below pin the full concept; read them before writing any code.

## Decisions resolved by the Orchestrator

These are pinned. Do not re-deliberate them; implement them.

- **Concept (the load-bearing reframe):** this is a program-level INSIGHT dashboard for the project-manager coordinator, not a per-issue kanban. It surfaces: the plan/roadmap and milestone progress, the department roster with per-department insight (including departments that do not exist yet), an org chart, and a cross-workspace activity feed. The inspiration (`~/rogue/ai-workspaces/project-manager/dashboard`) was already mined and verified by the Orchestrator; its transferable patterns are encoded in this kickoff. You do NOT read it; rogue's game/math/build-specific logic does not apply to Corral.
- **Location and domain:** all code lives under `ai-infrastructure/project-manager/dashboard/` (greenfield; the prior build was deleted). This is AI-infrastructure (domain 2) tooling.
- **UI technology:** React built with Vite into a static bundle. Plain JavaScript/JSX, not TypeScript. Two views in one single-page app with HASH-BASED routing, so it serves correctly from a static file server: a landing/overview view (empty hash) and a per-workspace detail view (e.g. hash `#/workspace/<slug>`). The "two-page model" is realized as two hash routes in one `index.html`.
- **Serving model:** static-generate plus `python -m http.server`. The Python ETL generates `data.json` at container start; the static server serves the built bundle plus `data.json`. The snapshot is taken per container start; refresh is `docker compose restart`.
- **Container:** one multi-stage Dockerfile. Stage 1 (`node:20-slim`): `npm ci` plus `vite build`, producing a static `dist/`. Stage 2 (`python:3.12-slim`): install PyYAML, copy `dist/` into the served dir, copy the ETL; the entrypoint runs the ETL (which writes `data.json` into the served dir) and then execs `python -m http.server 8420 --directory <served> --bind 0.0.0.0`. Entrypoint order is ETL first, then server.
- **Compose:** a standalone one-service `ai-infrastructure/project-manager/dashboard/docker-compose.yml`. Publish host port 8420 (`8420:8420`; confirmed free on the user's host, 8000 was taken). Do NOT create a repo-root compose file.
- **Mount:** bind-mount the REPOSITORY ROOT read-only into the container. In the compose file, `source: ../../../` relative to the dashboard dir resolves to the repo root; the target is e.g. `/repo`, mounted read-only. The ETL reads `/repo/ai-infrastructure/...` for tasks/STATUS/decisions/OBSERVATIONS and `/repo/.claude/commands/...` for orchestrator-command presence. The generated `data.json` is written to a container-internal served dir, never back to the mount.
- **ETL data sources** (the ETL reads each of these; you MUST NOT add or edit any source content, only read it):
  - **(a) Roadmap:** the `roadmap` block in `ai-infrastructure/project-manager/STATUS.md` frontmatter (already authored by the Orchestrator; a list of `{phase, title, deliverables}`). The ETL DERIVES each phase's status from the top-level `phase` field: phase < current is "done", phase == current is "current", phase > current is "upcoming". Do NOT add or edit the roadmap block; read it only.
  - **(b) Coordinator and workspace STATUS:** parse `ai-infrastructure/*/STATUS.md` frontmatter tolerantly. The coordinator (project-manager) carries `phase`/`phase_title`/`last_updated`/`recent_updates`/`roadmap`; a department STATUS carries `department`/`last_updated`/`recent_updates`. Include present fields, omit absent ones.
  - **(c) Departments roster:** the ADR-021 blessed list, encoded as an ETL constant with a comment citing ADR-021 as the authority. The list: AI-infrastructure domain = `agent-development`, `test-design`, `docs-curation`; web-app domain = `backend-api`, `database`, `mcp-server`, `frontend-ui`, `devops`. The coordinator is `project-manager` (root of the org chart, not a department). Per department, compute: `exists` (is there an `ai-infrastructure/<slug>/` workspace dir with a `STATUS.md`?), `orchestrator_command` (does `/repo/.claude/commands/<slug>-orchestrator.md` exist?), `status` (phase/last_updated from its STATUS.md if it exists, else null), and `task_counts` (the `dept:<slug>`-labelled slice of the shared pool, by status). A department can have labelled tasks while its workspace dir does not exist yet (for example `dept:agent-development` has tasks today but no workspace); show both signals. Not-yet-created departments render as "planned".
  - **(d) Shared task pool:** `ai-infrastructure/project-manager/tasks/{backlog,in-progress,blocked,done}/*.md`. Status is taken from the CONTAINING DIRECTORY (authoritative per `./ai-infrastructure/project-manager/tasks/README.md`), not from frontmatter. Used for overall counts and per-`dept:`-label counts. Parse frontmatter with PyYAML.
  - **(e) Coordinator ADRs:** `ai-infrastructure/project-manager/decisions/ADR-*.md` frontmatter (`id`, `adr` number, `title`, `status`, `date`) for the coordinator detail view.
  - **(f) Observations count:** count `COR-NN` entries in `ai-infrastructure/project-manager/OBSERVATIONS.md`.
- **JSON data contract** (`data.json`), pinned shape. You may finalize the exact nesting, but you must cover every field below:
  - `meta`: `{ generated_at (ISO-8601 UTC), source: "markdown" (the dogfood seam marker, which flips to the app/MCP source at the dogfood milestone), project: "Corral", current_phase (int), current_phase_title, last_updated, next_step (the STATUS "Next step" narrative text) }`.
  - `roadmap`: `[ { phase, title, deliverables, status: "done"|"current"|"upcoming" (derived) } ]`.
  - `org_chart`: an ASCII org-chart string with `project-manager` at the root and the departments as branches (grouped by domain is fine), generated in Python.
  - `departments`: `[ { slug, domain: "ai-infrastructure"|"web-app", exists (bool), orchestrator_command (bool), label: "dept:<slug>", status: {phase, last_updated}|null, task_counts: {backlog, in-progress, blocked, done, total} } ]` for every blessed department.
  - `coordinator`: `{ slug: "project-manager", phase, phase_title, last_updated }` (the root workspace).
  - `workspace_details`: an object keyed by slug covering the coordinator and every department; each value: `{ header: {slug, display_name, domain, role ("coordinator"|"department"), exists, planned (bool), phase, last_updated}, recent_updates: [{date, text}] (newest-first, capped ~10) or null, adrs: [{id, adr, title, status, date}] or null, observations_count (int) or null, task_counts: {...} }`. For not-yet-created departments, render a thin "planned" detail (`exists:false`, `planned:true`, the dept-label `task_counts`, nulls elsewhere).
  - `recent_activity`: `[ {workspace (slug), date, text} ]` aggregated from every existing workspace's STATUS `recent_updates`, newest-first, capped ~30.
- **React rendering:** the landing view renders meta/pulse, the roadmap (done/current/upcoming milestones with deliverables), the org chart, the departments roster table (domain, exists/planned, orchestrator-command, phase, task counts), and the recent-activity feed. The per-workspace detail view (hash route) renders `workspace_details[slug]`: header, recent_updates timeline, ADRs, observations count, task counts; a "planned" department shows a thin stub. Department/workspace names in the roster link to their detail route. Styling is clean, functional CSS (no framework required).
- **Repo hygiene:** a `dashboard/.gitignore` excluding `node_modules/`, `dist/`, the generated `data.json`, and any local `served/`; commit `package.json` plus `package-lock.json` so `npm ci` is reproducible.
- **Documentation-placement hard rule:** NO `.md` file inside `dashboard/` (the `./CLAUDE.md` placement rule). Inline docs go in the ETL module docstring and code comments; run instructions are reported in your closing report, not committed as a dashboard README.
- **Pending-ADR decoupling:** ADR-015 (frontend build), ADR-017 (board columns), and ADR-018 (label taxonomy) are PENDING. The dashboard's Vite/static build and its generic `dept:*` label reads ALIGN with their leanings but DO NOT decide or bind them; the app's eventual frontend/board/label decisions stay open (COR-T-008 owns ADR-018). Read `dept:*` labels by prefix only; hard-code no label family.

## Deliverables

1. `ai-infrastructure/project-manager/dashboard/etl.py`: the Python ETL producing the pinned `data.json` contract from the sources above. Its module docstring documents the sources, the contract shape, the directory-authoritative task-status rule, and the roadmap-status derivation.
2. The React (Vite, JS) two-view app under `ai-infrastructure/project-manager/dashboard/`: `package.json`, `package-lock.json`, `vite.config.js`, `index.html`, and a `src/` tree carrying the landing view, the per-workspace detail view, hash routing, and the panels (pulse, roadmap, org chart, departments roster, recent activity, workspace detail).
3. `ai-infrastructure/project-manager/dashboard/Dockerfile`: the multi-stage Node-build-then-python-slim-serve image, with the ETL-then-`http.server` entrypoint on port 8420.
4. `ai-infrastructure/project-manager/dashboard/docker-compose.yml`: one service that builds the Dockerfile, publishes `8420:8420`, and read-only bind-mounts the repo root (`../../../`).
5. `ai-infrastructure/project-manager/dashboard/.gitignore`.
6. `ai-infrastructure/project-manager/STATUS.md` edits per "STATUS deltas" below (Next step rewrite plus universal hygiene only; do NOT touch the roadmap frontmatter block).

## Files in scope

- Everything new under `ai-infrastructure/project-manager/dashboard/` (greenfield; create it).
- `ai-infrastructure/project-manager/STATUS.md` (STATUS deltas plus universal hygiene only; the roadmap block is already authored and is OUT of scope to change).

## Files out of scope

Do not create, edit, or decide any of these:

- The `roadmap` frontmatter block in `ai-infrastructure/project-manager/STATUS.md` (already authored by the Orchestrator; read-only for you).
- Any repo-root `docker-compose.yml`, or anything under `app/`.
- ADR-015, ADR-017, ADR-018 (pending; align but do not decide).
- ADR-021, ADR-027, and any other ADRs; `OBSERVATIONS.md`; role docs; agent definitions; commands; `README`.
- The `ai-infrastructure/project-manager/tasks/` tree (you never transition or edit task files).
- Any `.md` file inside `dashboard/`.

## References

Read these in order; each carries context you need to execute:

- `./ai-infrastructure/project-manager/tasks/in-progress/COR-T-014-build-project-manager-dashboard.md`: the task, carrying the full resolved-decisions list.
- `./ai-infrastructure/project-manager/decisions/ADR-027-ai-infrastructure-workspace-structure.md`: Fork E plus the 2026-06-10 forward-pointer clarifying the dashboard is program-insight.
- `./ai-infrastructure/project-manager/decisions/ADR-021-candidate-departments.md`: the blessed department roster the ETL encodes.
- `./ai-infrastructure/project-manager/decisions/ADR-001-self-hosted-issue-tracker-scope.md`: why the per-issue kanban is the app's surface, not the dashboard's.
- `./ai-infrastructure/project-manager/decisions/ADR-003-docker-compose-runtime.md`: the compose-only run policy.
- `./ai-infrastructure/project-manager/decisions/ADR-008-bootstrap-tasks-dogfood-milestone.md`: the dogfood repoint the `source: "markdown"` seam reserves.
- `./ai-infrastructure/project-manager/decisions/ADR-002-tech-stack.md`: React is the frontend stack.
- `./ai-infrastructure/project-manager/tasks/README.md`: the task schema plus the directory-authoritative status rule.
- `./ai-infrastructure/project-manager/CLAUDE.md`: run policy, path conventions, no `.md` in source dirs.
- `./ai-infrastructure/project-manager/STATUS.md`: the roadmap block to read, the Next-step delta to apply, and a sample workspace STATUS the ETL parses.

## Related tasks and ADRs

- ADR-027 Fork E (plus the 2026-06-10 forward-pointer): the dashboard spec, clarified to program-insight.
- ADR-021 (candidate departments): the blessed roster the ETL encodes; departments are lazily created.
- ADR-001 (self-hosted issue tracker scope): the per-issue kanban is the Corral app's surface, distinguishing it from this insight dashboard.
- ADR-003 (compose runtime): the hard compose-only run policy.
- ADR-008 (dogfood milestone): the future repoint the `source: "markdown"` seam reserves.
- ADR-002 (tech stack): React is the chosen frontend.
- ADR-015 / ADR-017 / ADR-018 (PENDING): the dashboard aligns with their leanings but does not decide them; COR-T-008 owns ADR-018.
- COR-T-012 (restructure): established the `dashboard/` location and the shared task-pool path.
- COR-T-013 (create-department recipe): departments are created with a STATUS.md and a `/<slug>-orchestrator` command, the two signals the roster's `exists` and `orchestrator_command` fields read.

## STATUS deltas

Apply these task-specific edits to `ai-infrastructure/project-manager/STATUS.md`, in the same pass as your universal hygiene:

- Rewrite the "Next step" section. It currently names COR-T-014 as the sole remaining ADR-027 follow-on. After this task, all three ADR-027 follow-ons (COR-T-012 restructure, COR-T-013 create-department, COR-T-014 dashboard) are complete; the remaining Phase 1 work is the pending-ADR resolution tasks COR-T-008 (ADR-018), COR-T-009 (ADR-025), and COR-T-010 (ADR-026). Note that the dashboard reads the markdown sources now and repoints to the app at the dogfood milestone (ADR-008).

Universal STATUS hygiene (your standard duty per `./docs/ai-orchestration/roles/WORKER-ROLE.md`): bump `last_updated` and prepend a `recent_updates` entry describing the insight-dashboard build. Do NOT rewrite existing dated history lines, and do NOT touch the roadmap frontmatter block.

## Hard rules

- **No `.md` file inside `dashboard/`.** Per the `./CLAUDE.md` documentation-placement rule, all dashboard documentation lives inline (the ETL module docstring and code comments). Run instructions go in your closing report, not in a committed dashboard README.
- **The roadmap frontmatter block in STATUS.md is read-only.** The ETL reads it; you do not add to it or edit it. Your only STATUS edits are the Next-step rewrite and the universal hygiene.
- **Read `dept:*` labels by prefix only.** Do not hard-code a label family or decide the label taxonomy; ADR-018 is pending and COR-T-008 owns it.
- **The repo-root bind-mount is read-only.** The ETL reads from the mount and writes `data.json` only into the container-internal served dir; it never writes back to the mount.
- **Acceptance gate (single gate, authored self-consistency).** The deliverable is accepted when all artifacts are present and correct: the ETL logically produces the pinned `data.json` contract (roadmap status derivation, directory-authoritative task status, per-dept label counts, departments-roster existence logic, tolerant STATUS parsing, observations count, ADR parse), and the Dockerfile and compose are valid and internally consistent (port 8420, repo-root read-only mount, ETL-then-server entrypoint order). You self-verify statically: read your own ETL against the pinned contract and the data sources, and read the Dockerfile and compose against the serving model. You do NOT run docker; per the compose-only run policy you do not assume a host Python/Node toolchain, and the runtime build/serve/visual confirmation is the Orchestrator's standing user runtime-gate AFTER you return, not a step in this task.

## Worker pointer

You are the dispatched `worker-agent` (`./ai-infrastructure/project-manager/decisions/ADR-028-worker-as-dispatched-subagent.md`). Universal worker conventions, including the run policy and the file-edit hygiene, live in `./docs/ai-orchestration/roles/WORKER-ROLE.md`. Write your closing report to `./.claude/artifacts/handoffs/COR-T-014-KICKOFF-REPORT.md` per `WORKER-ROLE.md`, section "Report shape" (the six-section, dual-channel report). Your run-instruction notes (the compose command the user runs to build and serve the dashboard) belong in that report's "Build / verification status" section, not in any committed dashboard file.
