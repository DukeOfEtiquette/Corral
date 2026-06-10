---
schema_version: 1
phase: 1
phase_title: "AI infrastructure: role docs, agents, blocking ADRs"
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
        status: in-progress
      - id: P1-6
        title: "Roadmap sub-milestone granularity in the dashboard"
        status: in-progress
        task: COR-T-017
  - phase: 2
    title: "API + DB core"
    deliverables: "Postgres schema, FastAPI endpoints, auth/sessions, invite tokens, migrations, admin seeding"
    milestones:
      - id: P2-1
        title: "Postgres schema (ADR-012)"
        status: planned
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
last_updated: "2026-06-10"
recent_updates:
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

**Phase 1: AI infrastructure.** The orchestration layer now exists: orchestrator and worker role docs (`docs/ai-orchestration/roles/`), the drafter+checker dispatch loop with four universal subagents (ADR-023), the `/project-manager-orchestrator` command, and the dispatched `worker-agent` (ADR-028) as the single worker execution path (the former `/corral-worker` command was retired). Remaining Phase 1 work: resolve the blocking pending ADRs and the department structure. See `README.md` for the full roadmap.

## Next step

All three ADR-027 follow-on backbone tasks are now complete: COR-T-012 (ai-infrastructure restructure), COR-T-013 (create-department recipe), and COR-T-014 (project-manager dashboard). The dashboard reads the markdown sources (source: "markdown") and will repoint to the Corral app at the dogfood milestone (ADR-008). Remaining Phase 1 work is the three pending-ADR resolution tasks: COR-T-008 (resolve ADR-018: label taxonomy), COR-T-009 (resolve ADR-025: native epics), and COR-T-010 (resolve ADR-026: per-agent MCP identity).

## Blocked on

Nothing. All remaining Phase 1 tasks are actionable.
