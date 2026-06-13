---
schema_version: 1
adr: 39
title: "STATUS.md ownership: derive the activity surface, hand-author only forward intent"
status: "pending"
date: "2026-06-13"
related_adrs: [37, 8, 27, 12, 23, 24, 29]
supersedes: []
superseded_by: null
---

# ADR-039: STATUS.md ownership: derive the activity surface, hand-author only forward intent

> Pending: this ADR frames the question and records the operator's leanings; no decision is taken yet. The Alternatives, Decision, and Consequences below are framing stubs to be filled in when the ADR is resolved (per the Pending-ADR resolution playbook in `docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md`). Resolvable next session; not phase-gated.

## Context

Every workspace owns a `STATUS.md` whose frontmatter carries two hand-maintained fields, `last_updated` (a date) and `recent_updates` (a curated changelog of one rich entry per task/decision), plus a hand-authored body (`## Current phase`, `## Next step` on department STATUS, `## Blocked on`). The "universal STATUS hygiene" obligation (bump `last_updated`, append a `recent_updates` entry at the end of any session that makes progress) is wired into `EXECUTOR-ROLE.md`, `TEST-DESIGNER-ROLE.md`, `ORCHESTRATOR-ROLE.md`, all three orchestrator commands, the department command template, and the R6 kickoff convention.

This surface drifts. The motivating instance: a fresh `/database-orchestrator` survey (2026-06-13) found `ai-infrastructure/database/STATUS.md` stale at `last_updated: 2026-06-11` with no `recent_updates` mention of the `DB-E-001` epics/ tree or `DB-T-002`, both of which exist on disk. Root cause: COR-T-044/045 (coordinator tasks) created those artifacts inside the database workspace under coordinator write authority (ADR-027) but applied STATUS hygiene only to the coordinator STATUS. Cross-workspace writes silently destale the target workspace's STATUS, because the hygiene obligation targets the kickoff-named workspace, not every workspace a task touches.

This is the COR-03 pattern continuing (`OBSERVATIONS.md`): each time a hand-maintained pointer is replaced by derivation, the drift relocates to whatever is still hand-maintained. ADR-037 already derived the roadmap out of STATUS frontmatter (the churn-coupling resolution), eliminating roadmap/structural-status drift. The remaining hand-maintained surface, the activity log (`last_updated` + `recent_updates`), is now the drift carrier. ADR-037 is the direct precedent: it kept the `data.json` contract stable and changed only the source.

Two further alignments motivate acting now rather than continuing to hand-maintain:

- **The dogfood end-state (ADR-008, ADR-012).** After the dogfood migration, tracker activity is the app's `issue_events` audit log, derived, not hand-authored. A derived markdown-era activity feed is the analog of that end-state, so deriving now moves toward the eventual shape, not away from it.
- **Commit discipline already exists (ADR-024).** Handoff artifacts and deliverables are committed with task-ID-tagged messages; the git history is already a high-fidelity, per-workspace-attributable activity record.

The question this ADR frames is broader than just the activity fields: **which parts of `STATUS.md` should remain hand-authored, and which should become derived?** The operator's framing principle is "history is derived; intent is authored": backward-looking facts (timestamps, what-happened) are mechanically recoverable and should be derived; forward-looking intent (current focus, next step, what we are blocked on) is human judgement and stays authored.

## Open dimensions

To be resolved when the ADR is taken up. Each is framed with the operator's current leaning.

1. **Scope split (the core principle).** Lean: `last_updated` and `recent_updates` become DERIVED; `## Current phase`, `## Next step`, and `## Blocked on` stay HAND-AUTHORED (forward intent). STATUS.md frontmatter shrinks to `schema_version` (+ `department`). Open: whether `## Current phase` should instead derive its factual half (the phase number/title, already derived to `data.json`) while keeping only the narrative.

