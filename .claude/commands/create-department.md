---
description: Stamp out a new department workspace from the template baseline and wire its orchestrator command
---

# /create-department

## Inputs

This command takes four arguments:

- `<slug>`: the department slug in kebab-case (e.g. `test-design`). Must be a blessed entry in the ADR-021 menu.
- `<Display Name>`: the human-readable department name (e.g. `Test Design`).
- `<OBS-PREFIX>`: the uppercase observation ID prefix for the department (e.g. `TST`). Operator-supplied; not auto-derived from the slug.
- `<TASK-PREFIX>`: the uppercase task ID prefix for the department (e.g. `TST`). Operator-supplied; not auto-derived from the slug. Independent of `<OBS-PREFIX>`; they may be the same value (e.g. both `DB` for the `database` department) or different.

Example invocation: `/create-department test-design "Test Design" TST TST`

## Precondition: blessed ADR-021 menu entry

**Stop and surface to the user before proceeding if the slug is not a blessed entry in the ADR-021 department menu.**

The blessed entries are defined in `ai-infrastructure/project-manager/decisions/ADR-021-candidate-departments.md`. Read that ADR before resolving `{{DEPT_SCOPE}}`. Creating an off-menu department requires extending the ADR-021 menu first (a separate orchestrator-direct ADR edit), not silently inventing an off-menu workspace. If the slug is not on the menu, surface this fact and stop; do not draft a kickoff.

## What this command creates

When invoked with a valid blessed-menu slug, this command drives the orchestrator through the dispatched-worker flow to produce:

1. A stamped department workspace at `ai-infrastructure/<slug>/` containing all template files with tokens substituted:
   - `ai-infrastructure/<slug>/CLAUDE.md`
   - `ai-infrastructure/<slug>/README.md`
   - `ai-infrastructure/<slug>/STATUS.md`
   - `ai-infrastructure/<slug>/OBSERVATIONS.md`
   - `ai-infrastructure/<slug>/decisions/README.md`
   - `ai-infrastructure/<slug>/tasks/.next-task-id` (seeded to `1`)
   - `ai-infrastructure/<slug>/tasks/backlog/.gitkeep`
   - `ai-infrastructure/<slug>/tasks/in-progress/.gitkeep`
   - `ai-infrastructure/<slug>/tasks/blocked/.gitkeep`
   - `ai-infrastructure/<slug>/tasks/done/.gitkeep`
2. A stamped orchestrator command at `.claude/commands/<slug>-orchestrator.md`.

The template source is `ai-infrastructure/project-manager/templates/department/`. The scaffold contract is `ai-infrastructure/project-manager/decisions/ADR-030-department-scaffold-contract-create-department-recipe.md`.

## Token substitution

Substitute these tokens throughout all template files:

| Token | Value |
|---|---|
| `{{DEPT_SLUG}}` | The `<slug>` argument |
| `{{DEPT_NAME}}` | The `<Display Name>` argument |
| `{{DEPT_OBS_PREFIX}}` | The `<OBS-PREFIX>` argument |
| `{{DEPT_TASK_PREFIX}}` | The `<TASK-PREFIX>` argument |
| `{{DEPT_SCOPE}}` | The "Would own" line for this slug from the ADR-021 menu |
| `{{DATE}}` | Today's date in `YYYY-MM-DD` format |


## Execution flow

This command drives the orchestrator through the standard dispatched-worker flow. Do not stamp the workspace directly in-session; route through the worker per ADR-028 (deliverables are worker work, not orchestrator-direct work).

**Step 1: Resolve arguments and scope.**

Read `ai-infrastructure/project-manager/decisions/ADR-021-candidate-departments.md` to:
- Confirm the slug is a blessed menu entry (stop if not, per the precondition above).
- Extract the "Would own" scope line for `{{DEPT_SCOPE}}`.

**Step 2: Draft and check the kickoff.**

Resolve any residual anticipated decisions with the user. Then run the drafter+checker dispatch loop per `ORCHESTRATOR-ROLE.md` (section "Drafter+checker dispatch loop") to produce a kickoff at `.claude/artifacts/handoffs/<SLUG>-DEPT-CREATE-KICKOFF.md`. The kickoff's deliverable is the stamped workspace and the stamped orchestrator command, with all tokens substituted. Reference the template files and the scaffold contract (ADR-030) in the kickoff's explicit_reads.

