---
schema_version: 1
roadmap:
  - phase: 0
    title: "Bootstrap"
    deliverables: "Docs, decision records, task convention"
    milestones:
      - id: P0-1
        title: "Docs scaffold (README, CLAUDE.md)"
        status: done
      - id: P0-2
        title: "Decision records ADR-001..009 accepted"
        status: done
      - id: P0-3
        title: "Task convention seeded (COR-T-001..006)"
        status: done
  - phase: 1
    title: "AI infrastructure"
    deliverables: "Orchestrator/worker role docs, the dispatch loop, the blocking ADRs, and the department structure"
    milestones:
      - id: P1-1
        title: "Orchestrator/worker role docs + drafter+checker dispatch loop"
        status: done
        task: COR-T-001
      - id: P1-2
        title: "Blocking ADRs: schema, API shape, MCP surface, auth"
        status: done
      - id: P1-3
        title: "Department structure + workspace restructure"
        status: done
      - id: P1-4
        title: "project-manager insight dashboard"
        status: done
        task: COR-T-014
      - id: P1-5
        title: "Resolve pending ADRs: label taxonomy, native epics, per-agent MCP identity"
        status: done
      - id: P1-6
        title: "Roadmap sub-milestone granularity in the dashboard"
        status: done
        task: COR-T-017
  - phase: 2
    title: "API + DB core"
    deliverables: "Postgres schema, FastAPI endpoints, auth/sessions, invite tokens, migrations, admin seeding"
    milestones:
      - id: P2-0
        title: "Create web-app departments (database, backend-api) via create-department"
        status: done
        task: COR-T-023
      - id: P2-1
        title: "Postgres schema (ADR-012)"
        status: done
        task: DB-T-001
      - id: P2-2
        title: "FastAPI endpoints with house rules"
        status: planned
      - id: P2-3
        title: "Auth/sessions + invite tokens (ADR-011)"
        status: planned
      - id: P2-4
        title: "Migrations + admin seeding (ADR-014, ADR-006)"
        status: planned
  - phase: 3
    title: "MCP server"
    deliverables: "FastMCP server as an authenticated API client; the agent seam goes live"
    milestones:
      - id: P3-1
        title: "FastMCP server as authenticated API client (ADR-004)"
        status: planned
      - id: P3-2
        title: "Nine-tool agent seam goes live (ADR-013)"
        status: planned
  - phase: 4
    title: "Kanban UI"
    deliverables: "React multi-view board with per-view label filters, admin page"
    milestones:
      - id: P4-1
        title: "React multi-view board with per-view label filters (ADR-015, ADR-017, ADR-018)"
        status: planned
      - id: P4-2
        title: "Admin page"
        status: planned
  - phase: 5
    title: "Dogfood milestone"
    deliverables: "Import the markdown tasks into the app via the MCP server; the project tracks itself; markdown tasks frozen"
    milestones:
      - id: P5-1
        title: "Import markdown tasks into the app via the MCP server (ADR-008)"
        status: planned
      - id: P5-2
        title: "Freeze markdown tasks; the project tracks itself"
        status: planned
      - id: P5-3
        title: "Multi-user/agent concurrency live (ADR-020)"
        status: planned
