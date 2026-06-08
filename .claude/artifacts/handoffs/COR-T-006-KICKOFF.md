# Resolve ADR-021: finalize the candidate-department menu

## Target

This is AI-infrastructure work (domain 2, per `./decisions/ADR-005-two-domains-ai-first.md`). The artifact in scope is one pending ADR: `./decisions/ADR-021-candidate-departments.md`. Your job is to take it from `pending` to `accepted` in place, the same way the COR-T-002/003/004/005 runs resolved their pending ADRs. The decision being recorded is the department structure of Corral's AI infrastructure: a blessed nine-entry menu (one coordinator plus eight departments) and a lazy-creation policy. There is no web-app code, no file moves, no `ai-infrastructure/` directory creation, and no department-workspace creation in this task. You resolve one ADR plus apply STATUS hygiene.

The procedure mirrors the prior pending-to-accepted runs and the append-only convention in `./decisions/README.md`. You edit ADR-021 in place: expand "Alternatives considered" with honest selected/rejected reasoning, fill the stubbed "Decision" and "Consequences" sections, flip the frontmatter `status` to `accepted`, and set `date` to `2026-06-08`. The append-only rule (`./decisions/README.md`, section "Append-only") forbids deleting the existing Context, the "Candidate departments" brainstorm table, or the Option A / Option B framing under "Alternatives considered"; those stay as historical framing. The one removal allowed is the `> Pending:` blockquote callout directly under the H1, which is a status marker that comes off when the ADR goes accepted. The authoritative final menu lives in the "Decision" section you fill in; the brainstorm table above it remains as the historical candidate list that fed the decision.

## Decisions resolved by the Orchestrator

These are pinned. Encode them into ADR-021; do not re-open them or present any of them as an open choice for a later session.

- **Frontmatter on resolve.** Set `status: "accepted"`, `date: "2026-06-08"`, and `related_adrs: [1, 5, 8, 9, 18, 27]`. The current value is `[5, 9, 18]`. The Decision and Consequences sections you write newly cite ADR-001 (the board-per-department-label headline use case), ADR-008 (departments map to filtered boards at the dogfood milestone), and ADR-027 (the authoritative workspace-structure ADR), so add `1, 8, 27`. This is reference bookkeeping per `./decisions/README.md` (frontmatter schema), not a new decision.

