# COR-T-004: Resolve ADR-013 (MCP tool surface and server-enforced house rules), and queue pending ADR-025 (native epics)

## Target

This is web-app domain work (ADR-005): the artifacts are decision records about the web app's MCP server and its house rules, plus two downstream doc propagations. No application code, MCP server code, OpenAPI/tool-schema, SQL, or migration files exist yet and none is written by this task. You resolve ADR-013 in place, author a new pending ADR-025 for native epics, update one clause in `./docs/architecture/OVERVIEW.md`, and apply STATUS hygiene plus the task-specific STATUS deltas named below.

Procedure note: this resolves the same way the COR-T-002 (ADR-012) and COR-T-003 (ADR-010) runs did. Edit the pending ADR in place per the conventions in `./decisions/README.md`: expand "Alternatives considered" with honest selected/rejected reasoning, fill the stubbed Decision and Consequences sections, flip frontmatter `status` to `accepted`, and set frontmatter `date` to the work date. The append-only rule (`./decisions/README.md`) forbids deleting the existing Context or option framing; the `> Pending:` blockquote callout directly under the H1 is a status marker, not decision content, and is removed when the ADR goes accepted.

## Decisions resolved by the Orchestrator

These are pinned. Encode them into the ADR text; do not re-open or re-deliberate any of them.

- **ADR-013 frontmatter on resolve.** Set `status: "accepted"`, `date: "2026-06-07"`, and `related_adrs: [4, 8, 10, 12, 17, 18, 19, 20, 25]`. The current `related_adrs` is `[4, 10, 12, 19]`; the Consequences you write newly cite ADR-008, ADR-017, ADR-018, ADR-020, and ADR-025, so add `8, 17, 18, 20, 25`. This is reference bookkeeping per `./decisions/README.md`, not a new decision.

- **v1 tool surface: a ghtask mirror minus the GitHub-workaround tools.** The v1 surface is eight base tools, renamed from rogue's ghtask `task_*` to this domain's `issue_*`: `issue_list`, `issue_get`, `issue_create`, `issue_claim`, `issue_move`, `issue_comment`, `issue_label`, plus `view_list`. These map onto the accepted ADR-012 schema (issues, issue_labels, views, issue_comments, issue_events, the minimal users reference). This is ADR-013's Option A (mirror the ghtask set), narrowed. Rationale to record: familiar to the existing agent fleet, proven ergonomics, and a 1:1 fit with the accepted schema.

- **Three ghtask tools are deliberately not ported.** State all three in ADR-013 as explicitly considered-and-excluded with the one-line rationale each, so a future reader knows they were weighed, not forgotten:
  - `task_link` is dropped. In ghtask it appends `- [ ] #child` under a `## Tracked work` body section, a markdown workaround for GitHub Issues' lack of native epics. Corral will support epics natively instead (see the ADR-025 deliverable), so the body-convention link tool is not carried over.
  - `task_check` is dropped. It ticks markdown checklist items in an issue body, the same body-convention family as `task_link`, and is likewise a GitHub workaround Corral does not need.
  - `task_lint` is deferred. It conformance-checks issues against house rules, but the house-rule specifics (label families) are not yet pinned, and rules are enforced at write time by the API. A separate lint tool can be added later if needed.

- **The ADR-008 dogfood importer is a ninth MCP tool.** Add `issue_import`, mirroring ghtask's `task_migrate`. It is idempotent via the `external_ref` unique column from ADR-012 (which carries the `COR-T-NNN` task id), so re-running the import does not duplicate issues. Rationale to record: the dogfood import (ADR-008) is agent-run, and ADR-004 makes the MCP server the only sanctioned agent path, so the importer must live on the MCP surface; it also exercises the seam end-to-end, which is the dogfood milestone's purpose.

- **Status transitions are free within the ADR-012 CHECK set, not a server-enforced graph.** `issue_move` accepts any of the four statuses (`backlog`, `in-progress`, `blocked`, `done`) and permits any-to-any transition; the ADR-012 column CHECK constraint already confines the value set. Every move is recorded in the `issue_events` table (ADR-012) as the activity record. Rationale to record: this matches GitHub's reopen-anything model, keeps the lifecycle a convention rather than a hard graph, is the cheapest v1, and precludes nothing (a transition graph can be added later). A transition-graph enforcement on the transitions dimension is the rejected alternative.

