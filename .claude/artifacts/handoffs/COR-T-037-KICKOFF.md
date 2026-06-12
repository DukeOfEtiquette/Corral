# Dashboard: add an Agent Fleet panel listing the cross-department agents

## Target

This is AI-infrastructure work (domain 2 per ADR-005): a feature addition to the project-manager dashboard, the React SPA fed by `etl.py` that lives under `./ai-infrastructure/project-manager/dashboard/`. Task COR-T-037 adds a new full-width "Agent Fleet" panel to the dashboard landing view, surfacing the six shared cross-department agents (Tier 2 per ADR-032) that are otherwise invisible on the dashboard. The two existing Roster boxes show departments and their orchestrators; this new panel shows the dispatched agent fleet beneath them. Delivering it touches four layers: the ETL reader (`etl.py`), the new panel component, the landing-view wiring, the stylesheet, and a one-line frontmatter addition to each of the six agent files.

## Decisions resolved by the Orchestrator

These are pinned. Execute them as written; do not re-derive or substitute.

- **Goal and placement.** Add a new "Agent Fleet" panel to the landing view. It is full-width and sits between the closing `</div>` of the `.roster-row` and the `<RoadmapPanel ... />`. The two existing Roster boxes show departments and orchestrators; this panel shows the dispatched agent fleet.

- **Data source: a new pure reader `collect_agents(agents_dir)` in `etl.py`.** It scans `.claude/agents/*.md`, parses each file's YAML frontmatter with the existing `parse_frontmatter` helper (tolerant: skip files whose frontmatter is absent or invalid), and returns a list of dicts each carrying exactly these four keys: `name` (frontmatter `name`), `model` (frontmatter `model`), `kind` (frontmatter `kind`, see the classification decision below), and `purpose` (the first sentence of the frontmatter `description`, that is the text up to and including the first period). Emit the list sorted by `name`. Do NOT emit the agent `color`, `tools`, or the full description. `collect_agents` is a pure reader like the other `collect_*` functions: tolerant parsing, deterministic name-sorted output, no side effects, reads only the frontmatter (not the description examples). Rationale: mirrors the established `collect_*` contract in this module.

- **Wire `collect_agents` into `run_etl`.** Call it with `agents_dir = repo_root / ".claude" / "agents"`, and add `"agents": agents` to the assembled `data` dict.

- **Update the module docstring.** Document the new agents source as item `(g)` in the Sources list, and add the `agents` field to the JSON-contract shape block. Describe the shape `collect_agents` actually emits (the four keys: `name`, `model`, `kind`, `purpose`). Rationale: the docstring is the data.json contract of record in this module; keep it matching the emitted shape.

- **Classification via a new `kind:` frontmatter field on each of the six agent files.** Add a `kind:` line to the frontmatter of each agent file. Values: `executor` for `executor.md` and `test-designer.md`; `dispatch` for `kickoff-drafter.md`, `kickoff-checker.md`, `worker-prelaunch-checker.md`, and `worker-close-checker.md`. Place the `kind` line alongside the existing frontmatter keys (for example after `model` or `color`). Do not change any other frontmatter field, and do not touch `color` or `tools`. Rationale: the user chose a machine-readable frontmatter field over an ETL-side map so the ADR-032 taxonomy lives in the agent files themselves; the ETL reads `kind` and the panel groups by it.

- **New panel `src/panels/AgentsPanel.jsx`.** A full-width `.card` titled "Agent Fleet". It receives `agents` as a prop. It renders two groups in this order: "Executors" (agents with kind `executor`) then "Dispatch-loop & checkers" (agents with kind `dispatch`). Within each group, render agents in the order received from data.json (already name-sorted; do not re-sort). Each agent row shows the agent `name`, a model badge displaying the `model` value (opus / sonnet), and the one-line `purpose`. Mirror the structural idiom of `DepartmentsPanel.jsx`: a `.card` with an `<h3>` title and a table or list inside. Rationale: consistency with the existing panel pattern.

- **LandingView wiring.** Import `AgentsPanel` and insert `<AgentsPanel agents={data.agents} />` between the closing `</div>` of the `.roster-row` and `<RoadmapPanel ... />`. Rationale: this is the placement decided above.

