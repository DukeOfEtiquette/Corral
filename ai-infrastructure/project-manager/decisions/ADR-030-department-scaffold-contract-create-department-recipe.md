---
schema_version: 1
adr: 30
title: "Department scaffold contract and the /create-department recipe"
status: "accepted"
date: "2026-06-10"
related_adrs: [9, 18, 21, 23, 27, 28, 29]
supersedes: []
superseded_by: null
---

# ADR-030: Department scaffold contract and the /create-department recipe

> **Forward pointer (2026-06-11):** ADR-031 amends the scaffold's "A department has NO own `tasks/`" clause (item 1, the template file set, and the "does NOT contain a `tasks/` directory" note). Per ADR-031 (reversing ADR-027 Fork B), the department baseline now DOES include a `tasks/` tree (`backlog/`, `in-progress/`, `blocked/`, `done/`, plus `.next-task-id`) and a department task-ID-prefix token, and the stamped `/<slug>-orchestrator` surveys the department's own `tasks/` tree rather than the coordinator pool filtered by `dept:<slug>`. The rest of the contract (the other file set, the orchestrator-command wiring, the no-`/<slug>-worker` and no-role-doc-copy rules) is unaffected. See ADR-031.

> **Forward pointer (2026-06-12):** ADR-037 extends the per-workspace tree model with a lazily-created `epics/` sibling tree. Each workspace that owns epics gains an `epics/` directory alongside its `tasks/` tree (own `.next-epic-id` counter, pure YAML epic files with bottom-up `epic:` linkage from task frontmatter). The coordinator additionally owns a `phases/` tree (`ai-infrastructure/project-manager/phases/`). The `epics/` tree is NOT stamped by the create-department recipe; it is created on the workspace's first epic (lazy creation per ADR-021 and ADR-031). The template files and this contract are otherwise unaffected. See ADR-037.

## Context

ADR-027 Fork D named a create-department recipe as a follow-on deliverable and sketched the department baseline: `CLAUDE.md`, `README.md`, `STATUS.md`, `OBSERVATIONS.md` (with a `<DEPT>-NN` observation prefix), a `decisions/` directory, a reserved `dept:<slug>` label (ADR-018), and "a paired `/<dept>-orchestrator` (Opus) and `/<dept>-worker` (Sonnet) slash-command set under root `.claude/commands/`." COR-T-013 builds that recipe. This ADR records the contract the COR-T-013 worker builds to.

One element of Fork D's sketch is foreclosed by a later decision: **ADR-028** (accepted 2026-06-09) retired the `/corral-worker` slash command and made the single worker execution path the universal dispatched `worker-agent` (root `.claude/agents/worker-agent.md`, Sonnet, foreground). A per-department `/<dept>-worker` command is therefore foreclosed; department deliverable work executes through the universal dispatched `worker-agent`, exactly as the coordinator's does.

The rest of Fork D stands and is enriched here. A new department is a **fully-wired, functional unit**: it gets its own real `/<dept>-orchestrator` (Opus) command that adopts the shared `ORCHESTRATOR-ROLE.md` by reference (ADR-029), layers the department's own context, and dispatches the universal `worker-agent` through the standard dispatched-worker flow. The worker and the role docs are the already-built universal/shared ones; the department is wired to use them, not given private copies (ADR-028 keeps one worker; ADR-029 keeps one shared set of role docs). This is the deliberate division: per-department orchestration entry point and context, shared execution machinery.

This ADR is a partial amendment of ADR-027 Fork D, in the same spirit ADR-029 partially amended ADR-027's `docs/` placement. Per the append-only convention (ADR-024 precedent, reaffirmed by ADR-029), ADR-027's `supersedes` / `superseded_by` fields are left untouched; ADR-027 gains a forward-pointer note and is listed in `related_adrs`.

