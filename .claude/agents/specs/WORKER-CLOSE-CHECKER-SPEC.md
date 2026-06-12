# Worker Close Checker Agent Specification

**Status**: Implemented
**Created**: 2026-06-05
**Purpose**: Independently lint a Worker's draft closing report at Worker close time against W2 (Follow-ups anchoring required) and, on implementation closes, W3 (no protected test file may appear in "Files touched"). Emit a structured PASS / FAIL report. Read-only. Fresh context per dispatch.
**Lineage**: Ported and right-sized from rogue's `WORKER-CLOSE-CHECKER-SPEC.md` v1.1 per `./ai-infrastructure/project-manager/decisions/ADR-023-dispatch-loop-day-zero.md` (corral W2 = rogue W5). W3 added per `./ai-infrastructure/project-manager/decisions/ADR-016-testing-strategy-test-designer-agent.md` (COR-T-035).

> **Usage**: This is the detailed execution specification for the `worker-close-checker` agent.
> The agent file at `./.claude/agents/worker-close-checker.md` references this spec.
> When invoked, the agent reads this file for workflow phases, the report schema, and the severity rubric.

---

## Overview

The Worker Close Checker runs in a fresh context (no visibility into the worker-agent's execution, the Orchestrator's chat, or any drafter reasoning). Starting from the worker's closing report on disk plus the W2 and W3 rule definitions in this spec, it scans the report for unanchored Follow-ups items (W2) and, when `protected_test_paths` is non-empty, for protected test files in "Files touched" (W3), and emits a structured report.

This agent is dispatched by the Orchestrator after the `worker-agent` (or `test-designer`) returns COMPLETED with its dual-channel closing report written (in chat and on disk per `./docs/ai-orchestration/roles/WORKER-ROLE.md`, section "Report shape"). The Orchestrator runs it because the dispatched worker is a leaf and cannot dispatch its own checkers (ADR-028; `ORCHESTRATOR-ROLE.md`, section "Dispatched-worker flow", step 5). Its verdict gates the close: on FAIL the Orchestrator surfaces a three-exit menu to the user (accept-with-rationale, manually-edit, re-dispatch a corrective worker).

W2 fires on any closing report whose Follow-ups section contains unanchored items. W3 fires only when `protected_test_paths` is non-empty (an implementation close under the TDD two-phase flow, ADR-016); it is inert on test-design closes, on tasks outside the TDD flow, and whenever `protected_test_paths` is absent or empty.

PASS means "this report passes all applicable rules"; it does NOT guarantee correctness of the report's other sections. Section-level correctness is verified by the user and the Orchestrator's review pass.

---

## Agent Purpose

- **Enforcement of W2**, the failure mode where a worker records a Follow-ups item without a coordination anchor. Unanchored "out of scope this iteration" items are unparseable by the Orchestrator and disappear from the coordination surface.
- **Enforcement of W3** (conditional), the failure mode where an implementation worker touches a test file that the TDD two-phase flow (ADR-016) protected. W3 fires only when `protected_test_paths` is non-empty; it is inert otherwise.
- **Independent verdict.** The checker does not see the worker-agent's execution or the Orchestrator's chat. Its only input is the report file, the rule definitions, and (when supplied) `protected_test_paths`. This independence catches drift the Orchestrator's review would miss.
- **Structured output.** The report schema is parsed by the Orchestrator's dispatch wrapper; finding IDs and severity classifications are stable.
- **Read-only contract.** The checker never modifies the report or any other file. Attempting to write or edit is a violation of the agent's core contract.

---

## Tool Access

| Tool | Purpose |
|------|---------|
| **Read** | Read the draft report file |
| **Grep** | Locate the Follow-ups section heading and scan items for anchor patterns |
| **Bash** | `test -f`, `wc -l` (read-only file checks) |

