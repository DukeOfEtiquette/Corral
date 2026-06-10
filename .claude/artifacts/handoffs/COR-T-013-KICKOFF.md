# Build the create-department recipe: the `templates/department/` baseline (including the per-department orchestrator-command template) and the `/create-department` command

## Target

This is **AI-infrastructure** work (ADR-005 domain 2): the orchestration machinery that builds and maintains the web app, not the web app itself. The task is COR-T-013, the create-department recipe named as a follow-on in ADR-027 Fork D and given its full contract in ADR-030.

The artifact in scope is a **recipe**, not a department. You build two things: (1) the `templates/department/` baseline under the coordinator workspace, a set of placeholder-tokenized template files that a future `/create-department` run stamps out into a real department workspace; and (2) the `.claude/commands/create-department.md` command that drives that stamping through the dispatched-worker flow. You create NO actual department workspace under `ai-infrastructure/<dept>/`; that happens only when `/create-department` is first run, which is out of scope here.

The authoritative specification is `./ai-infrastructure/project-manager/decisions/ADR-030-department-scaffold-contract-create-department-recipe.md`. Build deliverables 1 and 2 to that ADR exactly. ADR-030's own deliverable 3 (the recipe ADR) is already authored by the Orchestrator and is out of scope.

## Decisions resolved by the Orchestrator

Every decision below is pinned. Do not re-deliberate any of them; build to them.

- **The authoritative contract is ADR-030.** Build deliverables 1 and 2 to `./ai-infrastructure/project-manager/decisions/ADR-030-department-scaffold-contract-create-department-recipe.md` exactly. When this kickoff and ADR-030 appear to diverge on a detail, ADR-030 is the spec; surface the divergence rather than guessing. ADR-030 deliverable 3 (the recipe ADR itself) is already authored and out of scope.
- **Command surface: one per-department orchestrator command, no worker command.** The scaffold includes exactly ONE per-department `/<slug>-orchestrator` (Opus) command, delivered as the placeholder-tokenized `orchestrator-command.md` template. There is NO `/<slug>-worker` command, NO per-department `worker-agent`, and NO per-department role-doc copies. A department dispatches the single universal `worker-agent` (ADR-028) and reuses the shared root role docs by reference (ADR-029). This is ADR-030 Decision items 1 and 3 (the resolved "Department command surface" decision); it is pinned, not a choice for you to weigh.
- **Template location:** `ai-infrastructure/project-manager/templates/department/` (ADR-030 item 1; the coordinator owns the recipe per the ADR-027 tree).
- **Template file set, exactly these six and no others:** `CLAUDE.md`, `README.md`, `STATUS.md`, `OBSERVATIONS.md`, `decisions/README.md`, `orchestrator-command.md` (ADR-030 item 1). The template contains NO `tasks/` directory (ADR-027 Fork B, shared labeled pool), NO per-department role docs (ADR-029), and NO worker command or worker-agent (ADR-028).
- **Per-file content of the template files (ADR-030 item 1):**
  - `CLAUDE.md`: the department's operating rules and workspace routing. It references (does not duplicate) the global root `CLAUDE.md`, the coordinator's write authority over the workspace (ADR-027), the shared role docs at their root path by reference (ADR-029), the path conventions, and the MCP seam and run policy. It carries an "Operated by" section naming the department's own `/{{DEPT_SLUG}}-orchestrator` command, the universal dispatched `worker-agent` (ADR-028) it dispatches, and the universal checker fleet (ADR-023). It states the department has NO own `tasks/`. It carries the one-line department-scoped checker slot reservation note (ADR-027 Consequences, ADR-023, ADR-030 item 6).
  - `README.md`: the department charter for humans: its ADR-021 menu scope line (rendered as `{{DEPT_SCOPE}}`), its boundary, and a pointer to the coordinator.
  - `STATUS.md`: frontmatter (`schema_version`, a department identifier, `last_updated`, `recent_updates`) plus a narrative section, mirroring the coordinator's STATUS shape scoped to the department.
  - `OBSERVATIONS.md`: an append-only pattern log mirroring the coordinator's, using the department's `{{DEPT_OBS_PREFIX}}-NN` observation ID convention (for example `TST-01`) in place of `COR-NN`.
  - `decisions/README.md`: a stub for the department's `decisions/` directory that points at the coordinator's `decisions/README.md` (at `ai-infrastructure/project-manager/decisions/README.md`) for the ADR body convention, and leaves department-local ADR numbering to the department's first ADR. The file also exists so git tracks the otherwise-empty `decisions/` directory.
  - `orchestrator-command.md`: the per-department orchestrator command template (see the next bullet).
