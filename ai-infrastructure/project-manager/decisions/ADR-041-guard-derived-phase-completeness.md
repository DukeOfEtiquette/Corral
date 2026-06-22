---
schema_version: 1
adr: 41
title: "Guard derived phase-completeness against unfiled epics"
status: "accepted"
date: "2026-06-14"
related_adrs: [21, 30, 31, 35, 36, 37, 40]
supersedes: []
superseded_by: null
---

# ADR-041: Guard derived phase-completeness against unfiled epics

> Accepted 2026-06-14. Promotes observation COR-08. Adopts the eager-forming-epic discipline plus a dashboard consistency check (Option D), the same convention-plus-check model ADR-036 uses for its cardinality minimums. Does not change ADR-036's rollup semantics.

> **Forward pointer (2026-06-22):** ADR-045 adds another owned-but-advisory check to this ETL warning family: a service's declared port in its `services.yml` versus the value in `app/docker-compose.yml`. Same warn-only, does-not-alter-derived-status model as the checks here. See ADR-045.

## Context

ADR-037 made the roadmap a derived view: the dashboard ETL reconstructs the phase -> epic -> task structure from the `epics/` and `phases/` files and rolls status up per ADR-036 (a phase is done when all its epics are done; an epic is done when it has at least one task and all are done). ADR-040 extended the same derive-everything direction to the STATUS narrative.

On 2026-06-14, COR-T-050 phase-1 verification surfaced a false positive in that derivation (logged as COR-08). The running dashboard showed `current_phase: 3` / `next_step: ""`. Root cause: Phase 2's only *filed* epic, `DB-E-001` (database), was done, and the Backend API epic existed only in intent (the `backend-api` workspace had no `epics/` tree yet, lazy creation per ADR-021/ADR-031). With every filed Phase-2 epic done, the rollup marked Phase 2 done and advanced `current_phase` to Phase 3 (which has no epics, hence the empty `next_step`). The instance was fixed by filing the Backend API forming epic `API-E-001` (0 tasks -> `planned`), restoring Phase 2 as current.

The general problem is structural, not a one-off: **a derived completeness surface is only as correct as its source files are complete.** An epic that is anticipated but not yet filed makes its phase read prematurely done. This is the flip side of the full-derivation push and a continuation of the COR-03 lineage (each derivation removes a hand-maintained surface but introduces a new correctness dependency, here eager epic filing). The roster of which departments belong to which phase is itself known (ADR-021 candidate departments; the phase/epic `dept` linkage in ADR-036), so the gap between "a phase's departments" and "the epics actually filed for that phase" is mechanically detectable. This ADR frames how to close it.

## Alternatives considered

### Option A: Discipline only (file forming epics eagerly)

Make it a convention that a department's first (forming) epic is filed when the department is stood up (the create-department recipe, ADR-030) or when its phase becomes active, so no active phase is ever epic-empty while work is anticipated. No code change; a convention in `tasks/README.md` and the recipe. Adopted as half the decision: it closes the gap at the source (a department is never epic-empty), but on its own it is unenforced and already slipped once (backend-api), so it is paired with the check.

### Option B: Dashboard consistency check (owned-but-advisory)

Add a check in the ETL (the ADR-036 consistency-check family, owned-but-advisory per ADR-035/ADR-039) that flags a phase reading done while a rostered member department has a non-empty task tree (or simply exists on the roster) but no epic in that phase. The roadmap still derives as today; the check surfaces the suspicious "done." Adopted as the other half: the precise trigger is an existing department (DEPARTMENTS_ROSTER `exists`) with zero epics (the exact signature of the surfaced bug, independent of task counts); warn-only (owned-but-advisory), it does not suppress or alter the derived status.

### Option C: Derivation-semantics change

Change the rollup so a phase is not done unless every rostered member department has at least one epic in it (a department-without-an-epic-in-its-active-phase blocks the phase from reading done). More invasive; amends ADR-036's pure epic-rollup. Rejected: phase files do not encode member departments today (just id/title/description/order), so this needs new phase-to-department data, and it over-couples the ADR-021 roster to ADR-036's rollup semantics for no gain the discipline-plus-check does not already provide.

### Option D: Combination (discipline + check) (selected)

Adopt the eager-filing discipline (A) and back it with the advisory check (B), mirroring how other COR-NN patterns were resolved (a convention plus a mechanical backstop). Selected: the discipline prevents the gap at creation, and the check is the safety net for departments created by hand or before the recipe change. The two are not redundant; each covers what the other misses. This is exactly how ADR-036 enforces its `>= 2` cardinality minimums (a discipline plus a dashboard consistency check).

## Decision

Adopt Option D.

1. **Eager forming-epic discipline.** A department files at least one (forming) epic for its active or next phase at stand-up time, so its anticipated work is represented in the derived roadmap and no active phase reads done while a member department is unrepresented. Encoded in two places: a step in the ADR-030 create-department recipe (stamp a forming epic alongside the workspace), and a convention in the `tasks/README.md` "Epics and phases" section. A forming epic with zero tasks is legitimate (`planned`) per ADR-036's intended-shape allowance.

2. **Dashboard consistency check (owned-but-advisory).** A new check in `etl.py`, joining the existing warning family (`phase_warning`, `epic_warning`, `cross_dept_warning`), flags any existing department (DEPARTMENTS_ROSTER `exists` true) that has zero epics, rendered as an advisory warning on the dashboard. It is warn-only per the ADR-035 / ADR-039 owned-but-advisory model: it surfaces the smell and does not change or suppress the derived phase/epic status.

3. **Rollup semantics unchanged (Option C rejected).** ADR-036's rule (a phase is done when all its epics are done) is not amended; no phase-to-department membership data is added and done-ness is not gated on it. The discipline keeps the epic set complete, the check backstops it, and the derivation stays simple.

4. **Implementation spawns as a task.** The etl check plus the recipe and convention edits are a dispatched follow-on, COR-T-051 (the analog of how ADR-040 spawned COR-T-050).

## Consequences

1. **The false-"done" class is mitigated at two layers.** The discipline prevents the gap at department creation (no existing department is epic-empty); the check catches any department that slips through (created by hand, or before the recipe step existed). Neither alone suffices: the discipline is unenforced, the check is after-the-fact.

2. **The create-department recipe gains a forming-epic step (amends ADR-030).** Newly stamped departments carry a roadmap presence from day one. A forward-pointer note is added to ADR-030.

3. **The check joins the existing warning family at near-zero cost (extends ADR-036).** The etl warning infrastructure and its dashboard rendering already exist; this is one more advisory warning, not new machinery. ADR-036's rollup semantics are untouched; a forward-pointer note is added to ADR-036.

4. **The roster is the check's input (ADR-021).** The check reads DEPARTMENTS_ROSTER `exists` to distinguish existing departments (which should have an epic) from planned ones (which should not yet).

5. **The instance that surfaced this is already fixed.** Phase 2 / backend-api was corrected by filing API-E-001 (commit 530b671), so the check currently passes; ADR-041 guards against recurrence rather than fixing a live defect.

6. **COR-08 reaches promoted.** The observation is canonicalized here; its lifecycle note points to this ADR.

7. **Cost: COR-T-051.** A small dispatched task: one etl check plus its dashboard rendering, and the recipe and `tasks/README.md` convention edits.