- **Priority is required at create time.** ADR-012 makes `issues.priority` NOT NULL with a CHECK of `P0 | P1 | P2 | P3`, so `issue_create` requires a `priority` argument confined to that set (mirrors ghtask `task_create`, where priority is a required arg). Record this as a server-enforced house rule that is mechanical from ADR-012, not a new choice.

- **Label governance: pin the mechanism, defer the specifics.** ADR-013 pins that the API server-enforces (a) reserved-label-family invariants and (b) label-creation rights, exposed through `issue_label` and `issue_create`. ADR-013 does not pin the concrete families, their cardinalities (for example, at-most-one `dept:*`), or the creation-rights table (admin-only vs any-user). Those specifics are owned by ADR-018 (department label taxonomy, pending) and ADR-021 (candidate departments, pending). Record this boundary explicitly in Consequences. The flat-labels-no-families alternative is not the choice; families exist, their content is deferred.

- **Enforcement location: the API layer; the MCP server stays thin.** All house rules above are enforced in the HTTP API (ADR-010's single enforcement seam); the MCP server calls the API and does not re-implement rules. ADR-013's Decision and Consequences must be consistent with ADR-010 and reference it; this ADR does not re-decide the data path.

- **Surface-evolution and concurrency are out of scope: named, not decided.**
  - How the tool surface is versioned as it grows (for example, adding epic tools additively later) is owned by ADR-019 (MCP contract versioning, pending). ADR-013 names it and stops.
  - Including `issue_claim` (sets `issues.assignee_id` per ADR-012; mirrors ghtask `task_claim` with its `force` option) does not decide the multi-user concurrency model; whether claim acts as a lease, and last-write-wins vs optimistic versioning, are owned by ADR-020 (pending). Record a one-line non-preclusion note for ADR-020.

- **Native epics get a new pending ADR-025, not a resolution here.** Author `./decisions/ADR-025-native-epics.md` as a `pending` ADR that reserves the number and frames the question, in the same style as the other Phase-0-seeded pending ADRs (a `> Pending: ...` blockquote callout under the H1; Context written; Alternatives stubbed as framed options; Decision and Consequences as the literal `{Pending.}` stub). This is a question-framing ADR; do not select an option or pre-resolve it. The exact framing to encode is in Deliverable 2 below.

- **OVERVIEW propagation.** The `mcp` bullet's clause "Tool surface and house rules pending (ADR-013)." is now stale. Rewrite it to state that the v1 tool surface and house rules are decided in ADR-013 (accepted), keeping the rest of that bullet intact (the "calls the api service over HTTP per ADR-010 and never touches postgres directly" clause). The diagram and the other OVERVIEW bullets stay unchanged.

## Deliverables

1. **`./decisions/ADR-013-mcp-tool-surface-house-rules.md` resolved in place.**
   - Frontmatter: `status: "accepted"`, `date: "2026-06-07"`, `related_adrs: [4, 8, 10, 12, 17, 18, 19, 20, 25]`.
   - The `> Pending:` blockquote callout under the H1 is removed.
   - "Alternatives considered" expanded: Option A (mirror the ghtask set) selected and narrowed; Option B (leaner surface) rejected with reasoning; the three not-ported ghtask tools (`task_link`, `task_check`, `task_lint`) recorded as considered-and-excluded with their one-line rationales; the open house-rule dimensions resolved per the decisions above.
   - "Decision" filled declaratively: the nine-tool surface (`issue_list`, `issue_get`, `issue_create`, `issue_claim`, `issue_move`, `issue_comment`, `issue_label`, `view_list`, `issue_import`), the free-transition rule, priority-required-at-create, the label-governance mechanism, and API-layer enforcement.
   - "Consequences" filled: importer/dogfood per ADR-008; the label-governance boundary deferred to ADR-018/ADR-021; the ADR-020 claim non-preclusion note; ADR-019 surface-evolution ownership; the ADR-025 epics deferral and the dropped `issue_link` rationale; the single enforcement seam consistent with ADR-010.
2. **`./decisions/ADR-025-native-epics.md` created as a new `pending` ADR.** Frontmatter: `schema_version: 1`, `adr: 25`, `status: "pending"`, `date: "2026-06-07"`, `related_adrs: [1, 12, 13, 17]`, `supersedes: []`, `superseded_by: null`. Body, framed (not resolved):
   - **Context:** Corral wants native epics (parent issues that group child issues), unlike the GitHub Issues workflow it replaces, where epics were faked with the `task_link` body-convention (a markdown checklist under `## Tracked work`). That workaround is deliberately not ported (see ADR-013). This ADR frames how native epics are modeled and exposed. It depends on the accepted schema (ADR-012, which has no parent/child relation today) and the accepted v1 MCP surface (ADR-013, which omits epic tools); resolving it will amend ADR-012's schema via a new ADR (the ADR-024 precedent: an accepted ADR is amended by a later ADR, not edited in place) and add epic tools additively to the ADR-013 surface (policy per ADR-019).
   - **Alternatives considered (stubs, no selection):** Option A, epic as a distinct entity/table with a child-membership join. Option B, a self-referential parent relation on `issues` (for example, a nullable `parent_id` / `epic_id` column). Option C, an issue `type` field (epic vs task) plus a parent relation. Each line notes the schema-amendment shape it implies and its board/UI treatment.
   - **Open dimensions to name:** the MCP tool additions (for example, `epic_create`, child attach/detach, or an `epic` param on `issue_create`); how epics render across multi-view boards (ADR-017 territory); whether an issue may belong to more than one epic; and the migration that introduces the relation.
   - **Decision:** the literal `{Pending.}` stub.
   - **Consequences:** the literal `{Pending.}` stub.
3. **`./docs/architecture/OVERVIEW.md` `mcp`-bullet clause updated** as described in the decisions above; nothing else in OVERVIEW changes (diagram and other bullets untouched).
4. **`./STATUS.md` updated** per the STATUS deltas section below (universal hygiene plus the task-specific edits named there).

## Files in scope

- `./decisions/ADR-013-mcp-tool-surface-house-rules.md` (resolve in place)
- `./decisions/ADR-025-native-epics.md` (create new, pending)
- `./docs/architecture/OVERVIEW.md` (the single `mcp`-bullet clause only)
- `./STATUS.md` (task-specific delta plus universal hygiene)

## Files out of scope

- **Every other ADR.** ADR-011 and ADR-014 through ADR-021 (except their OVERVIEW/STATUS effects) remain pending and unedited; ADR-019 and ADR-020 in particular stay pending. ADR-013's Consequences reference these but never edit them. ADR-004, ADR-008, ADR-010, and ADR-012 (accepted) are not edited; their content is referenced only. Do not resolve ADR-018, ADR-019, ADR-020, or ADR-021, and do not pre-resolve the new ADR-025.
- **The `./tasks/` tree**, including `./tasks/backlog/COR-T-004-resolve-adr-013-mcp-surface.md`. Task transitions are Orchestrator-only. You may read the task file for context; never move, edit, or create files under `./tasks/`.
- **Any application code**, MCP server code, OpenAPI/tool-schema files, SQL, migration files, or compose files. This task writes decision records and two doc edits only. The concrete tool parameter schemas, endpoint wiring, and the epic schema are implementation/future-ADR work, not authored here.
- **`./README.md` roadmap.** Not edited. Its row-1 list of Phase-1 blocking ADRs remains an accurate historical deliverable list after ADR-013 resolves (matching how the ADR-010 run left README row 1).

## References

Read these in the order listed.

- `./decisions/ADR-013-mcp-tool-surface-house-rules.md`: the target; read first. Carries the Context and the Option A / Option B / open-house-rule-dimensions framing you expand.
- `./decisions/README.md`: ADR conventions: frontmatter schema, status values, the four-section body convention, the append-only rule, and the pending-ADR shape you reuse for ADR-025.
- `./decisions/ADR-012-issue-label-view-schema.md`: the accepted schema the tool surface binds to (issues with status/priority CHECKs and `external_ref`, issue_labels, views, issue_comments, issue_events, the minimal users reference). Source of the priority-required and free-transition mechanics.
- `./decisions/ADR-010-api-shape-and-mcp-data-path.md`: the accepted data path and single-enforcement-seam decision; house rules live in the API layer, the MCP server is a thin client.
- `./decisions/ADR-004-mcp-server-as-llm-contract.md`: the MCP-as-sole-seam guardrail rationale; why the importer must be an MCP tool.
- `./decisions/ADR-008-bootstrap-tasks-dogfood-milestone.md`: the dogfood milestone the importer serves, and the `external_ref` idempotent-import contract.
- `./decisions/ADR-024-git-tracked-handoff-artifacts.md`: the precedent that an accepted ADR is amended by a later ADR, not edited in place (cited in ADR-025's Context for the future ADR-012 amendment).
- `./decisions/ADR-018-department-label-taxonomy.md` and `./decisions/ADR-021-candidate-departments.md`: pending neighbours that own the label-family and department specifics ADR-013 defers; read so the boundary note is accurate.
- `./decisions/ADR-019-mcp-contract-versioning.md` and `./decisions/ADR-020-multi-user-concurrency-model.md`: pending neighbours ADR-013 names without resolving (surface evolution; claim/concurrency).
- `./decisions/ADR-017-board-column-status-mapping.md`: pending neighbour; board/transition treatment cross-referenced by ADR-013 and ADR-025.
- `./docs/architecture/OVERVIEW.md`: carries the `mcp`-bullet clause in scope.
- `/home/adam/rogue/.claude/tools/ghtask/server.py` and `/home/adam/rogue/.claude/tools/ghtask/README.md`: the ghtask reference surface, read-only context for what the tools do and which were dropped. This is an external reference repo, not part of Corral; do not edit it.

## Related tasks and ADRs

- COR-T-004 (`./tasks/backlog/COR-T-004-resolve-adr-013-mcp-surface.md`): this task's tracking file; read for context, do not edit.
- COR-T-003 (`./tasks/done/COR-T-003-resolve-adr-010-api-shape.md`): delivered the accepted data path and single-enforcement-seam this surface binds to.
- COR-T-002 (`./tasks/done/COR-T-002-resolve-adr-012-schema.md`): delivered the accepted schema the tools map onto.
- COR-T-006 (`./tasks/backlog/COR-T-006-resolve-adr-021-departments.md`): will resolve ADR-021, which (with ADR-018) owns the label-family specifics ADR-013 defers.
- ADR-012: the accepted schema; binds the tool surface and the importer's `external_ref` idempotency.
- ADR-010 / ADR-004: the data path and sole-seam contract; house rules in the API layer, importer on the MCP surface.
- ADR-008: the dogfood milestone the importer serves.
- ADR-018 / ADR-021: own the deferred label-family and department specifics.
- ADR-019 / ADR-020: own the deferred surface-versioning and concurrency questions ADR-013 names.
- ADR-025: the new pending ADR this task creates for native epics; the home of the dropped `issue_link`'s native replacement.

## STATUS deltas

Beyond universal STATUS hygiene (bump `last_updated` to 2026-06-07 and append a `recent_updates` entry, per `WORKER-ROLE.md`), apply these task-specific edits to `./STATUS.md`:

- Under "Next step", the line currently reads: "Work the remaining Phase 1 backlog: COR-T-004 (MCP surface, ADR-013), COR-T-005 (auth, ADR-011), COR-T-006 (departments, ADR-021). These are the first candidates for the new kickoff/worker workflow." Drop the "COR-T-004 (MCP surface, ADR-013)" entry; leave COR-T-005 and COR-T-006 and the rest of the line intact.
- The `recent_updates` entry should note both ADR-013 accepted (nine-tool MCP surface, free transitions, label-governance mechanism deferred to ADR-018/ADR-021) and ADR-025 queued pending (native epics).

## Hard rules

- The append-only ADR convention (`./decisions/README.md`) binds this task: do not delete the existing Context or option-framing text in ADR-013. Expand the option framing and fill the stubs; the only deletion permitted is the `> Pending:` status-marker blockquote when the ADR goes accepted.
- ADR-025 is a question-framing pending ADR. Do not select an option, do not write a Decision, and do not pre-resolve it. Its Decision and Consequences are the literal `{Pending.}` stub.
- ADR-013's Decision and Consequences must stay consistent with the accepted ADR-010 (single enforcement seam) and ADR-012 (schema): cite them, do not re-decide them.
- The OVERVIEW edit touches only the `mcp` bullet's pending clause. Do not alter the diagram or any other bullet.

## Worker pointer

The Worker session is `/corral-worker`. Universal worker conventions live in `./docs/ai-orchestration/roles/WORKER-ROLE.md`. The closing report is written to `./.claude/artifacts/handoffs/COR-T-004-KICKOFF-REPORT.md` per WORKER-ROLE.md, section "Report shape".
