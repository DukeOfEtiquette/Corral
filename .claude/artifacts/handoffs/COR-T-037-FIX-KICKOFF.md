# Fix collect_agents so the dashboard Agent Fleet panel populates

## Target

This is AI-infrastructure work (ADR-005), a corrective pass within in-progress COR-T-037. The dashboard Agent Fleet panel renders empty because the ETL collector `collect_agents` returns an empty list. The artifact in scope is the single function `collect_agents` in `./ai-infrastructure/project-manager/dashboard/etl.py`. The panel, its wiring, the CSS, the watch-set, and the six agents' frontmatter are all correct and verified; only the collector is broken.

## Decisions resolved by the Orchestrator

- **Root cause (verified).** The Agent Fleet panel renders empty because `collect_agents` calls the shared `parse_frontmatter`, which runs `yaml.safe_load` over the whole frontmatter block. Each agent file's `description` frontmatter value is an unquoted YAML plain scalar on a single physical line containing `": "` (colon-space) sequences (from embedded text like "Context: ", "user: ", "(first line RETURN: COMPLETED)"). PyYAML rejects this with "mapping values are not allowed here"; `parse_frontmatter` catches the `YAMLError` and returns `{}`, so `collect_agents` skips all six agents and emits an empty list. Confirmed 2026-06-12 by running the parser against all six `.claude/agents/*.md` files: every one raises the same error.

- **Fix (pinned): line-based field extraction inside `collect_agents` only.** Stop using `parse_frontmatter` / `yaml` for the agent files. In `collect_agents`, read each file's text, isolate the frontmatter block (the text between the opening `---` and the next `\n---`), and extract the needed fields by scanning that block's physical lines:
  - For `name`, `model`, and `kind`: take the line whose stripped text starts with `name:` / `model:` / `kind:`, and use the text after the first colon, stripped.
  - For `description`: take the line that starts with `description:`, use the remainder after the first colon, and extract the first sentence (up to and including the first period) for `purpose`.

  Each of name/model/kind is a single simple physical line; description is a single long physical line; so a per-line scan is robust and does not invoke yaml. The frontmatter-block isolation uses the same `text.find("\n---", 3)` idiom that `parse_frontmatter` and `extract_body` already use in this file.

- **Preserve existing behavior otherwise.** Skip an agent when `name`, `model`, or `kind` is missing or empty. Emit dicts with exactly the keys `name`, `model`, `kind`, `purpose`. Return the list sorted by `name`.

- **Update the docstring.** The `collect_agents` docstring should note that it does line-based frontmatter extraction (not yaml) because the agent `description` scalar is not yaml-safe.

- **Do not touch the shared `parse_frontmatter`.** ADRs and tasks rely on it and parse correctly; the change is local to `collect_agents`.

- **Do not reformat or quote the agent files' frontmatter.** Claude Code's agent loader requires the current format; the fix is in the reader, not the data.

- **Everything else from COR-T-037 is correct and out of scope.** The panel (`AgentsPanel.jsx`), the `LandingView` wiring, the CSS, the watch-set addition, and the six agents' `kind` values are all correct and verified; do not change them. Only `collect_agents` is broken.

## Deliverables

- EDIT `./ai-infrastructure/project-manager/dashboard/etl.py`: rewrite the body of `collect_agents` to extract `name`, `model`, `kind`, and the `description` first-sentence (as `purpose`) via a line-based scan of the frontmatter block, with no `yaml` use and no `parse_frontmatter` call. Preserve the emitted dict shape (`name`, `model`, `kind`, `purpose`), the skip-when-missing behavior (skip when `name`, `model`, or `kind` is missing or empty), and the name-sorted output. Update the function docstring to state that extraction is line-based (not yaml) because the agent `description` scalar is not yaml-safe.

## Files in scope

- `./ai-infrastructure/project-manager/dashboard/etl.py` (the `collect_agents` function body and docstring only)

## Files out of scope

- The shared `parse_frontmatter` function in the same file: do not modify; other collectors (`collect_tasks`, `collect_adrs`, the STATUS readers) depend on it.
- `./ai-infrastructure/project-manager/dashboard/src/panels/AgentsPanel.jsx` (correct; do not touch)
- `./ai-infrastructure/project-manager/dashboard/src/views/LandingView.jsx` (correct; do not touch)
- `./ai-infrastructure/project-manager/dashboard/src/styles.css` (correct; do not touch)
- The six `./.claude/agents/*.md` files: their `kind` values are correct; do not reformat their frontmatter.
- `./ai-infrastructure/project-manager/STATUS.md` (see STATUS deltas: leave untouched)
- The append-only trees (`./.claude/artifacts/handoffs/`, `./ai-infrastructure/project-manager/tasks/`, `./ai-infrastructure/project-manager/OBSERVATIONS.md`)

## References

- `./ai-infrastructure/project-manager/dashboard/etl.py` (the current `collect_agents` and `parse_frontmatter`; the frontmatter-block isolation idiom is the same `text.find("\n---", 3)` approach `parse_frontmatter` and `extract_body` already use)
- `./.claude/agents/executor.md` (an example agent file: the frontmatter carries `name`, `description` (one long physical line), `model`, `color`, `kind` as single physical lines)

## Related tasks and ADRs

- COR-T-037 (this corrective pass belongs to it; the initial executor run added the panel but `collect_agents` returned empty)
- ADR-032 (the taxonomy the `kind` field and the panel grouping encode)
- COR-T-014 (built the dashboard ETL the `parse_frontmatter` helper lives in)

## STATUS deltas

No STATUS write. This is a corrective pass within in-progress COR-T-037, whose STATUS `recent_updates` entry was already written by the prior executor run. Leave `./ai-infrastructure/project-manager/STATUS.md` untouched: do not apply universal hygiene, and do not add or edit any entry. (This overrides the default universal STATUS hygiene named in `EXECUTOR-ROLE.md`; the workspace STATUS is explicitly out of scope for this dispatch.)

## Hard rules

- The change is confined to the `collect_agents` function (its body and docstring). Do not edit `parse_frontmatter`, do not edit any other function, and do not add module-level imports beyond what the function needs (no new import is required; the function reads file text directly and uses no yaml).
- Do not invoke `yaml` or call `parse_frontmatter` from inside `collect_agents`.
- Verify the fix by running the ETL the compose way per the run policy in `./ai-infrastructure/project-manager/CLAUDE.md` and `EXECUTOR-ROLE.md`, OR, if a one-shot module check is simpler, run it through the project's compose-based path rather than assuming a host Python. Confirm `collect_agents` returns six name-sorted dicts (one per `./.claude/agents/*.md` file), each with non-empty `name`, `model`, `kind`, and a `purpose` that is the first sentence of the file's `description`. Record what you ran and what you observed in the report's "Build / verification status" section.
- This is the single acceptance gate: `collect_agents` emits one dict per agent file with the four keys populated and the list sorted by `name`, with no `yaml` involvement. The closing report confirms it.

## Executor pointer

The executor is the dispatched `executor` (ADR-028). Universal executor conventions (the six-section report shape, dual-channel write, file-edit hygiene, run policy, git boundaries) live in `./docs/ai-orchestration/roles/EXECUTOR-ROLE.md`. The closing report is written to `./.claude/artifacts/handoffs/COR-T-037-FIX-KICKOFF-REPORT.md` per `EXECUTOR-ROLE.md`, section "Report shape".
