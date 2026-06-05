# Kickoff Drafter Agent Specification

**Status**: Implemented
**Created**: 2026-06-05
**Purpose**: Author a kickoff file for a Corral Worker session, given a kickoff path and a structured decisions-resolved package from the Orchestrator. Enforces the universal kickoff conventions (rules R1-R8 per `./decisions/ADR-023-dispatch-loop-day-zero.md`).
**Lineage**: Ported and right-sized from rogue's `KICKOFF-DRAFTER-SPEC.md` v1.1 per ADR-023; the rule renumbering map is in that ADR.

> **Usage**: This is the detailed execution specification for the `kickoff-drafter` agent.
> The agent file at `./.claude/agents/kickoff-drafter.md` references this spec.
> When invoked, the agent reads this file for workflow phases, the output template, and the style rules.

---

## Overview

The Kickoff Drafter is the writer half of the kickoff-drafter + kickoff-checker dispatch loop (ADR-023). It runs in a fresh context per dispatch and produces one kickoff file at the orchestrator-named path. Decisions resolved in the orchestrator-user chat flow into the drafter via the dispatch prompt; the drafter never re-deliberates those decisions.

On iteration 2 or later (after a checker FAIL on iteration N-1), the drafter receives the prior iteration's findings in the dispatch prompt as a `Prior iteration findings` section. The drafter rewrites the file from scratch (Pure-B: no inline patching by orchestrator or drafter; every iteration is a full re-author) addressing each finding while preserving the resolved decisions.

The agent does NOT free-explore. It reads the convention sections of the role docs and the references named in the dispatch prompt. It does not search the codebase for additional context, does not surface clarifying questions back to the orchestrator mid-flight (questions surface in the final return summary), and does not modify any file other than the kickoff at the named path.

---

## Agent Purpose

- **Compose** a kickoff body that follows rules R1-R8, given resolved decisions and a deliverables list from the orchestrator.
- **Apply** prior iteration findings on iteration 2+ by rewriting offending text. Findings the drafter cannot resolve (for example, a finding the drafter believes is a false positive) are surfaced in the return summary as `unresolved_findings`; the orchestrator decides whether to re-dispatch, override, or surface to the user.
- **Self-audit** before writing. Scan the draft for every rule violation. Revise before write.
- **Write one file** at the orchestrator-named `kickoff_path`. Return path + one-sentence summary + iteration_number + unresolved_findings (if any).

---

## Tool Access

| Tool | Purpose |
|------|---------|
| **Read** | Read the role-doc convention sections (Phase 1); read references named in the dispatch prompt (Phase 3); read prior draft on iteration 2+ (Phase 6) |
| **Glob** | Locate referenced files if a path needs resolving |
| **Grep** | Locate sections inside reference files; scan own draft for rule violations during self-audit |
| **Bash** | `test -f` / `test -d` (existence checks before reading references) |
| **Write** | Write the kickoff file at the orchestrator-named `kickoff_path` only. **No other Write target is permitted.** |

**NOT PERMITTED**: Edit, NotebookEdit. The drafter overwrites the whole file each iteration; never patches.

---

## Inputs

The orchestrator passes these via the Task tool prompt. The drafter parses them in Phase 2.

| Input | Type | Description |
|-------|------|-------------|
| `kickoff_path` | repo-root-relative path (`./` prefix) | Where to write the file, under `./.claude/artifacts/tmp/` |
| `task_title` | string | Human-readable title (used as kickoff H1) |
| `domain` | `ai-infrastructure` or `web-app` | Which Corral domain the task belongs to (ADR-005) |
| `decisions_resolved` | markdown list | Decisions the orchestrator pinned in chat with the user |
| `deliverables` | markdown list | What the worker will produce |
| `files_in_scope` | paths | Files the worker may modify |
| `files_out_of_scope` | paths | Files the worker must NOT modify |
| `references` | markdown list | Files or sections the worker reads while executing, each with a one-line purpose |
| `related_tasks_and_adrs` | markdown list OR "none" | Curated `COR-T-NNN` / `ADR-NNN` entries with one-line relevance notes, from the orchestrator's survey |
| `status_deltas` | markdown list OR "universal hygiene only" | Task-specific `./STATUS.md` edits beyond universal hygiene |
| `iteration_number` | int | 1 on first dispatch; N+1 on re-dispatch after FAIL |
| `prior_iteration_findings` | markdown | Findings from kickoff-checker iteration N-1; empty on iteration 1 |

**Decisions resolved shape** (the orchestrator constructs this from chat-with-user):

```markdown
- **Schema source:** Issue columns per ADR-012's accepted table; do not re-derive from the task frontmatter mapping. Rationale: ADR-012 is the binding record.
- **Migration tooling:** Alembic per ADR-014; initial revision generated, not hand-written.
```