**Step 3: Run the prelaunch checker.**

Dispatch `worker-prelaunch-checker` via the Task tool with the kickoff path. On FAIL, route back to step 2.

**Step 4: Dispatch the worker-agent.**

Dispatch the universal `worker-agent` (Sonnet, foreground) via the Task tool with the explicit-context-pass-down package. The worker stamps all template files with tokens substituted and writes the report dual-channel.

Interactive back-and-forth at creation time is expected and acceptable: escalation round-trips (if the worker surfaces an ambiguity) or Plan Mode for a genuinely unanticipated decision. Re-dispatch with the escalation answer folded in per the standard dispatched-worker escalation protocol (ADR-028, ceiling: 2 round-trips before mandatory user-surface).

**Step 5: Run the close checker.**

Dispatch `worker-close-checker` via the Task tool with the report path. On FAIL, surface to the user with the three-exit menu (accept-with-rationale / manually-edit / re-dispatch a corrective worker).

**Step 6: Verify against disk.**

Independently confirm that all seven target files exist on disk with tokens substituted (no literal `{{DEPT_SLUG}}` or other token strings remaining). Confirm `ai-infrastructure/project-manager/STATUS.md` appears in the report's "Files touched" (the worker applies STATUS hygiene once).

**Step 7: Apply STATUS hygiene (orchestrator-direct, after worker COMPLETED).**

Update `ai-infrastructure/project-manager/STATUS.md`:
- Bump `last_updated` to today's date.
- Prepend a `recent_updates` entry noting the new department was created.
- Update the "Next step" section to reflect the new department's existence.

Note: the worker applies its own STATUS hygiene to `ai-infrastructure/project-manager/STATUS.md` as part of the COMPLETED return (universal hygiene plus any kickoff-named deltas). Confirm this happened; do not double-stamp.

**Step 8: Commit gate (user-gated).**

Per `ORCHESTRATOR-ROLE.md` (section "Task lifecycle", Resolve step): draft the commit message, get user approval, commit the attributable changes (the stamped department workspace, the stamped orchestrator command, the kickoff/report pair, and the STATUS update), and record the short hash(es).

## dept:<slug> label reservation

Creating a department using a blessed ADR-021 menu slug is the label reservation in the markdown era. The `dept:<slug>` label name is established; it will be applied to the department's tasks at the dogfood import (ADR-008), derived from the department's own `tasks/` tree, at which point ADR-001's single-pool/per-label-board model takes over inside the app. Tasks in the department tree do NOT carry a hand-applied `dept:<slug>` label in the markdown era. There is no label registry to mutate at this time; the label becomes a real record at the dogfood milestone. Label governance (enforcement, color/metadata) is owned by ADR-018 (pending, COR-T-008).

## What this command does NOT create

- No `/<slug>-worker` command. Department deliverable work runs through the universal `worker-agent` (ADR-028). The single universal worker execution path is shared across all departments.
- No per-department role-doc copies. The department's orchestrator command adopts `docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md` by reference (ADR-029). The worker uses `docs/ai-orchestration/roles/WORKER-ROLE.md` by reference. No copies.
- No department-scoped checker. The optional department-scoped checker slot is reserved (see the department `CLAUDE.md`); none is created by the recipe.

## References

- `ai-infrastructure/project-manager/decisions/ADR-030-department-scaffold-contract-create-department-recipe.md`: the scaffold contract this command builds to.
- `ai-infrastructure/project-manager/decisions/ADR-021-candidate-departments.md`: the blessed menu and scope lines.
- `ai-infrastructure/project-manager/decisions/ADR-028-worker-as-dispatched-subagent.md`: single universal worker; no per-department worker command.
- `ai-infrastructure/project-manager/decisions/ADR-029-shared-role-docs-stay-at-repo-root.md`: shared role docs by reference; no per-department copies.
- `ai-infrastructure/project-manager/decisions/ADR-027-ai-infrastructure-workspace-structure.md`: workspace tree; Fork B (shared task pool); Fork D (department scaffold).
- `ai-infrastructure/project-manager/decisions/ADR-023-dispatch-loop-day-zero.md`: universal checker fleet; department-scoped checker slot.
- `ai-infrastructure/project-manager/decisions/ADR-018-department-label-taxonomy.md`: pending; label governance deferred here.
- `ai-infrastructure/project-manager/templates/department/`: the template source files this command stamps from.
