# Mark planned departments in the dashboard org chart

## Target

This is AI-infrastructure work (ADR-005): the project-manager dashboard is a domain-2 tooling artifact, not part of the web app. The task (COR-T-022) is a small, surgical change to the dashboard ETL so that the org-chart panel distinguishes departments that actually exist from those that are merely blessed-but-planned. The artifact in scope is `build_org_chart` and its single call site in `run_etl`, both in `ai-infrastructure/project-manager/dashboard/etl.py`.

## Decisions resolved by the Orchestrator

- **Problem being fixed:** `build_org_chart` currently renders every entry of the hardcoded `DEPARTMENTS_ROSTER` (the ADR-021 blessed roster) with no created-vs-planned distinction. Blessed-but-not-instantiated departments (`agent-development`, `test-design`, `docs-curation`, and the five web-app departments) appear in the chart as if they exist, which contradicts the Departments panel that already badges each department `exists` vs `planned`. Only `project-manager` is actually instantiated today (ADR-027: lazy department creation).
- **The fix:** In `build_org_chart`, append the literal suffix `" (planned)"` to each department whose `exists` flag is false. Render created departments and the coordinator root line with NO suffix. The wording `"(planned)"` matches the Departments panel badge text, for cross-panel consistency.
- **Wiring (the load-bearing change):** `build_org_chart` is currently called as `build_org_chart(DEPARTMENTS_ROSTER)`; roster entries carry only `slug` and `domain`, with no existence information. Change the call site in `run_etl` to pass the already-computed `departments` list instead. That list carries the `exists` boolean (derived from `dept_exists`) for each entry, alongside `slug` and `domain`. `build_org_chart` then reads each entry's `exists` to decide the suffix; treat a missing or falsey `exists` as planned.
- **The `departments` list is already available at the call site:** it is built earlier in `run_etl` (the loop over `DEPARTMENTS_ROSTER` that produces dicts with `slug`, `domain`, `exists`, and more), and that loop runs before the `org_chart = build_org_chart(...)` line. No reordering of `run_etl` is needed; just pass `departments` instead of `DEPARTMENTS_ROSTER`.
- **Scope limit, text only:** the planned marker is plain text inside the `org_chart` string the ETL emits. `OrgChartPanel` renders that string verbatim inside a `<pre>`, so NO JSX or CSS change is needed or wanted. The data.json contract keeps `org_chart` as a string; only its content gains the markers, so the JSON shape is unchanged.
- **Preserve the tree structure exactly:** keep the domain grouping (AI-infrastructure domain, then Web-app domain), the ASCII tree connectors (`+--`, the backtick-dash last-child connector, the indentation), and the coordinator root line exactly as they are now. Only the per-department label text changes; the connector logic and grouping are untouched.
- **Docstring:** update the `build_org_chart` docstring to note the planned-suffix behavior.
- **No em dashes:** per the global writing rule in `./CLAUDE.md`, use a comma, colon, semicolon, or rephrase. This binds both code comments and the docstring you edit.

## Deliverables

- `ai-infrastructure/project-manager/dashboard/etl.py`, function `build_org_chart`: appends `" (planned)"` to each non-created department label (driven by the actual `exists` flag, treating missing/falsey as planned); created departments and the coordinator root line are unmarked. The domain grouping and ASCII connectors are preserved exactly.
- `ai-infrastructure/project-manager/dashboard/etl.py`, the call site in `run_etl`: passes the already-computed `departments` list instead of `DEPARTMENTS_ROSTER`.
- `ai-infrastructure/project-manager/dashboard/etl.py`, the `build_org_chart` docstring: updated to describe the planned-suffix behavior.
- Universal STATUS hygiene only (see STATUS deltas below).

## Files in scope

- `ai-infrastructure/project-manager/dashboard/etl.py` (only `build_org_chart` and its call site in `run_etl`)
- `ai-infrastructure/project-manager/STATUS.md` (universal hygiene only)

## Files out of scope

