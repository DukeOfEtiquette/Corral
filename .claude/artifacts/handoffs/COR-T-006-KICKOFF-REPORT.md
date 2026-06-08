## Deliverables completed

- [x] `./decisions/ADR-021-candidate-departments.md` resolved in place:
  - Frontmatter: `status: "accepted"`, `date: "2026-06-08"`, `related_adrs: [1, 5, 8, 9, 18, 27]` (added 1, 8, 27).
  - `> Pending:` blockquote under the H1 removed.
  - "Alternatives considered" expanded: Option A expanded with "Selected." reasoning (lazy creation, menu as the ready list, `project-manager` exception, `dept:*` labels as taxonomy ahead of workspace creation); Option B expanded with "Rejected." reasoning (empty scaffolding, guessed conventions, structural overhead). Existing headings and leaning lines preserved unchanged.
  - "Decision" filled: nine-entry menu in two tables (coordinator + AI-infrastructure departments + web-app departments), coordinator/department distinction, label and board mapping (ADR-018, ADR-001, ADR-008), lazy creation policy statement.
  - "Consequences" filled: `project-manager` coordinator role and write authority; `ai-infra` as a domain not a department with COR-T-007 relabel deferred to ADR-018/COR-T-008; `dept:*` labels as taxonomy ahead of workspace creation; create-department recipe pointer to ADR-027 Fork D; dogfood milestone board mapping; ADR-027 as the authoritative structure ADR.
  - Existing Context and "Candidate departments" brainstorm tables preserved unchanged.

- [x] `./STATUS.md` updated:
  - New `recent_updates` entry prepended (COR-T-006 outcome).
  - "Next step" COR-T-006 clause removed.
  - `last_updated` already at `2026-06-08`; no bump needed.

## Decisions made

All decisions were pre-resolved by the Orchestrator in the kickoff. No Worker-level choices were required. Decisions encoded as directed:

- Frontmatter fields set per spec (`status: "accepted"`, `date: "2026-06-08"`, `related_adrs: [1, 5, 8, 9, 18, 27]`).
- Blessed menu: nine entries (`project-manager` coordinator + 3 AI-infra departments + 5 web-app departments).
- `project-manager` recorded as coordinator (not a tenth peer department), instantiated by the restructure, not lazily created.
- Lazy creation (Option A) recorded as selected; Option B recorded as rejected.
- `ai-infra` recorded as a domain name not a department; COR-T-007 `dept:ai-infra` relabel deferred to ADR-018/COR-T-008.
- ADR-027 cited as the authoritative structure ADR throughout Decision and Consequences.

## Surprises

(none)

## Follow-ups

- **COR-T-008: `dept:ai-infra` relabel of COR-T-007.** COR-T-007 currently carries an off-menu `dept:ai-infra` label. The reconciliation is label-taxonomy hygiene owned by ADR-018; its resolution is COR-T-008 (`./tasks/backlog/COR-T-008-resolve-adr-018-label-taxonomy.md`). Do not relabel COR-T-007 before COR-T-008 is executed. (COR-T candidate: COR-T-008)

## Files touched

- `./decisions/ADR-021-candidate-departments.md` (resolved in place: pending -> accepted)
- `./STATUS.md` (recent_updates entry prepended; Next step COR-T-006 clause removed)
- `./.claude/artifacts/handoffs/COR-T-006-KICKOFF-REPORT.md` (this report)

## Build / verification status

No build or compose verification required by this kickoff. The deliverable is a documentation change (one ADR resolution and STATUS hygiene). No code, no migrations, no running services touched. User may verify by reading the updated `./decisions/ADR-021-candidate-departments.md` directly.