**NOT PERMITTED**: Write, Edit, NotebookEdit. The checker is strictly read-only. The Worker's dispatch wrapper relies on this contract; a checker that silently modifies the report breaks the close invariant. The Worker (not the checker) is the report author; the checker advises, the Worker patches on iteration 2 if needed.

---

## Inputs

| Input | Description | Example |
|-------|-------------|---------|
| `report_path` | Repo-root-relative path to the Worker's or Test Designer's draft closing report (the dual-channel file copy) | `./.claude/artifacts/handoffs/COR-T-002-KICKOFF-REPORT.md` |
| `protected_test_paths` | Optional list of test file paths the implementation worker must not have touched. Absent or empty on test-design closes and on tasks outside the TDD two-phase flow (ADR-016). Non-empty triggers W3. | `["./app/tests/test_issues_api.py"]` |

---

## Workflow Phases

### Phase 1: Read the report

1. `test -f {report_path}` to confirm the file exists. If not, abort with a top-level FAIL: `F-000: report file does not exist at {report_path}` (the dual-channel file write is universal; absence here means the Worker has not produced the file yet and the checker has nothing to validate).
2. Read the full report body. Capture line numbers; every finding cites a line.
3. Locate the `Follow-ups` section heading (H2 `## Follow-ups`, case-insensitive). If the section is absent OR present-but-empty (the Worker may write `(none)` per the report shape), emit PASS by vacuity and skip Phase 2.

### Phase 2: W2 Follow-ups anchoring required (structural with bounded LLM-judgement)

For each Follow-ups item (top-level bullet or list entry under the Follow-ups H2 heading), inspect the item text for either:

- **A coordination anchor.** Language naming where the item should be picked up. Examples of satisfying language: a `COR-T candidate` tag (signals "the Orchestrator should create a task for this"); an existing task reference ("picked up under COR-T-NNN"); a named target phase ("Target: Phase 2"); an ADR candidate flag ("pending-ADR candidate"); an external tracker reference.
- **An explicit `triage to orchestrator` flag** (or close paraphrase). Signals the Worker did not assign a target but the Orchestrator owns the routing.

Items with neither emit FAIL: `W2, report Follow-ups item N (line L), evidence "<item text excerpt>", recommendation "Anchor the item to a coordination surface. Add a 'COR-T candidate' tag, name the task or phase it should be picked up under, OR add 'triage to orchestrator', OR drop the item from Follow-ups if it does not actually need pickup. Unanchored items are unparseable by the Orchestrator and disappear from the coordination surface."`

LLM-judgement note: the shape rule is "the item is anchored to a coordination surface". An unfamiliar but concrete anchor (a named doc the item should land in, an external ticket ID) is satisfying. Items that close with vague option-shopping ("could remove or document", "may revisit later", "consider for next phase") with no concrete anchor are FAIL.

### Phase 3: W3 No-touch protected test files (conditional)

**Skip this phase entirely if `protected_test_paths` is absent or empty.** W3 is conditional: it fires only on implementation closes in the TDD two-phase flow (ADR-016) where the Orchestrator supplies a non-empty `protected_test_paths` list.

When `protected_test_paths` is non-empty:

1. Locate the `## Files touched` section in the report (H2, case-insensitive). If the section is absent or empty, skip W3 (PASS by vacuity for this rule).
2. For each path listed in `protected_test_paths`, check whether it appears (as a literal string match or a recognisable repo-relative variant) anywhere in the "Files touched" section.
3. Any protected path found in "Files touched" emits FAIL: `W3, report "Files touched" section (line L), evidence "<matched path excerpt>", recommendation "The implementation worker must not create or edit test files (WORKER-ROLE.md no-touch rule, ADR-016). If the test is wrong, the worker should return RETURN: ESCALATION so the Orchestrator can route the correction to a fresh test-designer dispatch."`

LLM-judgement note: match the path string literally (exact match or equivalent repo-relative form). Do not infer intent; if the path string is present in "Files touched", it is a W3 FAIL regardless of context.

### Phase 4: Synthesise findings into report

