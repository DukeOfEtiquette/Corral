# Executor Agent Specification

**Status**: Implemented
**Created**: 2026-06-09
**Purpose**: Execute one drafted kickoff against the Corral workspace as an Orchestrator-dispatched subagent, and return one of two verdict-lined results (COMPLETED report or ESCALATION). Adopts the Executor role; reads exactly the files the Orchestrator names (explicit context pass-down). This is the single executor execution path in Corral.
**Lineage**: Ported and right-sized from rogue's `worker-agent` / `WORKER-AGENT-SPEC.md` (rogue ADR-025) per `./ai-infrastructure/project-manager/decisions/ADR-028-worker-as-dispatched-subagent.md`. The spike that grounds the mechanics (no Agent tool in a dispatched subagent; no in-place resume; the `model` override works; foreground-only for interactive approvals) is rogue's #146; Corral inherits the validated design rather than re-spiking.

> **Usage**: This is the detailed execution specification for the `executor` agent.
> The agent file at `./.claude/agents/executor.md` references this spec and `./docs/ai-orchestration/roles/EXECUTOR-ROLE.md`.
> When invoked, the agent reads both for the workflow phases, the return schemas, and the role it adopts.

---

## Table of Contents

1. Overview
2. Agent Purpose
3. Tool Access
4. Inputs
5. Workflow Phases
6. Return Schema
7. Style Rules
8. Error Handling
9. Invocation Examples
10. Design Rationale
11. Revision History

---

## Overview

The Executor Agent is the dispatched-subagent execution path for Corral kickoffs, established by ADR-028. The Orchestrator drafts and checks a kickoff (the `kickoff-drafter` / `kickoff-checker` loop), runs the prelaunch checker, then dispatches this agent via the Task tool (`model: sonnet`, foreground) to execute it. The user interacts only with the Orchestrator; the Orchestrator dispatches and supervises the executor. There is no parallel human-driven executor session (ADR-028 retired the `/corral-worker` slash command).

Three hard constraints, inherited from rogue's validating spike (#146) and recorded in ADR-028, shape this spec:

- A dispatched subagent has NO Agent/Task tool. The executor cannot dispatch its own prelaunch/close checkers; the Orchestrator runs them. The executor is a leaf.
- In-place resume is unavailable on the dispatched-subagent path. Escalation is therefore return-and-re-dispatch: the executor returns an escalation, the Orchestrator answers, a FRESH executor is dispatched with the answer folded in.
- The `model: sonnet` dispatch override works; the executor runs on Sonnet independent of the Opus Orchestrator.

The executor does NOT free-explore. It reads the kickoff, the `explicit_reads` the Orchestrator names, and (on re-dispatch) the `resume_anchor`. It does not survey workspace state, does not draft kickoffs, and does not run the Orchestrator command (`EXECUTOR-ROLE.md` section "Not in scope").

---

## Agent Purpose

- **Execute** the kickoff at `kickoff_path` against `workspace`, making the changes the kickoff specifies against the files it names, per `EXECUTOR-ROLE.md` section "Execute the plan".
- **Escalate by return value** when an `EXECUTOR-ROLE.md` failure mode fires (ambiguous kickoff, kickoff-vs-observed-state conflict, convention conflict, an unpinned decision the work requires). Return `RETURN: ESCALATION` with the four-part block; do not guess, and do not ask the user directly (the Orchestrator is the interlocutor).
- **Complete and report** when the deliverables are done. Return `RETURN: COMPLETED` with the six-section report, write the dual-channel report file, and apply STATUS hygiene once.
- **Resume on re-dispatch** by reconstructing state from the kickoff + `resume_anchor` + `escalation_answer` + `prior_progress_summary`, not by re-executing completed work.

---

## Tool Access

| Tool | Purpose |
|------|---------|
| **Read** | Read `kickoff_path`, every file in `explicit_reads`, and (on re-dispatch) `resume_anchor`. No other reads. |
| **Glob / Grep** | Locate exact lines/sections inside the named reads when the kickoff cites a symbol or section. Bounded to the named files/dirs; NOT free-exploration. |
| **Bash** | Shell-only operations the kickoff specifies (file moves, `git status` / `git diff` for crash-recovery diagnosis). Not for builds (compose-only per ADR-003, and builds are user-run per `EXECUTOR-ROLE.md`). |
| **Edit** | In-place changes to existing in-scope files. |
| **Write** | New in-scope files and the dual-channel report at `report_path`. |

**NOT PERMITTED**: Agent / Task (the executor is a leaf; a dispatched subagent has no Agent tool). The executor dispatches no subagents.

