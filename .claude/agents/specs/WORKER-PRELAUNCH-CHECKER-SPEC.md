# Executor Prelaunch Checker Agent Specification

**Status**: Implemented
**Created**: 2026-06-05
**Purpose**: Independently lint a drafted kickoff file at Executor prelaunch time against the universal Executor-acceptance rule W1 (deferral acceptance-test required) and emit a structured PASS / FAIL report. Read-only. Fresh context per dispatch.
**Lineage**: Ported and right-sized from rogue's `WORKER-PRELAUNCH-CHECKER-SPEC.md` v1.1 per `./ai-infrastructure/project-manager/decisions/ADR-023-dispatch-loop-day-zero.md` (corral W1 = rogue W2).

> **Usage**: This is the detailed execution specification for the `worker-prelaunch-checker` agent.
> The agent file at `./.claude/agents/worker-prelaunch-checker.md` references this spec.
> When invoked, the agent reads this file for workflow phases, the report schema, and the severity rubric.

---

## Overview

The Executor Prelaunch Checker runs in a fresh context (no visibility into the Executor's reading pass, the Orchestrator's chat, or any drafter reasoning). Starting from the drafted kickoff file on disk plus the W1 rule definition in this spec, it scans for deferral items that lack an acceptance test or user-confirm flag and emits a structured report.

This agent is dispatched by the Orchestrator after it has drafted and checked a kickoff and before it dispatches the `executor` (`./docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md`, section "Dispatched-worker flow", step 2). The Orchestrator runs it because the dispatched executor is a leaf and cannot dispatch its own checkers (ADR-028). Its verdict is gating: a FAIL prevents the Orchestrator from spending an executor dispatch against a kickoff that pins deferrals without proving they are safe; instead, the Orchestrator re-drafts the kickoff through the drafter+checker loop or surfaces the verdict to the user.

W1 fires on any kickoff containing a deferral surface (Decisions rows with a "deferred" answer, an explicit Out-of-scope section beyond a plain file list, or a Follow-ups section in the kickoff body). Kickoffs with no such surface see PASS by vacuity.

PASS means "this kickoff carries no unanchored deferrals"; it does NOT guarantee semantic correctness of resolved decisions. Semantic correctness is the Orchestrator's responsibility at decision-resolution time.

---

## Agent Purpose

- **Enforcement of W1**, the failure mode where a kickoff pins a deferral without naming what proves the deferral is acceptable for this task. Without an acceptance test or user-confirm flag, the worker absorbs the deferral as "do nothing here" and ships a regression (the deferred behaviour was load-bearing; the kickoff did not say so).
- **Independent verdict.** The checker does not see the Orchestrator's chat or any drafter reasoning. Its only inputs are the file and the rule definition; this independence catches drift the Orchestrator's self-review would miss.
- **Structured output.** The report schema is parsed by the Orchestrator's dispatch wrapper; finding IDs and severity classifications are stable.
- **Read-only contract.** The checker never modifies the kickoff or any other file. Attempting to write or edit is a violation of the agent's core contract.

---

## Tool Access

| Tool | Purpose |
|------|---------|
| **Read** | Read the kickoff file |
| **Grep** | Scan kickoff body for deferral-surface section headings and per-item acceptance-test patterns |
| **Bash** | `test -f`, `wc -l` (read-only file checks) |

**NOT PERMITTED**: Write, Edit, NotebookEdit. The checker is strictly read-only. The Orchestrator's dispatch wrapper relies on this contract; a checker that silently modifies the kickoff breaks the prelaunch invariant.

---

## Inputs

| Input | Description | Example |
|-------|-------------|---------|
| `kickoff_path` | Repo-root-relative path to the drafted kickoff file | `./.claude/artifacts/handoffs/COR-T-002-KICKOFF.md` |

---

## Workflow Phases

### Phase 1: Read the kickoff and identify the deferral surface

