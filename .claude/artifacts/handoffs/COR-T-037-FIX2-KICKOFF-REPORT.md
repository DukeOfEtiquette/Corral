---
kickoff: COR-T-037-FIX2-KICKOFF.md
attempt: 1
verdict: COMPLETED
---

## Deliverables completed

- EDIT `./ai-infrastructure/project-manager/dashboard/etl.py`: replaced the naive `description.find(".")` first-period rule in `collect_agents` with `re.search(r"\.\s", description)`. The new logic slices `description[: m.start() + 1]` (up to and including the matched period) when a match is found, and falls back to `description.strip()` when no period-then-whitespace occurs. No other logic changed.
- DOCSTRING updated: the `collect_agents` function docstring's purpose-rule sentence now reads "text up to and including the first period-then-whitespace; falls back to the whole description when no such match exists."
- MODULE DOCSTRING updated: both the Sources block (section g) and the JSON contract shape block (agents entry) now reflect the new period-then-whitespace rule and fallback. No other text changed.

## Decisions made

No decisions deferred to this executor; the kickoff pinned every choice. The regex `r"\.\s"` and the `m.start() + 1` slice are exactly what the kickoff specified.

## Surprises

None. The file was exactly as the kickoff described: `re` already imported at line 71, the `description.find(".")` block was at lines 399-404, and the function docstring was at lines 365-370. No other changes were in flight.

## Follow-ups

- COR-T candidate (triage to orchestrator): The module docstring also carried a stale inline comment at line 399 ("Extract first sentence of description: text up to and including the first period.") -- this was replaced as part of updating the code comment block, not a separate issue. No remaining stale doc.

## Files touched

- `./ai-infrastructure/project-manager/dashboard/etl.py` (four edits: extraction logic, inline comment, function docstring, module docstring x2)
- `./.claude/artifacts/handoffs/COR-T-037-FIX2-KICKOFF-REPORT.md` (this report)

## Build / verification status

Structural verification only (no docker compose per ADR-003; leaf node). Verified:

- `re` is imported at line 71 (no new import needed).
- The extraction block at lines 403-410 now uses `re.search(r"\.\s", description)`; the match-found branch slices `description[: m.start() + 1]`; the fallback branch returns `description.strip()`.
- No em dashes introduced in any edited text (grep confirmed zero hits).
- The emitted dict shape (`name`, `model`, `kind`, `purpose`), skip-when-missing behavior, and name-sorted output are unchanged.
- The shared `parse_frontmatter` helper is untouched.
- `./ai-infrastructure/project-manager/STATUS.md` was not touched (per kickoff STATUS deltas: leave untouched).

Expected outcome when the Orchestrator re-runs extraction against the six agent files: `kickoff-checker`'s purpose will read the full first sentence up to the period before the first space following `)` in the sentence ending "...section 'Kickoff drafting convention')." rather than truncating at the period inside `./docs`. The other five agents whose descriptions do not have a path-embedded period before the sentence end are unaffected.
