# Sweep retired milestone vocabulary + cleared gating from the remaining department STATUS narrative (database)

## Target

This is AI-infrastructure work (domain 2, per `ai-infrastructure/project-manager/decisions/ADR-005-two-domains-ai-first.md`), task COR-T-049. The artifact in scope is the hand-authored narrative prose in `ai-infrastructure/database/STATUS.md`. The ADR-036 vocabulary cascade (COR-T-042) deliberately scoped itself out of the `STATUS.md` narratives, so the database department's STATUS still carries the retired `P<phase>-<n>` milestone-ID scheme that ADR-036 retired. Your job is a minimal-diff edit that replaces exactly two retired-milestone-ID spots with current ADR-036 Phase/Epic/Task vocabulary, preserving everything else verbatim. The two peer STATUS files (the coordinator's and backend-api's) were already corrected coordinator-direct and are out of scope. This file has no stale gating to fix; the only defect is retired vocabulary.

## Decisions resolved by the Orchestrator

- **Single target.** Among the three `ai-infrastructure/*/STATUS.md` files, only `ai-infrastructure/database/STATUS.md` still carries retired vocabulary. The coordinator (`ai-infrastructure/project-manager/STATUS.md`) and `ai-infrastructure/backend-api/STATUS.md` were already corrected coordinator-direct and are out of scope. Begin by running the confirming grep `grep -rn 'P[0-9]-[0-9]' ai-infrastructure/*/STATUS.md` and verify that `ai-infrastructure/database/STATUS.md` is the only file with hits. If any other STATUS file unexpectedly hits, sweep it under the same rules below and note it in your report.

- **Defect type: retired milestone vocabulary only.** This file has no stale gating to fix (the database work is done and its downstream is described accurately). The only change is replacing the retired `P<phase>-<n>` milestone IDs with ADR-036 taxonomy (Phase / Epic / Task). Exactly two spots, both verified against disk:
  1. The "## Current phase" body heading at line 12 currently reads `**P2-1 delivered and test-covered.**`. Reword the heading so it no longer uses the retired `P2-1` milestone ID while keeping the same meaning (the Phase 2 schema work is delivered and test-covered). For example, a Phase/Epic framing such as the Database schema-and-migrations epic being delivered and test-covered. You author the exact wording; the constraint is: no `P2-1`, meaning preserved.
  2. The "## Next step" clause at line 16 currently reads `Immediate downstream is backend-api P2-2 (FastAPI endpoints) and P2-3 (auth/sessions), built against this tested schema.`. Reword to name the downstream as the Backend API epic (Phase 2) and its work (FastAPI endpoints, auth/sessions) without the retired `P2-2` / `P2-3` IDs.

- **Vocabulary source of truth (pinned).** `ai-infrastructure/project-manager/decisions/ADR-036-work-item-taxonomy.md` plus the "Vocabulary" section of `ai-infrastructure/project-manager/tasks/README.md`. Under ADR-036 the canonical terms are Roadmap / Phase / Epic / Task / ADR; the `P<phase>-<n>` milestone-ID scheme is retired.

- **Current-state facts (pinned so you do NOT survey to discover them).** The database department's epic is `DB-E-001` (schema & migrations), and it is complete (`DB-T-001`, `DB-T-002`, `DB-T-003` all done). The downstream consumer is the Backend API epic in Phase 2 (department `backend-api`); its first surface will be `API-T-001` (FastAPI endpoints), followed by auth/sessions and migrations + admin seeding. The active phase is Phase 2, titled "API + DB core". Do not re-derive these facts by surveying the trees; they are pinned here.

- **Preserve everything else verbatim.** All accurate technical content stays: the `DB-T-001` / `DB-T-002` / `DB-T-003` and `DB-E-001` task/epic references (these are already correct ADR-036 vocabulary; do not alter), the migration `0001` / `app/db/` / compose `test` and `test-roundtrip` details, and the "## Blocked on" section (`Nothing. The workspace is ready for work.` is accurate). Change ONLY the two retired-milestone-ID spots above. This is a minimal-diff edit, not a rewrite.