ADR-018 (department label taxonomy) is still pending. This ADR does not block on it: ADR-021 blesses `dept:<slug>` labels "running ahead of workspace creation," and the naming is already in use across the task pool. The recipe documents the `dept:<slug>` naming and defers label registry, enforcement, and color/metadata to ADR-018, which lands as real labels at the dogfood milestone (ADR-008).

## Alternatives considered

### Department command surface

**Option A: No per-department commands; the universal orchestrator serves every department via the department `CLAUDE.md` (rejected).** A department would be workspace files plus a label, with the universal `/corral-orchestrator` loading the department's `CLAUDE.md` as context.

**Rejected because:** the decision is for each department to be a fully-wired unit with its own orchestration entry point, not to lean implicitly on the universal orchestrator. A department needs a real, working `/<dept>-orchestrator` it can be driven through.

**Option B: A real, fully-wired `/<dept>-orchestrator` (Opus) command per department that dispatches the universal `worker-agent` (selected).** Each department gets its own orchestrator command. It adopts the shared `ORCHESTRATOR-ROLE.md` by reference (ADR-029), layers the department's context (the department `CLAUDE.md`, its `dept:<slug>`-scoped slice of the shared task pool), runs the same drafter+checker dispatch loop and dispatched-worker flow as the coordinator, dispatches the universal `worker-agent` (ADR-028), and uses the universal checker fleet (ADR-023). There is NO `/<dept>-worker` command. The optional department-scoped checker slot (ADR-027, ADR-023) is reserved, not filled.

