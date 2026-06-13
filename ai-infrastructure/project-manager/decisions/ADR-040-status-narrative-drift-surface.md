---
schema_version: 1
adr: 40
title: "Derive the full STATUS narrative: zero hand-authored body, intent included"
status: "accepted"
date: "2026-06-13"
related_adrs: [8, 27, 36, 37, 39]
supersedes: []
superseded_by: null
---

# ADR-040: Derive the full STATUS narrative: zero hand-authored body, intent included

## Context

ADR-037 derived the roadmap out of `STATUS.md` frontmatter; ADR-039 derived the activity surface (`last_updated` + `recent_updates`) and pinned the principle "history is derived; intent is authored," deliberately keeping the body sections (`## Current phase`, `## Next step`, `## Blocked on`) hand-authored as forward intent. Both followed the ADR-037 source-only pattern: move the source, preserve the `data.json` contract.

On 2026-06-13 a `/backend-api-orchestrator` survey surfaced that the hand-authored narrative had drifted in two ways: it carried the `P<phase>-<n>` milestone vocabulary that ADR-036 retired ("P2-2", "P2-3"), and it carried a gating precondition that had since cleared ("file these when the database schema DB-T-001 is under way"). The same staleness was found in the coordinator's own `STATUS.md`. The immediate cleanup was filed and dispatched as COR-T-049; this ADR addresses the standing question that cleanup did not answer.

Investigation produced the decisive finding: **`etl.py` does not consume the narrative bodies at all.** It derives `current_phase`, `current_phase_title`, and `next_step` from the roadmap files (COR-T-029/045) and the activity feed from git (ADR-039), reading only STATUS *frontmatter*. The drifted prose lived only in `STATUS.md`-the-file, read directly by agents (which is how it surfaced). So the narrative is **redundant authored prose**: it restates facts the dashboard already derives (phase, next step) plus one that is trivially derivable (`## Blocked on` is the contents of the `blocked/` task trees). It exists only to drift.

The operator set the framing: the north star is zero hand-authored content in the dashboard, with ADR-037 (roadmap) and ADR-039 (activity) being the increments already shipped. The narrative is the next derivation target, and the operator selected the most aggressive increment: derive it fully now, including the intent sections, rather than guarding it as a permanent authored surface. That makes this ADR the point where the COR-03 lineage ("each time a hand-maintained pointer is replaced by derivation, the drift relocates to whatever is still hand-maintained") removes the last hand-authored content from `STATUS.md`, advancing ADR-039's principle from "intent is authored" to "intent is authored only until a structured source can carry it, and the structured sources now can."

## Alternatives considered

The decision had two axes: whether to keep the narrative authored at all, and how aggressive this increment should be.

### Axis 1: keep authored vs derive

**Option A: Accept as-is (status quo).** No mechanism; drift caught by the routine orchestrator survey (the path that just caught this one). Rejected: reactive, guarantees recurrence of the vocabulary-drift class, and leaves a redundant authored surface whose only function is to drift.

**Option B: Guard the authored narrative with a lint.** Keep it authored, add a retired-vocabulary consistency check in `etl.py` (the ADR-036 consistency-check mechanism), owned-but-advisory per ADR-035/ADR-039. Rejected as the end-state: it spends effort hardening a surface that is pure redundancy and contradicts the north star by enshrining the hand-authored narrative permanently. A lint guards what should not exist.

**Option C: Derive the narrative; eliminate the redundancy (selected).** Since the dashboard already derives phase and next step, and `blocked/` already holds the blocked set, the narrative restates derived facts and can be removed in favor of those derived surfaces. This removes the drift class structurally (nothing authored, nothing to drift), is the honest application of the north star, and extends the ADR-037 -> ADR-039 derivation line one more hop.

### Axis 2: increment aggressiveness (within Option C)

**Collapse redundancy only.** Derive `## Blocked on`, strip the restated facts from the other two sections, leave an irreducible authored "why" residue, lint the residue. Considered and not selected: it leaves a hand-authored residue and a throwaway lint, stopping short of the north star.

**Full derivation now (selected).** Derive all three sections, including the synthesized intent prose, leaving zero hand-authored narrative. The "why/context" the narrative synthesized is itself recoverable from surfaces the dashboard already renders (the roadmap panel's done/in-progress epics and tasks, and the git activity feed), so removing the authored synthesis loses little. Accepts lower narrative richness, the same trade-off ADR-039 accepted when it took the git-derived feed over hand-curated paragraphs.

**Record trajectory + lint only.** Pin the principle, ship only the lint now, defer all derivation. Rejected: the operator chose to do the derivation now, not defer it.

### Materialization (mechanical, follows from Option C / full)

**M1: `etl.py` regenerates the `STATUS.md` body from derived data.** Rejected: it would make the dashboard write tracked repo files on every ETL run, contradicting ADR-039's explicit "STATUS.md is not touched" (`etl.py` reverts its one transient write) and coupling dashboard refresh to repo mutation.

**M2: the narrative sections leave `STATUS.md`; the dashboard / `data.json` is the single surface (selected).** No repo writes from the dashboard. `STATUS.md` reduces to its frontmatter plus a pointer to the derived surface. Survey doctrine redirects to the dashboard / `data.json`, extending ADR-039 decision 3 (which already redirected activity reads to git / the dashboard).

## Decision

Adopt Option C, full derivation now, with materialization M2.

1. **Scope (the principle advances).** ADR-039's "history is derived; intent is authored" becomes: a derivable fact is never authored, including the forward-intent sections, wherever a structured source carries it. The structured sources now carry all three: `## Current phase` and `## Next step` from the roadmap rollup (already derived to `data.json` per COR-T-029/045), and `## Blocked on` from the `blocked/` task trees. All three sections become derived and leave the hand-authored `STATUS.md` body. This amends ADR-039 decision 1 (which kept them authored) by the later-ADR precedent (ADR-024); ADR-039 is not edited in place.

2. **Sources.**
   - `## Current phase` / `## Next step`: the existing roadmap derivation (`derive_current_phase` / `derive_current_phase_title` / `derive_next_step` in `etl.py`); no new source.
   - `## Blocked on`: derived from each workspace's `tasks/blocked/` tree (the blocked task ids plus each task's recorded reason). New derivation, the analog of ADR-039's git-by-path source decision.
   - The synthesized "what/why" context is not re-authored anywhere; it is recoverable from the already-derived roadmap panel (done / in-progress epics and tasks) and the git activity feed.

