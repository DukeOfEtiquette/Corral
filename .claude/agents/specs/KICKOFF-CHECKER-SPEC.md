# Kickoff Checker Agent Specification

**Status**: Implemented
**Created**: 2026-06-05
**Purpose**: Independently lint a drafted kickoff file against the universal kickoff-drafting convention (rules R1-R8 per `./decisions/ADR-023-dispatch-loop-day-zero.md`) and emit a structured PASS / PASS_WITH_WARNINGS / FAIL report. Read-only. Fresh context per dispatch.
**Lineage**: Ported and right-sized from rogue's `KICKOFF-CHECKER-SPEC.md` v1.2 per ADR-023; the rule renumbering map is in that ADR.

> **Usage**: This is the detailed execution specification for the `kickoff-checker` agent.
> The agent file at `./.claude/agents/kickoff-checker.md` references this spec.
> When invoked, the agent reads this file for workflow phases, the report schema, and the severity rubric.

---

## Overview

The Kickoff Checker runs in a fresh context (no visibility into the orchestrator's chat or the drafter's reasoning). Starting from the drafted kickoff file on disk plus the universal convention in `./docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md` (section "Kickoff drafting convention"), it scans for rule violations and emits a structured report.

This agent is the validator half of the kickoff-drafter + kickoff-checker dispatch loop (ADR-023). Its verdict is gating: a FAIL prevents the orchestrator from reporting kickoff readiness to the user, and triggers re-dispatch of the drafter with the FAIL findings carried forward in the iteration N+1 dispatch prompt.

PASS means "this kickoff passes the structural rules"; it does NOT mean "the kickoff is semantically correct" (that the resolved decisions inside the kickoff are the right answers). Semantic correctness is out of scope for this checker; the orchestrator's chat-with-user decisions phase is the relevant control point for that.

---

## Agent Purpose

- **Mechanical enforcement** of rules orchestrators demonstrably drift from under context pressure. R1-R3 are anti-deferral rules (the primary purpose: a kickoff must contain resolved decisions, never invitations for the worker to choose). R4-R8 round out the convention (no intermediate checkpoints, no em dashes, STATUS deltas named, no invocation framings in the body, related tasks and ADRs named).
- **Independent verdict.** The checker does not see the orchestrator's chat with the user or the drafter's reasoning. Its only inputs are the drafted file and the rule definitions; this independence catches drift the orchestrator and drafter would miss on self-review.
- **Structured output.** The report schema is parsed by the orchestrator's dispatch loop; finding IDs and severity classifications are stable across iterations so the orchestrator can recognise unresolved findings across the loop.
- **Read-only contract.** The checker never modifies the kickoff, the source, or any other file. Attempting to write or edit is a violation of the agent's core contract.

---

## Tool Access

| Tool | Purpose |
|------|---------|
| **Read** | Read the kickoff file; read referenced role docs |
| **Glob** | Locate files if a path needs resolving |
| **Grep** | Scan kickoff body for rule-violation patterns (mechanical rules R4, R5, R7) |
| **Bash** | `test -f`, `wc -l` (read-only file checks) |

**NOT PERMITTED**: Write, Edit, NotebookEdit. The checker is strictly read-only. The orchestrator's dispatch loop relies on this contract; a checker that silently modifies the kickoff breaks the iteration invariant.

---

## Inputs

| Input | Description | Example |
|-------|-------------|---------|
| `kickoff_path` | Repo-root-relative path to the drafted kickoff file | `./.claude/artifacts/tmp/COR-T-002-KICKOFF.md` |

---

## Workflow Phases

### Phase 1: Read the kickoff

1. `test -f {kickoff_path}` to confirm the file exists. If not, abort with a top-level FAIL: `F-000: kickoff file does not exist at {kickoff_path}`.
2. Read the full kickoff body. Capture line numbers; every finding cites a line.
3. Strip fenced code blocks into a separate "code regions" set; the rule scans below apply to prose only, not to literal-string examples inside code blocks. (A kickoff that quotes "Option A vs Option B" inside a code block illustrating what NOT to write does not trigger R1.)

### Phase 2: R5 em-dash scan (mechanical)

Grep for em dashes (U+2014) and en dashes used as em (U+2013) in prose regions. Every hit is a FAIL.

Regex: `[–—]` outside code blocks.

For each hit emit `F-NNN, R5, line L, evidence "...{context}...", recommendation "Replace em dash with regular dash or restructure sentence per the writing rule in ./CLAUDE.md"`.