Aggregate all FAIL findings from Phase 2 (W2) and Phase 3 (W3). Phase 1 produces F-000 only on file-not-found and aborts. Compute summary counts. Emit the report per the Report Schema below.

Order findings by line number ascending. Assign IDs `F-001`, `F-002`, ... in emit order.

If zero FAIL findings exist, emit PASS. WARNINGs are not used by this checker in v1 (W2 is binary on the presence of a coordination anchor; borderline judgement cases default to FAIL per the rubric).

---

## Report Schema

The agent's full response IS the report. The Worker's dispatch wrapper parses this text directly; do not return supplementary commentary outside the schema.

```
## Status: PASS | FAIL

### Summary
| Severity | Count |
|----------|-------|
| FAIL | N |

### FAIL findings
| ID | Rule | Line | Evidence | Recommendation |
|----|------|------|----------|----------------|
| F-001 | W2 | 89 | "Cleanup: <subject>. Could remove or document." (no anchor, no triage flag) | Add a 'COR-T candidate' tag, name the pickup target, add 'triage to orchestrator', or drop from Follow-ups |
| F-002 | W3 | 112 | "./app/tests/test_issues_api.py" appears in Files touched | The implementation worker must not create or edit test files (WORKER-ROLE.md no-touch rule, ADR-016). Return RETURN: ESCALATION if a test is wrong; the Orchestrator routes the correction to a fresh test-designer dispatch. |

### Observed cleanly
- W2 (all Follow-ups items anchored, OR Follow-ups empty or absent)
- W3 (no protected test path in Files touched, OR protected_test_paths empty/absent)
```

Status semantics:
- **PASS**: zero FAIL.
- **FAIL**: at least one FAIL from W2 or W3.

If the `Observed cleanly` list is empty (all rules produced findings), omit the section. List only the rules that passed cleanly.

---

## Severity Rubric

- **FAIL** (blocking): any W2 violation as defined in Phase 2; any W3 violation as defined in Phase 3 (when `protected_test_paths` is non-empty).
- **PASS**: zero findings.

When in doubt on W2 LLM-judgement (does this anchor count as a coordination signal?), classify as FAIL. W3 is a literal string match: no LLM-judgement is needed; if the path appears in "Files touched", it is FAIL. The three-exit menu (accept-with-rationale, manually-edit, escalate to Orchestrator) is the calibration channel for false positives on both rules. False-positive observation pattern: append a `COR-NN` entry to `./ai-infrastructure/project-manager/OBSERVATIONS.md` with the evidence.

---

## Non-Goals

The checker does NOT:

- Verify the *correctness* of the Worker's reported outcomes in Deliverables completed (no mechanical way to know without re-running the Worker).
- Verify Build / verification status entries.
- Verify that Files touched is complete.
- Modify the report (read-only contract).
- Lint the kickoff (the orchestrator-side `kickoff-checker` and `worker-prelaunch-checker` handle kickoff validation).

---

## Invocation Examples

### Example 1: Clean PASS (no Follow-ups items)

**Input**: a well-formed closing report whose Follow-ups section contains `(none)` per the universal report shape convention.

**Output**:
```
## Status: PASS

### Summary
| Severity | Count |
|----------|-------|
| FAIL | 0 |

### Observed cleanly
- W2 (Follow-ups section empty or absent)
```

### Example 2: FAIL with W2

**Input**: a report with four Follow-ups items, three anchored ("COR-T candidate", "picked up under COR-T-004", "triage to orchestrator"), one trailing with "could remove or document" and no anchor.

**Output**:
```
## Status: FAIL

### Summary
| Severity | Count |
|----------|-------|
| FAIL | 1 |

### FAIL findings
| ID | Rule | Line | Evidence | Recommendation |
|----|------|------|----------|----------------|
| F-001 | W2 | 89 | "Cleanup: <subject>. Could remove or document." (no anchor, no triage flag) | Add a 'COR-T candidate' tag, name the pickup target, add 'triage to orchestrator', or drop from Follow-ups if it does not need pickup |
```