2. **Source for `recent_updates`.** The central fork:
   - **git-by-path**: `git log -- <workspace-path>` (complete: catches task-less events like ADR edits and hygiene fixes; lower per-entry richness; makes commit-message quality a contract; needs git in the container).
   - **task-activity-logs**: aggregate the newest activity-log lines across the workspace's task files (keeps curation; no container change; misses task-less events).
   - **hybrid**: git as the spine, enriched by task-activity-log text where a commit maps to a task.
   Lean: git-by-path (completeness wins; commit discipline is already strong and task-ID-tagged), revisited if the richness loss proves too costly.

3. **Source for `last_updated`.** Lean: `git log -1 -- <workspace-path>` date (more accurate than `max(task updated:)` because it catches non-task changes). Low controversy.

4. **Materialization and survey doctrine.** If the activity surface leaves STATUS.md, a surveying orchestrator can no longer read `recent_updates` from frontmatter. Lean: materialize the derived feed in the dashboard `data.json` (contract already has `recent_activity`), and change the survey doctrine so orchestrators consult `git log -- <workspace>` (or the dashboard) for recent activity. This is a doctrine cascade (see dimension 7).

5. **ETL / container feasibility.** The dashboard serve image is `python:3.12-slim` (PyYAML + watchdog only); the compose bind-mount is the whole repo root read-only, so `/repo/.git` is present but no git binary is. git-by-path requires either `apt-get install git` + shelling out, or a pure-Python reader (dulwich), plus handling git's `safe.directory` ownership check under a read-only mount. task-activity-logs need no container change. Lean: acceptable cost (install git or add dulwich); confirm read-only-mount `git log` works in-container during implementation.

6. **Commit-message discipline as contract.** If the source is git, commit subjects become the activity feed, so their quality/format is load-bearing. Lean: codify the already-de-facto convention (every commit subject leads with the task/ADR ID and a specific summary); decide whether to enforce it (a hook or checker) or leave it advisory.

7. **Doctrine cascade (a consequence to scope, not a separate decision).** Deriving the activity surface removes the "universal STATUS hygiene" obligation from `EXECUTOR-ROLE.md`, `TEST-DESIGNER-ROLE.md`, `ORCHESTRATOR-ROLE.md` (the lifecycle + R6 convention), the three orchestrator commands, and the department command template. This is a simplifying cascade (it deletes a per-session chore and a drift class), filed as an implementation task when the ADR is accepted (analog of COR-T-046). It also resolves the cross-workspace-write hygiene gap structurally (no target-workspace edit is needed, because there is nothing hand-maintained to edit).

8. **Relationship to the dogfood seam (ADR-008).** At dogfood, STATUS-as-tracked-markdown freezes and activity comes from `issue_events`. Deriving now should be designed so the derived feed is conceptually the same object the app will later serve from the events table, so the dogfood transition swaps the source again without reshaping the contract.

## Alternatives considered

> Stubs; expand on resolution.

### Option A: Status quo (hand-author the whole STATUS surface)

Keep `last_updated` + `recent_updates` hand-maintained. **Leaning: rejected** (it is the drift carrier this ADR exists to remove; the cross-workspace-write gap has no clean doctrine patch).

### Option B: Derive `last_updated` only

Lowest-risk partial step; leaves the `recent_updates` drift in place. **Leaning: insufficient** (the flagged drift was in `recent_updates` content, not just the date).

### Option C: Derive the full activity surface; hand-author only forward intent

`last_updated` + `recent_updates` derived (source per dimension 2); `## Current phase` / `## Next step` / `## Blocked on` stay authored. **Leaning: selected**, pending resolution of the source fork (dimension 2) and feasibility (dimension 5).

## Decision

Pending.

## Consequences

Pending. Anticipated when Option C is taken: the `data.json` contract shape is preserved (source-only change, per ADR-037); the dashboard container gains a git (or dulwich) dependency; a doctrine cascade removes universal STATUS hygiene across the role docs, commands, template, and R6 convention (filed as an implementation task); the cross-workspace-write drift gap is structurally closed; and the markdown-era activity feed is aligned with the ADR-008 `issue_events` end-state.