- **Styles in `styles.css`.** Add the CSS the panel needs: group sub-headings, the agent rows, and the model badges. Reuse `.card` for the container. For the model badges, mirror the existing `.badge-*` idiom already in the file (for example `.badge-model-opus` / `.badge-model-sonnet`, or a single `.agent-model` class). No em dashes in the CSS. Rationale: the file already establishes a `.badge-*` convention (see `.badge-role`, `.badge-domain`, `.badge-milestone-*`); the model badges follow it.

- **Live-reload watch set.** The ETL `--watch` source set currently covers `ai-infrastructure/**/*.md` and `.claude/commands/**/*.md` but NOT `.claude/agents/`, so agent edits would not rebuild the dashboard. Add the watch pattern `re.compile(r".*\.claude/agents/.*\.md$")` to `WATCH_PATTERNS`, and add `repo_root / ".claude" / "agents"` to the `watch_dirs` list in `run_watch`. Mirror the existing `.claude/commands` handling in both spots. Rationale: without it, the `kind` edits and future agent edits would not trigger a rebuild.

## Deliverables

- NEW `./ai-infrastructure/project-manager/dashboard/src/panels/AgentsPanel.jsx`: the grouped "Agent Fleet" panel, per the panel decision above.
- EDIT `./ai-infrastructure/project-manager/dashboard/etl.py`: add `collect_agents`, wire it into `run_etl` (`"agents": agents` in the data dict), update the module docstring (Sources item `(g)` and the JSON-contract shape), and add the two watch-set entries (`WATCH_PATTERNS` pattern and `watch_dirs` directory).
- EDIT `./ai-infrastructure/project-manager/dashboard/src/views/LandingView.jsx`: import `AgentsPanel` and insert `<AgentsPanel agents={data.agents} />` between the `.roster-row` close and `RoadmapPanel`.
- EDIT `./ai-infrastructure/project-manager/dashboard/src/styles.css`: add the panel, group-heading, agent-row, and model-badge classes the panel references.
- EDIT the six agent files (`./.claude/agents/executor.md`, `test-designer.md`, `kickoff-drafter.md`, `kickoff-checker.md`, `worker-prelaunch-checker.md`, `worker-close-checker.md`): add the `kind:` frontmatter line with the correct value per the classification decision.

## Files in scope

- `./ai-infrastructure/project-manager/dashboard/src/panels/AgentsPanel.jsx` (new)
- `./ai-infrastructure/project-manager/dashboard/etl.py`
- `./ai-infrastructure/project-manager/dashboard/src/views/LandingView.jsx`
- `./ai-infrastructure/project-manager/dashboard/src/styles.css`
- `./.claude/agents/executor.md`
- `./.claude/agents/test-designer.md`
- `./.claude/agents/kickoff-drafter.md`
- `./.claude/agents/kickoff-checker.md`
- `./.claude/agents/worker-prelaunch-checker.md`
- `./.claude/agents/worker-close-checker.md`
- `./ai-infrastructure/project-manager/STATUS.md` (universal hygiene write only)

## Files out of scope

- The other dashboard panels (`PulsePanel`, `RoadmapPanel`, `ActivityPanel`, `DepartmentsPanel`, `TaskCountsPanel`) and `src/views/WorkspaceView.jsx`. Do not modify them.
- The agent `color` and `tools` frontmatter fields. Do not surface them in the ETL or change them in the agent files.
- The dashboard `Dockerfile`, `entrypoint.sh`, `package.json`, `vite.config.js`. No new dependencies; this is pure React/JSX, CSS, and Python stdlib plus the `yaml` module already in use.
- Any ADR under `./ai-infrastructure/project-manager/decisions/`. The ADR-032 taxonomy touch-up is a separate, out-of-scope item.
- The append-only trees: `./.claude/artifacts/handoffs/`, `./ai-infrastructure/project-manager/tasks/`, `./ai-infrastructure/project-manager/OBSERVATIONS.md`.

## References

Read these in order; each is named for a specific reason.

