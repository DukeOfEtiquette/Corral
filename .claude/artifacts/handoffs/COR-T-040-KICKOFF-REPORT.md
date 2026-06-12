## Deliverables completed

All corrections from attempt 2 re-dispatch applied. Attempt 1 base work stands unchanged.

**Fix 1 (Critical - blank-page regression): RoadmapPanel.jsx**
- Renamed the `ref` prop (reserved React prop, silently dropped, causing `r` to be `undefined` and crashing the tree) to `badge` at all 4 component destructures and all 5 call sites:
  - `function SingleBadge({ badge: r })` (was `ref: r`)
  - `function RangeBadge({ badge: r })` (was `ref: r`)
  - `function UnresolvedBadge({ badge: r })` (was `ref: r`)
  - `function RefBadge({ badge: r })` (was `ref: r`)
  - `<RangeBadge badge={r} />` (was `ref={r}`)
  - `<UnresolvedBadge badge={r} />` (was `ref={r}`)
  - `<SingleBadge badge={r} />` (was `ref={r}`)
  - `<RefBadge key={i} badge={r} />` (was `ref={r}`)
- Swept the file for other reserved-prop usage: `key` is used correctly as the list key (built-in list key, fine); no other `ref` data-prop usage found.
- The internal local name `r` is preserved throughout; only the prop name changed.

**Fix 2 (Rollup semantic): etl.py `derive_effective_status`**
- Updated the function to filter refs to `type == 'task'` before rolling up for effective status.
- If task refs exist: roll up only those (all done/accepted -> 'done'; any in-progress/blocked -> 'in-progress'; else 'planned').
- If zero task refs (regardless of ADR refs): fall back to hand-set `status` frontmatter field.
- ADR refs are still resolved and emitted in the `refs` list for badge rendering; they do not influence `effective_status`.
- `resolve_milestone_refs` is unchanged; badge output and flavor for ADRs is unchanged.

**Attempt 1 deliverables (unchanged, carried forward):**
- `etl.py`: reference-resolution helpers (`expand_range_token`, `resolve_ref_status`, `_rollup_statuses`, `resolve_milestone_refs`, `derive_effective_status`), roadmap assembly reordered so `all_tasks`/`adrs` collected before roadmap, `derive_current_phase`/`derive_next_step` updated to use effective status, per-milestone `effective_status` + `refs` emitted, module docstring updated.
- `RoadmapPanel.jsx`: phase and milestone status badge removed, `STATUS_LABELS`/`MILESTONE_STATUS_LABELS` removed, `refBadgeClass` + sub-components render `ms.refs`.
- `styles.css`: `.badge-ref*` classes added (done/in-progress/blocked/planned/mixed/unresolved).

## Decisions made

- **Prop rename scope**: All 4 destructure sites and all call sites (including the map call in `RoadmapPanel`'s render) renamed. The `key={i}` on `<RefBadge>` is correct (list key, not a data prop) and was left as-is.
- **No-cache rebuild required**: The earlier build had cached layers for the JS build stage. A `--no-cache` rebuild was run to ensure the updated JSX was compiled into the bundle. Build succeeded: 292 modules transformed, Vite bundle produced without error.
- **Task-only rollup**: A range token in a `tasks:` list has `type: 'task'` (set by `process_list` in `resolve_milestone_refs` via `expected_type_hint`), so task ranges count as task refs and drive done-ness. A range token in an `adrs:` list has `type: 'adr'` and is informational only.

## Surprises

- The attempt 1 build had cached the build stage from before the JSX edits. A `--no-cache` rebuild was needed to pick up the `RoadmapPanel.jsx` changes. Both builds (cache-hit and no-cache) succeeded; the no-cache build is the one that contains Fix 1.
- No new surprises beyond what attempt 1 recorded (ADR-011 is `accepted` not `pending`).

## Follow-ups

- **P2-3/P2-4 milestone status drift**: The hand-set `status: planned` on P2-3 and P2-4 is now the fallback for `effective_status` (as intended by Fix 2: ADR-only milestones fall back to hand-set). The field is accurate. However, the attempt 1 surprise (ADR-011 is actually `accepted`) means the kickoff's stated expectation was stale. The Orchestrator may want to update P2-3 hand-set `status` to reflect the ADR being accepted, or document that the escape-hatch field governs only the phase/current-step derivation for ADR-only milestones. Triage to Orchestrator.
- **ADR template (ADR-000)**: The `collect_adrs` scan picks up an ADR with `id='0'` and `status='template'`. Harmless but creates a spurious entry in the ADR list. Low-priority cleanup. COR-T candidate.

## Files touched

- `./.claude/artifacts/handoffs/COR-T-040-KICKOFF-REPORT.md` (this file)
- `./ai-infrastructure/project-manager/dashboard/etl.py`
- `./ai-infrastructure/project-manager/dashboard/src/panels/RoadmapPanel.jsx`

## Build / verification status

**Build:** `docker compose -f ai-infrastructure/project-manager/dashboard/docker-compose.yml up --build` with `--no-cache` ran successfully. Vite built 292 modules, ETL ran, wrote `/served/data.json` (255307 bytes) without error.

**Fix 2 effective_status verification (from live data.json):**

| Milestone | Task refs | ADR refs | Expected effective_status | Actual |
|---|---|---|---|---|
| P2-3 | none | ADR-011 (accepted) | planned (hand-set fallback) | planned |
| P2-4 | none | ADR-014, ADR-006 (accepted) | planned (hand-set fallback) | planned |
| P0-2 | none | ADR-001..009 range (accepted) | done (hand-set fallback) | done |
| P2-1 | DB-T-001 (done) | ADR-012 (accepted) | done (task drives it) | done |
| P0-3 | COR-T-001..006 range (all done) | none | done | done |
| P1-1/P1-4/P1-6/P2-0 | single task (done) | none | done | done |

All Fix 2 expectations confirmed. ADR badges for P2-3 and P2-4 still render green (informational); `effective_status` for those milestones is `planned` (hand-set fallback).

**current_phase and next_step:** `current_phase: 2`, `next_step: "P2-2: FastAPI endpoints with house rules"`. Correct.

**Fix 1 reasoning:** The `badge` prop is a non-reserved name; React forwards it to the function component normally, making `r` defined inside each badge component. The `r.resolved_status`, `r.label`, `r.member_count`, `r.rollup_status`, and `r.flavor` accesses are all safe. No undefined-access patterns remain. The `key={i}` on `<RefBadge>` is a list key (built-in React mechanism, not a data prop), so it is correct and unchanged.

**Visual render confirmation:** Not performed by this executor. The user performs visual confirmation after compose up on port 8420.

**No-live-instance branches (code-confirmed, not live-verified):**
- `in-progress` badge: fires when a task ref resolves to the `in-progress` directory or range rollup includes in-progress/blocked.
- `blocked` badge: fires when a task ref resolves to the `blocked` directory.
- `mixed` range badge: fires when a range has differing member statuses with no in-progress/blocked.
- `unresolved` badge: fires when an ID resolves to no record in the task or ADR pool.
