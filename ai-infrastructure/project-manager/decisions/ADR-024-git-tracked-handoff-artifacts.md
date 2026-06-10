---
schema_version: 1
adr: 24
title: "Handoff artifacts (kickoffs, reports) are git-tracked in .claude/artifacts/handoffs/"
status: "accepted"
date: "2026-06-05"
related_adrs: [5, 8, 23]
supersedes: []
superseded_by: null
---

# ADR-024: Handoff artifacts (kickoffs, reports) are git-tracked in .claude/artifacts/handoffs/

## Context

ADR-023 placed kickoff prompts and worker closing reports in gitignored `.claude/artifacts/tmp/`, mirroring rogue, with the trade-off accepted explicitly: "handoff history is not preserved in git". After the first three dispatch-loop runs (COR-T-001 through COR-T-003), the user reversed that trade-off (2026-06-05): the kickoff/report pairs are a record of how each task was specified and executed, and that record should be preserved in version control alongside the task files and commits it explains.

ADR-023 bundles two decisions: the dispatch-loop machinery itself, and the scratch-artifact location. Only the location decision is being revisited; the dispatch loop is unchanged and in force. The ADR schema (`./decisions/README.md`) supports supersession only at whole-ADR granularity, so flipping ADR-023 to `superseded` would wrongly retire the loop decision. This ADR therefore amends ADR-023 by reference rather than superseding it.

## Alternatives considered

### Option A: New tracked directory `.claude/artifacts/handoffs/`, `tmp/` stays gitignored for other scratch

Kickoffs and reports move to a tracked sibling directory. `.claude/artifacts/tmp/` keeps its gitignore rule and its scratch role for genuinely single-use files (status snapshots, intermediate analyses).

**Selected because:** the user chose it (2026-06-05). The handoff pairs get durable history with clear semantics, while the scratch category survives intact for artifacts that genuinely should not be tracked. Trade-off accepted: the path convention changes across the role docs, slash commands, agent definitions, and specs, and the repo accumulates one kickoff/report pair per dispatched task.

### Option B: Track `.claude/artifacts/tmp/` in place

Remove the gitignore rule and track the existing directory.

**Rejected because:** "tmp" would misname durable history, and every scratch artifact type would become tracked, not just the handoff pairs.

### Option C: Move handoffs under `docs/ai-orchestration/`

Place the tracked artifacts in the sanctioned documentation tree.

**Rejected because:** handoff artifacts are AI-infrastructure working files (ADR-005 domain 2), not documentation; ADR-023 already drew that line and this decision does not redraw it.

### Commit timing: resolve-time commit gate (selected) vs commit-on-creation

Handoff files are committed as part of the task's existing resolve-time commit gate, riding along with the changes they specified. Commit-on-creation (kickoff committed when the dispatch loop passes, report at Worker close) was rejected: it adds two commit points per task, and Workers never commit under the current git boundary.

## Decision

Kickoff and report handoff artifacts live in git-tracked `.claude/artifacts/handoffs/`. `.claude/artifacts/tmp/` remains gitignored and holds only genuinely scratch files. Handoff files are committed at the task's resolve-time commit gate. The four pre-existing artifacts (the COR-T-002 and COR-T-003 kickoff/report pairs) are adopted retroactively. This amends the scratch-artifact-location decision of ADR-023; the dispatch-loop decision of ADR-023 is unchanged.

## Consequences

- Handoff history is preserved in git; the durable record of a task now includes its kickoff/report pair alongside the task file's activity log and the resulting commits.
- Handoff pairs are no longer delete-once-consumed. The "safe to delete once consumed" guidance applies only to `.claude/artifacts/tmp/` scratch.
- The following ADR-023 passages are superseded by this decision and read as historical: the title's "with scratch handoffs in gitignored .claude/artifacts/tmp/" clause, the "Scratch-artifact location" alternative, the Decision sentence "Scratch handoff artifacts (kickoffs, reports) live in gitignored `.claude/artifacts/tmp/`", and the Consequences line adding `.claude/artifacts/tmp/` to `.gitignore`. ADR-023 itself stays `accepted` (append-only convention; its dispatch-loop decision is in force).
- Path and classification sweep across: `CLAUDE.md` (documentation placement exception), `docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md` (artifact locations, scratch-vs-durable table, dispatch-loop step 1), `docs/ai-orchestration/roles/WORKER-ROLE.md` (report path example, default kickoff lookup), `docs/README.md` (navigation), `.claude/commands/corral-orchestrator.md` and `.claude/commands/corral-worker.md`, the four agent definitions in `.claude/agents/`, and the four specs in `.claude/agents/specs/`. Executed under COR-T-007.
- A kickoff sits uncommitted in `.claude/artifacts/handoffs/` while its Worker session runs; the working tree is not clean mid-task. This is the same window in which the task file sits in `./tasks/in-progress/`, so no new ambiguity is introduced.
