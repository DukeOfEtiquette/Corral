---
schema_version: 1
id: COR-T-049
title: "Sweep retired milestone vocabulary + cleared gating from all department STATUS narratives"
status: done
labels: []
priority: P2
created: 2026-06-13
updated: 2026-06-13
---

## Description

The ADR-036 vocabulary cascade (COR-T-042) deliberately scoped itself to three doc spots plus the `tasks/README.md` Vocabulary section and **did not touch any `STATUS.md` narrative**. As a result the hand-authored "Current phase" / "Next step" / "Blocked on" prose in the STATUS files still carries the retired `P<phase>-<n>` milestone-ID scheme that ADR-036 retired, and in places carries stale gating (preconditions that have since cleared). This was surfaced 2026-06-13 by the backend-api department survey ("file P2-2/P2-3 when DB-T-001 is under way" - but DB-T-001 is done).

Two STATUS narratives were already corrected coordinator-direct as STATUS hygiene at filing time and are **out of scope** here:

- `ai-infrastructure/project-manager/STATUS.md` (Current phase + Blocked on) - fixed.
- `ai-infrastructure/backend-api/STATUS.md` (Next step) - fixed.

### Scope

Sweep every remaining `ai-infrastructure/*/STATUS.md` narrative for both defects:

1. **Retired milestone vocabulary.** Replace the `P<phase>-<n>` milestone IDs (for example `P2-1`, `P2-2`, `P2-3`) with current ADR-036 taxonomy: Phase / Epic / Task references (for example "the Database epic `DB-E-001`", "the Backend API epic", "`API-T-001`"). Vocabulary source of truth is ADR-036 (`ai-infrastructure/project-manager/decisions/ADR-036-work-item-taxonomy.md`) and the Vocabulary section of `ai-infrastructure/project-manager/tasks/README.md`.
2. **Cleared gating.** Rewrite forward-intent prose whose stated precondition has since cleared (for example "downstream is ... when the schema is under way" when the schema epic is done).

Known hit at filing time (re-verify against disk when picked up; treat as a survey, not an exhaustive list):

- `ai-infrastructure/database/STATUS.md` - lines ~12 and ~16 carry `P2-1`, `P2-2`, `P2-3`.

Do NOT touch the dogfood-*event* sense of "milestone" anywhere (it is correct as written, per the COR-T-042 do-not-touch list), and do not rewrite derived dashboard/roadmap surfaces (those are already drift-proof via COR-T-045 / COR-T-047); this task is only the hand-authored STATUS narrative prose.

Routes through the dispatched-worker flow as a documentation deliverable (the COR-T-042 precedent).

Related: ADR-040 (pending) frames the root-cause question - whether the hand-authored STATUS narrative should remain a standing drift surface at all. This task is the one-time cleanup regardless of how ADR-040 resolves; if ADR-040 introduces a guard, fold that in then.

## Activity log

- 2026-06-13: Created in backlog. Surfaced by the backend-api department survey (retired P2-2 vocabulary + stale DB-T-001 gating). The two STATUS narratives the operator named were fixed coordinator-direct at filing time; this task covers the remaining department STATUS files (known: database). Filed but not dispatched. Unlabelled per ADR-031.
- 2026-06-13: Picked up (in-progress). Routing through the dispatched-worker flow (documentation deliverable, COR-T-042 precedent) per operator direction. Zero anticipated decisions: target verified (only `database/STATUS.md` remains among the three `ai-infrastructure/*/STATUS.md` files), vocabulary mapping pinned to ADR-036 + tasks/README Vocabulary, current-state facts verified (DB-E-001 complete; downstream is the Backend API epic).
- 2026-06-13: Done. Dispatched executor made a minimal-diff edit to `database/STATUS.md` (Current phase heading `P2-1` -> `Database schema-and-migrations epic (DB-E-001)`; Next step downstream clause `backend-api P2-2/P2-3` -> `the Backend API epic (Phase 2): FastAPI endpoints (API-T-001) and auth/sessions`), preserving all technical content. Drafter+checker PASS iteration 1 (0 findings); prelaunch W1 PASS; close W2 PASS. Independently verified against disk: `grep -rn 'P[0-9]-[0-9]' ai-infrastructure/*/STATUS.md` returns no hits across all three STATUS files; preserved DB-T/DB-E refs and Blocked-on intact. Deliverable + the two coordinator-direct STATUS fixes + kickoff/report pair committed in db39ec4 (ADR-024). Follow-up: ADR-040 (pending) frames whether the hand-authored STATUS narrative should remain a standing drift surface; triage when ready to resolve.
