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
- state: promoted -> `docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md`, "Stale-reference sweep when resolving ADRs" bullet under "Kickoff drafting convention" (promoted 2026-06-05 after occurrences in COR-T-002 (tasks/README vs ADR-018 leaning), COR-T-003 pre-kickoff (README roadmap vs ADR-010 leaning), and COR-T-003 review (ADR-004 consequence staleness))
- context: While resolving anticipated decisions for COR-T-002 (ADR-012 schema), the Orchestrator found `./tasks/README.md` (migration mapping) pinning `priority` as an issue column while `./decisions/ADR-018-department-label-taxonomy.md` (Option A leaning text) listed `priority:P0..P3` as a reserved label family. Both were written during Phase 0 bootstrap; neither was a taken decision. Resolved with the user 2026-06-05: priority is a first-class column, and the COR-T-002 kickoff directs ADR-012's Consequences to record the narrowing of ADR-018's open question.
- pattern: Pending ADRs carry leaning text and examples drafted before any decision was taken; sibling pending ADRs and convention docs can encode contradictory assumptions about the same dimension. Each resolved ADR can silently invalidate a neighbour's framing. When resolving any pending ADR, sweep its `related_adrs` and the convention docs it touches for contradicted leanings, surface conflicts to the user as part of decision resolution, and record narrowings in the accepted ADR's Consequences section.

### COR-02: orchestrator-direct ADR resolution follows a repeatable seven-step flow

- date: 2026-06-10
- state: promoted -> `docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md`, "Pending-ADR resolution playbook" subsection (promoted 2026-06-10 via COR-T-019, after two clean instances: COR-T-008 (ADR-018) and COR-T-009 (ADR-025))
- context: COR-T-008 and COR-T-009 each took a pending ADR to accepted as orchestrator-direct work (the `decisions/` carve-out). Both ran the identical shape: read the pending ADR and its `related_adrs`; do the homework and form grounded recommendations; frame only the binding decisions with the user while letting the mechanical ones flow; set the ADR pending -> accepted; forward-pointer sweep both directions (subsuming COR-01); STATUS hygiene plus the Next-step/roadmap delta; and a two-commit close (accept, then move-to-done citing the accept hash). The shape was stable enough across the two runs to canonicalize.
- pattern: Resolving a pending ADR is a recurring orchestrator-direct task type with a fixed sequence, not an ad hoc activity. Promoted into the role doc so future orchestrators follow the seven steps rather than re-deriving them; the playbook cross-references COR-01's stale-reference sweep bullet (step 5) rather than duplicating it. The two-commit close (step 7) is the reusable mechanism for recording a deliverable's hash in its own done line.