---

## Inputs

The Orchestrator passes these via the Task-tool dispatch prompt. The executor parses them in Phase 1.

| Input | Type | Description | Example |
|-------|------|-------------|---------|
| `workspace` | string | Literal workspace name, named not deduced. Validated; abort on mismatch. | `corral` |
| `kickoff_path` | repo-relative path | The kickoff to execute. Read end-to-end before acting. | `./.claude/artifacts/handoffs/COR-T-015-KICKOFF.md` |
| `explicit_reads` | markdown list | Every file the executor loads, in order, each with a one-line why. `./CLAUDE.md` is auto-loaded; the list adds each reference the kickoff names. Read exactly these. | (see below) |
| `report_path` | repo-relative path OR "derive" | Dual-channel report destination. "derive" = `<kickoff-dir>/<KICKOFF-BASENAME>-REPORT.md` per `EXECUTOR-ROLE.md` section "Report shape", dual-channel. | (derived) |
| `status_deltas` | markdown list OR "universal hygiene only" | Task-specific STATUS fields to mutate on COMPLETED. | `phase ... ; "Next step" reword` |
| `attempt_number` | int | 1 on first dispatch; N+1 on re-dispatch. | `1` |
| `escalation_answer` | markdown OR "(none)" | The Orchestrator's pinned answer to the prior escalation. Empty on attempt 1. | `(none)` |
| `resume_anchor` | repo-relative path OR "(none)" | The prior attempt's partial `report_path`. Empty on attempt 1. | `(none)` |
| `prior_progress_summary` | markdown OR "(none)" | The prior attempt's "Progress so far" bullets. Empty on attempt 1. | `(none)` |

**`explicit_reads` shape** (the Orchestrator constructs this; the executor reads exactly these, in order):

```markdown
- ./docs/ai-orchestration/roles/EXECUTOR-ROLE.md (the role the executor adopts; the universal minimum)
- ./ai-infrastructure/project-manager/decisions/ADR-012-issue-label-view-schema.md (the schema the deliverable follows)
- ./ai-infrastructure/project-manager/docs/architecture/OVERVIEW.md (the target shape the kickoff draws from)
```

**Re-dispatch fields** (populated on `attempt_number > 1`):

```markdown
- escalation_answer:
  - **Output path:** Write the file to `./ai-infrastructure/project-manager/docs/architecture/NOTES.md`. Pinned by the Orchestrator; treat as an authoritative kickoff decision.
- resume_anchor: ./.claude/artifacts/handoffs/COR-T-015-KICKOFF-REPORT.md
- prior_progress_summary:
  - Drafted sections 1-2 of the file body (uncommitted; in the partial report).
  - Stopped at the output-path ambiguity before writing the file.
```

---

## Workflow Phases

### Phase 1: Parse inputs and adopt the role

1. Adopt the Executor role per `EXECUTOR-ROLE.md` (all sections apply except the Identity deltas in the agent file: you return to the Orchestrator, you escalate by return value, you run no checker subagents).
2. Parse every input. Validate:
   - `workspace` is the expected literal (`corral`); abort on mismatch.
   - `kickoff_path` exists (`test -f`); abort if missing.
   - `attempt_number` is a positive integer; the re-dispatch fields are present iff `attempt_number > 1`.
   - `report_path` resolves (use the derivation rule if "derive").
3. If `attempt_number == 1`, escalation fields must all be "(none)".

### Phase 2: Load explicit reads

1. Read `kickoff_path` end-to-end before acting on any instruction.
2. Read each file in `explicit_reads`, in order. Order encodes how the Orchestrator intends context to layer.
3. On `attempt_number > 1`, read `resume_anchor` (the prior partial report) to learn what the prior attempt completed.
4. Read NOTHING else. No surveying, no workspace deduction, no free-exploration. If a file in `explicit_reads` is missing, that is a kickoff-vs-observed-state conflict: escalate (Phase 4) rather than guessing.

### Phase 3: Execute the kickoff

1. Make the changes the kickoff specifies, in order, against the in-scope files it names, per `EXECUTOR-ROLE.md` section "Execute the plan". Advance one step at a time; verify intermediate state.
2. On `attempt_number > 1`: treat `escalation_answer` as a pinned decision (authoritative, like a kickoff decision); treat `prior_progress_summary` as already done (do NOT re-execute it); continue from the resume point.
3. At each step, watch for an `EXECUTOR-ROLE.md` failure mode. If one fires and the work cannot proceed correctly without a decision you must not make, go to Phase 4 (escalate). Otherwise continue to Phase 5 (complete).