- **Do not touch the dogfood-event sense of "milestone"** anywhere (none appears in this file, but the rule holds), and do not touch any derived dashboard / roadmap / ETL surface (those are already drift-proof via COR-T-045 / COR-T-047). This task is hand-authored STATUS narrative prose only.

## Deliverables

- `ai-infrastructure/database/STATUS.md` edited so the "## Current phase" heading and the "## Next step" downstream clause use ADR-036 Phase/Epic/Task vocabulary instead of the retired `P2-1` / `P2-2` / `P2-3` milestone IDs, with all other content preserved verbatim (minimal diff).
- The six-section closing report at the derived report path, including a confirming-grep result showing no `P[0-9]-[0-9]` milestone IDs remain in any `ai-infrastructure/*/STATUS.md` narrative.

## Files in scope

- `ai-infrastructure/database/STATUS.md`

## Files out of scope

- `ai-infrastructure/project-manager/STATUS.md` (already corrected coordinator-direct; do not touch)
- `ai-infrastructure/backend-api/STATUS.md` (already corrected coordinator-direct; do not touch)
- Any derived dashboard / roadmap / ETL surface (drift-proof already; not narrative prose)
- The dogfood-event sense of "milestone" wherever it appears (correct as written)

## References

- `ai-infrastructure/project-manager/decisions/ADR-036-work-item-taxonomy.md` (the work-item taxonomy: canonical Roadmap / Phase / Epic / Task / ADR terms; retires the `P<phase>-<n>` milestone-ID scheme)
- `ai-infrastructure/project-manager/tasks/README.md` (the "Vocabulary" section: the operating how for ADR-036, with the term table and storage convention)
- `ai-infrastructure/project-manager/tasks/in-progress/COR-T-049-status-narrative-vocabulary-sweep.md` (this task file: scope, known hit, and the do-not-touch list)

## Related tasks and ADRs

- ADR-036 - the work-item taxonomy whose vocabulary is being applied (retires the `P<phase>-<n>` milestone IDs).
- COR-T-042 - the prior ADR-036 vocabulary cascade that deliberately scoped OUT all STATUS narratives; this task is the follow-on that finishes the STATUS files.
- ADR-040 (pending) - frames the root-cause question (should the hand-authored STATUS narrative remain a standing drift surface); informational only, no action in this task.
- COR-T-045 / COR-T-047 - made the derived roadmap/activity surfaces drift-proof; those surfaces are explicitly out of scope here.

## STATUS deltas

This task's deliverable IS a STATUS narrative edit, so `ai-infrastructure/database/STATUS.md` legitimately appears in your "Files touched": the "## Current phase" heading and the "## Next step" downstream clause are reworded from the retired `P2-x` milestone IDs to ADR-036 Phase/Epic/Task vocabulary. There is no separate coordinator STATUS delta (the coordinator's STATUS.md was already corrected and is out of scope). The activity surface (`last_updated`, `recent_updates`) is git-derived per ADR-039 and is never hand-edited.

## Hard rules

- Minimal diff: change only the two retired-milestone-ID spots. Do not reflow, reorder, or reword any other prose, and do not alter the `DB-T-001/002/003`, `DB-E-001`, migration `0001`, `app/db/`, or compose `test` / `test-roundtrip` content.
- Preserve the meaning of each edited spot exactly; the edit removes the retired ID scheme, it does not change what the sentence asserts.

## Executor pointer

The executor is the dispatched `executor` (ADR-028). Universal executor conventions (the writing rules and Agent Discipline in `./CLAUDE.md`, the compose-only run policy, git boundaries, and the pinned six-section report shape) live in `docs/ai-orchestration/roles/EXECUTOR-ROLE.md`; follow them rather than re-deriving them here. The closing report is written to the derived report path alongside this kickoff per `EXECUTOR-ROLE.md`, section "Report shape".