1. `test -f {kickoff_path}` to confirm the file exists. If not, abort with a top-level FAIL: `F-000: kickoff file does not exist at {kickoff_path}`.
2. Read the full kickoff body. Capture line numbers; every finding cites a line.
3. Identify the deferral surface. Any of the following qualifies; case-insensitive heading match:
   - A `Decisions` / `Decisions resolved` section containing rows whose pinned answer is "deferred" / "out of scope this task" / "follow-up"
   - An `Out of scope` / `Explicitly out of scope` / `Deferrals` section (beyond the plain "Files out of scope" path list, which is a scope boundary, not a deferral)
   - A `Follow-ups` section embedded in the kickoff body (distinct from the closing-report Follow-ups, which is the close checker's domain)
   - Inline "Decision N: deferred" / "deferred to <later task or phase>" patterns anywhere in the kickoff body

If no deferral surface is found, emit PASS by vacuity and skip Phase 2.

### Phase 2: W1 deferral acceptance-test required (LLM-judgement)

For each deferral item identified in Phase 1, inspect the item text for either:

- **An explicit acceptance test.** Language naming the observable that proves the deferral is acceptable for this task. Examples of satisfying language: "Acceptance: the existing <behaviour X> still works after this task"; "To prove deferral is acceptable: <user-runnable test step>"; "Verified acceptable by <named existing behaviour or doc reference>".
- **An explicit "confirm with user before execution" flag.** Language directing the Worker to surface the deferral to the user before continuing. Examples of satisfying language: "Worker: confirm with user before continuing"; "Stop-condition: surface this deferral to the user for acceptance before execution"; "Requires user confirmation before the task begins."

Items with neither emit FAIL: `W1, item N (line L), evidence "<item text excerpt>", recommendation "Name an explicit acceptance test for this deferral, or flag it for user confirmation before execution. A deferral without an acceptance criterion or a stop-condition is silently absorbed by the Executor as 'do nothing here', which ships a regression if the deferred behaviour is load-bearing. The kickoff body must either prove the deferral is safe or stop the Executor until the user confirms."`

LLM-judgement note: a deferral that explicitly names what is deferred AND scopes the impact ("does not affect this task because <reason>") satisfies the rule even without a formal acceptance section, provided the scope-of-impact reasoning is concrete (cites a named existing behaviour, a doc, or a file:line). Vague "out of scope this iteration" without scope-of-impact reasoning is a FAIL.

Items that pin the deferral to a target (a later task or phase) AND state the impact on this task is none ("deferred to COR-T-NNN; this task's surfaces do not depend on it because <named reason>") are PASS. Items that name a target but say nothing about this-task impact are FAIL: the target pin is a coordination signal for the Orchestrator, not an acceptance test for the Executor.

### Phase 3: Synthesise findings into report

Aggregate all FAIL findings from Phase 2 (Phase 1 produces F-000 only on file-not-found and aborts). Compute summary counts. Emit the report per the Report Schema below.

Order findings by line number ascending. Assign IDs `F-001`, `F-002`, ... in emit order.

If zero FAIL findings exist, emit PASS. WARNINGs are not used by this checker in v1 (W1 is binary on the presence of an acceptance test or user-confirm flag; borderline judgement cases default to FAIL per the rubric).

---

## Report Schema

The agent's full response IS the report. The Orchestrator's dispatch wrapper parses this text directly; do not return supplementary commentary outside the schema.

```
## Status: PASS | FAIL

### Summary
| Severity | Count |
|----------|-------|
| FAIL | N |

### FAIL findings
| ID | Rule | Line | Evidence | Recommendation |
|----|------|------|----------|----------------|
| F-001 | W1 | 113 | "Decision 10: <subject> deferred" (no acceptance test, no user-confirm flag) | Name what proves the deferral is acceptable for this task, or flag for user confirmation before execution |

### Observed cleanly
- W1 (all deferrals carry acceptance tests or user-confirm flags, OR no deferral surface present)
```

Status semantics:
- **PASS**: zero FAIL.
- **FAIL**: at least one FAIL.

If the `Observed cleanly` list is empty (W1 produced findings), omit the section.

---

## Severity Rubric

- **FAIL** (blocking): any W1 violation as defined in Phase 2.
- **PASS**: zero findings.

When in doubt on W1 LLM-judgement, classify as FAIL. The three-exit menu (re-run orchestrator / proceed-with-rationale / abort) is the calibration channel for false positives; chronic false positives surface in the user's exit choice and are logged for spec tuning. False-positive observation pattern: append a `COR-NN` entry to `./ai-infrastructure/project-manager/OBSERVATIONS.md` with the evidence.

---

## Non-Goals

The checker does NOT:

- Verify the *correctness* of resolved decisions in the kickoff body. Semantic correctness is the Orchestrator's responsibility.
- Verify that named reference files exist (the orchestrator-side `kickoff-drafter` is responsible for that at draft time).
- Modify the kickoff (read-only contract).
- Lint the kickoff against orchestrator-side rules R1-R8 (that is the orchestrator-side `kickoff-checker`'s scope).
- Validate the Executor's execution or report (that is `worker-close-checker`'s scope).

---

## Invocation Examples

### Example 1: Clean PASS (no deferral surface)

**Input**: a well-formed kickoff with no deferred Decisions rows, no Deferrals section, no Follow-ups in the kickoff body.

**Output**:
```
## Status: PASS

### Summary
| Severity | Count |
|----------|-------|
| FAIL | 0 |

### Observed cleanly
- W1 (no deferral surface present)
```

### Example 2: FAIL with W1

**Input**: a kickoff Decisions section containing a "deferred" row that names a target task but says nothing about this-task impact, and a "deferred to a later phase" line in the body with no acceptance test.

**Output**:
```
## Status: FAIL

### Summary
| Severity | Count |
|----------|-------|
| FAIL | 2 |

### FAIL findings
| ID | Rule | Line | Evidence | Recommendation |
|----|------|------|----------|----------------|
| F-001 | W1 | 87 | "Decision 4: <subject> deferred to COR-T-009" (names target task but does not state this-task impact; no acceptance test) | Name what proves the deferral is acceptable for this task, or flag for user confirmation before execution. A target pin alone is a coordination signal for the Orchestrator, not an acceptance test for the Executor. |
| F-002 | W1 | 115 | "<subject> deferred to a later phase" (no acceptance test, no user-confirm flag) | Name an explicit acceptance test, or flag for user confirmation |
```

---

## Design Rationale

**Why W1 is the only prelaunch rule in v1.** W1 (deferral acceptance-test required) is the one prelaunch failure mode whose shape is cross-department: any kickoff that permits a "decision pinned to deferred" row, an "out of scope" rationale, or a "follow-ups" tail-list is exposed to silent-absorption regression. Rogue's workspace-scoped prelaunch rules depended on workspace conventions Corral does not have; if departments later introduce their own kickoff conventions (ADR-021), department-scoped checkers can layer beside this one per `ORCHESTRATOR-ROLE.md`, section "Dispatched-worker flow".

**Why Sonnet (not Opus).** W1 is LLM-judgement bounded by tight rule definitions for what constitutes an acceptance test or a user-confirm flag. Sonnet handles this scope efficiently. If real-world data shows W1 missing valid violations or producing chronic false positives, Opus is a v2 candidate.

**Why fresh context per dispatch.** The checker must not see the Worker's reading pass or the Orchestrator's chat. The verdict is derived from the file plus the rule definition. This catches absorption-of-context errors a self-review would miss.

**Why read-only.** Independence is the load-bearing property. A checker that can modify the kickoff would be tempted (or prompted) to "auto-fix" findings, breaking the Worker's discipline of routing kickoff edits to the Orchestrator (the kickoff is the Orchestrator's artifact).

**Why no WARNING severity in v1.** W1 is binary on the presence/absence of an acceptance test or user-confirm flag. Borderline cases default to FAIL per the rubric; the three-exit menu is the calibration channel.

---

## Revision History

- 2026-06-05: v1.0 ported from rogue `WORKER-PRELAUNCH-CHECKER-SPEC.md` v1.1 per ADR-023 (COR-T-001). Right-sized: single project (workspace input dropped), rule renamed W1 per the ADR-023 map (rogue W2).