- **The orchestrator-command template (ADR-030 items 1, 3, 4).** It lives inside `templates/department/` as `orchestrator-command.md`, NOT under `.claude/commands/`, so the template file is not itself a live command. The `/create-department` recipe stamps it out to `.claude/commands/{{DEPT_SLUG}}-orchestrator.md` with tokens substituted. Its body mirrors the structure of `.claude/commands/corral-orchestrator.md` (adopt the shared `ORCHESTRATOR-ROLE.md`, load context, survey state, run the drafter+checker dispatch loop, run the dispatched-worker flow) but scoped to the department: role name "`{{DEPT_NAME}}` Orchestrator", loads the department `CLAUDE.md` and the department's `dept:{{DEPT_SLUG}}`-scoped slice of the shared `ai-infrastructure/project-manager/tasks/` pool, dispatches the universal `worker-agent`, and uses the universal checker fleet. No `/{{DEPT_SLUG}}-worker` command appears anywhere.
- **Placeholder token convention (ADR-030 item 2).** Template files use `{{UPPER_SNAKE}}` tokens, substituted at stamp time. Use these exact tokens throughout the template files wherever the per-department value belongs:
  - `{{DEPT_SLUG}}`: the kebab slug (for example `test-design`); used in paths, the command name, and the `dept:<slug>` label.
  - `{{DEPT_NAME}}`: the display name (for example `Test Design`).
  - `{{DEPT_OBS_PREFIX}}`: the uppercase observation prefix (for example `TST`); operator-supplied, not auto-derived.
  - `{{DEPT_SCOPE}}`: the one-line "would own" scope from the ADR-021 menu.
  - `{{DATE}}`: the creation date, `YYYY-MM-DD`.
- **The `/create-department` command (ADR-030 item 4).** Build it at `.claude/commands/create-department.md`. Inputs: `<slug>` (kebab), `<Display Name>`, `<OBS-PREFIX>` (uppercase). Precondition it states and enforces by stopping: the slug SHOULD be a blessed ADR-021 menu entry; creating an off-menu department requires extending the ADR-021 menu first. The command does not silently invent an off-menu department. Behavior: it drives the running orchestrator through the dispatched-worker flow: resolve the arguments and `{{DEPT_SCOPE}}` from the ADR-021 menu; draft and check a kickoff whose deliverable is the stamped workspace at `ai-infrastructure/<slug>/` (every template file with tokens substituted) plus the stamped `.claude/commands/<slug>-orchestrator.md`; run the prelaunch checker; dispatch the `worker-agent`; then run the close checker, verify-against-disk, and the commit gate. The command also reserves the `dept:<slug>` label in the markdown-era sense (next bullet) and applies STATUS hygiene. It explicitly notes that interactive back-and-forth at run time (escalation round-trips, or Plan Mode for a genuinely unanticipated decision) is expected and acceptable.
- **`dept:<slug>` label reservation in the markdown era (ADR-030 item 5).** "Reserve a `dept:<slug>` label" today means: use the established `dept:<slug>` naming (ADR-021) and ensure the slug is a blessed ADR-021 menu entry. There is no label registry to mutate in the markdown era; labels become real records at the dogfood milestone (ADR-008). Taxonomy, enforcement, and color/metadata are owned by ADR-018 (pending). The recipe documents the naming and defers the rest to ADR-018. Do NOT build any label registry.
- **Path conventions in the authored template files.** Generalize the project-manager `CLAUDE.md` "Path conventions", scoped to `ai-infrastructure/<slug>/`: inside the department workspace, `./X` resolves workspace-relative; references to root-staying shared infrastructure (`.claude/`, `docs/ai-orchestration/`, the repo-root `CLAUDE.md` / `README.md`) and to the coordinator (`ai-infrastructure/project-manager/...`) use bare repo-root-relative paths with no `./` prefix. The `.claude/commands/create-department.md` command is a root-level shared-infrastructure file; it uses bare repo-root-relative paths for the trees it touches (`ai-infrastructure/...`, `.claude/...`), matching how `.claude/commands/corral-orchestrator.md` and the universal agents reference the structure.
- **Do NOT edit `ORCHESTRATOR-ROLE.md` or any role doc.** ADR-030 Consequences pins that updating the role doc's one-Orchestrator line is a first-department-creation follow-up, NOT part of this task. The role docs are read-only references here.

## Deliverables