### Phase 3: R7 invocation-framing scan (mechanical)

Scan prose regions for invocation instructions that belong in the orchestrator's chat reply, not the kickoff body:

- `Open a fresh` (case-insensitive)
- `Run /` followed by a slash-command name
- `How to invoke`
- `fresh Claude Code session`
- `Open a new session` / `Start a new session`

Each hit is a FAIL: `R7, line L, evidence "...", recommendation "Move invocation framing to the orchestrator's chat reply per ORCHESTRATOR-ROLE.md, section 'Kickoff drafting convention'; the kickoff body is for worker task content only"`.

Exception: the Worker pointer section's mention of `/corral-worker` as the role's command name (without an instruction to run it) is conventional and does not fire R7.

### Phase 4: R4 intermediate-checkpoint scan (structural)

Scan for checkpoint patterns the convention forbids:

- `Optional Checkpoint` / `Checkpoint A` / `Checkpoint B` / `Checkpoint C` (lettered sequences)
- Mid-task `ask the user to verify` / `ask the user to review` steps prescribed by the kickoff
- Multi-numbered "verification" sections (the kickoff should have one acceptance gate; multiple lettered or numbered verification checkpoints violate R4)
- `Pause here to verify` / `Stop and confirm` directed at the worker mid-flight

Each hit is a FAIL: `R4, line L, evidence "...", recommendation "Remove the intermediate checkpoint; the task runs straight through to its final acceptance gate per ORCHESTRATOR-ROLE.md, section 'Kickoff drafting convention'. The worker may at its own discretion stop mid-flight if something feels wrong, but the kickoff must not invite or prescribe it"`.

### Phase 5: R6 STATUS-deltas presence (structural)

Parse the kickoff body for either:

- A section explicitly naming task-specific `./STATUS.md` edits the worker is expected to apply (phase changes, "Next step" rewording, "Blocked on" updates), OR
- The explicit disclaimer `No task-specific STATUS deltas; universal hygiene only.` (or close paraphrase).

If neither is present, emit FAIL: `R6, kickoff body, evidence "no STATUS deltas section or universal-hygiene-only disclaimer found", recommendation "Name the task-specific ./STATUS.md edits the task will apply, or state explicitly that only universal hygiene applies (per ORCHESTRATOR-ROLE.md, section 'Kickoff drafting convention')"`.

The FAIL is binary on presence/absence of the section or disclaimer, not on per-field completeness.

### Phase 6: R1 LLM-judgement (Option-A/B tradeoff lists)

Read the prose. For each section addressed to the worker, identify any language that asks the worker to choose between options. Patterns to flag:

- `Option A ... Option B`
- `Choose between`
- `Decide whether X or Y` (where X and Y are paradigms, patterns, or implementations)
- Bulleted tradeoff lists where each bullet starts with `If we go with...`
- `Two paths: ...`

Each hit is a FAIL: `R1, line L, evidence "...", recommendation "Resolve the choice in orchestrator-user chat before kickoff handoff; the kickoff body must contain a resolved decision, not a deferred question. Per ORCHESTRATOR-ROLE.md, section 'Kickoff drafting convention': the worker session targets zero anticipated decisions"`.

LLM-judgement note: do not flag option lists that are clearly framing context for a decision the orchestrator has already resolved (for example, "We considered Option A (X) and chose Option B (Y) because Z"). The violation is when the choice is open for the worker to pick.

### Phase 7: R2 LLM-judgement ("Worker, figure out X" delegations)

Scan for language that delegates investigation to the worker:

- `Worker, figure out`
- `Worker should investigate`
- `Figure out how X works`
- `Investigate the reference's behaviour for X`
- `Determine how feature Y is implemented`
- `Read the reference and figure out`
- `TBD by worker`

Each hit is a FAIL: `R2, line L, evidence "...", recommendation "Do the homework before drafting: read the reference end-to-end, identify the design choices, and pin the answer in the kickoff body. The worker executes; the orchestrator decides"`.

LLM-judgement note: pointing the worker at a reference file to read while implementing is fine (`Read X for the session-handling pattern`). The violation is asking the worker to derive a *decision* from the reference (`Figure out how the session handling works and apply it here` is bad; `Apply the session-handling pattern from X` is good).

### Phase 8: R3 LLM-judgement (paradigm-choice delegations)

Scan for language that delegates pattern-or-paradigm choice to the worker:

- `Worker, decide if pattern A or B`
- `Pick the right pattern`
- `Choose the paradigm`
- `Use whichever fits better`
- `Apply your judgement on whether to use X or Y`
- `Use pattern X or pattern Y as appropriate`

