## Deliverables completed

- `git mv` executed for all 55 renames: `STATUS.md`, `OBSERVATIONS.md`, `CLAUDE.md`, `decisions/` (30 ADRs + README), `tasks/` (entire tree including COR-T-012 itself), and `docs/architecture/OVERVIEW.md` all moved into `ai-infrastructure/project-manager/`.
- Thin root `CLAUDE.md` authored from scratch: contains Two Domains (ref to ADR-005 at new path), Agent Discipline (authoritative copy, with note it is the authoritative copy), Secrets, Documentation Placement (updated for new structure), Writing Style, and a Workspace Orientation table pointing to `./ai-infrastructure/project-manager/`.
- `ai-infrastructure/project-manager/CLAUDE.md` rewritten from original: contains Path Conventions (two-domain bare-vs-dot-slash rule explained), Coordinator Write Authority (D8 addition per ADR-027), MCP Seam, Tasks, Decisions, Run Policy, Pointers table. Agent Discipline mentions the root CLAUDE.md as authoritative and does not duplicate the section body.
- `ai-infrastructure/project-manager/README.md` authored: workspace charter explaining purpose, contents table, shared-infra-at-root explanation.
- `ai-infrastructure/project-manager/STATUS.md` bare-path rewrites applied (D4a); Next Step paragraph updated to reflect COR-T-012 completion and name COR-T-013/COR-T-014 as remaining follow-ons; `recent_updates` prepend and `last_updated` bump applied (STATUS hygiene).
- `ai-infrastructure/project-manager/OBSERVATIONS.md` bare-path rewrite applied (D4a).
- `ai-infrastructure/project-manager/decisions/ADR-023` and `ADR-024` bare-path rewrites applied (D4a).
- `docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md` D4b rewrites applied: all `./decisions/ADR-NNN` to `./ai-infrastructure/project-manager/decisions/ADR-NNN`, `./STATUS.md`, `./OBSERVATIONS.md`, `./tasks/`, `./docs/architecture/OVERVIEW.md` refs updated; split-routed CLAUDE.md refs (decisions rule to PM CLAUDE.md, writing rule/Agent Discipline to root CLAUDE.md).
- `docs/ai-orchestration/roles/WORKER-ROLE.md` D4b rewrites applied.
- `.claude/agents/worker-agent.md` D4b rewrites applied.
- `.claude/agents/kickoff-drafter.md` D4b rewrites applied.
- `.claude/agents/kickoff-checker.md` D4b rewrites applied.
- `.claude/agents/worker-close-checker.md` D4b rewrites applied.
- `.claude/agents/worker-prelaunch-checker.md` D4b rewrites applied.
- `.claude/agents/specs/WORKER-AGENT-SPEC.md` D4b rewrites applied.
- `.claude/agents/specs/KICKOFF-DRAFTER-SPEC.md` D4b rewrites applied.
- `.claude/agents/specs/KICKOFF-CHECKER-SPEC.md` D4b rewrites applied.
- `.claude/agents/specs/WORKER-PRELAUNCH-CHECKER-SPEC.md` D4b rewrites applied.
- `.claude/agents/specs/WORKER-CLOSE-CHECKER-SPEC.md` D4b rewrites applied.
- `.claude/commands/corral-orchestrator.md` D4b rewrites applied.
- `README.md` D5 rewrites applied: `./STATUS.md`, `./decisions/ADR-NNN`, `./docs/architecture/OVERVIEW.md` all repointed; repository layout table updated.
- `docs/README.md` updated: OVERVIEW.md removed from "This tree", new "AI-infrastructure workspace (project-manager)" section added, "Elsewhere in the repo" updated.
- No placeholder directories created (`app/`, `templates/department/`, `dashboard/`).
- Historical handoff artifacts in `.claude/artifacts/handoffs/` left untouched (D9).
- Task files not edited (Orchestrator-only rule).

## Decisions made

All nine decisions were pre-resolved in the kickoff. No new decisions made during execution:

- D1: `git mv` used for all moves (history preserved).
- D2: No new `workspace:` frontmatter field added to moved files.
- D3: Thin root CLAUDE.md split executed (truly-global rules at root; AI-infra operating specifics in PM CLAUDE.md).
- D4(a): Inside moved workspace, root-pointing refs rewritten to bare paths (no `./` prefix).
- D4(b): Root-staying files rewrite refs to moved content as `./ai-infrastructure/project-manager/...`.
- D5: README.md received D4(b) treatment (moved content) plus layout table update.
- D6: `docs/README.md` updated without relocating it.
- D7: `ai-infrastructure/project-manager/README.md` workspace charter authored (new file).
- D8: Coordinator write authority documented in PM CLAUDE.md.
- D9: Historical handoff artifacts out of scope.

## Surprises

- The empty `docs/architecture/` directory persisted after `git mv docs/architecture/OVERVIEW.md`; git does not track empty directories so this is expected and harmless. No action taken.
- OVERVIEW.md's `../../STATUS.md` relative references automatically resolve correctly from the new location (`ai-infrastructure/project-manager/docs/architecture/`), so no rewrite was needed inside that file.
- STATUS.md's `recent_updates` historical narrative entries contained old-style paths (e.g. `./.claude/agents/worker-agent.md` in a description of a past action). These were left as-is: they are historical narrative, not navigable links. Only navigable references in the `Current phase` and `Next step` prose sections received D4(a) bare-path treatment.
- CLAUDE.md split-routing for CLAUDE.md self-references in role docs required per-rule routing: rules that moved to PM CLAUDE.md pointed there; rules that stayed at root CLAUDE.md pointed to root. No ambiguous cases arose.

