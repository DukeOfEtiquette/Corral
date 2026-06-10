## Deliverables completed

All seven deliverables from the kickoff are complete, built to ADR-030:

1. `ai-infrastructure/project-manager/templates/department/CLAUDE.md` - department operating rules and workspace routing template. References global root `CLAUDE.md`, coordinator write authority (ADR-027), shared role docs by reference (ADR-029), path conventions, MCP seam and run policy. "Operated by" section names the `/{{DEPT_SLUG}}-orchestrator` command, the universal `worker-agent` (ADR-028), and the universal checker fleet (ADR-023). States no own `tasks/` and reserves the department-scoped checker slot.

2. `ai-infrastructure/project-manager/templates/department/README.md` - department charter template. Contains the ADR-021 scope line (`{{DEPT_SCOPE}}`), boundary statement, coordinator pointer, and "Operated by" note.

3. `ai-infrastructure/project-manager/templates/department/STATUS.md` - department STATUS template. Frontmatter with `schema_version`, `department`, `last_updated`, `recent_updates`. Narrative section mirrors the coordinator STATUS shape.

4. `ai-infrastructure/project-manager/templates/department/OBSERVATIONS.md` - append-only pattern log template. Uses `{{DEPT_OBS_PREFIX}}-NN` IDs in place of `COR-NN`. Mirrors coordinator OBSERVATIONS conventions.

5. `ai-infrastructure/project-manager/templates/department/decisions/README.md` - department decisions stub. Points at the coordinator's `decisions/README.md` for the ADR body convention. Leaves department-local numbering to the department's first ADR. Exists so git tracks the otherwise-empty `decisions/` directory.

6. `ai-infrastructure/project-manager/templates/department/orchestrator-command.md` - per-department orchestrator command template. Mirrors the five-phase structure of `.claude/commands/corral-orchestrator.md` (adopt role, load context, survey state, report findings, wait for direction), scoped to the department and tokenized. Role name is "`{{DEPT_NAME}}` Orchestrator". Loads the department `CLAUDE.md` and the `dept:{{DEPT_SLUG}}`-scoped slice of the shared task pool. Dispatches the universal `worker-agent` (ADR-028). References the universal checker fleet (ADR-023). No `/{{DEPT_SLUG}}-worker` command anywhere.

7. `.claude/commands/create-department.md` - the recipe command. Inputs: `<slug>`, `<Display Name>`, `<OBS-PREFIX>`. States and enforces the blessed-ADR-021-menu precondition (stops rather than silently creating an off-menu department). Drives the orchestrator through the dispatched-worker flow: resolve arguments and `{{DEPT_SCOPE}}` from ADR-021, draft and check a kickoff, run prelaunch checker, dispatch `worker-agent`, run close checker, verify-against-disk, commit gate. Includes the `dept:<slug>` label reservation note (markdown-era naming, ADR-018 deferred). Token substitution table with all five `{{UPPER_SNAKE}}` tokens. Explicit "what this command does NOT create" section (no worker command, no role-doc copies, no tasks/ directory, no department-scoped checker).

`ai-infrastructure/project-manager/STATUS.md` - universal hygiene applied (bumped `last_updated` to 2026-06-10, prepended a `recent_updates` entry) and task-specific delta applied (rewrote "Next step" section per kickoff).

## Decisions made

All decisions were pre-pinned by the Orchestrator. No new decisions were made during execution. Followed ADR-030 as the authoritative spec throughout.

One minor correction applied during execution: the `CLAUDE.md` template initially had a single-brace `/{DEPT_SLUG}-worker` in the "Operated by" paragraph (a transcription slip). Corrected to `{{DEPT_SLUG}}` (double braces) for token-convention consistency per ADR-030 item 2.

## Surprises

- The `ai-infrastructure/project-manager/templates/` directory did not yet exist (as expected; the kickoff confirmed this is the first deliverable to create it). Created via `mkdir -p` along with the `decisions/` subdirectory.
- The `CLAUDE.md` template's "Operated by" section had a single-brace slip (`/{DEPT_SLUG}-worker`) caught on token verification. Corrected before finalizing.

## Follow-ups

- The `ORCHESTRATOR-ROLE.md` one-Orchestrator line ("Corral is a single project, so there is one Orchestrator") needs updating when the first real `/create-department` run stamps the first department. This is the ADR-030 Consequences note: a first-department-creation follow-up, NOT part of COR-T-013. Triage to Orchestrator: queue as a follow-up task or note to pick up when the first department is created. COR-T candidate.
- COR-T-014 (project-manager dashboard) is the sole remaining ADR-027 follow-on, now that COR-T-013 is complete. Triage to Orchestrator: pick up when ready.

## Files touched

- `ai-infrastructure/project-manager/templates/department/CLAUDE.md` (new)
- `ai-infrastructure/project-manager/templates/department/README.md` (new)
- `ai-infrastructure/project-manager/templates/department/STATUS.md` (new)
- `ai-infrastructure/project-manager/templates/department/OBSERVATIONS.md` (new)
- `ai-infrastructure/project-manager/templates/department/decisions/README.md` (new)
- `ai-infrastructure/project-manager/templates/department/orchestrator-command.md` (new)
- `.claude/commands/create-department.md` (new)
- `ai-infrastructure/project-manager/STATUS.md` (bumped `last_updated`, prepended `recent_updates` entry, rewrote "Next step" section)
- `.claude/artifacts/handoffs/COR-T-013-KICKOFF-REPORT.md` (this report)

## Build / verification status

- All seven deliverable files verified on disk via `find` (all present, correct paths).
- All five `{{UPPER_SNAKE}}` tokens (`{{DEPT_SLUG}}`, `{{DEPT_NAME}}`, `{{DEPT_OBS_PREFIX}}`, `{{DEPT_SCOPE}}`, `{{DATE}}`) verified present in the template files via `grep -rl`.
- No em dashes found in any authored file (verified via `grep`).
- No literal department values hard-coded; no live commands under `.claude/commands/` that shouldn't be (the `orchestrator-command.md` lives only in the template directory).
- No actual department workspace created under `ai-infrastructure/<dept>/` (confirmed: none exists).
- No ADRs or role docs edited (read-only per the kickoff's hard rules).
- STATUS hygiene applied once on COMPLETED: `last_updated` bumped to 2026-06-10, `recent_updates` entry prepended, "Next step" rewritten per kickoff STATUS deltas.
- No compose/runtime verification applicable (this is template and command authoring, no runnable code).
