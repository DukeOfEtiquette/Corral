---
schema_version: 1
id: COR-T-013
title: "Build the create-department recipe (template, command, recipe ADR)"
status: done
labels: [dept:agent-development]
priority: P2
created: 2026-06-08
updated: 2026-06-10
---

## Description

Build the create-department recipe per `./decisions/ADR-027-ai-infrastructure-workspace-structure.md` Fork D: a `templates/department/` baseline scaffold (`CLAUDE.md`, `README.md`, `STATUS.md`, `OBSERVATIONS.md` with a `<DEPT>-NN` observation prefix, a `decisions/` directory, paired `/<dept>-orchestrator` (Opus) and `/<dept>-worker` (Sonnet) slash-command stubs, and a reserved `dept:<slug>` label per ADR-018); a `/create-department` command that stamps the baseline out; and a recipe ADR recording the scaffold contract. Departments get no own `tasks/` directory (Fork B: shared labeled pool). Gated on the restructure (COR-T-012), which establishes the `ai-infrastructure/project-manager/` location.

**Authoritative contract: `./decisions/ADR-030-department-scaffold-contract-create-department-recipe.md`** (authored 2026-06-10, the deliverable-3 recipe ADR). ADR-030 amends Fork D's paired-command sketch above: the scaffold carries a single fully-wired per-department `/<slug>-orchestrator` (Opus) command and NO `/<slug>-worker` command (department work runs through the universal dispatched `worker-agent`, ADR-028); role docs are reused by reference (ADR-029). The worker builds deliverables 1 (the `templates/department/` baseline, including the orchestrator-command template) and 2 (the `/create-department` command) to the ADR-030 contract; deliverable 3 (ADR-030) is already authored by the orchestrator.

## Activity log

- 2026-06-08: Created in backlog. Named follow-on deliverable 2 of ADR-027 (COR-T-011); gives the project-manager its on-demand department-creation capability.
- 2026-06-10: Picked up; moved to in-progress. Orchestrator begins decision-resolution homework ahead of the dispatched-worker flow.
- 2026-06-10: Resolved the scaffold-contract decisions with the user. Command surface: each department gets its own fully-wired /<slug>-orchestrator (Opus) command that adopts the shared ORCHESTRATOR-ROLE.md by reference (ADR-029), layers department context, and dispatches the universal worker-agent (ADR-028) via the standard dispatched-worker flow; NO /<slug>-worker command, NO per-department worker-agent or role-doc copies (ADR-028/ADR-029 intact). Stamp model: /create-department drafts a kickoff and routes department creation through the dispatched-worker flow, interactive back-and-forth at run time accepted. Reconciled Fork D's stale paired-command sketch. Authored ADR-030 (recipe ADR, deliverable 3) recording the full contract; appended and updated the forward-pointer on ADR-027 Fork D. Remaining deliverables (templates/department/ baseline incl. the orchestrator-command template + /create-department command) routed to the dispatched-worker flow.
- 2026-06-10: Worker returned COMPLETED; both checkers passed (kickoff PASS, prelaunch PASS W1, close PASS W2) and the orchestrator verified all claims against disk. Then, at the user's direction and with the user authorizing an orchestrator-direct exception to the deliverable-routing rule, reframed the stale "Corral is a single project, so there is one Orchestrator" line in docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md to the coordinator-plus-per-department-orchestrator model (pulled forward from the ADR-030 first-creation follow-up); synced the ADR-030 Consequences notes accordingly.
- 2026-06-10: Done. Deliverables and coordination artifacts committed as 6688a11 (templates/department/ baseline, /create-department command, ADR-030, ADR-027 forward-pointer amendment, ORCHESTRATOR-ROLE.md reframe, STATUS hygiene + Next-step rewrite, kickoff/report pair). Moved to done; this task-resolution move committed separately.
