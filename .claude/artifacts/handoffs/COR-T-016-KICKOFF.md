# Rename the coordinator orchestrator command to /project-manager-orchestrator

## Target

This is **AI-infrastructure** work (domain 2 per `./ai-infrastructure/project-manager/decisions/ADR-005-two-domains-ai-first.md`), task `COR-T-016`. You are renaming the coordinator Orchestrator's instantiation command from `/corral-orchestrator` to `/project-manager-orchestrator` and its user-facing role display name from "Corral Orchestrator" to "Project Manager Orchestrator", so the coordinator command matches the `/<slug>-orchestrator` convention every department command already follows (ADR-021, ADR-030; the coordinator workspace slug is `project-manager`). This is a naming and consistency fix, not a behaviour change. The artifacts in scope are the command file, the two shared role docs that name the command, the universal `worker-agent` definition, and the project-manager STATUS narrative.

Path-convention note (per `./ai-infrastructure/project-manager/CLAUDE.md`, "Path conventions"): references to the shared tree (`.claude/`, `docs/ai-orchestration/`) use a BARE path with no `./` prefix; references to the coordinator workspace (`./ai-infrastructure/project-manager/...`) keep the `./` prefix. The paths in this kickoff already follow that split; preserve each file's own existing path style when editing.

## Decisions resolved by the Orchestrator

