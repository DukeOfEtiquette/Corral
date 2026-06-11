# COR-T-029 Worker Report

Kickoff: `.claude/artifacts/handoffs/COR-T-029-KICKOFF.md`
Attempt: 1

---

## Deliverables completed

1. **`./ai-infrastructure/project-manager/dashboard/etl.py` updated** - All changes landed:
   - Added three new derivation functions after `derive_roadmap_status`: `derive_current_phase`, `derive_current_phase_title`, and `derive_next_step`, implementing exactly the pinned derivation rules.
   - Updated `run_etl` (lines 342-355 in the new file): removed the reads of `phase`, `phase_title` from frontmatter and the `extract_next_step(status_path)` call; replaced with calls to the three new functions operating on `roadmap_raw`.
   - Removed `extract_next_step` (confirmed no other callers remained after the change; the function was the sole reader of the `## Next step` section and was referenced only at the now-replaced line 283).
   - Updated the Sources block docstring (a, line 10-12): now describes phase status as derived from per-milestone statuses, not from the top-level `phase` field.
   - Updated the JSON contract docstring (meta line, lines 28-31): now annotates `current_phase`, `current_phase_title`, and `next_step` as DERIVED from roadmap milestone statuses.
   - `derive_roadmap_status(phase_num, current_phase)` function body is unchanged; only its `current_phase` input now comes from derivation rather than frontmatter.

2. **`./ai-infrastructure/project-manager/STATUS.md` updated**:
   - Removed `phase: 2` frontmatter field.
   - Removed `phase_title: "API + DB core: schema, endpoints, auth, migrations"` frontmatter field.
   - Removed the entire `## Next step` body section.
   - `## Current phase` narrative section left intact.
   - `roadmap:` block and all milestones left intact.
   - STATUS hygiene applied: `last_updated` was already `2026-06-11`; prepended one `recent_updates` entry recording COR-T-029 outcomes.

---

## Decisions made

- **Derivation runs before the roadmap loop.** `roadmap_raw` is parsed from frontmatter first, then `derive_current_phase(roadmap_raw)` is called, then the roadmap loop runs using the derived `current_phase` for `derive_roadmap_status`. This ordering mirrors the original code's structure where `current_phase` was available before the loop.

- **`extract_next_step` removed.** Grep confirmed no other caller in `etl.py` after the `next_step = extract_next_step(status_path)` call was removed; the function was deleted.

- **Blank line added between derivation block and roadmap loop.** Minor style consistency fix (within scope of the edit; no unrelated changes).

---

## Surprises

- **`current_phase_title` value differs from the kickoff expectation.** The kickoff stated the expected value as `"API + DB core: schema, endpoints, auth, migrations"` (the old `phase_title` frontmatter value). The roadmap entry's `title` field (line 43 of STATUS.md) is `"API + DB core"` - a shorter form. The derivation correctly returns the roadmap `title`; the kickoff's expected value was based on the now-removed, separately maintained `phase_title` frontmatter field that had a longer form. The derived value `"API + DB core"` is what the roadmap data actually contains. Verified: `curl localhost:8420/data.json` returns `"current_phase_title": "API + DB core"`.

---

## Follow-ups

- **COR-T candidate: update the kickoff verification expectation for `current_phase_title`.** The verification section of the kickoff listed `"API + DB core: schema, endpoints, auth, migrations"` as the expected `current_phase_title`, but the roadmap `title` field is the shorter `"API + DB core"`. If the longer title is desired in the dashboard, the roadmap `title` field in STATUS.md should be updated. This is a content decision for the Orchestrator or user to make, not a derivation bug. Triage to Orchestrator.

---

## Files touched

- `./ai-infrastructure/project-manager/dashboard/etl.py`
- `./ai-infrastructure/project-manager/STATUS.md`
- `./.claude/artifacts/handoffs/COR-T-029-KICKOFF-REPORT.md` (this file)

---

## Build / verification status

**Rebuilt and verified.**

- `docker compose up -d --build` run in `./ai-infrastructure/project-manager/dashboard/`. Container rebuilt with the new `etl.py` baked in; previous container recreated.
- `curl localhost:8420/data.json` confirmed:
  - `meta.current_phase` = 2 (expected: 2)
  - `meta.current_phase_title` = `"API + DB core"` (note: roadmap title is shorter than the old `phase_title` frontmatter; see Surprises)
  - `meta.next_step` = `"P2-2: FastAPI endpoints with house rules"` (expected: same)
  - Roadmap phase statuses: Phase 0 `done`, Phase 1 `done`, Phase 2 `current`, Phases 3-5 `upcoming` (all correct)
- `STATUS.md` structural checks passed:
  - No `phase:` frontmatter field present (grep -n "^phase:": no match)
  - No `phase_title:` frontmatter field present (grep -n "^phase_title:": no match)
  - No `## Next step` heading present (grep -n "^## Next step": no match)
  - `roadmap:` block intact at line 3
  - `## Current phase` section intact at line 150
- Dashboard container left running (port 8420).
- No em dashes introduced in any written file.
