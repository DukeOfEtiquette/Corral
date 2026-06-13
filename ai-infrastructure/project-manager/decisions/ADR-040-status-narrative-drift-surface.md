---
schema_version: 1
adr: 40
title: "The hand-authored STATUS narrative as a standing drift surface: guard, reduce, or accept"
status: "pending"
date: "2026-06-13"
related_adrs: [36, 37, 39]
supersedes: []
superseded_by: null
---

# ADR-040: The hand-authored STATUS narrative as a standing drift surface: guard, reduce, or accept

> Pending. This ADR reserves a number and frames the question; the Alternatives, Decision, and Consequences are stubs to be filled in when it is taken up.

## Context

A sequence of work removed drift from the project's *derived* status surfaces. ADR-037 (COR-T-044/COR-T-045) made the roadmap a derived view, reconstructed from the `epics/` and `phases/` files rather than authored as a frontmatter block. ADR-039 (COR-T-047) moved `last_updated` and `recent_updates` out of STATUS.md frontmatter and made them git-derived. Earlier, COR-T-029 made `current_phase` and `next_step` derived for the dashboard. The shared principle: a surface computed from a single source of truth cannot rot by hand.

Each of those decisions deliberately left one surface hand-authored: the **"Current phase" / "Next step" / "Blocked on" narrative prose** in every `STATUS.md` (coordinator and department). ADR-039 and the repo `CLAUDE.md` both frame this prose as hand-authored *forward intent* - a thing an agent or operator writes on purpose, not a thing derived from state.

On 2026-06-13 a backend-api department survey surfaced that this prose had drifted in two ways at once: it carried the `P<phase>-<n>` milestone vocabulary that ADR-036 retired ("P2-2", "P2-3"), and it carried a gating precondition that had since cleared ("file these when the database schema DB-T-001 is under way" - but that work is done). Investigation showed the same staleness in the coordinator's own STATUS.md narrative. Two contributing facts:

1. **No cascade reaches it.** The ADR-036 vocabulary cascade (COR-T-042) was explicitly scoped to skip STATUS narratives, so the retired vocabulary was never swept from them.
2. **No mechanism guards it.** Unlike the derived surfaces, nothing recomputes or lint-checks the narrative, so a stale gating clause or a retired term persists silently until a human reads it.

The one-time cleanup is filed as COR-T-049. This ADR addresses the standing question that cleanup does not answer: **should the hand-authored STATUS narrative remain a permanent, unguarded drift surface, or should it be guarded or reduced?** This is the natural continuation of the ADR-037 / ADR-039 "move the source, preserve the contract" line of reasoning, applied to the last surface those ADRs left by hand.

## Alternatives considered

> Stubs - dimensions to work when this ADR is taken up. Not yet decided.

### Option A: Accept it as intended forward intent (status quo)

The narrative is hand-authored on purpose; staleness is the cost of human-authored intent and is caught by review (surveys, the orchestrator's STATUS-hygiene step). No new mechanism. Question to resolve: is periodic survey-driven correction (the COR-T-049 path, repeated as needed) sufficient, or does the 2026-06-13 incident show it is not?

### Option B: Guard it with a check

Keep the narrative hand-authored but add a lint that flags known drift signals - retired `P<phase>-<n>` vocabulary, references to tasks/epics whose state contradicts the prose, gating clauses naming a now-done dependency. Peer to the dashboard consistency checks ADR-036 introduced for cardinality. Questions: what is cheaply checkable (vocabulary regex vs. semantic gating)? Where does the check run (dashboard ETL, a commit hook, a checker subagent)? Is it owned-but-advisory (ADR-035) or blocking?

### Option C: Reduce the hand-authored surface

Shrink what the narrative must say by deriving more of it. "Next step" already exists as a derived dashboard value; the STATUS prose could point at the derived value instead of restating it. Push the durable facts (current phase, blocking dependencies) toward derivation and leave only genuinely non-derivable intent in prose. Question: what residue is genuinely non-derivable forward intent, and is the smaller surface worth the added derivation machinery?

### Option D: Hybrid (reduce the derivable parts, guard the residue)

Combine B and C: derive what can be derived (C), and lint the irreducible hand-authored residue for drift signals (B).

## Decision

> To be filled in when this ADR is taken up.

## Consequences

> To be filled in when this ADR is taken up.