- **Rename target is `/project-manager-orchestrator`.** It matches the `/<slug>-orchestrator` convention established for departments (ADR-030's `orchestrator-command.md` template; ADR-021's coordinator-plus-departments model), where the coordinator workspace slug is `project-manager`. `/corral-orchestrator` is the lone command named after the repo rather than its workspace, which misleadingly implies it is the project-manager.
- **A single `git mv` renames both the slash command and the skill.** The skill name derives from the command filename, so moving `.claude/commands/corral-orchestrator.md` to `.claude/commands/project-manager-orchestrator.md` renames the slash command AND the registered skill in one operation. There is no separate skill-registration file to edit.
- **The role display name becomes "Project Manager Orchestrator" only where the coordinator names itself.** Those locations are: the command file (its `description:` frontmatter, its `# Corral Orchestrator` H1 heading, and its Phase 1 sentence `Your role name for the user is "Corral Orchestrator."`), and `ORCHESTRATOR-ROLE.md`'s Instantiation section (the line `Role name for the user: "Corral Orchestrator".`).
- **`worker-agent.md`'s two "Corral Orchestrator" mentions are GENERALISED to "the Orchestrator", not renamed to "Project Manager Orchestrator".** The `worker-agent` is the single universal worker dispatched by EVERY orchestrator (the project-manager coordinator and each department orchestrator, per ADR-028 and ADR-029); naming one specific orchestrator there would be inaccurate. Generalising preserves the agent's universal role.
- **The ADRs (ADR-023, ADR-024, ADR-028, ADR-030) are NOT edited.** Their `/corral-orchestrator` references are append-only historical decision records. Precedent: when `/corral-worker` was retired (COR-T-015 / ADR-028), its references were deliberately left intact across ADR-023/024/028 rather than scrubbed. Do the same here.
- **Settled history is NOT edited.** The `recent_updates` dated log lines in STATUS.md, the COR-T-012 and COR-T-013 handoff kickoff/report pairs under `.claude/artifacts/handoffs/`, and the done `COR-T-015` task file all keep their `/corral-orchestrator` references as point-in-time records.
- **No new ADR is created.** This is alignment with the already-accepted `/<slug>-orchestrator` convention, not a new binding decision. The change is recorded in STATUS and the task activity log only (the task activity log is the Orchestrator's job; see STATUS deltas below for your part).

## Deliverables

1. **Rename the command file.** Run `git mv .claude/commands/corral-orchestrator.md .claude/commands/project-manager-orchestrator.md`. Inside the renamed file, change exactly three lines to "Project Manager Orchestrator":
   - the `description:` frontmatter value (currently `Adopt the Corral Orchestrator role, survey project state, and wait for direction`),
   - the `# Corral Orchestrator` H1 heading,
   - the Phase 1 role-name sentence `Your role name for the user is "Corral Orchestrator."`.

   Leave every other line byte-for-byte unchanged: all phase content, every `./ai-infrastructure/...` and `./docs/...` and `.claude/...` path, every ADR reference, and the `worker-agent` references. The filename change is the only structural edit; the three display-name lines are the only content edits.

2. **Update `docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md`.** Change every live `/corral-orchestrator` command reference to `/project-manager-orchestrator`:
   - the opening coordinator paragraph near the top (`instantiated by the `/corral-orchestrator` command`),
   - the one-line note (`The role is instantiated via the `/corral-orchestrator` slash command`),
   - the Instantiation section's path `./.claude/commands/corral-orchestrator.md` becomes `./.claude/commands/project-manager-orchestrator.md`.

   Also in the Instantiation section, change `Role name for the user: "Corral Orchestrator".` to `Role name for the user: "Project Manager Orchestrator".`.

3. **Update `docs/ai-orchestration/roles/WORKER-ROLE.md`.** Change the single `/corral-orchestrator` reference (the sentence beginning `The Worker does not invoke `/corral-orchestrator` to "load context"...`) to `/project-manager-orchestrator`. This is the only edit in this file.

4. **Generalise `.claude/agents/worker-agent.md`.** Change the two "Corral Orchestrator" mentions to "the Orchestrator", preserving surrounding sentence grammar:
   - in the `description:` frontmatter (`Use this agent when the Corral Orchestrator dispatches a worker subagent...` and the in-`description` example line `Context: The Corral Orchestrator has drafted and checked a kickoff...`),
   - in the system-prompt body sentence `You are the Worker Agent. The Corral Orchestrator dispatches you...` becomes `You are the Worker Agent. The Orchestrator dispatches you...`.

   Do not introduce "Project Manager Orchestrator" anywhere in this file; the generic "the Orchestrator" is the resolved phrasing. Match the existing capitalisation pattern ("The Orchestrator" at sentence start, "the Orchestrator" mid-sentence).

5. **Apply the STATUS narrative delta plus universal hygiene in `ai-infrastructure/project-manager/STATUS.md`.** See the STATUS deltas section below for the exact task-specific edit. The universal hygiene (bump `last_updated`, prepend a `recent_updates` entry) is your standard duty per `docs/ai-orchestration/roles/WORKER-ROLE.md`, section "Wrap-up STATUS hygiene".

**Acceptance gate** (single gate; confirm it in the closing report's "Build / verification status" section):

- (a) `.claude/commands/project-manager-orchestrator.md` exists and `.claude/commands/corral-orchestrator.md` no longer exists.
- (b) The five in-scope files contain zero occurrences of `corral-orchestrator` and zero occurrences of the literal string "Corral Orchestrator". Scope this grep to the five in-scope files only, not the whole repo (the out-of-scope ADRs and settled-history files legitimately still contain those strings).
- (c) The four out-of-scope ADRs and the settled-history files STILL contain their `/corral-orchestrator` references (untouched). The `recent_updates` dated log lines inside STATUS.md still contain their `/corral-orchestrator` references; only the Current-phase narrative line changed.
- (d) No em dashes were introduced in any edited file (per `./CLAUDE.md`).

## Files in scope

- `.claude/commands/corral-orchestrator.md` (the `git mv` rename target; becomes `.claude/commands/project-manager-orchestrator.md`)
- `docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md`
- `docs/ai-orchestration/roles/WORKER-ROLE.md`
- `.claude/agents/worker-agent.md`
- `ai-infrastructure/project-manager/STATUS.md`

## Files out of scope

Do NOT modify these; they are verified correct and their `/corral-orchestrator` references are deliberately retained:

- `ai-infrastructure/project-manager/decisions/ADR-023-dispatch-loop-day-zero.md` (append-only; keep the historical `/corral-orchestrator` ref)
- `ai-infrastructure/project-manager/decisions/ADR-024-git-tracked-handoff-artifacts.md` (append-only)
- `ai-infrastructure/project-manager/decisions/ADR-028-worker-as-dispatched-subagent.md` (append-only)
- `ai-infrastructure/project-manager/decisions/ADR-030-department-scaffold-contract-create-department-recipe.md` (append-only)
- The `recent_updates` dated log lines inside `ai-infrastructure/project-manager/STATUS.md` (only the Current-phase NARRATIVE line changes; do not rewrite dated history)
- `.claude/artifacts/handoffs/COR-T-012-KICKOFF-REPORT.md`, `.claude/artifacts/handoffs/COR-T-013-KICKOFF.md`, `.claude/artifacts/handoffs/COR-T-013-KICKOFF-REPORT.md` (settled handoff history)
- `ai-infrastructure/project-manager/tasks/done/COR-T-015-port-dispatched-worker-agent.md` (settled history)
- `ai-infrastructure/project-manager/templates/department/orchestrator-command.md` and `.claude/commands/create-department.md` (use `{{DEPT_SLUG}}-orchestrator` tokens / contain no `corral-orchestrator` reference; nothing to change)

## References

- `./ai-infrastructure/project-manager/tasks/in-progress/COR-T-016-rename-orchestrator-command-to-project-manager.md` (the task file; carries the full resolved-decisions list and the live edit set)
- `.claude/commands/corral-orchestrator.md` (the command file to rename and edit; deliverable 1)
- `docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md` (the shared coordinator role doc; deliverable 2)
- `docs/ai-orchestration/roles/WORKER-ROLE.md` (the shared worker role doc; deliverable 3, and the source of the universal report shape and STATUS-hygiene rules you follow)
- `.claude/agents/worker-agent.md` (the universal worker definition; deliverable 4)
- `ai-infrastructure/project-manager/STATUS.md` (the coordinator status; deliverable 5)

## Related tasks and ADRs

- ADR-021 (candidate departments): establishes the project-manager as the coordinator workspace alongside lazily-created departments; grounds why the coordinator's slug is `project-manager`.
- ADR-030 (department scaffold contract / create-department recipe): defines the `/<slug>-orchestrator` command convention this rename aligns the coordinator to.
- ADR-029 (shared role docs stay at repo root): why `ORCHESTRATOR-ROLE.md` and `WORKER-ROLE.md` are shared docs that name the command.
- ADR-028 (worker as dispatched subagent): establishes the `worker-agent` as the single universal worker dispatched by every orchestrator; basis for generalising `worker-agent.md` rather than pinning it to the project-manager.
- COR-T-013 (built the create-department recipe / ADR-030): sibling task that created the `/<slug>-orchestrator` convention now being matched.
- COR-T-015 (retired /corral-worker): precedent for leaving historical command references intact in append-only ADRs.

## STATUS deltas

- In the "Current phase" narrative section of `ai-infrastructure/project-manager/STATUS.md` (the `**Phase 1: AI infrastructure.**` paragraph), change the phrase ``the `/corral-orchestrator` command`` to ``the `/project-manager-orchestrator` command``. This is the only task-specific narrative edit. Do NOT touch the `/corral-orchestrator` references in the `recent_updates` dated log lines above it; those are settled history.
- Universal hygiene (bump `last_updated` in the frontmatter to today's date, prepend a `recent_updates` entry summarising the rename) is your standard duty per `docs/ai-orchestration/roles/WORKER-ROLE.md`, section "Wrap-up STATUS hygiene", and is not itemised further here.

## Hard rules

- **Surgical edits only.** This task changes a command name and a display name; it does not rewrite content. For the command file specifically, the three display-name lines and the filename are the only changes; every other byte stays. Do not "improve", reflow, or reword any surrounding prose in any in-scope file.
- **Scope the verification grep to the five in-scope files.** A repo-wide grep for `corral-orchestrator` will (correctly) still return hits in the out-of-scope ADRs and settled-history files; that is expected and is part of acceptance criterion (c), not a failure.
- **"Project Manager Orchestrator" goes only where the coordinator names itself** (deliverables 1 and 2). The `worker-agent.md` mentions are generalised to "the Orchestrator" (deliverable 4), not renamed to the coordinator's display name.

## Worker pointer

You are the dispatched `worker-agent` (ADR-028). Universal worker conventions, the six-section report shape, the dual-channel report-to-file rule, and the wrap-up STATUS hygiene live in `docs/ai-orchestration/roles/WORKER-ROLE.md`. Write your closing report to the path derived per that doc's "Report shape" section (the kickoff's directory and basename with `-REPORT.md` appended).