- `./ai-infrastructure/project-manager/dashboard/etl.py`: the ETL to extend. Study the `collect_*` pattern (for example `collect_adrs`, `collect_tasks`), the `parse_frontmatter` helper you will reuse, the `run_etl` assembly and `data` dict, the JSON-contract docstring at the top, and `WATCH_PATTERNS` plus `run_watch` (the `watch_dirs` list and the `.claude/commands` handling to mirror).
- `./ai-infrastructure/project-manager/dashboard/src/views/LandingView.jsx`: the panel composition and the exact insertion point (between the `.roster-row` close and `<RoadmapPanel ... />`).
- `./ai-infrastructure/project-manager/dashboard/src/panels/DepartmentsPanel.jsx`: the panel pattern to mirror (a `.card` with an `<h3>` title and a table).
- `./ai-infrastructure/project-manager/dashboard/src/styles.css`: the existing `.card`, `.dept-table`, and `.badge-*` idioms to mirror for the new panel and model badges.
- `./.claude/agents/executor.md`: an example agent file showing the frontmatter shape and where the `kind` line goes. All six agent files get the `kind` field; this one is the structural example.
- `./ai-infrastructure/project-manager/decisions/ADR-032-cross-department-agent-tier.md`: the taxonomy the `kind` field encodes (executors versus the dispatch-loop and checkers) and the grouping the panel renders.

## Related tasks and ADRs

- COR-T-037: this task.
- ADR-032: the cross-department agent taxonomy the `kind` field and the panel grouping encode (executors versus the dispatch-loop validators and checkers).
- ADR-016: defines `test-designer`, one of the two `executor`-kind agents.
- ADR-023: defines the dispatch-loop validators (`kickoff-checker`) and the prelaunch/close checkers, the four `dispatch`-kind agents.
- ADR-028: the dispatched-subagent model the cross-department agents follow.
- COR-T-014: built the dashboard (the `etl.py` + React SPA pattern this extends).
- COR-T-017: extended the `etl.py` + panel pipeline end-to-end for roadmap sub-milestones; the precedent for adding a data.json field plus a new panel.
- COR-T-032: created the two-roster landing layout this panel sits directly beneath.

## STATUS deltas

No task-specific STATUS deltas; universal hygiene only. Apply the universal hygiene to `./ai-infrastructure/project-manager/STATUS.md`: bump `last_updated` and append one `recent_updates` entry summarizing the Agent Fleet panel (the new panel plus the `etl.py` agents source and the per-agent `kind` field). Do not edit the roadmap block or any narrative section.

## Hard rules

- The first-sentence `purpose` extraction must handle the actual agent descriptions, which begin with "Use this agent ...". Extract the text up to and including the first period. Verify against the real descriptions in the six agent files, not against a hypothetical shape.
- `collect_agents` reads only the frontmatter, never the description examples below the frontmatter. The `description` field whose first sentence you extract is the frontmatter `description` value.
- Do not surface or modify the agent `color` or `tools` fields anywhere.
- No new runtime dependencies. Use only React/JSX, CSS, and the Python stdlib plus the `yaml` module already imported in `etl.py`.

## Verification expectations

This is a visual dashboard change and you cannot run docker compose (ADR-003; you are a leaf). Do STRUCTURAL verification only:

- The data.json contract docstring matches the shape `collect_agents` emits (the four keys `name`, `model`, `kind`, `purpose`).
- `AgentsPanel`'s import and its `agents` prop are consistent with the wiring in `LandingView.jsx`.
- Every CSS class `AgentsPanel.jsx` references exists in `styles.css`.
- Each of the six agent files gained a valid `kind:` line with the correct value (`executor` for `executor.md` and `test-designer.md`; `dispatch` for the four checkers and the kickoff-drafter).
- The first-sentence `purpose` extraction handles the actual descriptions (which begin with "Use this agent ...").

Do NOT invent or run any docker compose command. The Orchestrator runs `docker compose -f ai-infrastructure/project-manager/dashboard/docker-compose.yml up --build` (single `dashboard` service, port 8420) for the visual confirmation. If your report names a run command, reference that exact command; do not construct a different one. Report what you verified structurally and what the Orchestrator must confirm visually under "Build / verification status".

## Executor pointer

You are the dispatched `executor` (ADR-028). Universal executor conventions live in `./docs/ai-orchestration/roles/EXECUTOR-ROLE.md`: the six-section report shape, the dual-channel report-to-file rule, the universal conventions (repo writing rules, the compose-only run policy, git boundaries), and the failure modes. The closing report is written to `./.claude/artifacts/handoffs/COR-T-037-KICKOFF-REPORT.md` per EXECUTOR-ROLE.md, section "Report shape".
