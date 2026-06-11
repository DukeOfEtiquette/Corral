# Observations

Append-only log of recurring patterns, friction points, and notable one-offs seen while working in the `Database` department. Convention inherited from the coordinator workspace (see `ai-infrastructure/project-manager/OBSERVATIONS.md`).

## Conventions

- Stable IDs: `DB-NN`, monotonically increasing, never reused.
- Lifecycle: **seen-once** (handled ad hoc, not yet logged) -> **logged** (an entry below, with context) -> **promoted** (canonicalized into a rule, template, role doc, or ADR; the entry records where it went).
- Entries are never edited after the fact except to update their lifecycle state and promotion pointer.

## Entry format

```markdown
### DB-NN: short title
- date: YYYY-MM-DD
- state: logged | promoted -> <where>
- context: what happened, where
- pattern: why this might recur / what to do about it
```

## Log

### DB-01: WORKER-ROLE wrap-up STATUS hygiene hardcoded the coordinator STATUS
- date: 2026-06-11
- state: promoted -> `docs/ai-orchestration/roles/WORKER-ROLE.md` ("Wrap-up STATUS hygiene" generalized to the kickoff-named workspace STATUS)
- context: During DB-T-001 (the first department deliverable dispatched under ADR-031's per-department task trees), `WORKER-ROLE.md`'s "Wrap-up STATUS hygiene" section named `ai-infrastructure/project-manager/STATUS.md` as the universal hygiene target. For a database-department task the correct target is the department STATUS (`ai-infrastructure/database/STATUS.md`). The orchestrator had to redirect the target via the kickoff's `status_deltas` so the worker neither touched the wrong STATUS nor escalated a kickoff-vs-convention conflict.
- pattern: the shared role docs predate ADR-031 (per-department task trees) and still assume a single coordinator STATUS; every department task hits this. Fixed at the source by generalizing the hygiene target to the workspace STATUS the kickoff names. The per-kickoff `status_deltas` redirect remains valid as the explicit override. Watch for other coordinator-hardcoded references in the shared role docs (for example survey-avoidance clauses) as more departments run tasks.
