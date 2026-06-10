## Deliverables completed

- `ai-infrastructure/project-manager/dashboard/etl.py`, function `build_org_chart` (lines 167-198): updated to read `exists` from each department entry and append `" (planned)"` suffix when `exists` is falsey (via an inner `label()` helper). Created departments and the coordinator root line are unlabelled. The iteration variable changed from `slug` (string) to `dept` (dict) so `label()` can access both `slug` and `exists`. ASCII tree connectors (`+--`, backtick-dash last-child), indentation, and domain grouping (AI-infrastructure then Web-app) are preserved exactly.
- `ai-infrastructure/project-manager/dashboard/etl.py`, call site in `run_etl` (line 377): changed from `build_org_chart(DEPARTMENTS_ROSTER)` to `build_org_chart(departments)`, passing the already-computed list that carries the `exists` boolean per entry. No reordering of `run_etl` was needed; `departments` is built before the call site.
- `ai-infrastructure/project-manager/dashboard/etl.py`, `build_org_chart` docstring: updated to describe the `exists`-driven planned-suffix behavior, the `" (planned)"` suffix for non-created departments, and that the coordinator root line is never suffixed.
- `ai-infrastructure/project-manager/STATUS.md`: universal hygiene applied (last_updated bumped to 2026-06-10; one new `recent_updates` entry prepended).

## Decisions made

- The inner `label()` helper is defined as a nested function inside `build_org_chart`. This is the simplest scope for a one-use formatter that needs access to both `slug` and `exists`; no new module-level helper was added.
- Loop variable renamed from `slug` (string) to `dept` (dict) so the label function can access the full entry. The connector logic is unchanged; only the string passed to `lines.append()` changed from `prefix + slug` to `prefix + label(dept)`.
- Treat `missing/falsey exists` as planned: `d.get("exists")` returns `None` for entries without the key (e.g., `DEPARTMENTS_ROSTER` entries, if ever passed directly), which is falsey, so the suffix fires. This matches the kickoff's "treat a missing or falsey exists as planned" decision.

## Surprises

- None. The `departments` list was confirmed to be built (lines 343-357 in the original, now 343-366 post-edit) before the `build_org_chart` call site. No reordering was needed, matching the kickoff's assertion.
- `OrgChartPanel.jsx` confirmed: renders `{orgChart}` verbatim inside `<pre className="org-chart">` (line 7); no JSX change needed.
- `DepartmentsPanel.jsx` confirmed: uses `<span className="badge badge-planned">planned</span>` (line 43); wording matches the `" (planned)"` suffix exactly.

## Follow-ups

- COR-T-018 (standalone dashboard ETL compose target, backlog): because `etl.py` is baked into the image, this org-chart change takes effect only after `docker compose up --build`. The live watch re-runs the in-container `etl.py` on markdown changes but does NOT pick up an `etl.py` code change without a rebuild (noted per COR-T-020 in the kickoff). Triage to Orchestrator: the Orchestrator's close step handles the compose rebuild gate.

## Files touched

- `ai-infrastructure/project-manager/dashboard/etl.py` (build_org_chart function body + docstring lines 167-198; call site line 377)
- `ai-infrastructure/project-manager/STATUS.md` (last_updated + new recent_updates entry)
- `.claude/artifacts/handoffs/COR-T-022-KICKOFF-REPORT.md` (this report)

## Build / verification status

Code-level verification completed in-session:

- `build_org_chart` at lines 167-198: `label()` returns `d["slug"] + ""` when `d.get("exists")` is truthy; returns `d["slug"] + " (planned)"` when falsey. Coordinator root line `"project-manager (coordinator)"` is hard-coded and never passes through `label()`.
- Call site at line 377: `build_org_chart(departments)` confirmed via grep. The `departments` list is built at lines 343-366 before the call site and carries `exists` per entry.
- ASCII connectors preserved: `"|   +-- "` / `"|   \`-- "` for AI-infra entries, `"    +-- "` / `"    \`-- "` for Web-app entries, unchanged.
- No em dashes in the docstring or code changes.
- `DEPARTMENTS_ROSTER` is untouched; the JSON contract `org_chart` type is unchanged (string).

Runtime confirmation (rendered chart in browser after `docker compose up --build`) is the Orchestrator's close gate per the kickoff's verification altitude note; not a step in this kickoff.