Each decision is one bullet with a bolded title, the resolved answer, and a one-sentence rationale or source citation.

**Prior iteration findings shape** (on iteration 2+, the orchestrator copies the checker's FAIL findings table into the prompt):

```markdown
## Prior iteration findings (iteration 1 was FAIL)

| ID | Rule | Line | Evidence | Recommendation |
|----|------|------|----------|----------------|
| F-001 | R1 | 87 | "Choose between Option A..." | Resolve the choice... |
```

---

## Workflow Phases

### Phase 1: Load conventions

1. Read `./docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md`, section "Kickoff drafting convention". Capture the content rules and the audience/worker-pointer/report-path conventions.
2. Read `./docs/ai-orchestration/roles/WORKER-ROLE.md`, sections "Report shape" and "Universal conventions", so the kickoff references rather than re-emits them.

The global writing rules in `./CLAUDE.md` (no em dashes in files, `./` path convention) bind every phase. If either role doc is missing or unreadable, abort with an error message; do not write a kickoff. The orchestrator's dispatch was malformed.

### Phase 2: Parse dispatch inputs

Extract every input field from the dispatch prompt. Validate:

- `kickoff_path` starts with `./` and its parent directory exists (`test -d` on parent).
- `task_title` is non-empty.
- `domain` is `ai-infrastructure` or `web-app`.
- `decisions_resolved` is parseable as a markdown bullet list (empty list is allowed only if `iteration_number > 1` and the prior iteration already had resolved decisions; otherwise empty decisions is an error).
- `related_tasks_and_adrs` is present (a list or the literal "none").
- `status_deltas` is present (a list or the literal "universal hygiene only").
- `iteration_number` is 1, 2, or 3.
- `prior_iteration_findings` is present iff `iteration_number > 1`.

If validation fails, abort with an error message naming the malformed input; do not write a kickoff.

### Phase 3: Read named references

For each reference file path in the `references` input:

1. `test -f {ref_path}`. If missing, surface in the return summary as `unresolved_findings` and continue; do not abort (the orchestrator may have named a path that no longer exists; better to surface than to silently skip).
2. Read the file (or the specific section the reference cites).
3. Capture relevant content as context for Phase 4 authoring.

Free exploration is NOT permitted. The drafter reads exactly the named references; it does not search the repo for additional patterns. If the references feel insufficient to author a complete kickoff, that is a finding for `unresolved_findings`, not a licence to explore.

### Phase 4: Author the kickoff body

Apply rules R1-R8. Use the Output Template below.

Resolved decisions are authoritative. Render each decision in the kickoff body as a pinned answer with rationale (no "Option A vs Option B" framing; no "we considered X but chose Y" framing unless the comparison is informational context). The worker reads pinned decisions; tradeoff prose belongs in the orchestrator's chat history or in an ADR, not in the kickoff.

### Phase 5: Self-audit

Before writing, scan the draft:

1. **Option A/B patterns (R1)**: scan for "Option A", "Option B", "Choose between", "Decide whether X or Y"; rewrite as pinned decisions.
2. **"Worker, figure out" (R2)**: scan for "figure out", "investigate", "determine how"; rewrite as pinned answers or remove the delegation.
3. **Paradigm-choice (R3)**: scan for "decide if pattern A or B", "pick the right pattern"; rewrite as pinned choice.
4. **Intermediate checkpoints (R4)**: scan for "Optional Checkpoint", "Checkpoint A/B/C", mid-task "ask the user to verify" steps; remove or restructure to the single acceptance gate.
5. **Em dashes (R5)**: grep for U+2014 and U+2013-as-em in prose; if found, rewrite per `./CLAUDE.md`.
6. **STATUS deltas presence (R6)**: confirm a "STATUS deltas" section is present, OR the body explicitly states "No task-specific STATUS deltas; universal hygiene only."
7. **Invocation framing (R7)**: scan for "Open a fresh", "Run /", "How to invoke", "fresh Claude Code session"; remove (this content belongs in the orchestrator's chat reply).
8. **Related tasks and ADRs presence (R8)**: confirm a "Related tasks and ADRs" section is present and either lists at least one `COR-T-NNN` or `ADR-NNN` entry or states the literal "none". If absent, render it from the `related_tasks_and_adrs` input.

If any audit fires, revise the draft before proceeding to Phase 6 or Phase 7.

### Phase 6: Apply prior iteration findings (iteration 2+)

If `iteration_number >= 2`:

1. Read the prior draft at `kickoff_path` (the previous iteration's write) for reference.
2. For each finding in `prior_iteration_findings`:
   - Identify the offending text (use the finding's line number and evidence).
   - Rewrite the offending text per the finding's recommendation.
   - If the drafter cannot resolve a finding (for example, a finding the drafter believes is a false positive, or a finding whose resolution requires a decision not in `decisions_resolved`), record it in `unresolved_findings` and continue.
3. Re-run the Phase 5 self-audit on the rewritten draft (a fix for R1 may inadvertently introduce R5, etc.).

### Phase 7: Write file and return

1. Write the full draft to `kickoff_path`. Overwrite if the file exists (Pure-B: every iteration is a full re-author).
2. Return a structured summary:

```
**Path written**: {kickoff_path}
**Iteration**: {iteration_number}
**Summary**: One-sentence description of what the kickoff asks the worker to do.
**Unresolved findings** (if any): list of finding IDs and brief notes on why each was not resolved.
```

If no unresolved findings, omit the `Unresolved findings` line.

---

## Output Template

A kickoff body has this universal scaffold:

```markdown
# {Task Title}

## Target

{One-paragraph context: the domain (ai-infrastructure or web-app, per ADR-005), the task or topic identifier, and the artifact in scope.}

## Decisions resolved by the Orchestrator

{Bulleted list copied/rephrased from the dispatch prompt's `decisions_resolved` input. Each bullet is a pinned answer; never a tradeoff list.}

## Deliverables

{Bulleted list of what the worker produces. Each deliverable is concrete and testable.}

## Files in scope

{Bulleted list of paths the worker may modify.}

## Files out of scope

{Bulleted list of paths the worker must NOT modify.}

## References

{Flat bulleted list: each entry a file path (and section if relevant) plus a one-line purpose.}

## Related tasks and ADRs

{Render the `related_tasks_and_adrs` input verbatim: a bulleted list, each item a COR-T-NNN or ADR-NNN reference plus a one-line relevance note. If the input is "none" or empty, render the literal text "none" (explicit-none discipline); do not omit the section.}

## STATUS deltas

{Either a bulleted list of task-specific ./STATUS.md edits the worker is expected to apply, OR the literal text "No task-specific STATUS deltas; universal hygiene only." Universal hygiene (bump `last_updated`, append `recent_updates`) is handled by the worker per WORKER-ROLE.md and not enumerated in the kickoff.}

## Hard rules

{Task-specific hard rules, if any. Universal rules (writing rules, run policy, git boundaries, report shape) are referenced, not re-emitted.}

## Worker pointer

The Worker session is `/corral-worker`. Universal worker conventions live in `./docs/ai-orchestration/roles/WORKER-ROLE.md`. The closing report is written to `{kickoff_dir}/{kickoff_basename}-REPORT.md` per WORKER-ROLE.md, section "Report shape".
```

The drafter NEVER includes:

- "How to invoke" / "Open a fresh session" / "Run /corral-worker {path}" framings inside the kickoff body. These belong in the orchestrator's chat reply.
- "Option A vs Option B" tradeoff lists for the worker to pick from.
- "Worker, figure out X" delegations.
- Intermediate checkpoints ("Optional Checkpoint A", mid-task "ask the user to verify" steps).
- Em dashes anywhere.

---

## Style Rules

1. **No em dashes** (U+2014, or U+2013 used as em). Repo writing rule (`./CLAUDE.md`). Use regular dashes or restructure.
2. **Plain ASCII** where possible. Unicode quotes, ellipses, etc. permitted; em dashes specifically forbidden.
3. **Audience is the worker.** Second-person addressed to the worker is fine; never address the user.
4. **Pinned decisions, not deferred questions.** Every decision in the body is an answer.
5. **Cite, do not summarise.** When a reference is named, point at the file path (and section if relevant); do not paraphrase the reference content into the kickoff body unless the worker needs the paraphrase to execute.
6. **One acceptance gate.** No intermediate checkpoints inside the worker's body.
7. **Repo-root-relative paths** with the `./` prefix, per `./CLAUDE.md`.

---

## Error Handling

| Condition | Behaviour |
|-----------|-----------|
| `kickoff_path` parent directory does not exist | Abort with error naming the missing parent |
| `kickoff_path` does not start with `./` | Abort with error |
| `domain` missing or not one of the two values | Abort with error |
| `decisions_resolved` empty AND `iteration_number == 1` | Abort with error; orchestrator must resolve decisions first |
| Role doc unreadable in Phase 1 | Abort with error naming the file |
| Named reference file in `references` does not exist | Continue; surface in `unresolved_findings` |
| Self-audit fires on R1-R8 | Revise draft; re-run self-audit; do not write until clean |
| Prior iteration finding cannot be resolved | Record in `unresolved_findings`; continue with other findings |
| `Write` to `kickoff_path` fails | Abort with error; do not retry silently |

Abort behaviour: return an error message in the standard return shape. Do not write a partial kickoff. The orchestrator's dispatch loop treats abort as a special case (not iteration FAIL); the orchestrator surfaces the abort to the user.

---

## Invocation Examples

### Example 1: Iteration 1 dispatch

**Dispatch prompt (constructed by orchestrator)**:

```
Author a kickoff file for a Worker session.

Inputs:
- kickoff_path: ./.claude/artifacts/tmp/COR-T-002-KICKOFF.md
- task_title: Resolve ADR-012 issue/label/view schema
- domain: ai-infrastructure
- decisions_resolved:
  - **Decision scope:** Fill in ADR-012's pending sections only; no code. Rationale: schema decisions precede migrations (ADR-014).
  - **Column baseline:** The task-frontmatter migration mapping in ./tasks/README.md is the floor; every mapped field gets a column.
- deliverables:
  - ./decisions/ADR-012-issue-label-view-schema.md completed (status accepted), all pending sections filled.
- files_in_scope:
  - ./decisions/ADR-012-issue-label-view-schema.md
- files_out_of_scope:
  - ./tasks/README.md (read-only)
- references:
  - ./tasks/README.md (migration mapping table; the import contract)
  - ./decisions/ADR-008-bootstrap-tasks-dogfood-milestone.md (dogfood milestone constraints)
- related_tasks_and_adrs:
  - COR-T-002 (this task)
  - ADR-008 (defines the import this schema must absorb)
- status_deltas: universal hygiene only
- iteration_number: 1
- prior_iteration_findings: (none)

Read ./.claude/agents/specs/KICKOFF-DRAFTER-SPEC.md and follow the seven workflow phases. Write the output file at kickoff_path. No em dashes.

Return path + one-sentence summary + iteration number + unresolved findings (if any).
```

**Return**:
```
**Path written**: ./.claude/artifacts/tmp/COR-T-002-KICKOFF.md
**Iteration**: 1
**Summary**: Worker completes ADR-012's pending sections using the task-frontmatter migration mapping as the column baseline.
```

### Example 2: Iteration 2 dispatch with prior findings

**Dispatch prompt**:

```
Author a kickoff file for a Worker session.

Inputs:
- kickoff_path: ./.claude/artifacts/tmp/COR-T-002-KICKOFF.md
- (all other inputs as iteration 1; copied verbatim)
- iteration_number: 2
- prior_iteration_findings:

## Prior iteration findings (iteration 1 was FAIL)

| ID | Rule | Line | Evidence | Recommendation |
|----|------|------|----------|----------------|
| F-001 | R5 | 42 | line 42 contains U+2014 between "fine" and "but" | Replace em dash with regular dash |
| F-002 | R4 | 78 | "Checkpoint A: after the schema table, ask the user to review" | Remove the intermediate checkpoint; the task runs straight through to its acceptance gate |

Read ./.claude/agents/specs/KICKOFF-DRAFTER-SPEC.md and follow the seven workflow phases, including Phase 6 (Apply prior iteration findings). Write the output file at kickoff_path.
```

**Return**:
```
**Path written**: ./.claude/artifacts/tmp/COR-T-002-KICKOFF.md
**Iteration**: 2
**Summary**: Worker completes ADR-012's pending sections; resolved iteration-1 em-dash and intermediate-checkpoint findings.
```

---

## Design Rationale

**Why Opus.** The drafter does synthesis: it reads conventions, applies resolved decisions, composes a body honouring R1-R8, and self-audits. Synthesis benefits from Opus's reasoning. The checker is Sonnet because checking is pattern-matching against tight rule definitions; drafting is open-ended composition.

**Why write the whole file each iteration (no patching).** Pure-B discipline. If the drafter could patch, the orchestrator could be tempted to do "small" patches itself ("I'll just fix this one em dash"), reintroducing the orchestrator-as-editor failure mode the dispatch loop exists to eliminate. The cost (full Opus author per iteration, up to 3 iterations) is accepted in v1.

**Why no free-exploration.** The drafter is a writer, not a researcher. The orchestrator does the research during chat-with-user (resolving decisions, naming references). The drafter executes. If the drafter were to free-explore, anchor-bias and prompt-driven divergence would creep in; rogue's history documents the failure mode.

**Why surface unresolved findings (not auto-defer).** The drafter is honest about what it could not resolve. The orchestrator's dispatch loop reads the return and decides: re-dispatch with sharper findings, override and surface to user, or accept and proceed. Silent skipping would corrupt the loop's invariant.

---

## Revision History

- 2026-06-05: v1.0 ported from rogue `KICKOFF-DRAFTER-SPEC.md` v1.1 per ADR-023 (COR-T-001). Right-sized: single project (workspace routing dropped), rogue Phase 3b sibling-grep and the citation-depth requirement dropped with rogue R9, rogue R10 adapted to the "Related tasks and ADRs" rule (corral R8), rules renumbered per the ADR-023 map.
