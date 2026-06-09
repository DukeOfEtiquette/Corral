---
schema_version: 1
adr: 23
title: "Adopt the full drafter+checker dispatch loop at day zero, with scratch handoffs in gitignored .claude/artifacts/tmp/"
status: "accepted"
date: "2026-06-05"
related_adrs: [3, 5, 8, 9, 21]
supersedes: []
superseded_by: null
---

# ADR-023: Adopt the full drafter+checker dispatch loop at day zero, with scratch handoffs in gitignored .claude/artifacts/tmp/

> **Forward pointer (2026-06-09):** ADR-028 extends this ADR by promoting the worker into the same orchestrator-dispatched-subagent model the checkers use. The dispatched `worker-agent` is a leaf, so `worker-prelaunch-checker` and `worker-close-checker` are now dispatched by the Orchestrator (not by the worker), and the `/corral-worker` slash command named here was retired. The drafter+checker loop and the day-zero machinery decision are otherwise unchanged. See ADR-028 and `ORCHESTRATOR-ROLE.md` section "Dispatched-worker flow".

## Context

COR-T-001 right-sizes rogue's orchestrator and worker role docs for this repo (ADR-009). The rogue source material includes enforcement machinery the role docs alone do not imply: kickoffs are authored by a `kickoff-drafter` subagent and validated by a `kickoff-checker` subagent in a bounded iteration loop, and worker sessions dispatch `worker-prelaunch-checker` and `worker-close-checker` subagents at two checkpoints. Rogue grew this machinery (its project-manager ADR-016) only after observing that orchestrators drift from prose rules under context pressure. ADR-009 left open whether a day-zero repo carries it, drops it, or defers it. Two adjacent questions surfaced at the same time: where kickoff prompts and worker reports (scratch handoff artifacts, all `.md` files) live given the documentation-placement rule in `./CLAUDE.md`, and whether the slash commands that instantiate the roles are authored alongside the role docs.

## Alternatives considered

### Option A: Carry the full dispatch loop from day zero

Port the four universal subagents (`kickoff-drafter`, `kickoff-checker`, `worker-prelaunch-checker`, `worker-close-checker`) with their specs, right-sized: single project (no workspace routing), rules renumbered after dropping rogue-domain-specific checks.

**Selected because:** the user chose it (2026-06-05). The machinery is proven in rogue, the drift it prevents is a property of LLM orchestrators generally rather than of rogue specifically, and adopting it before habits form is cheaper than retrofitting it after drift is observed. Trade-off accepted: enforcement infrastructure exists before any drift has been demonstrated in this repo, and four subagent specs must be maintained from day one.

### Option B: Drop the loop, note it as a promotion path

The orchestrator authors kickoffs inline; one paragraph in the role docs names the rogue dispatch pattern as the known fix if drift appears here.

**Rejected because:** the user declined it; it re-derives a lesson rogue already paid for.

### Option C: Queue a pending ADR and decide later

**Rejected because:** the question was decidable now, and the role docs would have needed rewriting on either outcome.

### Scratch-artifact location: gitignored `./.claude/artifacts/tmp/` (selected) vs a tracked docs directory

Kickoffs and worker reports are single-use handoff artifacts, not documentation. A tracked directory would accumulate repo noise and force every handoff through the documentation-placement rule. The gitignored location mirrors rogue. Trade-off accepted: handoff history is not preserved in git; the durable record of a task lives in the task file's activity log, the closing report consumed by the orchestrator, and the resulting commits.

## Decision

Corral adopts the rogue dispatch-loop machinery at day zero. Kickoffs are authored by `kickoff-drafter` (Opus) and validated by `kickoff-checker` (Sonnet) in the bounded loop defined in `./docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md`. Worker sessions dispatch `worker-prelaunch-checker` and `worker-close-checker` (both Sonnet) at the checkpoints defined in `./docs/ai-orchestration/roles/WORKER-ROLE.md`. Agent definitions live in `./.claude/agents/`, specs in `./.claude/agents/specs/`, and the instantiating slash commands (`/corral-orchestrator`, `/corral-worker`) in `./.claude/commands/`, all authored under COR-T-001. Scratch handoff artifacts (kickoffs, reports) live in gitignored `./.claude/artifacts/tmp/`. The `./.claude/` tree holds AI-infrastructure artifacts (ADR-005 domain 2), not documentation; the documentation-placement rule in `./CLAUDE.md` is clarified accordingly.

## Rule lineage

Corral renumbers the ported rules contiguously after dropping rogue-domain-specific checks. The map, for future cross-reading against rogue:

| Corral rule | Rogue rule | Check |
|---|---|---|
| R1 | R1 | No Option-A/B tradeoff lists in kickoffs |
| R2 | R2 | No "Worker, figure out X" delegations |
| R3 | R3 | No paradigm-choice delegations |
| R4 | R5 | No intermediate checkpoints; one gate per kickoff |
| R5 | R6 | No em dashes in files |
| R6 | R7 | STATUS-deltas section present, or the literal "universal hygiene only" |
| R7 | R8 | No invocation framings in the kickoff body |
| R8 | R10, adapted | "Related tasks and ADRs" section present: `COR-T-NNN` / `ADR-NNN` entries with one-line relevance, or the literal "none" |
| W1 | W2 | Every kickoff deferral carries an acceptance test or user-confirm flag (prelaunch) |
| W2 | W5 | Every report Follow-ups item names a target, a "COR-T candidate" tag, or a triage-to-orchestrator flag (close) |

Dropped: rogue R4 (game-type comparisons; a rogue-domain instance of R2/R3) and rogue R9 (observable-behaviours citation depth; an mvc-rewrites convention). Rogue W1, W3, W4 were workspace-scoped checkers and do not port.

## Consequences

- COR-T-001's scope includes the four agent definitions, four specs, and two slash commands, not just the two role docs.
- Kickoff quality is enforced mechanically from the first kickoff; the orchestrator is a dispatcher, not an inline author (Pure-B discipline per the role doc).
- `./.gitignore` gains `.claude/artifacts/tmp/`; `./CLAUDE.md` documentation placement gains a clarifying line about `./.claude/`.
- Four specs and four agent definitions become maintained artifacts; spec changes follow the same review discipline as any domain-2 artifact.
- If a rule fires falsely or a needed rule is missing, the fix is a spec edit plus an OBSERVATIONS entry, mirroring rogue's false-positive protocol.
- When departments land (ADR-021), department-scoped checkers can layer beside the universal four, mirroring rogue's universal-vs-workspace-scoped split.