- `ai-infrastructure/project-manager/dashboard/src/panels/OrgChartPanel.jsx`: it renders the `org_chart` string verbatim in a `<pre>`; a text marker is sufficient and no JSX change is needed. Do NOT edit.
- `ai-infrastructure/project-manager/dashboard/src/panels/DepartmentsPanel.jsx`: it already badges `exists` vs `planned`; it is the wording source, not a target. Do NOT edit.
- `DEPARTMENTS_ROSTER` in `etl.py`: the roster content is unchanged; ADR-021 owns it. Do NOT add an `exists` field to roster entries; existence comes from the computed `departments` list.
- The data.json contract shape: `org_chart` stays a string. Do NOT change its type or the surrounding `data` dict structure.
- `Dockerfile`, `docker-compose.yml`, `entrypoint.sh`: no runtime change.
- The `tasks/` tree and all ADRs.

## References

- `ai-infrastructure/project-manager/dashboard/etl.py`: `build_org_chart` is around lines 167-189 (currently takes a `departments` list parameter but reads only `slug` and `domain` to build the ASCII tree). The call site is around line 368 (`org_chart = build_org_chart(DEPARTMENTS_ROSTER)`). The computed `departments` list, carrying the `exists` flag per entry, is built around lines 343-357. `dept_exists` is defined around lines 327-328. `DEPARTMENTS_ROSTER` is around lines 62-71.
- `ai-infrastructure/project-manager/dashboard/src/panels/OrgChartPanel.jsx`: read for context only, to confirm it renders the `org_chart` string verbatim so a text marker suffices and no JSX change is needed. Do NOT edit it.
- `ai-infrastructure/project-manager/dashboard/src/panels/DepartmentsPanel.jsx`: read for context only, to match the `planned` wording it already uses for its badge. Do NOT edit it.

## Related tasks and ADRs

- COR-T-014: built the dashboard and the org chart; the origin of `build_org_chart`.
- COR-T-020: made the dashboard live. Note for your report: because `etl.py` is baked into the image, this org-chart change takes effect only after a `docker compose up --build`. The live watch re-runs the existing in-container `etl.py` on markdown changes and will NOT pick up an `etl.py` code change without a rebuild.
- ADR-021: the blessed department roster and the lazy-creation policy; the reason planned departments appear in the chart at all.
- ADR-027: lazily-created department workspaces; only `project-manager` exists today, which is why every other roster entry should read `(planned)`.

## STATUS deltas

No task-specific STATUS deltas; universal hygiene only. Apply universal STATUS hygiene per `./docs/ai-orchestration/roles/WORKER-ROLE.md` (bump `last_updated`, prepend a `recent_updates` entry in `ai-infrastructure/project-manager/STATUS.md`). Do not change the phase, the roadmap block, or "Next step".

## Hard rules

- Change only `build_org_chart` and its one call site in `run_etl`. Do not refactor the surrounding ETL, do not touch `DEPARTMENTS_ROSTER`, and do not alter the `data` dict assembly.
- The `org_chart` value stays a string. The only content change is the `" (planned)"` suffix on non-created department labels.
- Preserve the existing ASCII connectors and domain grouping byte-for-byte except for the per-department label text.
- The coordinator root line (`project-manager (coordinator)`) is never suffixed; it always exists.
- Verify your change by reading the resulting `build_org_chart` against the resolved decisions above; the runtime confirmation (a `docker compose up --build` and a visual check of the rendered chart) is the Orchestrator's gate, not a step in this kickoff.
- Universal conventions (the writing rules and Agent Discipline in `./CLAUDE.md`, the compose-only run policy, git boundaries, the pinned report shape) are referenced, not restated; follow `./docs/ai-orchestration/roles/WORKER-ROLE.md`.

## Worker pointer

You are the dispatched `worker-agent` (ADR-028). Universal worker conventions live in `./docs/ai-orchestration/roles/WORKER-ROLE.md`. Write your closing report to `./.claude/artifacts/handoffs/COR-T-022-KICKOFF-REPORT.md` per WORKER-ROLE.md, section "Report shape".
