---
schema_version: 1
adr: 35
title: "Cited-reference integrity for dispatched work: pin in kickoffs, resolve at close"
status: "accepted"
date: "2026-06-12"
related_adrs: [16, 23, 28, 34]
supersedes: []
superseded_by: null
---

# ADR-035: Cited-reference integrity for dispatched work: pin in kickoffs, resolve at close

## Context

The COR-04 / COR-05 / COR-06 family in `./OBSERVATIONS.md` is three logged instances of one root failure: a dispatched executor emits a repository-state claim that reads as authoritative but was never checked against disk.

- **COR-04**: plausible-but-wrong run/verification commands, naming compose services that do not exist.
- **COR-05**: self-stale follow-ups describing pre-edit state the same session had already changed.
- **COR-06**: fabricated file paths baked into the shipped deliverable (two ADR cross-reference links in `./END-GOAL.md`), reconstructed from the `ADR-NNN-kebab-title` naming convention for files the executor was not handed in `explicit_reads`. Both guessed slugs diverged from the real filenames and rendered as broken links.

The shared mechanism: an executor asked to name a path or command it was not given reconstructs it from a convention and guesses, and the guess often diverges from the real string. All three were caught by the orchestrator's verify-against-disk pass (`docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md`, Dispatched-worker flow step 6, originating in ADR-028).

The catch mechanism works and is already codified in-project, not in global config or user memory (verified 2026-06-12: it lives in ORCHESTRATOR-ROLE.md step 6 and ADR-028, with the universal "Verify before asserting" parent in the repo-root `CLAUDE.md`). It therefore already travels with the eventual plugin extraction (ADR-034). Two gaps remain:

1. The catch is reactive: the executor still wastes a round fabricating, and the orchestrator still has to spot-fix.
2. The specific sub-check COR-06 required, resolving every repo-relative path cited in the **deliverable** on disk, is emergent orchestrator judgement, not a written step. It is not guaranteed to be applied consistently, nor to survive into the extracted plugin.

The question: do we add enforcement on top of the working manual catch, and if so where, given that a per-close mechanical scan would be partly redundant with step 6 and would tax every close.

## Alternatives considered

### Option A: Prevention via kickoff citation-completeness, plus an explicit step-6 sub-step (selected)

Two near-zero-cost changes. (1) A kickoff-drafting convention: when a kickoff directs the executor to cite a repo-relative path or run a specific command, the exact string is carried in the kickoff's `references` / `explicit_reads` (or inline in the kickoff body), so the executor echoes a verified string rather than reconstructing it. This addresses the root cause of COR-04 and COR-06 at drafting time, before the executor runs, at the cost of a small drafting discipline and no extra dispatch. (2) ORCHESTRATOR-ROLE.md Dispatched-worker flow step 6 gains an explicit sub-step: resolve every repo-relative path cited in the deliverable on disk before close. This turns COR-06's emergent behaviour into a written step, so it applies consistently and travels with the plugin.

**Selected because:** it fixes the root cause cheaply (prevention) and codifies the one verification sub-step that was emergent, both without adding a new agent dispatch or a per-close scan. Trade-off accepted: the kickoff convention is owned-but-advisory (enforced by the drafter's discipline, not by an independent checker) until erosion justifies the weight; and COR-05 (self-stale follow-ups) is not a citation/command issue, so prevention does not cover it. It stays covered by the existing step-6 re-derivation only.

### Option B: Add a worker-close-checker detection rule (rejected)

A new W-rule that mechanically resolves every repo-relative path in the deliverable on disk at close time, independent of orchestrator diligence.

**Rejected because:** it duplicates Dispatched-worker flow step 6 (the orchestrator already re-derives against disk) and taxes every close, including the majority that cite no reconstructed paths, by having the checker read the full deliverable. The cost and redundancy are not justified while the working manual catch plus Option A's prevention covers the family. A re-open trigger is recorded in Consequences.

### Option C: A kickoff-checker R9 enforcing citation completeness (deferred)

Make Option A's convention a checker-enforced rule (R9) so it is independently verified at draft time rather than owned-but-advisory.

**Deferred because:** it is process weight (a ninth R-rule, plus drafter+checker churn) not yet justified by a single new drafting convention. Unlike Option B it is at least cheap (the kickoff-checker already reads every kickoff) and pre-dispatch, so it is the natural first escalation if the advisory convention erodes. Recorded as the re-open path, not adopted now.

### Option D: Status quo, leave COR-04/05/06 at logged (rejected)

Rely entirely on the orchestrator's emergent verify-against-disk judgement.

**Rejected because:** COR-06 put a fabricated link into a shipped deliverable, and the specific deliverable-path-resolution sub-check is unwritten, so it is not guaranteed across orchestrators or into the extracted plugin (ADR-034). The family is at three instances, the role doc's threshold for systematising a pattern.

## Decision

Adopt prevention-first cited-reference integrity for dispatched work (Option A). When a kickoff directs the executor to cite a repo-relative path or run a specific command, the kickoff carries that exact path/command in its `references` / `explicit_reads` so the executor echoes a verified string instead of reconstructing one. ORCHESTRATOR-ROLE.md Dispatched-worker flow step 6 gains an explicit sub-step requiring the orchestrator to resolve every repo-relative path cited in the deliverable on disk before close. No new close-checker rule (Option B) and no new kickoff-checker rule (Option C) are added now. This ADR promotes OBSERVATIONS COR-04, COR-05, and COR-06.

## Consequences

- The kickoff-drafting convention gains a citation-completeness rule, landing in the "Kickoff drafting convention" section of ORCHESTRATOR-ROLE.md and in `.claude/agents/specs/KICKOFF-DRAFTER-SPEC.md`. The implementation cascade (the role-doc convention bullet, the drafter-spec edit, and the explicit step-6 sub-step) is a deliverable and routes through the dispatched-worker flow; filed as COR-T-039.
- COR-04, COR-05, and COR-06 move from `logged` to `promoted -> ADR-035` in OBSERVATIONS.md (orchestrator-direct lifecycle update; entry bodies are unchanged per the append-only-except-lifecycle convention).
- Prevention is partial by design: it covers reconstructed paths and commands (COR-04, COR-06). Self-stale follow-ups (COR-05) and any other unverified report narration remain covered only by the orchestrator's step-6 re-derivation, which is unchanged and stays the backstop.
- The convention is owned-but-advisory: enforced by the drafter's discipline, not by an independent checker. Re-open trigger: if a fourth or later instance of the family shows the advisory convention is not holding, escalate to Option C (a kickoff-checker R9) first, and to Option B (a close-checker W-rule) only if pre-dispatch enforcement proves insufficient.
- Portability: because both changes land in ORCHESTRATOR-ROLE.md and KICKOFF-DRAFTER-SPEC.md (generic project-manager machinery, not Corral-app content), they travel with the plugin extraction (ADR-034), closing the gap that the deliverable-path-resolution sub-check was previously emergent.
- Forward-pointer notes are added to ADR-023 (the kickoff convention and R-rule set this extends) and ADR-028 (the verify-against-disk step 6 this makes explicit), per the amend-by-a-later-ADR precedent (ADR-024); neither accepted ADR's decision is edited in place.
</content>
</invoke>