## Follow-ups

- COR-T-013: create-department recipe (`templates/department/` baseline + `/create-department` command). Not started; queued.
- COR-T-014: project-manager dashboard (Python ETL over the shared task pool, compose-integrated). Not started; queued.
- COR-T-008: label taxonomy, ADR-018 resolution. Not started; queued.
- COR-T-009: native epics, ADR-025 resolution. Not started; queued.
- COR-T-010: per-agent MCP identity, ADR-026 resolution. Not started; queued.
- A final smoke-read of every moved file's internal cross-references would confirm no bare `.gitignore` or `.env.example` path ambiguity introduced by the two-domain convention. Low priority; no blocking issue observed.

## Files touched

Moved via git mv (55 renames):
- `/home/adam/src/corral/CLAUDE.md` (root - replaced with thin version) and `/home/adam/src/corral/ai-infrastructure/project-manager/CLAUDE.md` (destination, rewritten)
- `/home/adam/src/corral/ai-infrastructure/project-manager/STATUS.md`
- `/home/adam/src/corral/ai-infrastructure/project-manager/OBSERVATIONS.md`
- `/home/adam/src/corral/ai-infrastructure/project-manager/decisions/` (30 ADRs + README)
- `/home/adam/src/corral/ai-infrastructure/project-manager/tasks/` (entire tree)
- `/home/adam/src/corral/ai-infrastructure/project-manager/docs/architecture/OVERVIEW.md`

New files authored:
- `/home/adam/src/corral/ai-infrastructure/project-manager/README.md`
- `/home/adam/src/corral/.claude/artifacts/handoffs/COR-T-012-KICKOFF-REPORT.md` (this file)

Root-staying files modified (D4b / D5 path sweeps):
- `/home/adam/src/corral/README.md`
- `/home/adam/src/corral/docs/README.md`
- `/home/adam/src/corral/docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md`
- `/home/adam/src/corral/docs/ai-orchestration/roles/WORKER-ROLE.md`
- `/home/adam/src/corral/.claude/commands/corral-orchestrator.md`
- `/home/adam/src/corral/.claude/agents/worker-agent.md`
- `/home/adam/src/corral/.claude/agents/kickoff-drafter.md`
- `/home/adam/src/corral/.claude/agents/kickoff-checker.md`
- `/home/adam/src/corral/.claude/agents/worker-close-checker.md`
- `/home/adam/src/corral/.claude/agents/worker-prelaunch-checker.md`
- `/home/adam/src/corral/.claude/agents/specs/WORKER-AGENT-SPEC.md`
- `/home/adam/src/corral/.claude/agents/specs/KICKOFF-DRAFTER-SPEC.md`
- `/home/adam/src/corral/.claude/agents/specs/KICKOFF-CHECKER-SPEC.md`
- `/home/adam/src/corral/.claude/agents/specs/WORKER-PRELAUNCH-CHECKER-SPEC.md`
- `/home/adam/src/corral/.claude/agents/specs/WORKER-CLOSE-CHECKER-SPEC.md`

Moved files modified (D4a bare-path sweep in addition to the move itself):
- `/home/adam/src/corral/ai-infrastructure/project-manager/STATUS.md` (also STATUS hygiene)
- `/home/adam/src/corral/ai-infrastructure/project-manager/OBSERVATIONS.md`
- `/home/adam/src/corral/ai-infrastructure/project-manager/decisions/ADR-023-dispatch-loop-day-zero.md`
- `/home/adam/src/corral/ai-infrastructure/project-manager/decisions/ADR-024-git-tracked-handoff-artifacts.md`

## Build / verification status

- `git status` confirmed 55 rename records (R prefix); working tree clean after all edits.
- Repo root confirmed to contain only: `ai-infrastructure/`, `CLAUDE.md`, `docs/`, `README.md` (and `.claude/`, `.git/`, `.gitignore`, `.env.example`).
- `ai-infrastructure/project-manager/` confirmed to contain: `CLAUDE.md`, `decisions/`, `docs/`, `OBSERVATIONS.md`, `README.md`, `STATUS.md`, `tasks/`.
- Key existence checks passed: ADR-028, STATUS.md, COR-T-012 task file, WORKER-ROLE.md, worker-agent.md, OVERVIEW.md all found at expected new paths.
- Historical handoff artifacts confirmed unchanged (COR-T-002 through COR-T-012-KICKOFF.md).
- No placeholder directories created (confirmed no `app/`, `templates/department/`, `dashboard/` in tree).
- CLAUDE.md split verified: Agent Discipline authoritative copy in root CLAUDE.md only; PM CLAUDE.md references it without duplicating the section body.
- Final sweep: no remaining unrewritten `./decisions/`, `./STATUS.md`, `./OBSERVATIONS.md`, `./tasks/`, or `./docs/architecture` references in root-staying files.
- Em-dash check: no em dashes (U+2014/U+2013) found in any new or modified file.
- No subagents dispatched.
- No out-of-scope files edited.