last_updated: "2026-06-11"
recent_updates:
  - "2026-06-11: COR-T-030 executed: removed the dead PHASE column from the dashboard department roster (DepartmentsPanel.jsx) and stripped the dead department phase field from etl.py's dept_status(), both department workspace_details header branches, and the JSON-contract docstring. The data.json department/workspace_details entries no longer carry a phase key; the coordinator's derived phase is preserved."
  - "2026-06-11: Filed COR-T-030 (remove the dead PHASE column from the dashboard department roster) in backlog and logged observation COR-03 (hand-maintained milestone statuses are the dashboard's remaining drift surface, now load-bearing after COR-T-029). Allocated ID 30 (.next-task-id -> 31). Both surfaced during the COR-T-029 close review: the roster's PHASE column renders 'Phase null' for every existing department because it reads a `phase` frontmatter field departments have never defined (dead since COR-T-014); separately, deriving current_phase/next_step from milestone `status` values pushed the drift down to those hand-set statuses (cross-checkable against task-tree location for task-bearing milestones). COR-T-030 is a P2 deliverable; COR-03 is logged (candidate: an etl.py consistency check)."
  - "2026-06-11: COR-T-029 executed: dashboard now derives current_phase, current_phase_title, and next_step from roadmap milestone statuses (etl.py) instead of hand-maintained frontmatter fields. Removed the manual phase and phase_title frontmatter fields and the ## Next step body section from STATUS.md."
  - "2026-06-11: STATUS hygiene: advanced the coordinator `phase` pointer 1 -> 2 (and `phase_title` to the API + DB core title), and rewrote the 'Current phase' narrative for Phase 2. The frontmatter `phase` field had never been bumped when Phase 2 began (COR-T-023 departments, DB-T-001 P2-1), so the dashboard derived Phase 1 as CURRENT and Phase 2 as UPCOMING (etl.py derives phase badges purely from `phase == current_phase`) despite all P1 milestones being done and P2-0/P2-1 complete. Surfaced by the user viewing the live dashboard. Per-milestone DONE badges were already correct; only the phase-level pointer was stale."
  - "2026-06-11: Filed COR-T-028 (app/ skeleton devops follow-ups: Python dependency-management policy, .dockerignore, explicit compose project/service naming) in the coordinator backlog; allocated ID 28 (.next-task-id -> 29). Triaged from the DB-T-001 worker report's Follow-ups (items 2-4; item 1, the orphan container, was already resolved at close). Held in the coordinator tree as the interim catch-all because the devops department does not exist yet (lazy creation, ADR-021/ADR-027); relocate to the devops tasks tree on creation per the COR-T-024 -> DB-T-001 precedent (ADR-031). P3 (low-severity, non-blocking); items 1 and 3 flagged as pending-ADR candidates since they set precedent for the shared app/ topology every web-app department extends."
  - "2026-06-11: DB-T-001 delivered and closed (roadmap P2-1 done): authored app/db/ Alembic baseline migration 0001 building the full eleven-table v1 schema (ADR-012 core + ADR-025 epics + ADR-011 auth + ADR-026 machine users via a separate agent_credentials table) and app/docker-compose.yml (postgres + one-shot migrate). Verified against a Postgres compose service (11 tables, 13 FKs incl self-ref parent_id, 4 CHECKs, 7 indexes, jsonb payload; downgrade/upgrade round-trip clean). First domain-1 web-app code; the app/ root is established. Also fixed docs/ai-orchestration/roles/WORKER-ROLE.md (wrap-up STATUS hygiene now targets the kickoff-named workspace STATUS, not the hardcoded coordinator STATUS), logged as DB-01."
  - "2026-06-11: ADR-014 accepted (DB migrations tooling): Alembic with hand-written migrations; no ORM adopted in v1, so the data-access-layer choice (SQLAlchemy Core/ORM vs raw driver) stays a backend-api/P2-2 decision and is unforced by this choice. The v1 schema lands as a single baseline migration (0001) building the full schema; authoring it is DB-T-001. Option B (raw SQL + custom runner) and Option C (create_all) rejected. Forward-pointer note added to ADR-002. Recorded from the /database-orchestrator session at the user's direction (coordinator-owned ADR; the migration-tooling decision binds backend-api too). Roadmap P2-1 advanced planned -> in-progress, tagged task DB-T-001."
  - "2026-06-11: DB-T-001 (Postgres schema, P2-1) picked up in the database department and moved to in-progress; residual implementation-phase DDL decisions resolved with the user (full auth schema in the baseline migration; machine-user identity via a separate agent_credentials table with a kind discriminator on users). Next: draft+check the kickoff and dispatch the worker via /database-orchestrator."
  - "2026-06-11: COR-T-027 executed: removed the Org Chart panel from the project-manager dashboard and expanded the Roadmap to full channel width. OrgChartPanel.jsx deleted; LandingView.jsx updated to panel order PulsePanel -> DepartmentsPanel -> RoadmapPanel (full width) -> ActivityPanel with no two-col wrapper. styles.css .two-col, .org-chart-card, and .org-chart rules removed. etl.py build_org_chart function, its call site, and the org_chart field in the assembled data dict removed; data.json contract change: the org_chart field is no longer emitted."
  - "2026-06-11: Filed COR-T-027 (remove the dashboard Org Chart panel; expand Roadmap to full channel width) in backlog; allocated ID 27 (.next-task-id -> 28). Follow-up surfaced during the COR-T-026 close review: with the Department Roster now above the Roadmap/Org-Chart row, the Org Chart is redundant for a flat org. Target landing layout: PulsePanel -> DepartmentsPanel -> RoadmapPanel (full width) -> ActivityPanel. Open scoping decision flagged for pickup: whether to also strip the orphaned etl.py build_org_chart and the org_chart data.json field (lean: yes, since the field has no other consumer). Coordinator/agent-development presentational deliverable; routes through the dispatched-worker flow."
  - "2026-06-11: COR-T-026 executed: two presentational tweaks to the project-manager dashboard landing view. DepartmentsPanel (department roster) moved above the .two-col Roadmap/OrgChart grid in LandingView.jsx (panel order: PulsePanel -> DepartmentsPanel -> .two-col -> ActivityPanel). Org-chart whitespace fixed by adding org-chart-card class to OrgChartPanel.jsx card div and .org-chart-card { align-self: start; } rule to styles.css, so the org-chart card sizes to its content instead of stretching to the taller Roadmap card height."
  - "2026-06-11: COR-T-025 executed: ADR-031 implementation cascade landed. Template and /create-department recipe gain a tasks/ tree and a {{DEPT_TASK_PREFIX}} token (fourth /create-department argument). Database and backend-api department workspaces each now own their own tasks/ tree (DB-T and API-T prefixes). COR-T-024 relocated to DB-T-001 in ai-infrastructure/database/tasks/backlog/ (git mv, id updated, dept:database label stripped, activity log updated). etl.py updated to read every workspace tree (coordinator + departments) instead of one shared pool (per ADR-031). tasks/README.md reframed to per-workspace convention. Shared-pool language swept from all live docs, commands, templates, and department STATUS files."
  - "2026-06-11: ADR-031 accepted (per-department task trees; reverses ADR-027 Fork B). Surfaced by the COR-T-023 department smoke tests: Fork B's single shared `dept:`-labeled pool was an unintended divergence from the rogue inspiration (every rogue workspace owns its own `tasks/` tree). Decision: each workspace (coordinator + every department) owns a `tasks/` tree with per-department ID prefixes (DB-T, API-T; coordinator keeps COR-T unchanged); the `dept:<slug>` label is applied at the dogfood import (ADR-008), derived from the tree, where ADR-001's single-pool/per-label-board model takes over inside the app. Forward-pointer notes added to ADR-027 (Fork B), ADR-030 (scaffold gains tasks/), ADR-021 (board mapping timing). Implementation cascade (template/recipe, the two live department commands, etl.py, tasks/README.md, COR-T-024 -> DB-T-001 relocation, shared-pool language sweep) filed as COR-T-025 (dept:agent-development, backlog), not yet dispatched."
  - "2026-06-11: Filed COR-T-024 (author the Postgres schema, P2-1) in backlog, tagged `dept:database`; allocated ID 24 (.next-task-id -> 25). First filed deliverable for the database department; implements the already-accepted ADR-012 schema as amended by ADR-025 (native epics) and ADR-026 (machine users), plus the ADR-011 auth delta, via the ADR-014 migrations tooling. Routes through /database-orchestrator's dispatched-worker flow when picked up."
  - "2026-06-11: STATUS hygiene: corrected a stale 'Next step' clause. The reworded Next step from the COR-T-023 close carried forward 'The only open backlog item is COR-T-018' verbatim, but COR-T-018 is in tasks/done/ and the backlog is empty; replaced with 'The backlog is currently empty; P2-1 is the next deliverable to be filed.' Surfaced by both department-orchestrator smoke tests (/database-orchestrator and /backend-api-orchestrator), which independently flagged the desync and verified it before reporting."
  - "2026-06-10: BACKEND-API-DEPT-CREATE-KICKOFF executed: stamped the `backend-api` department workspace at `ai-infrastructure/backend-api/` (CLAUDE.md, README.md, STATUS.md, OBSERVATIONS.md, decisions/README.md) and wired its `/backend-api-orchestrator` command at `.claude/commands/backend-api-orchestrator.md`. All six output files have zero unreplaced tokens."
  - "2026-06-10: DATABASE-DEPT-CREATE-KICKOFF executed: stamped the `database` department workspace at `ai-infrastructure/database/` (CLAUDE.md, README.md, STATUS.md, OBSERVATIONS.md, decisions/README.md) and wired its `/database-orchestrator` command at `.claude/commands/database-orchestrator.md`. All six output files have zero unreplaced tokens."
  - "2026-06-10: Filed COR-T-023 (stand up the database and backend-api departments before Phase 2 code) and added roadmap milestone P2-0 'Create web-app departments (database, backend-api) via create-department' before P2-1. Encodes the lazy-creation sequencing (ADR-021/027: create a department at the moment its domain's work begins) structurally; COR-T-023 will be the first real end-to-end run of the create-department recipe (built in COR-T-013, never yet exercised). mcp-server (Phase 3) and frontend-ui (Phase 4) are stood up just-in-time when their phases begin."
  - "2026-06-10: COR-T-022 executed: etl.py build_org_chart now appends ' (planned)' to each department whose exists flag is false (treating missing/falsey as planned), driven by the already-computed departments list passed from run_etl instead of DEPARTMENTS_ROSTER; docstring updated to describe the planned-suffix behavior. Coordinator root line and created departments are unlabelled; ASCII tree connectors and domain grouping preserved."
  - "2026-06-10: COR-T-021 executed: thinned the README roadmap section to stable human orientation. The six-row phase table is kept, each cell reduced to one sentence of phase intent, all granular deliverable enumerations, inline ADR citations, and the stale '(this iteration)' marker removed. A lead-in pointer line directing readers to STATUS.md and the project-manager dashboard for live status was added under the heading."
  - "2026-06-10: STATUS hygiene: corrected roadmap milestone P1-6 (roadmap sub-milestone granularity) from in-progress to done. COR-T-017 delivered it and is in tasks/done; the milestone status had not been advanced. Flagged during the COR-T-020 session wrap-up."
  - "2026-06-10: COR-T-020 executed: made the project-manager dashboard live (auto-rebuild + browser soft-refresh). etl.py gains a --watch mode (argparse store_true) using PollingObserver, 350ms threading.Timer debounce, CONTENT_CHANGE_EVENTS filter, allowlisted WATCH_PATTERNS, watching ai-infrastructure/ and .claude/commands/ under REPO_ROOT recursively; one-shot default unchanged. Dockerfile adds watchdog==4.0.2 and adopts entrypoint.sh (initial ETL build, background python etl.py --watch, foreground http.server; background watch non-fatal to serving). App.jsx adds a 5000ms setInterval poller keyed on data.meta.generated_at with soft setData re-render, interval cleanup on unmount, and poll-error tolerance (no error-screen takeover)."
  - "2026-06-10: COR-T-010 executed (orchestrator-direct; first task run under the new Pending-ADR resolution playbook): ADR-026 accepted (per-agent MCP identity). Model: Option A, per-agent API keys generalizing ADR-011's single static service key (1 key -> 1 identity) to N keys -> N identities, same bearer-verified-API-side path, keys hashed at rest. Agents are first-class machine users (rows in `users` with `display_name` + hashed key, no human-auth fields email/password/session; a discriminator separates machine from human), so `issues.assignee_id` and `issue_events.actor_id` resolve per-agent. Keys provisioned in deploy config (`.env` per ADR-006), operator-managed, rotation/revocation = config change + restart; runtime admin revocation deferred and non-precluded. Resolves ADR-011 Consequence #5 (claim-lease + audit can now name the acting agent) and supplies ADR-020's assignee-as-lease prerequisite without deciding ADR-020. Exact DDL (users discriminator vs separate credential table, key storage) deferred to implementation-phase (ADR-014). Forward-pointer notes added to ADR-011 (Consequences 5/6), ADR-012 (Consequence 7), ADR-013 (Consequence 3), ADR-020 (Context); related_adrs cross-links updated. Closes roadmap milestone P1-5 (all three pending ADRs ADR-018/025/026 resolved)."
  - "2026-06-10: COR-T-019 executed (dispatched worker): added the 'Pending-ADR resolution playbook' subsection to docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md, placed between the 'Task lifecycle' and 'Handoff hygiene' sections, distilled from COR-T-008 and COR-T-009."
  - "2026-06-10: COR-T-009 executed (orchestrator-direct): ADR-025 accepted (native epics). Model: Option C, an explicit `issues.type` column (`task | epic`, CHECK-constrained, default `task`) plus a nullable self-referential `parent_id` FK (amends the ADR-012 schema via this later ADR per the ADR-024 precedent). Invariants (API-enforced per ADR-010): at-most-one parent (single FK, mirroring ADR-018's at-most-one `dept:*`), children are tasks and parents are epics, epics not nested in v1 (epic `parent_id` null), `type` backfills `task` on migration. MCP surface grows additively by three tools (`epic_create`, `epic_attach`, `epic_detach`); `issue_get`/`issue_list` surface `type`+`parent_id` as response-field/filter extensions, not new tools; the ADR-013 nine-tool table is unchanged. Board treatment deferred to the Kanban phase (ADR-015/017): epics reuse status columns, no new column, so ADR-017's fixed-global-columns leaning stands. `issue_link` stays dropped. Forward-pointer notes added to ADR-012 (Consequence 6), ADR-013 (Consequence 5 marked resolved), ADR-017 (Context); related_adrs cross-links updated."
  - "2026-06-10: COR-T-008 executed (orchestrator-direct): ADR-018 accepted (department label taxonomy). Pinned the label-family content ADR-013 deferred: namespaced `dept:*` is the sole reserved family in v1 (priority and status are first-class ADR-012 columns, not families; epic/type modeling deferred to ADR-025); `dept:*` cardinality is at-most-one per issue (0 or 1), amending ADR-021's exactly-one leaning (forward-pointer note added to ADR-021); creation rights are admin/auto-sanctioned for `dept:*` (from the ADR-021 roster) and any-authenticated-user for free-form labels, enforced API-side per the ADR-013 mechanism; labels carry an optional color with the concrete palette deferred to the Kanban UI phase (ADR-015/017). Hygiene: `dept:ai-infra` retired as invalid taxonomy (ai-infra is a domain not a department, ADR-021); COR-T-007 and COR-T-015 relabeled to `dept:agent-development`; tasks/README.md label example corrected."
  - "2026-06-10: COR-T-017 executed: extended the project-manager dashboard pipeline end-to-end with roadmap sub-milestones (P1-1/P1-2 granularity). ETL (etl.py) now carries a milestones array on each roadmap entry (id, title, authored status, optional task ref; empty list when absent); JSON-contract docstring updated. RoadmapPanel.jsx renders milestones as an always-visible nested sub-list with MILESTONE_STATUS_LABELS (done/in-progress/planned), badge-milestone-* pills, and a non-linking task tag. styles.css gains .roadmap-milestones layout, .roadmap-milestone-* element classes, and three .badge-milestone-* color classes mirroring the .badge-roadmap-* idiom."
  - "2026-06-10: COR-T-014 executed: built the project-manager insight dashboard (ADR-027 Fork E). Greenfield ai-infrastructure/project-manager/dashboard/: Python ETL (etl.py) reading roadmap/STATUS frontmatter, shared task pool, ADR-021 department roster, coordinator ADRs, and observations count, emitting a pinned data.json contract; React/Vite two-view SPA (landing overview + per-workspace detail, hash-routed); multi-stage Dockerfile (node:20-slim build stage, python:3.12-slim serve stage, ETL-then-http.server entrypoint on port 8420); standalone docker-compose.yml with read-only repo-root bind-mount at /repo. Dashboard reads markdown sources now and repoints to the app at the dogfood milestone (ADR-008). All three ADR-027 follow-ons (COR-T-012 restructure, COR-T-013 create-department, COR-T-014 dashboard) are now complete."
  - "2026-06-10: COR-T-016 executed: renamed the coordinator orchestrator command from /corral-orchestrator to /project-manager-orchestrator to match the /<slug>-orchestrator convention (ADR-021, ADR-030). git mv .claude/commands/corral-orchestrator.md -> project-manager-orchestrator.md; updated three display-name lines in the command file; updated ORCHESTRATOR-ROLE.md (three command refs + Instantiation role name); updated WORKER-ROLE.md (one Not-in-scope command ref); generalised worker-agent.md two Corral Orchestrator mentions to the Orchestrator; updated STATUS.md Current-phase narrative."
  - "2026-06-10: COR-T-013 executed: built the create-department recipe. Authored six placeholder-tokenized template files under ai-infrastructure/project-manager/templates/department/ (CLAUDE.md, README.md, STATUS.md, OBSERVATIONS.md, decisions/README.md, orchestrator-command.md) and the .claude/commands/create-department.md command. The scaffold contract is ADR-030; the orchestrator-command template mirrors the corral-orchestrator structure scoped to the department and uses five {{UPPER_SNAKE}} tokens. The /create-department command drives the orchestrator through the dispatched-worker flow to stamp the workspace."
  - "2026-06-09: COR-T-012 executed: moved root orchestration content into ai-infrastructure/project-manager/ via git mv (STATUS.md, OBSERVATIONS.md, decisions/, tasks/, docs/architecture/OVERVIEW.md); split CLAUDE.md into a thin repo-root global file and a workspace-operating file; authored ai-infrastructure/project-manager/README.md workspace charter; applied bidirectional two-domain path-reference sweep across all moved and root-staying files; new workspace layout per ADR-027 and ADR-029 is now in place."
  - "2026-06-09: Mined the first live dispatched-worker run (COR-T-012 fresh-session test). Finding: the orchestrator task pick-up direction said 'begin the work', which bypassed the Dispatched-worker flow and steered the orchestrator toward executing the deliverable itself. Fix: rewired the 'Pick up COR-T-NNN' direction in ORCHESTRATOR-ROLE.md (Task lifecycle) and /corral-orchestrator (Phase 5) to route deliverable tasks through the dispatched-worker flow (resolve decisions, draft+check kickoff, prelaunch, dispatch worker-agent, close), with the coordination carve-out for ADR/STATUS/triage work. Secondary fix: folded COR-T-012's resolved decisions (the ADR-029 docs split, the CLAUDE.md partition, the two-domain path convention, README charter, no placeholders, no new frontmatter) into the task's Description and corrected its stale path-rewrite line, so the next run reads pinned decisions instead of re-deriving them. The interrupted run's task-move was reset; COR-T-012 is back in backlog."
  - "2026-06-09: ADR-029 accepted (shared role docs stay at repo root). While resolving COR-T-012's anticipated decisions, surfaced that ADR-027's tree placed all of docs/ inside project-manager/, conflicting with the rogue exemplar (which keeps the universal role docs at repo root as shared infra, like .claude/) and with ADR-028's root-level worker-agent bootstrap. Decision: docs/ai-orchestration/ (role docs) stays at root; only docs/architecture/OVERVIEW.md moves into project-manager/docs/; docs/README.md stays at root with an updated pointer. Partially amends ADR-027 Fork A (forward-pointer note added); other forks unaffected. Also resolved for COR-T-012: thin root CLAUDE.md keeps truly-global rules + pointers while project-manager/CLAUDE.md holds AI-infra operating specifics; bare .claude/ = repo-root shared, ./ = workspace-relative inside moved files; no empty placeholders; author project-manager/README.md charter + coordinator-write-authority note; no new workspace frontmatter field."
  - "2026-06-09: COR-T-015 executed (ADR-028 implementation): authored the universal worker-agent (./.claude/agents/worker-agent.md) and its spec; added the Dispatched-worker flow (7-step orchestrator-run sequence) to ORCHESTRATOR-ROLE.md; reframed WORKER-ROLE.md for the dispatched-subagent model (Identity deltas, escalate-by-return-value, checkers now orchestrator-run); repointed the prelaunch/close checker agents and specs to orchestrator-run dispatch; repointed the kickoff-drafter/checker Worker-pointer convention off the slash command; wired /corral-orchestrator; deleted /corral-worker. Forward-pointer notes added to ADR-009 and ADR-023. COR-T-015 moved to done; decision committed as ce414d5, implementation in the follow-on commit."
  - "2026-06-09: ADR-028 accepted (worker as orchestrator-dispatched subagent; retire /corral-worker). Corral adopts rogue ADR-025's reshaped pattern: the orchestrator dispatches a universal worker-agent subagent (Task tool, Sonnet, foreground) with explicit context pass-down instead of handing kickoffs to a parallel human-driven /corral-worker session; the user interacts only with the orchestrator. Leaf worker (orchestrator runs prelaunch/close checkers), return-and-re-dispatch escalation (2 round-trip ceiling), verify-against-disk. Partially supersedes ADR-009's worker-invocation mechanism (forward-pointer note added), extends ADR-023. /corral-worker retired outright (no installed parallel-session base, unlike rogue which kept it). Implementation queued as COR-T-015."
  - "2026-06-08: COR-T-006 executed: ADR-021 accepted (candidate-department menu); project-manager coordinator plus three AI-infrastructure departments (agent-development, test-design, docs-curation) and five web-app departments (backend-api, database, mcp-server, frontend-ui, devops) blessed; lazy-creation policy confirmed (Option A); ai-infra noted as a domain not a department with dept:ai-infra relabel deferred to ADR-018 / COR-T-008; ADR-027 referenced as the authoritative workspace-structure ADR."
  - "2026-06-08: Queued COR-T-012 (execute the ai-infrastructure restructure), COR-T-013 (create-department recipe), and COR-T-014 (project-manager dashboard) as the three ADR-027 follow-on backbone tasks."
  - "2026-06-08: COR-T-011 executed: ADR-027 accepted (AI-infrastructure workspace structure). Corral adopts the rogue coordinator-plus-departments model as a real ai-infrastructure/ directory structure with ai-infrastructure/project-manager/ as the coordinator workspace (root orchestration to move there in a follow-on restructure task), a single shared dept:-labeled task pool (deliberate rogue divergence dogfooding ADR-001), lazily-created sibling department workspaces, an amendment of ADR-009's skip-workspaces framing, and three named follow-on deliverables: restructure execution, create-department recipe, and project-manager dashboard."
  - "2026-06-08: Queued COR-T-010 (resolve ADR-026 per-agent MCP identity) and framed ADR-026 pending. Triaged from the COR-T-005 Worker follow-up: ADR-011's single shared MCP service identity defers per-agent attribution and claim-lease (ADR-020)."
  - "2026-06-08: COR-T-005 executed: ADR-011 accepted (server-side cookie sessions; hand-rolled on vetted primitives; argon2id hashing, closing ADR-006; invite-token mechanics pinned, closing ADR-007; MCP-to-API static service API key with a single shared service identity, closing ADR-010 Consequence #3; auth schema delta owned per ADR-012 Consequence #3); per-agent MCP identity deferred to a future ADR; OVERVIEW.md line-25 \"pending\" annotation dropped."
  - "2026-06-07: Queued COR-T-008 (resolve ADR-018 label taxonomy) and COR-T-009 (resolve ADR-025 native epics), triaged from COR-T-004 Worker follow-ups."
  - "2026-06-07: COR-T-004 executed: ADR-013 accepted (nine-tool MCP surface: issue_list/get/create/claim/move/comment/label/view_list/import; free status transitions; priority required at create; label-governance mechanism pinned, specifics deferred to ADR-018/ADR-021); ADR-025 queued pending (native epics); OVERVIEW.md mcp-bullet clause updated."
  - "2026-06-05: COR-T-007 executed: ADR-024 accepted (kickoff/report handoffs git-tracked in .claude/artifacts/handoffs/, tmp/ stays gitignored scratch); four existing COR-T-002/003 artifacts adopted; path/classification sweep across CLAUDE.md, role docs, commands, agents, specs."
  - "2026-06-05: COR-T-003 executed: ADR-010 resolved from pending to accepted (REST API, /api/v1 prefix, MCP server as authenticated API client); README roadmap rows 2 and 3 swapped; OVERVIEW.md mcp bullet updated."
  - "2026-06-05: COR-T-002 executed: ADR-012 resolved from pending to accepted (issues/labels/views/comments/events schema pinned); OVERVIEW.md line 25 corrected to attribute users/invites to ADR-011."
  - "2026-06-05: COR-T-001 executed: orchestrator/worker role docs authored, full drafter+checker dispatch loop ported from rogue (ADR-023), /corral-orchestrator and /corral-worker commands created."
  - "2026-06-05: Project renamed from placeholder GHIssuesClone to Corral (ADR-022); ID prefixes GHI-T/GHI-NN renamed to COR-T/COR-NN."
  - "2026-06-05: Phase 0 executed: repo initialized, ADR-001..009 accepted, ADR-010..021 queued pending, task convention seeded with COR-T-001..006 (as GHI-T at the time)."
---

# Status

Single source of truth for current progress. Update at the end of any session that makes progress.

## Current phase

**Phase 2: API + DB core.** Phase 1 (AI infrastructure) is complete: the orchestrator/worker role docs, the drafter+checker dispatch loop with four universal subagents (ADR-023), the `/project-manager-orchestrator` command, the dispatched `worker-agent` (ADR-028), the department structure, and all blocking ADRs are in place (every P1 milestone done). Phase 2 is now under way: P2-0 (the `database` and `backend-api` department workspaces) and P2-1 (the Postgres baseline schema, DB-T-001, which established the `app/` root) are done; remaining Phase 2 work is P2-2/P2-3/P2-4 (FastAPI endpoints, auth/sessions, migrations + admin seeding) inside `backend-api`. See `README.md` for the full roadmap.

## Blocked on

Nothing. All remaining Phase 1 tasks are actionable.
