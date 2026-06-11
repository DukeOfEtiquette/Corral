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

### COR-03: hand-maintained roadmap milestone statuses are the dashboard's last drift surface, now load-bearing

- date: 2026-06-11
- state: logged
- context: The dashboard originally derived each phase's CURRENT/UPCOMING badge from a single hand-maintained `phase` field in coordinator STATUS frontmatter; that field drifted (stayed `phase: 1` after Phase 2 began via COR-T-023 and DB-T-001), so the live dashboard showed Phase 1 CURRENT while Phase 2 was already underway. The same class of drift had been seen once before (P1-6 milestone status left `in-progress` after COR-T-017 delivered it, corrected during the COR-T-020 wrap-up; recorded in STATUS recent_updates). COR-T-029 fixed the phase pointer by deriving `current_phase`, `current_phase_title`, and `next_step` from the per-milestone `status` values. But that pushed the hand-maintained surface down one level: every derived field now depends on the roadmap milestone `status` (`done`/`in-progress`/`planned`) values, which are still set by hand in the coordinator STATUS frontmatter and are read verbatim by `etl.py` (`ms.get("status")`). A milestone whose work is done but whose status was never flipped will now silently mis-drive the entire phase display, not just one badge.
- pattern: Each time a hand-maintained pointer is replaced by derivation, the drift relocates to whatever the derivation now reads, rather than disappearing. The remaining hand-set inputs are the milestone statuses. Many milestones carry a `task:` ref (e.g. P1-4 -> COR-T-014, P2-1 -> DB-T-001), so a milestone's `done`-ness could be cross-checked against (or derived from) whether that task file sits in a `tasks/done/` tree, catching the drift mechanically. Candidate promotion: a consistency check in `etl.py` (or a dashboard warning) that flags any `task`-bearing milestone whose authored status disagrees with its task's tree location; full auto-derivation is bounded because task-less milestones have no structural signal. Until promoted, milestone statuses remain a manual-accuracy dependency worth re-checking when advancing the roadmap. Separately, the dead department PHASE column (a hand-maintained field with no source at all) is tracked as the deliverable COR-T-030, distinct from this milestone-status surface.
