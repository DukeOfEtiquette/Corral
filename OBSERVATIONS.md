# Observations

Append-only log of recurring patterns, friction points, and notable one-offs seen while working in this repo. Convention inherited from rogue (ADR-009).

## Conventions

- Stable IDs: `COR-NN`, monotonically increasing, never reused.
- Lifecycle: **seen-once** (handled ad hoc, not yet logged) -> **logged** (an entry below, with context) -> **promoted** (canonicalized into a rule, template, role doc, or ADR; the entry records where it went).
- Entries are never edited after the fact except to update their lifecycle state and promotion pointer.

## Entry format

```markdown
### COR-NN: short title
- date: YYYY-MM-DD
- state: logged | promoted -> <where>
- context: what happened, where
- pattern: why this might recur / what to do about it
```

## Log

### COR-01: pending-ADR leaning text drifts against sibling docs

- date: 2026-06-05
- state: logged
- context: While resolving anticipated decisions for COR-T-002 (ADR-012 schema), the Orchestrator found `./tasks/README.md` (migration mapping) pinning `priority` as an issue column while `./decisions/ADR-018-department-label-taxonomy.md` (Option A leaning text) listed `priority:P0..P3` as a reserved label family. Both were written during Phase 0 bootstrap; neither was a taken decision. Resolved with the user 2026-06-05: priority is a first-class column, and the COR-T-002 kickoff directs ADR-012's Consequences to record the narrowing of ADR-018's open question.
- pattern: Pending ADRs carry leaning text and examples drafted before any decision was taken; sibling pending ADRs and convention docs can encode contradictory assumptions about the same dimension. Each resolved ADR can silently invalidate a neighbour's framing. When resolving any pending ADR, sweep its `related_adrs` and the convention docs it touches for contradicted leanings, surface conflicts to the user as part of decision resolution, and record narrowings in the accepted ADR's Consequences section.
