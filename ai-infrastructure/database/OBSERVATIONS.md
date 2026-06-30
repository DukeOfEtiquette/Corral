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

### DB-02: kickoff-drafter dispatched with the directing department's domain, not the artifact's domain
- date: 2026-06-30
- state: logged
- context: During DB-T-006 (a Database-department task editing the web-app-stack files `app/docker-compose.yml` and `app/.env.example`), the orchestrator dispatched `kickoff-drafter` with `domain: ai-infrastructure` (the directing department's domain). Iteration 1 rendered the Target section "This is ai-infrastructure work (ADR-005)". Per ADR-005's two-domains split, the in-scope artifacts are web-app-stack (domain 1) files; the Database department (domain 2) only *directs* the change. The drafter itself flagged the mismatch in its return note. The origin task's kickoff for the identical compose file (`.claude/artifacts/handoffs/API-T-006-IMPL-KICKOFF.md`) had it right: "This is web-app work (domain 1, ADR-005): operability hardening of the `app/` stack, directed by the backend-api department." The orchestrator re-dispatched the drafter (iteration 2) with `domain: web-app` and the directing-department framing; the corrected kickoff passed kickoff-checker, prelaunch, and close cleanly.
- pattern: the kickoff `domain` field tracks the ARTIFACT's domain (which conventions weigh heaviest for the executor), not the directing department's domain. A department orchestrator (DB, backend-api, frontend, etc.) naturally passes its own department's domain, which is `ai-infrastructure` for every department except where it directs a change to `app/` web-app-stack artifacts, where the correct domain is `web-app` (directed by the department). Expect this on every department-directed web-app deliverable. If it recurs, candidate promotions: tighten the "Name the domain" bullet in `ORCHESTRATOR-ROLE.md` ("Kickoff drafting convention") to state domain = the artifact's domain, not the director's, with the API-T-006 / DB-T-006 worked example; or add a `kickoff-drafter` / `kickoff-checker` rule cross-checking the stated domain against `files_in_scope` (any `app/` path implies `web-app`). Two occurrences so far (API-T-006 got it right by hand; DB-T-006 needed an iteration-2 correction); promote on the third.
