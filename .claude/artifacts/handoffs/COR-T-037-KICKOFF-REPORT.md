## Deliverables completed

All deliverables from the kickoff were completed.

- NEW `./.claude/agents/specs` is unchanged; NEW `./ai-infrastructure/project-manager/dashboard/src/panels/AgentsPanel.jsx`: full-width `.card` titled "Agent Fleet", renders two `AgentGroup` sub-components ("Executors" and "Dispatch-loop & checkers"), each with a `.agent-group-heading` and an `.agent-table`. Agents are rendered in received order (name-sorted from data.json). Each row shows the agent name (monospace), a model badge (`.badge.badge-model-opus` or `.badge.badge-model-sonnet`), and the one-line `purpose`.

- EDIT `./ai-infrastructure/project-manager/dashboard/etl.py`:
  - Module docstring updated: Sources item `(g)` added (agents from `.claude/agents/*.md`), `agents` field added to the JSON-contract shape block with the four keys (`name`, `model`, `kind`, `purpose`).
  - New `collect_agents(agents_dir: Path) -> list` function added (after `collect_adrs`): scans `*.md` files, uses `parse_frontmatter`, skips files with absent/invalid frontmatter or missing `name`/`model`/`kind`, extracts first sentence of `description` via `find(".")`, returns list sorted by `name`.
  - `run_etl`: `agents_dir = repo_root / ".claude" / "agents"` added; `agents = collect_agents(agents_dir)` called after observations count; `"agents": agents` added to the assembled `data` dict.
  - `WATCH_PATTERNS`: `re.compile(r".*\.claude/agents/.*\.md$")` added as third entry.
  - `run_watch`: `repo_root / ".claude" / "agents"` added to `watch_dirs`.

- EDIT `./ai-infrastructure/project-manager/dashboard/src/views/LandingView.jsx`: `import AgentsPanel from '../panels/AgentsPanel.jsx'` added; `<AgentsPanel agents={data.agents} />` inserted between the closing `</div>` of `.roster-row` and `<RoadmapPanel roadmap={data.roadmap} />` (verified: lines 41-43 of the updated file).

- EDIT `./ai-infrastructure/project-manager/dashboard/src/styles.css`: Added `.agent-group`, `.agent-group:last-child`, `.agent-group-heading`, `.agent-table`, `.agent-table th`, `.agent-table td`, `.agent-table tr:last-child td`, `.agent-table tr:hover td`, `.agent-name`, `.agent-purpose`, `.badge-model-opus`, `.badge-model-sonnet`.

- EDIT six agent files: `kind:` frontmatter line added after `model:` in each:
  - `./.claude/agents/executor.md`: `kind: executor`
  - `./.claude/agents/test-designer.md`: `kind: executor`
  - `./.claude/agents/kickoff-drafter.md`: `kind: dispatch`
  - `./.claude/agents/kickoff-checker.md`: `kind: dispatch`
  - `./.claude/agents/worker-prelaunch-checker.md`: `kind: dispatch`
  - `./.claude/agents/worker-close-checker.md`: `kind: dispatch`

## Decisions made

- No decisions were left open by the kickoff. All choices were pinned by the Orchestrator and executed as specified.
- First-sentence extraction: used `str(description).find(".")` to locate the first period; all six agent descriptions have a clean first sentence ending with a period and no internal periods, so the extraction is unambiguous.
- `collect_agents` skips files missing `name`, `model`, or `kind` (in addition to files with absent/invalid frontmatter), ensuring tolerance if a non-agent `.md` file appears in the agents directory.
- CSS placement: the Agent Fleet CSS was appended after the existing `.muted` / `code` utilities, following the file's existing section-per-component pattern.

## Surprises

- The `description` frontmatter values in the six agent files are stored as a single long string with `\n` characters embedded on one physical line in the file (YAML parses them as the full string). The first-sentence extraction via `find(".")` works correctly because none of the six descriptions contain a period before the sentence-ending period in the first sentence.

## Follow-ups

- COR-T candidate: the "Dispatch-loop & checkers" group title uses an ampersand (`&`) which renders correctly in JSX but could be written as `&amp;` for stricter HTML compliance. Current rendering in a React JSX context is correct; no action required. (triage to orchestrator)
- COR-T candidate: `worker-prelaunch-checker` and `worker-close-checker` retain the legacy `worker-` prefix per ADR-032's explicit deferral. ADR-032 notes this as a candidate follow-up (dropping the producer prefix). The Agent Fleet panel will display them correctly under "Dispatch-loop & checkers" regardless of their names. (triage to orchestrator)

## Files touched

- `./.claude/agents/executor.md` (kind: executor added)
- `./.claude/agents/test-designer.md` (kind: executor added)
- `./.claude/agents/kickoff-drafter.md` (kind: dispatch added)
- `./.claude/agents/kickoff-checker.md` (kind: dispatch added)
- `./.claude/agents/worker-prelaunch-checker.md` (kind: dispatch added)
- `./.claude/agents/worker-close-checker.md` (kind: dispatch added)
- `./ai-infrastructure/project-manager/dashboard/etl.py`
- `./ai-infrastructure/project-manager/dashboard/src/panels/AgentsPanel.jsx` (new)
- `./ai-infrastructure/project-manager/dashboard/src/views/LandingView.jsx`
- `./ai-infrastructure/project-manager/dashboard/src/styles.css`
- `./ai-infrastructure/project-manager/STATUS.md`
- `./.claude/artifacts/handoffs/COR-T-037-KICKOFF-REPORT.md` (this file)

## Build / verification status

Structural verification completed:

- Data contract: `etl.py` module docstring `agents` field lists four keys (`name`, `model`, `kind`, `purpose`); `collect_agents` emits exactly those four keys. Contract consistent.
- Wiring: `LandingView.jsx` imports `AgentsPanel` from `'../panels/AgentsPanel.jsx'` and renders `<AgentsPanel agents={data.agents} />`; `etl.py` `run_etl` assembles `"agents": agents` in the data dict. Consistent end-to-end.
- CSS coverage: every class referenced by `AgentsPanel.jsx` (`.card`, `.agent-group`, `.agent-group-heading`, `.agent-table`, `.agent-name`, `.badge`, `.badge-model-opus`, `.badge-model-sonnet`, `.agent-purpose`) exists in `styles.css`. Verified via grep.
- Agent `kind:` values: all six files verified with grep: `executor.md` and `test-designer.md` have `kind: executor`; `kickoff-drafter.md`, `kickoff-checker.md`, `worker-prelaunch-checker.md`, `worker-close-checker.md` have `kind: dispatch`.
- No em dashes in any written file (verified via grep -P).
- First-sentence extraction: all six agent descriptions begin with "Use this agent ..." and have a clear first sentence ending with a period. The `find(".")` extraction produces the full first sentence in each case.

Visual confirmation required from the Orchestrator: run `docker compose -f ai-infrastructure/project-manager/dashboard/docker-compose.yml up --build` (single `dashboard` service, port 8420) to confirm the Agent Fleet panel renders between the roster row and the Roadmap, with two groups ("Executors" showing executor and test-designer; "Dispatch-loop & checkers" showing the four dispatch-kind agents), model badges, and one-line purposes.