1. `./ai-infrastructure/project-manager/templates/department/CLAUDE.md` (department operating rules and workspace routing template, per the per-file content above).
2. `./ai-infrastructure/project-manager/templates/department/README.md` (department charter template).
3. `./ai-infrastructure/project-manager/templates/department/STATUS.md` (department STATUS template: frontmatter plus narrative).
4. `./ai-infrastructure/project-manager/templates/department/OBSERVATIONS.md` (department observations template, `{{DEPT_OBS_PREFIX}}-NN` IDs).
5. `./ai-infrastructure/project-manager/templates/department/decisions/README.md` (department decisions stub pointing at the coordinator's `decisions/README.md`).
6. `./ai-infrastructure/project-manager/templates/department/orchestrator-command.md` (the placeholder-tokenized per-department orchestrator command template; mirrors `corral-orchestrator.md` structure, scoped to the department).
7. `./.claude/commands/create-department.md` (the recipe command that stamps the workspace and the orchestrator command through the dispatched-worker flow).

All template files (1-6) use the `{{UPPER_SNAKE}}` tokens wherever a per-department value belongs. Creating these files creates the `templates/department/` and `templates/department/decisions/` directories.

## Files in scope

- `./ai-infrastructure/project-manager/templates/department/CLAUDE.md`
- `./ai-infrastructure/project-manager/templates/department/README.md`
- `./ai-infrastructure/project-manager/templates/department/STATUS.md`
- `./ai-infrastructure/project-manager/templates/department/OBSERVATIONS.md`
- `./ai-infrastructure/project-manager/templates/department/decisions/README.md`
- `./ai-infrastructure/project-manager/templates/department/orchestrator-command.md`
- `./.claude/commands/create-department.md`
- `./ai-infrastructure/project-manager/STATUS.md` (the task-specific "Next step" rewrite named under STATUS deltas, plus universal hygiene).

## Files out of scope

- `./ai-infrastructure/project-manager/decisions/ADR-030-department-scaffold-contract-create-department-recipe.md` (already authored by the Orchestrator; read-only reference, do not edit).
- `./ai-infrastructure/project-manager/decisions/ADR-027-ai-infrastructure-workspace-structure.md` (already amended; do not edit).
- All other ADRs.
- `./docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md` and `./docs/ai-orchestration/roles/WORKER-ROLE.md` (read-only references; do NOT edit, per the resolved decision on the one-Orchestrator line).
- The existing `./.claude/agents/*` files and their specs.
- `./.claude/commands/corral-orchestrator.md` (read-only structural exemplar; do NOT edit).
- Any actual department workspace under `ai-infrastructure/<dept>/`. NONE is created by this task; this builds the recipe only.
- The project-manager dashboard and any `dashboard/` content (that is COR-T-014).
- The `./ai-infrastructure/project-manager/tasks/` tree (task transitions are Orchestrator-only; the only STATUS edit is the named delta below).
- No new ADRs.

## References

Read these in order before authoring. They were read by the Orchestrator during decision resolution; you read them to ground the template content, not to re-open decisions.

- `./docs/ai-orchestration/roles/WORKER-ROLE.md`: your own role (universal conventions, report shape, STATUS hygiene). Note that the role docs stay at this root path and are referenced by departments, never copied.
- `./ai-infrastructure/project-manager/decisions/ADR-030-department-scaffold-contract-create-department-recipe.md`: THE authoritative contract; the spec you build deliverables 1 and 2 to. Decision items 1-6 map directly to the template file set, the token convention, the orchestrator command, the `/create-department` command, the label reservation, and the checker-slot note.
- `./ai-infrastructure/project-manager/decisions/ADR-027-ai-infrastructure-workspace-structure.md`: Fork D (the department scaffold sketch ADR-030 amends), the workspace tree, the coordinator write authority, and the forward-pointer notes. Fork B explains why there is no department `tasks/`.
- `./ai-infrastructure/project-manager/decisions/ADR-028-worker-as-dispatched-subagent.md`: the single universal dispatched `worker-agent`; the reason there is no `/<slug>-worker` command and no per-department worker-agent.
- `./ai-infrastructure/project-manager/decisions/ADR-029-shared-role-docs-stay-at-repo-root.md`: departments reuse the shared root role docs by reference, with no per-workspace copy; the bootstrap path stays `./docs/ai-orchestration/roles/...`.
- `./ai-infrastructure/project-manager/decisions/ADR-021-candidate-departments.md`: the blessed department menu and the "would own" scope lines that feed `{{DEPT_SCOPE}}`; the precondition the `/create-department` command enforces (the slug must be a blessed menu entry).
- `./ai-infrastructure/project-manager/decisions/ADR-018-department-label-taxonomy.md`: pending; label governance (registry, enforcement, color/metadata) is deferred to it. Confirms you build no label registry now.
- `./ai-infrastructure/project-manager/decisions/ADR-023-dispatch-loop-day-zero.md`: the universal checker fleet (the `worker-prelaunch-checker` / `worker-close-checker` pair) and the reserved department-scoped checker slot the template `CLAUDE.md` notes.
- `./docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md`: read-only. The role the stamped `/<slug>-orchestrator` command adopts by reference, and the dispatched-worker flow that command embodies. The "Drafter+checker dispatch loop" and "Dispatched-worker flow" sections are the behavior the `/create-department` command drives the orchestrator through.
- `./.claude/commands/corral-orchestrator.md`: read-only structural exemplar. The `orchestrator-command.md` template mirrors its five-phase structure (adopt role, load context, survey state, report, wait for direction), scoped to the department and tokenized.
- `./ai-infrastructure/project-manager/CLAUDE.md`: the "Path conventions" and "Coordinator write authority" sections, and the closest exemplar for the template `CLAUDE.md`. Generalize its path conventions to `ai-infrastructure/<slug>/`.
- `./ai-infrastructure/project-manager/STATUS.md`: shape exemplar for the template `STATUS.md` (frontmatter plus narrative sections), and the file where the STATUS delta below is applied.
- `./ai-infrastructure/project-manager/OBSERVATIONS.md`: shape exemplar for the template `OBSERVATIONS.md` (conventions, entry format, log; swap `COR-NN` for `{{DEPT_OBS_PREFIX}}-NN`).
- `./ai-infrastructure/project-manager/README.md`: charter shape exemplar for the template `README.md`.
- `./ai-infrastructure/project-manager/decisions/README.md`: the ADR body convention the template `decisions/README.md` stub points at (it is the target of the stub's pointer, not content to duplicate into the stub).

## Related tasks and ADRs

- ADR-030: the authoritative scaffold contract this task builds to.
- ADR-027 (Fork D): the parent decision that named the recipe; amended by ADR-030.
- ADR-028: single universal dispatched worker; the reason there is no `/<slug>-worker` command.
- ADR-029: shared role docs reused by reference; the reason there are no per-department role-doc copies.
- ADR-021: the department menu the recipe stamps from and the source of `{{DEPT_SCOPE}}`.
- ADR-018: pending label taxonomy; label governance is deferred to it.
- ADR-023: the universal checker fleet and the reserved department-scoped checker slot.
- COR-T-014: the project-manager dashboard, the other remaining ADR-027 follow-on; sibling, out of scope.
- COR-T-008: resolves ADR-018; the downstream owner of label governance the recipe defers.

## STATUS deltas

Task-specific delta, beyond universal hygiene: rewrite the "Next step" section of `./ai-infrastructure/project-manager/STATUS.md` so it states:

- The create-department recipe now exists: the `templates/department/` baseline (including the `orchestrator-command.md` template) plus the `/create-department` command, with the contract recorded in ADR-030.
- The sole remaining ADR-027 follow-on is COR-T-014 (the project-manager dashboard).
- COR-T-008 (label taxonomy, ADR-018), COR-T-009 (native epics, ADR-025), and COR-T-010 (per-agent MCP identity, ADR-026) remain queued for resolution.

Universal STATUS hygiene (bump `last_updated`, prepend a `recent_updates` entry) is handled per `./docs/ai-orchestration/roles/WORKER-ROLE.md` and is not itemized here.

## Hard rules

- **Build to ADR-030, not to this kickoff's paraphrase.** Where a detail here is terser than ADR-030, ADR-030 governs. Where they appear to conflict, surface it; do not silently pick one.
- **No `/<slug>-worker` command and no per-department worker-agent or role-doc copies anywhere** (ADR-028, ADR-029). The single universal `worker-agent` and the shared root role docs are referenced by the department, never duplicated.
- **The `orchestrator-command.md` template lives in `templates/department/`, not in `.claude/commands/`.** It is a template, not a live command; only the stamped output lands in `.claude/commands/`.
- **Use the five `{{UPPER_SNAKE}}` tokens** exactly as named (`{{DEPT_SLUG}}`, `{{DEPT_NAME}}`, `{{DEPT_OBS_PREFIX}}`, `{{DEPT_SCOPE}}`, `{{DATE}}`) wherever a per-department value belongs. Do not invent additional tokens or hard-code a sample department's values.
- **Build no label registry** (ADR-018 pending). `dept:<slug>` reservation in the markdown era is naming plus the blessed-menu precondition only.
- **Path conventions in authored files:** workspace-relative `./X` inside a department workspace; bare repo-root-relative paths for shared infrastructure and the coordinator. The root-level `.claude/commands/create-department.md` uses bare repo-root-relative paths throughout.
- **Do not create any actual department workspace.** This task builds the recipe; the first real `/create-department` run stamps the first department.
- **Do not edit any ADR or any role doc.** They are read-only references here.

## Worker pointer

You are the dispatched `worker-agent` (ADR-028). Universal worker conventions (the six-section report shape, dual-channel report write, STATUS hygiene, the no-em-dashes and repo-root-relative-path writing rules, the no-edits-outside-scope rule) live in `./docs/ai-orchestration/roles/WORKER-ROLE.md`; follow them rather than re-deriving them. Your closing report is written to `./.claude/artifacts/handoffs/COR-T-013-KICKOFF-REPORT.md` per WORKER-ROLE.md, section "Report shape".
