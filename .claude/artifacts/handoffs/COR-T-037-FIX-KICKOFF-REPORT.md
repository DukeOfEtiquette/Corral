## Deliverables completed

- EDITED `./ai-infrastructure/project-manager/dashboard/etl.py`: rewrote the body of `collect_agents` (lines 350-412 in the updated file) to extract `name`, `model`, `kind`, and `description` via a line-based scan of the frontmatter block. No `yaml` usage and no `parse_frontmatter` call inside the new implementation.
  - Frontmatter block isolation: `text.find("\n---", 3)` idiom, identical to `parse_frontmatter` and `extract_body`.
  - Field extraction: per-line scan of `fm_block.splitlines()`, matching `name:`, `model:`, `kind:`, `description:` prefixes, taking text after the first colon.
  - Skip-when-missing: skips any file where `name`, `model`, or `kind` is missing or empty after extraction.
  - Purpose extraction: first sentence of `description` (text up to and including the first `.`).
  - Output shape: dicts with keys `name`, `model`, `kind`, `purpose`; list sorted by `name`.
  - Docstring updated to state that extraction is line-based (not yaml) because the agent `description` scalar is not yaml-safe.

## Decisions made

- No decisions were required. The kickoff pinned the root cause, the fix approach, the output shape, the skip behavior, and the scope boundary (only `collect_agents`). Executed as specified.

## Surprises

- The `git diff --stat` shows multiple files changed; those are the prior executor run's uncommitted changes (agent `.md` files, STATUS.md, CSS, LandingView.jsx, tasks/.next-task-id). None of those were touched in this session. Only `collect_agents` in `etl.py` was edited here.
- The `kickoff-checker.md` agent's `purpose` field will truncate at the first period inside `"./docs/..."` in its description (producing: `"Use this agent to independently lint a drafted kickoff file against the universal kickoff-drafting convention (R1-R8 per ADR-023, defined in ."`). This is the correct behavior per the "first period" contract and matches what the original broken code would have produced if yaml had not rejected the file. Noted as out-of-scope; not a defect in the fix.

## Follow-ups

- COR-T-037 (triage to orchestrator): The dashboard compose stack should be verified end-to-end (docker compose up) once the prior executor run's changes and this fix are both staged, to confirm the Agent Fleet panel populates with all six agents. The structural simulation in this session confirmed the line-based logic produces the correct six-entry list, but a compose run was not performed per ADR-003 (executor is a leaf; no docker access in this dispatch context).

## Files touched

- `./ai-infrastructure/project-manager/dashboard/etl.py` (collect_agents function body and docstring rewritten; lines 350-412)
- `./.claude/artifacts/handoffs/COR-T-037-FIX-KICKOFF-REPORT.md` (this report, dual-channel)

## Build / verification status

- **Structural simulation run (host Python):** Executed the new `collect_agents` logic against all six `./.claude/agents/*.md` files using the host Python interpreter. Result: 6 name-sorted dicts, each with non-empty `name`, `model`, `kind`, and a `purpose` ending with a period.
  - executor: model=sonnet, kind=executor
  - kickoff-checker: model=sonnet, kind=dispatch
  - kickoff-drafter: model=opus, kind=dispatch
  - test-designer: model=opus, kind=executor
  - worker-close-checker: model=sonnet, kind=dispatch
  - worker-prelaunch-checker: model=sonnet, kind=dispatch
- **Acceptance gate met:** `collect_agents` emits one dict per agent file with all four keys populated, list sorted by name, no yaml involvement.
- **Compose run:** Not performed. Per ADR-003 and the run policy, compose is the only supported run path once code exists. The executor is a leaf node with no docker access in this dispatch context. End-to-end verification via `docker compose up` is deferred to the Orchestrator/user as a follow-up (see Follow-ups above).
- **parse_frontmatter untouched:** Verified at lines 105-122; unchanged.
- **yaml import retained:** Line 76; still present for parse_frontmatter's use by other collectors.
- **No em dashes in edited file:** Verified with grep.
- **STATUS.md untouched:** Per kickoff STATUS deltas instruction; not touched in this session.
