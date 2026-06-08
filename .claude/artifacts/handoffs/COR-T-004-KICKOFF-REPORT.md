# COR-T-004 Worker Closing Report

## Deliverables completed

- [x] **`./decisions/ADR-013-mcp-tool-surface-house-rules.md` resolved in place.** Frontmatter updated: `status: "accepted"`, `date: "2026-06-07"`, `related_adrs: [4, 8, 10, 12, 17, 18, 19, 20, 25]`. The `> Pending:` blockquote callout removed. Alternatives expanded: Option A selected-and-narrowed (eight base `issue_*` tools plus `issue_import`); three not-ported ghtask tools (`task_link`, `task_check`, `task_lint`) recorded as considered-and-excluded with one-line rationales; Option B rejected with reasoning; Open house-rule dimensions resolved (free transitions, priority required, label-governance mechanism, importer, surface evolution, enforcement location). Decision filled with nine-tool table plus declarative rules. Consequences filled with six items covering ADR-008 importer, label-governance boundary to ADR-018/ADR-021, ADR-020 claim non-preclusion, ADR-019 surface-evolution ownership, ADR-025 epics deferral and dropped `issue_link` rationale, single enforcement seam.

- [x] **`./decisions/ADR-025-native-epics.md` created as a new `pending` ADR.** Frontmatter: `schema_version: 1`, `adr: 25`, `status: "pending"`, `date: "2026-06-07"`, `related_adrs: [1, 12, 13, 17]`, `supersedes: []`, `superseded_by: null`. Body: `> Pending:` callout present; Context written (body-convention workaround not ported, dependency on ADR-012/ADR-013/ADR-024/ADR-019, open dimensions named); three alternatives stubbed (Option A: distinct epics table with join, Option B: self-referential parent_id on issues, Option C: type field plus parent relation), each noting schema-amendment shape and board/UI treatment; Decision and Consequences as `{Pending.}` stubs. No option selected; no resolution attempted.

- [x] **`./docs/architecture/OVERVIEW.md` mcp-bullet clause updated.** Changed "Tool surface and house rules pending (ADR-013)." to "v1 tool surface and house rules decided in ADR-013 (accepted)." The rest of that bullet (calls the api service over HTTP per ADR-010 and never touches postgres directly), the diagram, and all other bullets are untouched.

- [x] **`./STATUS.md` updated.** `last_updated` bumped to `2026-06-07`. New `recent_updates` entry prepended noting ADR-013 accepted (nine-tool surface, free transitions, priority required, label-governance mechanism deferred) and ADR-025 queued pending (native epics). Task-specific delta applied: "COR-T-004 (MCP surface, ADR-013)" removed from the "Next step" line; COR-T-005 and COR-T-006 and the rest of the sentence remain intact.

## Decisions made

No kickoff decisions were re-opened. All choices were pinned by the Orchestrator. One structural decision was made by the Worker in authoring:

- **ADR-025 `> Pending:` callout wording.** The kickoff specified a blockquote callout but did not dictate the exact text. Following the style of ADR-018, ADR-019, and ADR-021, the callout reads: "Pending: can wait. Frames the native epics model; needed before epic tools and schema amendments are scoped." This characterizes urgency (can wait) and naming purpose (question-framing), consistent with the other Phase-0-seeded pending ADRs.

## Surprises

(none)

## Follow-ups

- **ADR-018 and ADR-021 resolution needed before label-governance specifics can be implemented.** ADR-013 Consequences item 2 records the boundary; the concrete families, cardinalities, and creation-rights table are owned by ADR-018 and ADR-021, which remain pending. COR-T-006 (departments, ADR-021) is already in the Phase 1 backlog. ADR-018 does not yet have a corresponding COR-T tracking file. Triage to orchestrator: consider queuing a COR-T for ADR-018 alongside COR-T-006.

- **ADR-025 needs a COR-T tracking file.** ADR-025 is now queued pending but has no task file under `./tasks/`. The other Phase-0-seeded pending ADRs each have a corresponding `COR-T-NNN` backlog file. Triage to orchestrator: create a `COR-T` candidate for ADR-025 to track the native-epics resolution work.

## Files touched

- `./decisions/ADR-013-mcp-tool-surface-house-rules.md` (resolved in place)
- `./decisions/ADR-025-native-epics.md` (created)
- `./docs/architecture/OVERVIEW.md` (mcp-bullet clause updated)
- `./STATUS.md` (last_updated, recent_updates, Next step delta)
- `./.claude/artifacts/handoffs/COR-T-004-KICKOFF-REPORT.md` (this report)

All five files are staged. No commits made (per universal convention; commit gate is the Orchestrator's).

## Build / verification status

No build or runtime verification applies. This task writes decision records and two doc edits only; no application code, SQL, compose files, or migration files were produced. The user is expected to verify:

- ADR-013 content fidelity: the nine-tool table, the free-transition and priority rules, and the Consequences items match the kickoff's pinned decisions.
- ADR-025 content: no option is selected; Decision and Consequences are `{Pending.}` stubs; the three alternatives accurately capture the schema-amendment shapes.
- OVERVIEW.md: only the mcp-bullet pending clause changed; diagram and other bullets unchanged.
- STATUS.md: `last_updated` is `2026-06-07`; new entry prepended in `recent_updates`; "Next step" retains COR-T-005 and COR-T-006 with COR-T-004 removed.