### Phase 4: Escalation return (when a failure mode blocks correct execution)

A genuine gap the executor must not resolve itself: an ambiguous kickoff, a kickoff-vs-observed-state conflict (including a missing `explicit_reads` file), a kickoff request that conflicts with a universal convention, or an out-of-scope decision the kickoff did not pin. When one blocks correct execution:

1. Write a PARTIAL report to `report_path`: the six-section shape with completed sections filled in, unfinished sections marked `(incomplete: blocked on escalation)`, and the four-part escalation block appended.
2. Do NOT apply STATUS hygiene (the task is not done).
3. Return `RETURN: ESCALATION` + the four-part block (see Return Schema).

Escalation is a faithful surfacing of a real gap, not an Option-A/B deferral. If the kickoff genuinely pins the decision and the executor simply did not look hard enough, that is not an escalation; re-read and proceed.

### Phase 5: Completion return

When the deliverables are done:

1. Apply STATUS hygiene ONCE per `EXECUTOR-ROLE.md` section "Wrap-up STATUS hygiene": bump `last_updated`, append one `recent_updates` entry, apply the kickoff's named `status_deltas`. This is the ONLY phase that mutates `./ai-infrastructure/project-manager/STATUS.md`.
2. Write the full six-section report to `report_path` (dual-channel). List `report_path` and `./ai-infrastructure/project-manager/STATUS.md` under "Files touched".
3. Return `RETURN: COMPLETED` + the six-section report (identical to the file).

---

## Return Schema

The final message begins with a verdict line the Orchestrator parses to branch. Exactly one mode.

### Mode A: COMPLETED

```
RETURN: COMPLETED

## Deliverables completed
## Decisions made
## Surprises
## Follow-ups
## Files touched
## Build / verification status
```

Side effects before returning: the identical six sections are written to `report_path`; STATUS hygiene is applied once. "Files touched" lists `report_path` and `./ai-infrastructure/project-manager/STATUS.md`.

### Mode B: ESCALATION

```
RETURN: ESCALATION

## Escalation question
(One specific question the executor must not resolve itself, tied to an EXECUTOR-ROLE.md failure mode.)

## Context to answer
(What the executor observed, with file:line citations; why the kickoff is silent or contradictory; the candidate readings the executor sees and why it cannot pick among them. A faithful gap, not an Option-A/B deferral.)

## Progress so far
(2-4 cited bullets: which deliverables/steps completed before the blocker. Becomes the next attempt's prior_progress_summary.)

## Resume anchor
(Repo-relative path to the partial report just written to report_path.)
```

Side effect before returning: a partial report is written to `report_path`. STATUS is NOT touched.

---

## Style Rules

1. **Verdict line first.** The final message starts with `RETURN: COMPLETED` or `RETURN: ESCALATION`, nothing before it.
2. **No em dashes** in any file written (U+2014, U+2013). Repo writing rule (`./CLAUDE.md`).
3. **Explicit reads only.** Read `kickoff_path`, `explicit_reads`, `resume_anchor` (re-dispatch); nothing else.
4. **Leaf node.** Dispatch no subagents.
5. **STATUS-once.** Mutate `./ai-infrastructure/project-manager/STATUS.md` only on COMPLETED, exactly one `recent_updates` entry and one `last_updated` bump.
6. **Repo-relative `./` paths.** Per `./CLAUDE.md`, cite paths repo-root-relative, not absolute.
7. **Cite, do not invent.** Per `./CLAUDE.md` Agent Discipline, every claim about repo state in the report is verified in-session.

---

## Error Handling

| Condition | Behaviour |
|-----------|-----------|
| `workspace` not the expected literal (`corral`) | Abort with error; do not execute. |
| `kickoff_path` missing / unreadable | Abort with error naming the path. |
| `attempt_number > 1` but re-dispatch fields absent | Abort with error; the dispatch was malformed. |
| A file in `explicit_reads` is missing | Escalate (kickoff-vs-observed-state conflict); do not guess. |
| Kickoff asks the executor to dispatch a subagent | Note it; the Orchestrator runs subagents. Proceed if non-blocking; escalate if blocking. |
| `report_path` directory not writable | Escalate (surface the path conflict); do not skip the file write silently. |
| Deliverables done but STATUS deltas ambiguous | Apply only the universal two (`last_updated`, `recent_updates`) plus exactly what the kickoff named; do not invent fields. |

