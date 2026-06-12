# ADR-032 implementation cascade: rename worker-agent to executor; docs-curation to docs

## Target

This is AI-infrastructure work (domain 2 per ADR-005), task COR-T-036. It is the mechanical implementation cascade for ADR-032 (accepted), which renames the general execution agent `worker-agent` to `executor`, renames its role doc and spec, renames the `docs-curation` department slug to `docs`, and introduces the term "cross-department agent" in place of the informal "universal agent" where it describes these tier-2 agents. The artifacts in scope are the live agent definitions, role docs, specs, orchestrator commands, department CLAUDE files, templates, the docs navigation index, and the dashboard ETL. ADR-032 has already pinned every decision; you carry those decisions into the live files. This is the structural analog of COR-T-025 (the ADR-031 cascade): one task, a bounded repo-wide rename and term sweep, no re-deliberation.

## Decisions resolved by the Orchestrator

- **You implement ADR-032; you do not re-decide it.** ADR-032 (accepted) is the binding record. Do not edit ADR-032, and do not reopen any choice it pins (the executor name, the docs slug, the term, the checker-names-stay consequence, the bounded sweep). Carry the decisions into the live files exactly as ADR-032 states them.
- **Three file renames via `git mv`, each followed by content edits.** Use `git mv` so history follows the rename:
  - `git mv .claude/agents/worker-agent.md .claude/agents/executor.md`
  - `git mv docs/ai-orchestration/roles/WORKER-ROLE.md docs/ai-orchestration/roles/EXECUTOR-ROLE.md`
  - `git mv .claude/agents/specs/WORKER-AGENT-SPEC.md .claude/agents/specs/EXECUTOR-AGENT-SPEC.md`

  After each rename, edit the renamed file's content: frontmatter `name: executor` (in the agent definition), titles ("Worker Role" to "Executor Role", "Worker Agent" to "Executor Agent"), every self-reference, and every bootstrap-read pointer that names an old filename so it names the new filename.
- **Three exact-string global replacements, safe across every in-scope file.** Apply these three exact-string replacements wherever they appear in the in-scope files:
  - `worker-agent` to `executor`
  - `WORKER-ROLE` to `EXECUTOR-ROLE` (this covers `WORKER-ROLE.md`)
  - `WORKER-AGENT-SPEC` to `EXECUTOR-AGENT-SPEC`

  These three strings are safe to replace globally because none is a substring of a checker name: the checker agents are `worker-prelaunch-checker` and `worker-close-checker`, which contain none of `worker-agent`, `WORKER-ROLE`, or `WORKER-AGENT-SPEC`.
