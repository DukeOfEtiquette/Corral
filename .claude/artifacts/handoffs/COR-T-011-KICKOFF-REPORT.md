## Deliverables completed

- [x] `./decisions/ADR-027-ai-infrastructure-workspace-structure.md` created whole as `status: "accepted"`. Frontmatter matches pinned values verbatim (schema_version: 1, adr: 27, title, date: 2026-06-08, related_adrs: [1, 3, 5, 8, 9, 18, 21, 23, 24], supersedes: [], superseded_by: null). Body covers all four sections per `./decisions/README.md` body convention: Context, Alternatives considered, Decision, Consequences. All five forks (A through E) encoded. Target directory tree encoded verbatim. ADR-009 amendment recorded. Coordinator write authority recorded. Three named follow-on deliverables described without unallocated IDs. No em dashes in file.
- [x] `./STATUS.md` updated: `last_updated` confirmed as 2026-06-08 (already correct); `recent_updates` entry prepended recording ADR-027 acceptance and the structure decided; "Next step" paragraph rewritten to describe the restructure, create-department recipe, and dashboard as the next backbone steps, with COR-T-006 riding alongside and COR-T-008/009/010 remaining queued.

## Decisions made

- **Fork B rationale placement:** the kickoff listed the shared-pool dogfood rationale in the "Decisions resolved" section; the ADR encodes it as the central justification in the Alternatives section ("per-department task trees" subsection) and mirrors it in the Decision section, so the rogue divergence is readable in the ADR on its own terms.
- **"Next step" phrasing in STATUS.md:** the kickoff asked for a rewrite that names the three follow-on deliverables descriptively without unallocated IDs. Composed as a single paragraph naming the restructure, create-department recipe, and dashboard in sequence, with COR-T-006 and the remaining backlog items appended.
- **Consequences ordering in ADR-027:** ordered as: ADR-009 amendment, coordinator write authority, Fork C interim state, path-convention rule, three follow-on tasks, dogfood arc, department-scoped checkers note. This places the structural and governance consequences before the execution-plan consequences.

## Surprises

- **Pre-staged task file move in the staging area.** Before this session began, `tasks/backlog/COR-T-006-resolve-adr-021-departments.md -> tasks/in-progress/COR-T-006-resolve-adr-021-departments.md` was already staged (visible in `git diff --staged`). This Worker did not move it; it was a prior Orchestrator action. It will ride along in the next commit. No action taken (task transitions are Orchestrator-only; the Worker does not touch `./tasks/`).

## Follow-ups

- **COR-T candidate: restructure execution.** Execute the physical `git mv` of root orchestration content (`CLAUDE.md`, `STATUS.md`, `OBSERVATIONS.md`, `decisions/`, `docs/`, `tasks/`) into `ai-infrastructure/project-manager/`, rewrite the thin repo-root `CLAUDE.md`, and update all path-convention references in role docs, slash commands, and agent specs. ADR-027 Decision section is the spec. Triage to orchestrator to queue as the next backbone task.
- **COR-T candidate: create-department recipe.** Build the `templates/department/` baseline and `/create-department` command, and author a recipe ADR to record the scaffold contract. Triage to orchestrator after restructure task is queued.
- **COR-T candidate: project-manager dashboard.** Build the Fork E dashboard: Python ETL over shared `tasks/` pool, JSON data contract, minimal board UI, compose-integrated, with a planned repoint to the Corral web app at the dogfood milestone (ADR-008). Triage to orchestrator alongside the recipe task.

## Files touched

- `./decisions/ADR-027-ai-infrastructure-workspace-structure.md` (created)
- `./STATUS.md` (updated)
- `./.claude/artifacts/handoffs/COR-T-011-KICKOFF-REPORT.md` (this report, created)

## Build / verification status

No build or runtime verification applies to this task. The deliverables are a new markdown ADR and a STATUS.md update; both are human-readable artifacts with no executable components. The user is expected to review:
- `./decisions/ADR-027-ai-infrastructure-workspace-structure.md` for content accuracy against the kickoff's pinned decisions.
- `./STATUS.md` "Next step" paragraph for appropriate framing of the restructure sequence.
- `git diff --staged` to confirm the pre-staged COR-T-006 task move rides along as intended before committing.