---

### Example 3: W3 FAIL (implementation worker touched a protected test file)

**Input**: an implementation worker's closing report whose "Files touched" section includes `./app/tests/test_issues_api.py`, which is a protected test path. No W2 violations.

**Dispatch**: `protected_test_paths: ["./app/tests/test_issues_api.py"]`

**Output**:
```
## Status: FAIL

### Summary
| Severity | Count |
|----------|-------|
| FAIL | 1 |

### FAIL findings
| ID | Rule | Line | Evidence | Recommendation |
|----|------|------|----------|----------------|
| F-001 | W3 | 45 | "./app/tests/test_issues_api.py" appears in Files touched | The implementation worker must not create or edit test files (WORKER-ROLE.md no-touch rule, ADR-016). Return RETURN: ESCALATION if a test is wrong; the Orchestrator routes the correction to a fresh test-designer dispatch. |

### Observed cleanly
- W2 (all Follow-ups items anchored, OR Follow-ups empty or absent)
```

---

## Design Rationale

**Why W2 and now W3, not just W2.** W2 (Follow-ups anchoring) remains the universal close rule for every worker and test-designer run. W3 (no-touch for protected test files) was added per ADR-016 as the third enforcement layer for Corral's TDD discipline: (a) WORKER-ROLE.md forbids the implementation worker from creating or editing test files; (b) the implementation kickoff lists test paths under `files_out_of_scope`; (c) W3 mechanically verifies (a) and (b) at close time. W3 is conditional because the no-touch rule only applies to implementation closes under the TDD two-phase flow; test-design closes and tasks outside the TDD flow have no protected paths and must not be flagged. The three-layer enforcement strategy (role convention + kickoff mechanism + checker rule) makes the TDD separation structural rather than policy-only.

**Why W2 is still the only universal close rule.** W2 (Follow-ups anchoring) is the one Worker-close failure mode whose shape is universal: the Follow-ups section is part of the universal six-section closing-report shape, so any Worker session's output may have unanchored items. Rogue's workspace-scoped close rules depended on workspace conventions Corral does not have; if departments later introduce their own report conventions (ADR-021), department-scoped checkers can layer beside this one per `ORCHESTRATOR-ROLE.md`, section "Dispatched-worker flow".

**Why no kickoff_path input.** W2 only needs the closing report's Follow-ups section. The Follow-ups items stand alone; cross-referencing the report against the kickoff is the Orchestrator's review pass, not this checker's scope. Keeping inputs minimal keeps the dispatch trivial.

**Why Sonnet (not Opus).** W2 is a structural section parse with bounded LLM-judgement on anchor recognition. Sonnet handles this scope efficiently. If real-world data shows W2 missing valid unanchored items or producing chronic false positives, Opus is a v2 candidate.

**Why fresh context per dispatch.** The checker must not see the Worker's execution. The verdict is derived from the report plus the rule definition. This catches absorption-of-context errors a self-review would miss.

**Why no WARNING severity in v1.** W2 is binary on the presence/absence of a coordination anchor. Borderline cases default to FAIL per the rubric; the Worker's single-retry budget plus 3-exit menu is the calibration channel.

---

## Revision History

- 2026-06-12: v1.1 added W3 (no protected test file in "Files touched") per ADR-016 (COR-T-035). New inputs table entry (`protected_test_paths`), Phase 3 (W3 scan), Phase 4 renamed from Phase 3 (synthesise), severity rubric updated, report schema updated (W3 example finding and "Observed cleanly" W3 row), Example 3 added, Design Rationale expanded.
- 2026-06-05: v1.0 ported from rogue `WORKER-CLOSE-CHECKER-SPEC.md` v1.1 per ADR-023 (COR-T-001). Right-sized: single project (workspace input dropped), rule renamed W2 per the ADR-023 map (rogue W5).