Abort behaviour: return an error message (not a COMPLETED or ESCALATION verdict). The Orchestrator treats abort as a malformed-dispatch case and surfaces it to the user.

---

## Invocation Examples

### Example 1: Happy path (attempt 1, COMPLETED)

**Dispatch prompt (constructed by the Orchestrator; dispatched with `model: sonnet`, foreground):**

```
Execute a kickoff as a dispatched Executor. Read ./.claude/agents/specs/EXECUTOR-AGENT-SPEC.md and ./docs/ai-orchestration/roles/EXECUTOR-ROLE.md first.

Inputs:
- workspace: corral
- kickoff_path: ./.claude/artifacts/handoffs/COR-T-015-KICKOFF.md
- explicit_reads:
  - ./docs/ai-orchestration/roles/EXECUTOR-ROLE.md (the role to adopt)
- report_path: derive
- status_deltas: universal hygiene only
- attempt_number: 1
- escalation_answer: (none)
- resume_anchor: (none)
- prior_progress_summary: (none)

Return RETURN: COMPLETED + the six-section report, or RETURN: ESCALATION + the four-part block.
```

**Return:** `RETURN: COMPLETED` + the six-section report; `COR-T-015-KICKOFF-REPORT.md` and `./ai-infrastructure/project-manager/STATUS.md` written.

### Example 2: Escalation then re-dispatch

Attempt 1 returns `RETURN: ESCALATION` (the kickoff's prose and its "Files in scope" line disagree on the output path). The Orchestrator answers and re-dispatches:

```
Inputs (attempt 2):
- ... (workspace, kickoff_path, explicit_reads, report_path unchanged) ...
- attempt_number: 2
- escalation_answer:
  - **Output path:** Write to ./ai-infrastructure/project-manager/docs/architecture/NOTES.md. Pinned; treat as authoritative.
- resume_anchor: ./.claude/artifacts/handoffs/COR-T-015-KICKOFF-REPORT.md
- prior_progress_summary:
  - Drafted the notes body in the partial report; stopped at the output-path ambiguity.
```

**Return:** `RETURN: COMPLETED` + report; STATUS hygiene applied once on this final attempt.

---

## Design Rationale

**Why cross-department (one agent, parameterised by workspace) instead of a Corral-specific executor.** Mirrors the `kickoff-drafter` rationale: one agent reads the minimum the Orchestrator names and adopts the cross-department `EXECUTOR-ROLE.md`; explicit context pass-down removes the need to bake workspace knowledge into the agent. Corral has a single workspace today; building the agent workspace-agnostic by construction (everything comes from inputs) avoids a rename if departments are created later (ADR-021).

**Why two verdict-lined return modes.** The Orchestrator must branch mechanically on the executor's return without parsing prose, exactly as the drafter+checker loop branches on a checker's verdict line. COMPLETED vs ESCALATION is the executor's analogue.

**Why return-and-re-dispatch instead of in-place resume.** In-place resume is unavailable on the dispatched-subagent path (rogue spike #146, recorded in ADR-028). The fresh-executor re-dispatch reconstructs state from the kickoff + the dual-channel report (the resume anchor) + the pinned answer, the same three-source pattern `EXECUTOR-ROLE.md` section "Crash recovery" already uses, with the escalation answer added.

**Why STATUS-once on COMPLETED.** A multi-attempt task must not double-stamp STATUS (multiple `recent_updates` entries, premature phase flips). Making hygiene a COMPLETED-only side effect keeps one task to one STATUS update, and makes the close-checker-visible signal (`./ai-infrastructure/project-manager/STATUS.md` in "Files touched") appear only on the truly-final attempt.

**Why the executor is a leaf (checkers Orchestrator-run).** A dispatched subagent has no Agent tool. So the prelaunch and close checkers move up to the Orchestrator (which already dispatches `kickoff-drafter` / `kickoff-checker` per ADR-023). This is the key structural difference from the old `/corral-worker` session, which dispatched its own checkers; the dispatched executor cannot. The full orchestrator-run protocol is in `./docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md` section "Dispatched-worker flow".

---

## Revision History

- 2026-06-09: v1.0 initial authoring for the ADR-028 dispatched-worker flow (COR-T-015). Single executor execution path; the `/corral-worker` slash command was retired in the same task. Ported from rogue's `worker-agent` (rogue ADR-025) and grounded in rogue's spike #146 per ADR-028.
- 2026-06-12: renamed from `WORKER-AGENT-SPEC.md` to `EXECUTOR-AGENT-SPEC.md` per ADR-032 (COR-T-036).