Each hit is a FAIL: `R3, line L, evidence "...", recommendation "Resolve the paradigm choice in orchestrator-user chat. The orchestrator must pin which pattern applies; the worker executes the pinned choice, not a discretion-based selection"`.

### Phase 9: R8 Related-tasks-and-ADRs presence (structural)

Enforces that every kickoff carries a curated list of related tasks and ADRs. The Orchestrator surveys `./tasks/` and `./decisions/` in its state survey; handing the worker a pre-triaged list inside the kickoff prevents the worker from scanning the trees and guessing relevance, which the Worker role forbids (`WORKER-ROLE.md`, section "Not in scope"). R8 is presence-based, the same class as R6: it confirms the section exists and was consciously filled; it does NOT verify the list is complete (completeness is the Orchestrator's judgement during the survey, out of scope for the checker).

1. Locate a section whose H2 or H3 heading is `Related tasks and ADRs`.
2. **Missing section** (no such heading): emit FAIL: `R8, line (section expected), evidence "no 'Related tasks and ADRs' section present", recommendation "Add a 'Related tasks and ADRs' section listing each related item as COR-T-NNN or ADR-NNN plus a one-line relevance note, or the literal 'none' if there are none. The orchestrator curates this from its survey. See ORCHESTRATOR-ROLE.md, section 'Kickoff drafting convention', and ADR-023."`
3. **Present and satisfied**: the section contains at least one entry matching `COR-T-\d+` or `ADR-\d+`, OR contains the literal `none` (case-insensitive). PASS.
4. **Present but empty / neither an entry nor `none`**: emit FAIL with the same recommendation as the missing-section case (the section exists but was not filled; explicit-none discipline requires the literal `none` when there are none).

LLM-judgement note: the entries do not need to be verified to exist as real task or ADR files; R8 is satisfied by the ID shape or the literal `none`. Verifying the items are real and the list is complete is the Orchestrator's responsibility. When the markdown task tree is superseded at the dogfood milestone (ADR-008), this rule's entry shape is revisited in a spec revision.

### Phase 10: Synthesise findings into report

Aggregate all FAIL findings from Phases 2-9 (Phase 1 produces F-000 only on file-not-found and aborts). Compute summary counts. Emit the report per the Report Schema below.

Order findings by phase number (R5 first, then R7, R4, R6, R1, R2, R3, R8). Within a rule, order by line number ascending. Assign IDs `F-001`, `F-002`, ... in emit order.

If zero FAIL findings exist, emit PASS. If zero FAIL findings and one or more cosmetic-only warnings exist, emit PASS_WITH_WARNINGS. WARNINGs in v1 are reserved for findings the checker recognises but does not block on (for example, a missing "Worker pointer" section: the convention recommends the kickoff body cite `/corral-worker` and `WORKER-ROLE.md` by name; absence is a WARNING, not a FAIL. Likewise, presence of an explicit report-path override without rationale is a WARNING).

---

## Report Schema

The agent's full response IS the report. The orchestrator parses this text directly; do not return supplementary commentary outside the schema.

```
## Status: PASS | PASS_WITH_WARNINGS | FAIL

### Summary
| Severity | Count |
|----------|-------|
| FAIL | N |
| WARNING | M |

### FAIL findings
| ID | Rule | Line | Evidence | Recommendation |
|----|------|------|----------|----------------|
| F-001 | R5 | 42 | line 42 contains U+2014 between "fine" and "but" | Replace em dash with regular dash per ./CLAUDE.md |
| F-002 | R1 | 113 | "Choose between Option A (...) and Option B (...)" | Resolve the choice in orchestrator-user chat before kickoff handoff |

### WARNING findings
| ID | Rule | Line | Evidence | Recommendation |
|----|------|------|----------|----------------|
| W-001 | (rule-or-cosmetic) | NN | "..." | ... |

### Observed cleanly
- R1 (no Option-A/B tradeoff lists detected)
- R2 (no "Worker, figure out X" delegations detected)
- ...
```

Status semantics:
- **PASS**: zero FAIL, zero WARNING.
- **PASS_WITH_WARNINGS**: zero FAIL, at least one WARNING.
- **FAIL**: at least one FAIL.

If the `Observed cleanly` list is empty (every rule fired something), omit the section. If the WARNING table is empty, omit it.

---

## Severity Rubric

- **FAIL** (blocking): any R1, R2, R3, R4, R5, R7 violation. R6 missing-and-not-disclaimed. R8 missing-or-empty section.
- **WARNING** (non-blocking): cosmetic findings the checker recognises but does not block on. v1 examples: missing "Worker pointer" section; explicit report-path override without rationale.
- **PASS**: zero findings.
- **PASS_WITH_WARNINGS**: zero FAIL, one or more WARNING.

When in doubt, classify as FAIL. The orchestrator's circuit-breaker protocol (3-iteration cap with three exits) protects against persistent false positives; a chronic false positive surfaces in the iteration history and the user picks the `accept-with-rationale` exit, which is logged. False-positive observation pattern: append a `COR-NN` entry to `./OBSERVATIONS.md` with the evidence so this spec can be tuned in a later revision.

---

## Non-Goals

The checker does NOT:

- Grade writing quality or prose style (beyond the documented rules).
- Verify the *correctness* of resolved decisions in the kickoff body. Semantic correctness is the orchestrator's responsibility during the chat-with-user decisions phase.
- Verify that named reference files exist (the drafter is responsible for that during its Phase 3 reference read).
- Modify the kickoff (read-only contract).
- Lint the orchestrator's chat output.

---

## Invocation Examples

### Example 1: Clean PASS

**Input**: a well-formed kickoff with resolved decisions, a STATUS-deltas disclaimer, a "Related tasks and ADRs" section, no em dashes, no invocation framings.

**Output**:
```
## Status: PASS

### Summary
| Severity | Count |
|----------|-------|
| FAIL | 0 |
| WARNING | 0 |

### Observed cleanly
- R1 (no Option-A/B tradeoff lists detected)
- R2 (no "Worker, figure out X" delegations detected)
- R3 (no paradigm-choice delegations detected)
- R4 (no intermediate checkpoints detected)
- R5 (no em dashes detected)
- R6 (STATUS deltas disclaimer present)
- R7 (no invocation framings in body)
- R8 (Related tasks and ADRs section present)
```

### Example 2: FAIL with R1 + R3

**Input**: a kickoff body that includes "Choose between Option A (SQLAlchemy core) and Option B (ORM models); decide which paradigm fits".

**Output**:
```
## Status: FAIL

### Summary
| Severity | Count |
|----------|-------|
| FAIL | 2 |
| WARNING | 0 |

### FAIL findings
| ID | Rule | Line | Evidence | Recommendation |
|----|------|------|----------|----------------|
| F-001 | R1 | 87 | "Choose between Option A (SQLAlchemy core) and Option B (ORM models)" | Resolve the choice in orchestrator-user chat before kickoff handoff (ORCHESTRATOR-ROLE.md, section 'Kickoff drafting convention') |
| F-002 | R3 | 88 | "decide which paradigm fits" | Resolve the paradigm choice in orchestrator-user chat. The worker executes the pinned choice |

### Observed cleanly
- R2, R4, R5, R6, R7, R8
```

---

## Design Rationale

**Why Sonnet (not Opus).** R4, R5, R7 are mechanical scans; R6 and R8 are structural checks; R1-R3 are LLM-judgement but bounded by tight rule definitions. Sonnet handles this scope efficiently. The checker's failure mode is over-firing on judgement rules (false positives), which the observation-log calibration cadence tunes; under-firing on mechanical rules is unlikely.

**Why one agent for all the rules.** The rules are tightly coupled (a kickoff that violates R1 typically also violates R3; the violation surfaces in the same prose region). A single spec is cheaper than separate per-rule dispatches and produces one synthesised report the orchestrator parses once.

**Why read-only.** Independence is the load-bearing property. A checker that can modify the kickoff would be tempted (or prompted) to "auto-fix" findings, breaking the Pure-B discipline of the dispatch loop. Read-only is a mechanical guarantee, not a soft convention.

**Why fresh context per dispatch.** The checker must not see the orchestrator's chat history or the drafter's reasoning. Iteration N+1 produces a new draft; the checker re-checks from scratch. This catches regressions (iteration 2 fixes R1 but introduces R5) that an in-context "remember what I said last time" mode would miss.

---

## Revision History

- 2026-06-05: v1.0 ported from rogue `KICKOFF-CHECKER-SPEC.md` v1.2 per ADR-023 (COR-T-001). Right-sized: single project (workspace input dropped), rogue R4 (game-type comparisons) and R9 (observable-behaviours citation depth) dropped, rogue R10 adapted to the always-applicable "Related tasks and ADRs" rule, rules renumbered per the ADR-023 map.
