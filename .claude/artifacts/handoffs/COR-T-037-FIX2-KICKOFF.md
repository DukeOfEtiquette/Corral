# Refine the Agent Fleet purpose extraction to split on sentence boundaries

## Target

This is AI-infrastructure work (ADR-005), a second corrective pass within in-progress task COR-T-037. The artifact in scope is the dashboard ETL at `./ai-infrastructure/project-manager/dashboard/etl.py`, specifically the `purpose` extraction inside the `collect_agents` function. The prior corrective pass already fixed `collect_agents` to populate the Agent Fleet panel via line-based frontmatter extraction; all six agents now appear. One blemish remains: the `purpose` is extracted as the text up to and including the FIRST bare period, which truncates `kickoff-checker`'s purpose at the period inside `./docs/...`, producing `Use this agent to independently lint a drafted kickoff file against the universal kickoff-drafting convention (R1-R8 per ADR-023, defined in .`. This pass polishes the purpose-extraction rule so the first sentence ends at a real sentence boundary.

## Decisions resolved by the Orchestrator

- **Root cause is the naive first-period rule, not a data problem.** A bare period inside a file path (`./docs`) or a reference (`ADR-016)`) ends the extracted sentence early. The agent description text is correct; the extraction rule is too coarse.
- **Fix: split on the first period-followed-by-whitespace, not a bare period.** In `collect_agents`, change the purpose extraction so the first sentence ends at the first occurrence of a period immediately followed by a whitespace character (for example `". "` or a period then a newline), and includes that period. Rationale: file paths like `./docs` and references like `ADR-016)` have a period with no following space, so they no longer falsely end the sentence; every agent's real first sentence ends with a period followed by a space.
- **Implementation: regex search for a period followed by whitespace, then slice up to and including that period.** Use `re.search(r"\.\s", description)` (or an equivalent that matches a period followed by any whitespace character). When a match is found, slice `description` up to and including the matched period. `re` is already imported at the top of `etl.py`; do not add an import.
- **Fallback: when no period-followed-by-whitespace occurs, use the whole description.** If the regex finds no match, set `purpose` to the whole `description` text, stripped. This preserves a sensible value for descriptions that have no sentence-terminating period followed by whitespace.
- **Docstring follows the code.** Update the `collect_agents` docstring's description of the purpose rule to match the new behavior: the first sentence is the text up to the first period-then-whitespace, else the whole description. Do not leave the docstring asserting the old "up to and including the first period" rule.

## Deliverables

- EDIT `./ai-infrastructure/project-manager/dashboard/etl.py`: change the `purpose` first-sentence extraction in `collect_agents` so it splits on the first period-followed-by-whitespace (including that period), with a whole-description (stripped) fallback when no such match exists. Update the `collect_agents` function docstring's purpose-rule wording to match. No other change.

## Files in scope

- `./ai-infrastructure/project-manager/dashboard/etl.py`

## Files out of scope

- The line-based name/model/kind extraction in `collect_agents` (it is correct; leave it).
- The emitted dict shape (`name`, `model`, `kind`, `purpose`), the skip-when-missing behavior, and the name-sorted output in `collect_agents` (leave all of these).
- The shared `parse_frontmatter` helper (do not touch).
- `AgentsPanel.jsx`, `LandingView.jsx`, `styles.css` (they are correct; do not touch).
- The six `.claude/agents/*.md` files (do not reformat).
- `./ai-infrastructure/project-manager/STATUS.md` (see STATUS deltas: leave untouched).
- The append-only trees (`handoffs/`, `tasks/`, `OBSERVATIONS.md`).

## References

- `./ai-infrastructure/project-manager/dashboard/etl.py`, function `collect_agents` (the current purpose-extraction block to change is the `description.find(".")` logic near the end of the function; `re` is already imported at the top of the module).

## Related tasks and ADRs

- COR-T-037 (this is a second corrective pass within it; the panel and the populate fix are done, this pass polishes the purpose text).
- ADR-032 (the taxonomy the Agent Fleet panel encodes).

## STATUS deltas

No task-specific STATUS deltas. This is a corrective pass within in-progress COR-T-037, whose STATUS `recent_updates` entry was already written by the first executor run. Leave `./ai-infrastructure/project-manager/STATUS.md` untouched: do not apply universal hygiene to it for this pass.

## Hard rules

- Scope is the purpose extraction only. Do not change the line-based name/model/kind extraction, the emitted dict shape, the skip-when-missing behavior, or the name-sorted output, or anything outside `collect_agents`.
- Structural verification only. You cannot run docker compose (ADR-003; you are a leaf node). Verify the change structurally by reading the resulting code. Verification expectation: after the change, `kickoff-checker`'s purpose reads the full first sentence ending at `...section "Kickoff drafting convention").` and the other five purposes are unchanged. The Orchestrator will re-run the extraction against the six agent files to confirm.

## Executor pointer

The executor is the dispatched `executor` (ADR-028). Universal executor conventions (the run policy, git boundaries, writing rules, Agent Discipline, and the pinned six-section closing report) live in `./docs/ai-orchestration/roles/EXECUTOR-ROLE.md`; reference them there rather than re-deriving. The closing report is written to `./.claude/artifacts/handoffs/COR-T-037-FIX2-KICKOFF-REPORT.md` per `EXECUTOR-ROLE.md`, section "Report shape".