- **The blessed final menu (record authoritatively in the "Decision" section).** Nine entries total. Keep all eight original candidates exactly as listed in the existing "Candidate departments" table, and add `project-manager` as the coordinator entry (the user's addition):
  - **Coordinator (already instantiated per ADR-027; not lazily created):** `project-manager`.
  - **AI-infrastructure domain departments (lazily created):** `agent-development`, `test-design`, `docs-curation`.
  - **Web-app domain departments (lazily created):** `backend-api`, `database`, `mcp-server`, `frontend-ui`, `devops`.

  Each entry maps to a `dept:<slug>` label (ADR-018) and, at the dogfood milestone, a filtered kanban board (ADR-001, ADR-008). The "would own" descriptions for the eight departments are already in the brainstorm table; reuse them. For `project-manager`, record its scope as "orchestration, dispatch, review, cross-department coordination, and the shared task pool" (the coordinator's scope per ADR-027).

- **`project-manager` is the coordinator, not a tenth department (the ADR-027 distinction).** It tracks, dispatches, and reviews; it does not author domain content; it holds write authority over the sibling department workspaces it coordinates (per `./decisions/ADR-027-ai-infrastructure-workspace-structure.md`, "Coordinator write authority"). It is on the menu so coordinator-level work has a `dept:project-manager` label and its own board, mirroring rogue's `workspace:project-manager`. Unlike the eight departments, it is not lazily created: it is instantiated by the restructure (ADR-027; a named follow-on task). Record this distinction explicitly so a reader does not mistake the coordinator for a tenth peer department.

- **Creation policy: lazy (Option A is the selected alternative).** No department workspace is created by this task or at this time. The menu is the ready list the `project-manager` stamps from on demand using the create-department recipe (ADR-027 Fork D, a named follow-on task). The `project-manager` coordinator is the lone exception: it is instantiated by the restructure, not lazily created. The `dept:*` labels already present on existing task files are taxonomy running ahead of formal workspace creation, which is consistent with ADR-027. Option B (create all departments up front) is the rejected alternative: most workspaces would sit empty and their conventions would be guessed rather than earned.

- **`ai-infra` is a domain, not a department.** `ai-infra` is the ADR-005 domain name, so it is deliberately NOT on the menu. One done task (`COR-T-007`) carries the off-menu `dept:ai-infra` label. Reconciling that label is label-taxonomy hygiene owned by ADR-018 (its resolution is COR-T-008), not resolved here. Record this as a note in "Consequences" and surface it in your closing report's Follow-ups so the Orchestrator carries it to COR-T-008. Do NOT relabel COR-T-007 in this task.

- **ADR-021 references ADR-027 for structure; it does not redefine what a department is.** ADR-027 owns the `ai-infrastructure/<workspace>/` structure, the coordinator/department model, the shared `dept:`-labeled task pool, and the create-department recipe. ADR-021's job is narrower: bless the menu and the lazy-creation policy, and point at ADR-027 for the rest. Keep the Decision and Consequences consistent with ADR-027; cite it, do not restate or re-decide its content.

## Deliverables

1. `./decisions/ADR-021-candidate-departments.md` resolved in place:
   - Frontmatter: `status: "accepted"`, `date: "2026-06-08"`, `related_adrs: [1, 5, 8, 9, 18, 27]`.
   - The `> Pending:` blockquote callout under the H1 removed.
   - "Alternatives considered" expanded: Option A (lazy creation) selected with reasoning; Option B (create all up front) rejected with reasoning. The existing Option A / Option B headings and their leaning lines stay; you expand them into honest selected/rejected reasoning.
   - "Decision" filled with the authoritative nine-entry menu, the coordinator/department distinction, the lazy-creation policy, and the `dept:<slug>`-label plus filtered-board mapping (ADR-018 for the label, ADR-001 and ADR-008 for the board).
   - "Consequences" filled: the `project-manager` coordinator role and its write authority per ADR-027; `ai-infra` is a domain not a department, with the COR-T-007 relabel deferred to ADR-018 / COR-T-008; the `dept:*` labels as taxonomy ahead of workspace creation; the create-department recipe living in ADR-027's named follow-on work; departments mapping to filtered boards at the dogfood milestone.
   - The existing Context and the "Candidate departments" brainstorm table are preserved unchanged (append-only).
2. `./STATUS.md` updated per the "STATUS deltas" section below.

## Files in scope

- `./decisions/ADR-021-candidate-departments.md` (resolve in place).
- `./STATUS.md` (task-specific deltas plus universal hygiene).

## Files out of scope

- Every other ADR. ADR-027 (accepted), ADR-005, ADR-009, ADR-018, ADR-001, and ADR-008 are cited but NOT edited. In particular, do NOT resolve or edit `./decisions/ADR-018-department-label-taxonomy.md`: the `dept:` label format and enforcement, and the `dept:ai-infra` relabel, are its job (COR-T-008), not this task's.
- The role docs (`./docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md`, `./docs/ai-orchestration/roles/WORKER-ROLE.md`), the slash commands, and `./CLAUDE.md`. ORCHESTRATOR-ROLE.md's line referencing "the coordinator described in ADR-021" becomes lightly stale now that ADR-027 is the authoritative structure ADR, but refreshing role-doc cross-references is part of the restructure task (COR-T-012), NOT this task. Do not edit them.
- The `./tasks/` tree, including `./tasks/in-progress/COR-T-006-resolve-adr-021-departments.md` and the `dept:ai-infra`-labeled `./tasks/done/COR-T-007-track-handoff-artifacts.md`. Task transitions and relabels are Orchestrator-only; read these for context, but never move, edit, or create anything under `./tasks/`. The COR-T-007 relabel is a COR-T-008 follow-up.
- No file moves, no `ai-infrastructure/` directory, no department workspaces, no templates, no dashboard. ADR-021 records the menu only.

## References

Read these in this order before editing:

- `./decisions/ADR-021-candidate-departments.md`: the target; read first. It carries the Context, the "Candidate departments" brainstorm table, and the Option A (lazy) / Option B (up-front) framing you expand.
- `./decisions/README.md`: ADR conventions: the frontmatter schema, the status values, the four-section body convention, the append-only rule, and how a pending ADR resolves to accepted.
- `./decisions/ADR-027-ai-infrastructure-workspace-structure.md`: the authoritative workspace-structure ADR (the coordinator/department model, lazy creation, the shared `dept:`-labeled pool, and the create-department recipe). ADR-021 references it and must stay consistent; read it so the coordinator/department distinction and the recipe pointer are accurate.
- `./decisions/ADR-018-department-label-taxonomy.md`: the pending label-taxonomy ADR that owns the `dept:` label format and enforcement and the `dept:ai-infra` relabel; ADR-021 defers those to it.
- `./decisions/ADR-005-two-domains-ai-first.md`: the two-domains split establishing that `ai-infra` is a domain, not a department.
- `./decisions/ADR-001-self-hosted-issue-tracker-scope.md`: the board-per-department-label headline use case.
- `./decisions/ADR-008-bootstrap-tasks-dogfood-milestone.md`: the dogfood milestone where departments map to filtered boards.
- `./decisions/ADR-009-adopt-rogue-orchestration-conventions.md`: the coordinator-plus-departments lineage from rogue.

## Related tasks and ADRs

- COR-T-006 (`./tasks/in-progress/COR-T-006-resolve-adr-021-departments.md`): this task's tracking file; read for context, do not edit.
- COR-T-011 (`./tasks/done/COR-T-011-author-adr-027-ai-infrastructure-structure.md`): delivered ADR-027, the structure ADR this resolution references.
- COR-T-008 (`./tasks/backlog/COR-T-008-resolve-adr-018-label-taxonomy.md`): resolves ADR-018, which owns the `dept:` label taxonomy and the `dept:ai-infra` relabel deferred here.
- COR-T-012 / COR-T-013 / COR-T-014 (`./tasks/backlog/`): the ADR-027 follow-on restructure, create-department recipe, and dashboard; the recipe is how menu departments are lazily created.
- ADR-027: the authoritative workspace structure; ADR-021 is the department menu feeding it.
- ADR-005 / ADR-001 / ADR-008 / ADR-018: the domains, the board use case, the dogfood mapping, and the label taxonomy.

## STATUS deltas

Beyond universal STATUS hygiene (bump `last_updated` to `2026-06-08` and append a `recent_updates` entry per `./docs/ai-orchestration/roles/WORKER-ROLE.md`, section "Wrap-up STATUS hygiene"), apply these task-specific edits to `./STATUS.md`:

- The `recent_updates` entry you append records: ADR-021 accepted; the candidate-department menu blessed (the `project-manager` coordinator plus three AI-infrastructure departments and five web-app departments); lazy creation confirmed; `ai-infra` noted as a domain not a department with the `dept:ai-infra` relabel deferred to ADR-018 / COR-T-008; and ADR-027 referenced as the authoritative structure.
- In the "Next step" paragraph, remove the clause stating that COR-T-006 (ADR-021 candidate-department finalization) "rides alongside and is not blocked by the restructure," since COR-T-006 is now resolved. Leave the COR-T-012/013/014 restructure sequence and the COR-T-008/009/010 queued list intact.
- The "Blocked on" section stays "Nothing." No edit there.

## Hard rules

- Edit ADR-021 in place. Do not create a new ADR file and do not renumber.
- Honor the append-only convention (`./decisions/README.md`): preserve the existing Context, the "Candidate departments" brainstorm table, and the Option A / Option B headings under "Alternatives considered". The only deletion permitted is the `> Pending:` blockquote under the H1.
- The authoritative final menu is the one in the "Decision" section. The brainstorm table is historical framing and is not edited to match; the eight candidates there already align with eight of the nine menu entries, and `project-manager` is the coordinator added in the Decision.
- Do not resolve, edit, or pre-empt ADR-018. The `dept:` label format and the `dept:ai-infra` relabel are deferred to it; cite the deferral, do not perform it.
- Surface the `dept:ai-infra` relabel of COR-T-007 in your closing report's Follow-ups (anchored to COR-T-008), per WORKER-ROLE.md rule W2. Do not relabel COR-T-007 yourself.

## Worker pointer

The Worker session is `/corral-worker`. Universal worker conventions live in `./docs/ai-orchestration/roles/WORKER-ROLE.md`. The closing report is written to `./.claude/artifacts/handoffs/COR-T-006-KICKOFF-REPORT.md` per WORKER-ROLE.md, section "Report shape".
