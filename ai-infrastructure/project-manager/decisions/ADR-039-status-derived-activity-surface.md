---
schema_version: 1
adr: 39
title: "STATUS.md ownership: derive the activity surface, hand-author only forward intent"
status: "accepted"
date: "2026-06-13"
related_adrs: [37, 8, 27, 12, 23, 24, 29, 35]
supersedes: []
superseded_by: null
---

# ADR-039: STATUS.md ownership: derive the activity surface, hand-author only forward intent

## Context

Every workspace owns a `STATUS.md` whose frontmatter carries two hand-maintained fields, `last_updated` (a date) and `recent_updates` (a curated changelog of one rich entry per task/decision), plus a hand-authored body (`## Current phase`, `## Next step` on department STATUS, `## Blocked on`). The "universal STATUS hygiene" obligation (bump `last_updated`, append a `recent_updates` entry at the end of any session that makes progress) is wired into `EXECUTOR-ROLE.md`, `TEST-DESIGNER-ROLE.md`, `ORCHESTRATOR-ROLE.md`, all three orchestrator commands, the department command template, and the R6 kickoff convention.

This surface drifts. The motivating instance: a fresh `/database-orchestrator` survey (2026-06-13) found `ai-infrastructure/database/STATUS.md` stale at `last_updated: 2026-06-11` with no `recent_updates` mention of the `DB-E-001` epics/ tree or `DB-T-002`, both of which exist on disk. Root cause: COR-T-044/045 (coordinator tasks) created those artifacts inside the database workspace under coordinator write authority (ADR-027) but applied STATUS hygiene only to the coordinator STATUS. Cross-workspace writes silently destale the target workspace's STATUS, because the hygiene obligation targets the kickoff-named workspace, not every workspace a task touches.

This is the COR-03 pattern continuing (`OBSERVATIONS.md`): each time a hand-maintained pointer is replaced by derivation, the drift relocates to whatever is still hand-maintained. ADR-037 already derived the roadmap out of STATUS frontmatter (the churn-coupling resolution), eliminating roadmap/structural-status drift. The remaining hand-maintained surface, the activity log (`last_updated` + `recent_updates`), is now the drift carrier. ADR-037 is the direct precedent: it kept the `data.json` contract stable and changed only the source.

Two further alignments motivated acting now rather than continuing to hand-maintain:

- **The dogfood end-state (ADR-008, ADR-012).** After the dogfood migration, tracker activity is the app's `issue_events` audit log, derived, not hand-authored. A derived markdown-era activity feed is the analog of that end-state, so deriving now moves toward the eventual shape, not away from it.
- **Commit discipline already exists (ADR-024).** Handoff artifacts and deliverables are committed with task-ID-tagged messages; the git history is already a high-fidelity, per-workspace-attributable activity record.

The question was broader than just the activity fields: which parts of `STATUS.md` should remain hand-authored, and which should become derived? The resolving principle is **"history is derived; intent is authored"**: backward-looking facts (timestamps, what-happened) are mechanically recoverable and are derived; forward-looking intent (current focus, next step, what we are blocked on) is human judgement and stays authored.

## Alternatives considered

The decision had two coupled axes: how much of STATUS.md to derive (scope), and where the derived activity feed comes from (source).

### Scope

**Option A: Status quo (hand-author the whole STATUS surface).** Keep `last_updated` + `recent_updates` hand-maintained. Rejected: it is the drift carrier this ADR exists to remove, and the cross-workspace-write gap has no clean doctrine patch (you cannot reliably ask every task to remember to hygiene every workspace it incidentally touched).

**Option B: Derive `last_updated` only.** Lowest-risk partial step. Rejected as insufficient: the flagged drift was in `recent_updates` content, not just the date.

**Option C: Derive the full activity surface; hand-author only forward intent.** `last_updated` + `recent_updates` derived; `## Current phase` / `## Next step` / `## Blocked on` stay authored. Selected: it removes the drift class entirely, structurally closes the cross-workspace-write gap (nothing hand-maintained means nothing to forget), and follows the proven ADR-037 source-only pattern.

### Source for the derived feed

**git-by-path.** Each workspace's feed is `git log -- <workspace-path>`. Selected: it is complete (it captures task-less events such as ADR edits and hygiene fixes, AND cross-workspace coordinator writes, which is the exact drift that motivated the ADR: the COR-T-044 commit touched `ai-infrastructure/database/` paths and so appears in the database feed for free). The accepted trade-offs are lower per-entry richness than the hand-curated paragraphs and making commit-message quality load-bearing.