**Selected because:** it gives each department a first-class orchestration entry point and context layer (the requested "fully wired" department) while keeping the single universal worker (ADR-028) and the single shared set of role docs (ADR-029) intact. It mirrors rogue's per-workspace orchestrators while honoring Corral's dispatched-worker divergence. The trade-off accepted: one orchestrator command per department to author and keep consistent with the shared role doc, and more than one orchestrator entry point in the repo (the coordinator plus each department's).

**Option C: A physically self-contained department with its own worker-agent and its own role-doc copies (rejected).** Each department would also get a private `.claude/agents/<dept>-worker-agent.md` and private role docs.

**Rejected because:** it contradicts ADR-028 (a single universal worker execution path) and ADR-029 (departments reuse the shared root role docs by reference, no per-workspace copy), and it was explicitly not wanted: department work fits the dispatched-worker-agent workflow, so the department dispatches the universal worker rather than carrying a private one. Choosing it would have required superseding two accepted ADRs and maintaining N worker-agents and N role-doc sets in sync, for autonomy the shared machinery already provides.

### /create-department execution model

**Option A: Direct in-session stamp (rejected).** `/create-department` performs the template expansion directly in the running session.

**Rejected because:** creating a department produces deliverable artifacts (a working orchestrator command, a workspace tree), and a fully-wired orchestrator command is real authoring, not decision-free token substitution. Deliverables route through the dispatched worker (ADR-028); direct in-session authoring is reserved for the orchestrator's own coordination surface.

**Option B: Draft a kickoff and route through the dispatched-worker flow (selected).** `/create-department` is an orchestrator-side recipe: it collects the department arguments, drafts and checks a kickoff whose deliverable is the stamped, fully-wired department, runs the prelaunch checker, dispatches the `worker-agent`, and runs the close checker, verify-against-disk, and commit gate. Interactive back-and-forth (escalation, or Plan Mode for a genuinely unanticipated decision) at creation time is expected and acceptable.

**Selected because:** it keeps department creation on the single audited execution path (ADR-028) and treats authoring a working `/<dept>-orchestrator` as the real deliverable work it is. The trade-off accepted: more ceremony, and possible interactive back-and-forth, in exchange for a genuinely functional department at the end rather than a paper stub.

## Decision

Corral's department scaffold contract and create-department recipe are as follows. COR-T-013's worker builds the template directory and the command to this contract; this ADR is the spec.

### 1. Template location and file set

The baseline lives at `ai-infrastructure/project-manager/templates/department/` (the coordinator owns the recipe; ADR-027 tree). It contains exactly:

- **`CLAUDE.md`** - the department's operating rules and workspace routing. References, does not duplicate: the global root `CLAUDE.md` (Agent Discipline, writing style, secrets, documentation placement, two-domains); the coordinator's write authority over this workspace (ADR-027); the shared role docs at their root path by reference (ADR-029); the path conventions (workspace-relative `./X` inside the workspace, bare repo-root-relative paths for shared infra, per the project-manager `CLAUDE.md` convention); the MCP seam and run policy by reference. Carries an "Operated by" section naming the department's own `/<slug>-orchestrator` command, the universal dispatched `worker-agent` (ADR-028) it dispatches, and the universal checker fleet (ADR-023). States the department has NO own `tasks/` (shared pool, ADR-027 Fork B). Carries the department-scoped checker slot reservation note (item 6).
- **`README.md`** - the department charter for humans: what the department owns (its ADR-021 menu scope line), its boundary, and a pointer to the coordinator.
- **`STATUS.md`** - frontmatter (`schema_version`, a department identifier, `last_updated`, `recent_updates`) plus a narrative section, mirroring the coordinator's `STATUS.md` shape scoped to the department.
- **`OBSERVATIONS.md`** - an append-only pattern log mirroring the coordinator's, using the department's `<PREFIX>-NN` observation ID convention (e.g. `TST-01`) in place of `COR-NN`.
- **`decisions/README.md`** - a stub for the department's `decisions/` directory, pointing at the coordinator's `decisions/README.md` for the ADR body convention and leaving the department-local numbering scheme to the department's first ADR. (The directory needs a tracked file because git does not track empty directories.)
- **`orchestrator-command.md`** - the template for the department's `/<slug>-orchestrator` slash command, placeholder-tokenized. It lives inside the template directory (NOT under `.claude/commands/`, so the template itself is not a live command) and is stamped out to `.claude/commands/<slug>-orchestrator.md` by the recipe (item 4). Its body mirrors `.claude/commands/corral-orchestrator.md` structure (adopt the shared `ORCHESTRATOR-ROLE.md`, load context, survey state, dispatch loop, dispatched-worker flow) scoped to the department: role name "`<DEPT_NAME>` Orchestrator", loads the department `CLAUDE.md` and the department's `dept:<slug>`-scoped slice of the shared task pool, dispatches the universal `worker-agent`, and uses the universal checker fleet.

The template does NOT contain: a `tasks/` directory (ADR-027 Fork B, shared labeled pool); any per-department role docs (ADR-029, reuse the shared root docs by reference); any `/<dept>-worker` command or per-department worker-agent (ADR-028, single universal dispatched worker).

### 2. Placeholder token convention

Template files use `{{UPPER_SNAKE}}` placeholder tokens, substituted at stamp time:

- `{{DEPT_SLUG}}` - the kebab slug (e.g. `test-design`); used in paths, the command name, and the `dept:<slug>` label.
- `{{DEPT_NAME}}` - the display name (e.g. `Test Design`).
- `{{DEPT_OBS_PREFIX}}` - the uppercase observation ID prefix (e.g. `TST`); supplied by the operator, not auto-derived.
- `{{DEPT_SCOPE}}` - the one-line "would own" scope from the ADR-021 menu.
- `{{DATE}}` - the creation date, `YYYY-MM-DD`.

### 3. The department orchestrator command `/<slug>-orchestrator`

When a department is created, the recipe stamps `templates/department/orchestrator-command.md` into `.claude/commands/<slug>-orchestrator.md` with tokens substituted. The command is a fully-wired, working orchestrator entry point for the department: it adopts the shared `ORCHESTRATOR-ROLE.md` (by reference; no copy, ADR-029), layers the department's context, dispatches the universal `worker-agent` (ADR-028) through the drafter+checker and dispatched-worker flows, and uses the universal checker fleet (ADR-023). There is no `/<slug>-worker` command.

### 4. The `/create-department` command

A root `.claude/commands/create-department.md` slash command. Inputs: `<slug>` (kebab), `<Display Name>`, `<OBS-PREFIX>` (uppercase). Precondition: the slug SHOULD be a blessed ADR-021 menu entry; creating an off-menu department requires extending the ADR-021 menu first (the command states this precondition and stops rather than silently inventing an off-menu department).

When invoked, the command drives the orchestrator through the dispatched-worker flow (execution-model Option B): it resolves the arguments and `{{DEPT_SCOPE}}`, drafts and checks a kickoff whose deliverable is the stamped workspace at `ai-infrastructure/<slug>/` (all template files, tokens substituted) plus the stamped `.claude/commands/<slug>-orchestrator.md`, runs the prelaunch checker, dispatches the `worker-agent`, and runs the close checker, verify-against-disk, and commit gate. The kickoff also reserves the `dept:<slug>` label in the markdown-era sense (item 5) and applies STATUS hygiene. Interactive back-and-forth at creation time (escalation round-trips, or Plan Mode for a genuinely unanticipated decision) is expected and acceptable.

### 5. `dept:<slug>` label reservation in the markdown era

"Reserve a `dept:<slug>` label" today means: use the established `dept:<slug>` naming (ADR-021) and ensure the slug is a blessed ADR-021 menu entry. There is no label registry to mutate in the markdown era; labels become real records at the dogfood milestone (ADR-008), and taxonomy, enforcement (for example at most one `dept:*` per task), and color/metadata are owned by ADR-018 (pending). The recipe documents the naming and defers the rest to ADR-018.

### 6. Department-scoped checker slot

Per ADR-027 Consequences and ADR-023, the template's `CLAUDE.md` carries a one-line note reserving the optional slot for a department-scoped checker that can layer beside the universal `worker-prelaunch-checker` / `worker-close-checker` pair if the department's work warrants it. No such checker is created by the recipe; the note reserves the slot.

## Consequences

- **ADR-027 Fork D partial amendment.** Fork D's "paired `/<dept>-orchestrator` and `/<dept>-worker` slash-command set" is amended: the department scaffold carries a single per-department `/<slug>-orchestrator` command and NO `/<slug>-worker` command (department deliverable work runs through the universal dispatched `worker-agent`, ADR-028). ADR-027 remains `accepted`, is not edited beyond a forward-pointer note, and is listed in `related_adrs`.
- **ADR-028 and ADR-029 intact.** The contract keeps the single universal dispatched worker (ADR-028) and the single shared set of role docs reused by reference (ADR-029). Per-department duplication of either was considered (Option C) and rejected.
- **Per-department orchestrator entry points.** Each department gains its own `/<slug>-orchestrator` command. This realizes the per-department layering that `ORCHESTRATOR-ROLE.md` anticipated. During COR-T-013 the user pulled that role-doc update forward: the doc's former "Corral is a single project, so there is one Orchestrator" framing was reframed (orchestrator-direct, user-authorized, 2026-06-10) to the coordinator-plus-per-department-orchestrator model, rather than waiting for first department creation.
- **ADR-018 dependency deferred, not blocking.** The recipe ships with `dept:<slug>` naming documented and label governance deferred to ADR-018 (COR-T-008). When ADR-018 resolves, it may add enforcement the recipe should reference; that is an ADR-018 follow-up.
- **Build split.** This ADR (the recipe ADR, COR-T-013 deliverable 3) is authored by the orchestrator directly (ADRs are orchestrator-direct). The `templates/department/` baseline including the orchestrator-command template (deliverable 1) and the `/create-department` command (deliverable 2) are built by a dispatched worker against this contract.
- **Lazy creation unchanged.** This ADR provides the recipe; ADR-021 provides the menu it stamps from; no department workspace is created by this ADR or by COR-T-013. The first real use of `/create-department` stamps the first department.
- **Department ADR numbering deferred.** The template's `decisions/README.md` stub leaves the department-local ADR numbering scheme to the department's first ADR, avoiding a premature global-versus-local numbering decision before any department ADR exists.