3. **Materialization (M2).** The three narrative sections are removed from every `ai-infrastructure/*/STATUS.md`. `STATUS.md` reduces to its frontmatter (`schema_version`, plus `department` on department STATUS) and a one-line pointer to the derived surface. The dashboard / `data.json` is the single read surface for current phase, next step, and blocked set. The dashboard does the materialization; the dashboard never writes back into the repo.

4. **Survey doctrine.** A surveying orchestrator reads current phase / next step / blocked from the dashboard or `data.json` (or, offline, from the structured roadmap and `tasks/blocked/` trees directly), not from a `STATUS.md` body. This extends ADR-039 decision 3.

5. **Richness trade-off.** The derived surface is structured-field-driven; a templated prose blurb is an optional future enrichment, deferred (mirroring ADR-039 deferring the hybrid feed). Lower richness than the hand-crafted synthesis is accepted, consistent with ADR-039.

6. **No transitional lint.** Option B's retired-vocabulary lint is not built. Because the narrative is being removed, a guard on it would be throwaway; the brief window between this acceptance and COR-T-050 landing is covered by the existing orchestrator survey, and the COR-T-049 cleanup left the current narrative correct. The drift class is removed structurally, not guarded.

7. **Implementation cascade (COR-T-050).** Filed as the implementation task, the analog of ADR-039's COR-T-047: add the `## Blocked on` derivation and a blocked surface to the dashboard; remove the three narrative sections from all `STATUS.md` files; reduce each `STATUS.md` to frontmatter plus the pointer line; cascade the survey-doctrine and `STATUS.md`-description changes through the role docs, the three orchestrator commands, and the department command template. Sequenced as ADR-039 was: the derived blocked surface lands and is render-verified FIRST, then the `STATUS.md` body removal and the doctrine cascade, so there is never a window where a section is neither authored nor derived.

8. **Dogfood alignment.** A fully derived current-state surface is the markdown-era analog of reading project state from the app's own tables post-dogfood (ADR-008, ADR-012); the transition re-points the source without reshaping the `data.json` contract.

## Consequences

1. **The STATUS-narrative drift class is eliminated structurally.** With no hand-authored body, the COR-T-049 incident class (retired vocabulary, cleared gating restated in prose) cannot recur: there is nothing authored to drift. The COR-03 lineage reaches its true terminus for `STATUS.md` here; ADR-039 named itself terminal for the activity surface but the narrative body was one more hop, now closed.

2. **`STATUS.md` becomes a thin frontmatter-plus-pointer file** across every workspace. The many `./STATUS.md` references in `CLAUDE.md` files, role docs, and commands stay valid (the file still exists), but their description ("current phase and next step for this department") shifts to "pointer to the derived dashboard surface." COR-T-050's doctrine cascade updates those descriptions.

3. **`## Blocked on` derivation makes the task tree load-bearing for blocked reasons.** A blocked task with no recorded reason yields a thinner blocked-on line, the same way ADR-039 made commit-message quality load-bearing for the activity feed. Accepted on the same terms.

4. **The dashboard is the single read surface for current state.** An agent surveying without a built dashboard reads `data.json` or the structured roadmap / `tasks/blocked/` trees directly. ADR-039 already pointed surveys at git / the dashboard, so this is the consistent next step, not a new burden.

5. **Lower narrative richness is accepted.** The hand-crafted synthesis prose is not reproduced; its content is recoverable from the roadmap and activity panels the dashboard already renders. Templated or generated prose remains a future enrichment.

6. **Forward pointers and lineage.** Forward-pointer notes are added to ADR-039 (this amends its decision 1/3: intent is now derived where a structured source carries it), ADR-037 (its derivation pattern extends once more, to the narrative), and ADR-008 (the derived current-state surface pre-stages the post-dogfood read-from-tables end-state). COR-03 in `OBSERVATIONS.md` is updated: its ADR-039 "terminal" note advances to ADR-040 as the actual terminus for `STATUS.md` body content. ADR-027 is referenced because the cross-workspace-write drift gap it opened is now fully closed for `STATUS.md` (no hand-maintained body remains to destale).

7. **Cost: COR-T-050.** A non-trivial implementation task (new dashboard derivation plus a doctrine cascade across role docs and commands), sequenced to avoid an unguarded window. This is the price of removing the last hand-authored `STATUS.md` content.
