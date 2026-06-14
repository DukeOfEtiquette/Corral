---
schema_version: 1
adr: 41
title: "Guard derived phase-completeness against unfiled epics"
status: "pending"
date: "2026-06-14"
related_adrs: [21, 30, 31, 36, 37, 40]
supersedes: []
superseded_by: null
---

# ADR-041: Guard derived phase-completeness against unfiled epics

> Pending. This ADR reserves a number and frames the question; the Alternatives, Decision, and Consequences are stubs to be filled in when it is taken up. Promotes observation COR-08.

## Context

ADR-037 made the roadmap a derived view: the dashboard ETL reconstructs the phase -> epic -> task structure from the `epics/` and `phases/` files and rolls status up per ADR-036 (a phase is done when all its epics are done; an epic is done when it has at least one task and all are done). ADR-040 extended the same derive-everything direction to the STATUS narrative.

On 2026-06-14, COR-T-050 phase-1 verification surfaced a false positive in that derivation (logged as COR-08). The running dashboard showed `current_phase: 3` / `next_step: ""`. Root cause: Phase 2's only *filed* epic, `DB-E-001` (database), was done, and the Backend API epic existed only in intent (the `backend-api` workspace had no `epics/` tree yet, lazy creation per ADR-021/ADR-031). With every filed Phase-2 epic done, the rollup marked Phase 2 done and advanced `current_phase` to Phase 3 (which has no epics, hence the empty `next_step`). The instance was fixed by filing the Backend API forming epic `API-E-001` (0 tasks -> `planned`), restoring Phase 2 as current.

The general problem is structural, not a one-off: **a derived completeness surface is only as correct as its source files are complete.** An epic that is anticipated but not yet filed makes its phase read prematurely done. This is the flip side of the full-derivation push and a continuation of the COR-03 lineage (each derivation removes a hand-maintained surface but introduces a new correctness dependency, here eager epic filing). The roster of which departments belong to which phase is itself known (ADR-021 candidate departments; the phase/epic `dept` linkage in ADR-036), so the gap between "a phase's departments" and "the epics actually filed for that phase" is mechanically detectable. This ADR frames how to close it.

## Alternatives considered

> Stubs - dimensions to work when this ADR is taken up. Not yet decided.

### Option A: Discipline only (file forming epics eagerly)

Make it a convention that a department's first (forming) epic is filed when the department is stood up (the create-department recipe, ADR-030) or when its phase becomes active, so no active phase is ever epic-empty while work is anticipated. No code change; a convention in `tasks/README.md` and the recipe. Question: is an unenforced convention sufficient given this drift already slipped through once?

### Option B: Dashboard consistency check (owned-but-advisory)

Add a check in the ETL (the ADR-036 consistency-check family, owned-but-advisory per ADR-035/ADR-039) that flags a phase reading done while a rostered member department has a non-empty task tree (or simply exists on the roster) but no epic in that phase. The roadmap still derives as today; the check surfaces the suspicious "done." Questions: what is the precise trigger (department has open tasks? department exists at all?); does it warn-only or also suppress the false `done`?

### Option C: Derivation-semantics change

Change the rollup so a phase is not done unless every rostered member department has at least one epic in it (a department-without-an-epic-in-its-active-phase blocks the phase from reading done). More invasive; amends ADR-036's pure epic-rollup. Question: does this over-couple the roster to the rollup (e.g. for phases whose member set is not yet fixed)?

### Option D: Combination (discipline + check)

Adopt the eager-filing discipline (A) and back it with the advisory check (B), mirroring how other COR-NN patterns were resolved (a convention plus a mechanical backstop). Question: is the check redundant once the discipline holds, or is it the needed safety net?

## Decision

> To be filled in when this ADR is taken up.

## Consequences

> To be filled in when this ADR is taken up.