- **The checker agents are NOT renamed.** Per ADR-032 (Consequences, "The 'worker-' prefixed checkers keep their names for now"), the agents `worker-prelaunch-checker` and `worker-close-checker`, their filenames, and their spec filenames (`WORKER-PRELAUNCH-CHECKER-SPEC.md`, `WORKER-CLOSE-CHECKER-SPEC.md`) keep their names. Inside those four files you repoint references to the executor agent (`worker-agent` to `executor`) and the executor role (`WORKER-ROLE.md` to `EXECUTOR-ROLE.md`), and you change prose that names "the Worker" (meaning the executor) to "the Executor"; but you do NOT rename the checker agents, their files, or their spec files, and you do NOT change the string `worker-prelaunch-checker` or `worker-close-checker` anywhere.
- **Prose role-concept rename, by judgement.** Beyond the three exact strings, update prose that refers to the general execution agent by role concept: "the Worker" to "the Executor", "Worker role" to "Executor role", "Worker session" to "Executor session", "Worker Agent" to "Executor Agent", where it denotes the renamed agent. In `EXECUTOR-ROLE.md`, state explicitly that "execute" means "carry out the kickoff's deliverables", not strictly code (ADR-032's executor-over-implementer rationale, Alternatives considered). Use judgement: a generic English "worker" not denoting this agent (rare) stays; the role/agent references change.
- **Bounded term sweep: "universal" to "cross-department", only for the agents-as-a-class.** Change "universal" to "cross-department" ONLY where it describes these tier-2 agents (for example "the universal worker-agent", "universal `test-designer`", "four universal subagents/checkers", "universal worker"). Do NOT touch other uses of "universal": "universal conventions", "universal hygiene", "universal kickoff conventions/convention", "universal minimum", "universal rule W1/W2", "universal Worker-close/Worker-acceptance rule". When unsure whether a given "universal" describes the agents-as-a-class versus a convention or rule, leave it unchanged. ADR-032 frames this sweep as opportunistic, not exhaustive; the safer default is to leave it.
- **docs-curation to docs is a roster-label change in etl.py only.** In `ai-infrastructure/project-manager/dashboard/etl.py`, rename the `docs-curation` department slug to `docs` wherever the roster or department list defines it. No department workspace exists to rename (lazy creation, ADR-021/ADR-027); this is a roster-label change that flows to the dashboard via data.json. Do not touch `docs-curation` mentions in append-only history (see Files out of scope).
- **Append-only history is firmly out of scope.** Do NOT edit any file under `.claude/artifacts/handoffs/`, any file under `ai-infrastructure/project-manager/tasks/`, `ai-infrastructure/project-manager/OBSERVATIONS.md`, the historical `recent_updates` entries in `STATUS.md`, or any accepted ADR body under `ai-infrastructure/project-manager/decisions/` (the ADR-028 and ADR-021 forward-pointer notes are already in place). These name the agent as it was and must not be rewritten.
- **The agent renames its own definition; that is fine.** This kickoff is executed by the dispatched worker-agent, which will `git mv` and edit its own definition file `.claude/agents/worker-agent.md`. The running session is unaffected by the on-disk rename; future dispatches use `executor`. No special handling is needed.

## Deliverables

- The three `git mv` renames applied, each with its content updated: `worker-agent.md` to `executor.md` (frontmatter `name: executor`, title, self-references, bootstrap-read pointers); `WORKER-ROLE.md` to `EXECUTOR-ROLE.md` (title, self-references, bootstrap pointers, and the role-concept prose including the "execute means carry out the kickoff's deliverables" statement); `WORKER-AGENT-SPEC.md` to `EXECUTOR-AGENT-SPEC.md` (title, self-references, bootstrap pointers).
- Every in-scope file repointed: the three exact-string replacements applied; the checker-internal references updated without renaming the checkers; and the role-concept prose updated where it names the executor.
- The bounded "universal" to "cross-department" term sweep applied within the in-scope files, scoped to agents-as-a-class only.
- `etl.py`: the `docs-curation` department slug renamed to `docs` in the roster or department list definition.
- Result: zero residual live references to `worker-agent`, `WORKER-ROLE`, or `WORKER-AGENT-SPEC` outside the append-only trees, and the checker agent names (`worker-prelaunch-checker`, `worker-close-checker`) left intact. Verify this with a grep over the in-scope tree before you report (record the command and its output in the report's "Build / verification status" section).

## Files in scope

- `.claude/agents/worker-agent.md` (`git mv` to `.claude/agents/executor.md`, then edit)
- `docs/ai-orchestration/roles/WORKER-ROLE.md` (`git mv` to `docs/ai-orchestration/roles/EXECUTOR-ROLE.md`, then edit)
- `.claude/agents/specs/WORKER-AGENT-SPEC.md` (`git mv` to `.claude/agents/specs/EXECUTOR-AGENT-SPEC.md`, then edit)
- `.claude/agents/test-designer.md`
- `.claude/agents/specs/TEST-DESIGNER-AGENT-SPEC.md`
- `docs/ai-orchestration/roles/TEST-DESIGNER-ROLE.md`
- `docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md`
- `.claude/agents/kickoff-drafter.md`
- `.claude/agents/specs/KICKOFF-DRAFTER-SPEC.md`
- `.claude/agents/specs/KICKOFF-CHECKER-SPEC.md`
- `.claude/agents/worker-prelaunch-checker.md` (edit internal refs only; do NOT rename)
- `.claude/agents/worker-close-checker.md` (edit internal refs only; do NOT rename)
- `.claude/agents/specs/WORKER-PRELAUNCH-CHECKER-SPEC.md` (edit internal refs only; do NOT rename)
- `.claude/agents/specs/WORKER-CLOSE-CHECKER-SPEC.md` (edit internal refs only; do NOT rename)
- `.claude/commands/project-manager-orchestrator.md`
- `.claude/commands/backend-api-orchestrator.md`
- `.claude/commands/database-orchestrator.md`
- `.claude/commands/create-department.md`
- `ai-infrastructure/project-manager/CLAUDE.md`
- `ai-infrastructure/backend-api/CLAUDE.md`
- `ai-infrastructure/database/CLAUDE.md`
- `ai-infrastructure/project-manager/README.md`
- `ai-infrastructure/project-manager/templates/department/CLAUDE.md`
- `ai-infrastructure/project-manager/templates/department/orchestrator-command.md`
- `docs/README.md`
- `ai-infrastructure/project-manager/dashboard/etl.py` (docs-curation slug to docs)
- `ai-infrastructure/project-manager/STATUS.md` (universal STATUS hygiene write only; do NOT rewrite historical `recent_updates` entries)

## Files out of scope

- `.claude/artifacts/handoffs/` (all kickoffs and reports; append-only records named at the time, including this kickoff and its report)
- `ai-infrastructure/project-manager/tasks/` (task files; Orchestrator-only and historical)
- `ai-infrastructure/project-manager/OBSERVATIONS.md` (append-only log)
- `ai-infrastructure/project-manager/decisions/` (accepted ADR bodies are append-only; the ADR-028 and ADR-021 forward-pointer notes already carry the renames)
- `.claude/agents/kickoff-checker.md` (no executor/role reference to change; its "universal" uses are "universal kickoff conventions", which stay)

## References

- `ai-infrastructure/project-manager/decisions/ADR-032-cross-department-agent-tier.md`: the binding decision. It pins the tier taxonomy, the executor and docs renames, the term "cross-department agent", the checker-names-stay consequence, and the bounded term sweep. Read its Decision and Consequences sections before editing.

## Related tasks and ADRs

- COR-T-036 (this task): the ADR-032 implementation cascade.
- ADR-032: the decision this task implements (tier taxonomy, executor rename, docs slug rename, term, bounded sweep).
- COR-T-025: the structural precedent, the ADR-031 implementation cascade, a comparable repo-wide rename and sweep done in one task.
- ADR-028: established `worker-agent`; ADR-032 renames it to `executor`. Its forward-pointer note is already added (out of scope to edit).
- ADR-021: established the `docs-curation` menu entry; ADR-032 renames it to `docs`. Its forward-pointer note is already added (out of scope to edit).
- COR-T-035: authored `test-designer` and the close-checker W3; those files (`test-designer.md`, its spec and role, `worker-close-checker.md` and its spec) are in scope for the reference repoint.

## STATUS deltas

No task-specific STATUS deltas; universal hygiene only. Append one `recent_updates` entry in `ai-infrastructure/project-manager/STATUS.md` summarizing the rename cascade (worker-agent to executor across the live fleet, docs-curation to docs in the roster, the bounded term sweep). Do not alter historical `recent_updates` entries and do not change the roadmap or narrative.

## Hard rules

- **`git mv` for the three renames, not delete-and-recreate.** History must follow the file. Do the `git mv` first, then edit the moved file's content in place.
- **Append-only trees are firm boundaries.** No edits under `.claude/artifacts/handoffs/`, `ai-infrastructure/project-manager/tasks/`, `OBSERVATIONS.md`, the historical `recent_updates` block, or any ADR body. If you find a stale `worker-agent` or `WORKER-ROLE` reference inside one of these trees, leave it and note it under "Follow-ups" rather than editing it.
- **Checker names are inviolate.** The strings `worker-prelaunch-checker` and `worker-close-checker` (and their file and spec names) must be unchanged after your edits. A blind global sed of "worker" would break this; replace only the three exact strings named in the decisions, plus the judgement-scoped prose.
- **Bare paths inside the project-manager workspace.** Per `ai-infrastructure/project-manager/CLAUDE.md` ("Path conventions"), references from inside `ai-infrastructure/project-manager/` to the root-staying shared tree use a bare path with no `./` prefix (for example `.claude/agents/executor.md`, `docs/ai-orchestration/roles/EXECUTOR-ROLE.md`). Preserve whichever path style each file already uses; the rename changes the filename segment, not the path-prefix convention.
- **Verification gate.** Before reporting COMPLETED, grep the in-scope tree for residual `worker-agent`, `WORKER-ROLE`, and `WORKER-AGENT-SPEC` and confirm zero live hits outside the append-only trees, and grep for `worker-prelaunch-checker` and `worker-close-checker` to confirm they are still present. Record both greps and their output in "Build / verification status".

## Worker pointer

The worker is the dispatched `worker-agent` (ADR-028); this task renames that agent to `executor`, so you are editing your own definition file as part of the deliverable, which ADR-032 anticipates. Universal worker conventions live in `docs/ai-orchestration/roles/WORKER-ROLE.md`, which you rename to `EXECUTOR-ROLE.md` as part of this task; read it under its current name before you move it, and apply the role-doc conventions (Report shape, Universal conventions) from its content regardless of filename. Write the closing report to the dual-channel path derived per the Report shape section (`<kickoff-dir>/<KICKOFF-BASENAME>-REPORT.md`).