**task-activity-logs.** Aggregate the newest activity-log lines across a workspace's task files. Rejected as the primary source: it keeps curation and needs no container change, but it misses task-less events and coordinator cross-writes that create no task in that tree, so it would not have caught the motivating drift.

**hybrid (git spine enriched by activity-log text).** Best fidelity, most moving parts. Rejected for v1 as unnecessary complexity; the git spine is sufficient and the hybrid remains a future enrichment if commit-subject richness proves too thin.

## Decision

Adopt Option C with git-by-path. Specifically:

1. **Scope (history derived, intent authored).** `last_updated` and `recent_updates` become derived and leave `STATUS.md` frontmatter, which reduces to `schema_version` (+ `department` on department STATUS). `## Current phase`, `## Next step`, and `## Blocked on` stay hand-authored as forward intent. (The factual phase number/title already derives to `data.json`; only the narrative stays authored.)

2. **Source.** `recent_updates` / the per-workspace activity feed derives from `git log -- <workspace-path>`; `last_updated` derives from `git log -1 -- <workspace-path>`. The dashboard's existing `recent_activity` aggregate is the materialization, so the `data.json` contract shape is preserved (a source-only change, per ADR-037).

3. **Survey doctrine.** Because the activity surface leaves `STATUS.md`, a surveying orchestrator consults `git log -- <workspace>` (or the dashboard) for recent activity rather than reading `recent_updates` from frontmatter.

4. **ETL / container feasibility.** The dashboard serve image (`python:3.12-slim`) gains git so `etl.py` can read history; the compose bind-mount already includes `/repo/.git` read-only. The implementation handles git's `safe.directory` ownership check under the read-only mount. (dulwich, pure-Python, is the fallback if the git-binary route is problematic in-container.)

5. **Commit-message discipline (owned-but-advisory).** With git as the source, commit subjects are the feed, so the de-facto convention is codified: every commit subject leads with the task/ADR ID plus a specific summary. This is owned-but-advisory, mirroring the ADR-035 citation-completeness precedent; enforcement (a `commit-msg` hook or a checker rule) is the recorded re-open path if feed quality erodes.

6. **Doctrine cascade.** Deriving the activity surface removes the universal STATUS-hygiene obligation from `EXECUTOR-ROLE.md`, `TEST-DESIGNER-ROLE.md`, `ORCHESTRATOR-ROLE.md` (the lifecycle text and the R6 convention), the three orchestrator commands, and the department command template, and rewrites the survey doctrine per decision 3. Filed as implementation task COR-T-047. The cascade is sequenced: the derive-ETL and container change land and are render-verified FIRST, then the doctrine cascade and the frontmatter-field removal, so there is never a window where the activity surface is neither hand-maintained nor derived.

7. **Dogfood alignment.** The git-derived feed is the markdown-era analog of the app's `issue_events` audit log (ADR-008, ADR-012); the dogfood transition re-points the source from git to the events table without reshaping the `data.json` contract.

## Consequences

- The `last_updated` + `recent_updates` drift class is eliminated, and the cross-workspace-write drift gap (ADR-027 write authority) is structurally closed: there is no hand-maintained activity field left to forget.
- A per-session chore (universal STATUS hygiene) is deleted from every role doc, command, and the R6 convention. This is a net doctrine simplification; the implementation cascade (COR-T-047) is the cost.
- Commit-message quality becomes load-bearing for the activity feed (decision 5). Accepted as advisory with a recorded enforcement re-open path.
- The dashboard container gains a git (or dulwich) dependency and `safe.directory` handling; the `data.json` contract is unchanged (source-only, per ADR-037).
- `STATUS.md` becomes a thin forward-intent document (`## Current phase` / `## Next step` / `## Blocked on`); the historical record lives in git and, post-dogfood, in `issue_events`.
- Forward-pointer notes added to ADR-037 (this extends its derivation pattern to the activity surface), ADR-027 (this closes the cross-workspace-write drift gap its grant enabled), and ADR-008 (this pre-stages the `issue_events` activity end-state). related_adrs cross-links updated. COR-03 in `OBSERVATIONS.md` reaches its terminal derivation here (the last hand-maintained STATUS surface is derived); flip its note on resolution of COR-T-047.
