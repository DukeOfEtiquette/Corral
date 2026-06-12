# Author the universal test-designer agent and wire the TDD two-phase flow

## Target

This is AI-infrastructure work (domain 2 per ADR-005): you are authoring a new shared dispatched agent and wiring its flow into the universal role docs, specs, and checkers, not writing any web-app test (domain 1). Task COR-T-035. This task makes Corral's TDD discipline (`./ai-infrastructure/project-manager/decisions/ADR-016-testing-strategy-test-designer-agent.md`, accepted) operational. It is the structural analog of COR-T-015, which authored the `worker-agent`: author the new `test-designer` agent (agent file, full role doc, full spec), wire the two-phase test-design-then-implement flow into `ORCHESTRATOR-ROLE.md` and `WORKER-ROLE.md`, add the no-touch enforcement rule W3 to the existing `worker-close-checker`, and run the consistency sweep. The artifacts in scope are listed below; the new agent mirrors the `worker-agent` fleet member end to end, adapted for test design.

## Decisions resolved by the Orchestrator

- **You implement ADR-016; you do not edit it.** ADR-016 (accepted) is the binding decision: TDD, the test-designer, the two-phase flow, the three enforcement layers. Reference it by path; do not restate its content into the new docs and do not modify the ADR file. It is listed under files out of scope.
- **The test-designer reuses the worker dispatch spine.** Build `test-designer` as a near-clone of `worker-agent`: the same input package (`workspace`, `kickoff_path`, `explicit_reads`, `report_path`, `status_deltas`, `attempt_number`, `escalation_answer`, `resume_anchor`, `prior_progress_summary`), the same two verdict-lined return modes (`RETURN: COMPLETED` / `RETURN: ESCALATION`), the same six-section report shape, the same dual-channel report-to-file write, the same STATUS-once-on-COMPLETED rule, and the same prelaunch (W1) and close (W2) checkers run by the Orchestrator. Mirror the structure of `./.claude/agents/worker-agent.md` and `./.claude/agents/specs/WORKER-AGENT-SPEC.md` for the new agent file and spec. Rationale: ADR-016 defines the test-designer as a universal dispatched agent parallel to `worker-agent`; reusing the spine keeps the fleet coherent.
- **Test-design identity deltas (what distinguishes it from `worker-agent`).** The test-designer authors FAILING tests (red) for a surface against its contract (the ADRs, the ADR-012 schema, and the surface's endpoint or tool spec named in its own kickoff). It asserts observable behavior and the contract, never implementation internals. It OWNS test files and writes ONLY test files. Red-on-purpose is correct: tests precede the implementation, so a freshly authored test SHOULD fail. The test-designer is the design half of the TDD pair (ADR-016); `worker-agent` is the implementation half. Encode these deltas in the new agent file's Identity / Core principles and in the new role doc's Identity / Scope, paralleling how `worker-agent.md` encodes its own deltas against `WORKER-ROLE.md`.
- **Model tier: Opus.** The `test-designer` agent file pins `model: opus`, and the Orchestrator dispatches it with the `model: opus` override. Rationale: test design is judgement work (deciding coverage, enumerating edge cases, treating the contract as the spec), paralleling the Opus kickoff-drafter rather than the Sonnet worker-agent. State this asymmetry explicitly in the new role doc's model-tier section: `worker-agent` executes on Sonnet; the test-designer designs on Opus; Opus decides and designs, Sonnet executes.
- **Role doc: full standalone `TEST-DESIGNER-ROLE.md`.** Author a complete, self-contained role doc that mirrors `WORKER-ROLE.md` end to end (its own Identity, Scope, Responsibilities, Universal conventions, Failure modes, Crash recovery, Report shape, Dual-channel, Wrap-up STATUS hygiene, Model-tier convention, role/kickoff boundary, Not in scope, Checker dispatch, Instantiation), adapted for test design. Do NOT author a lean reference-only doc that points back to `WORKER-ROLE.md`; it is standalone.
- **Two-phase TDD surface flow in `ORCHESTRATOR-ROLE.md`.** Add a new subsection placed adjacent to the existing "Dispatched-worker flow" that composes the Dispatched-worker flow TWICE for every web-app surface under TDD (ADR-016): phase 1 dispatches the `test-designer` (red) with a test-design kickoff; phase 2 dispatches the `worker-agent` (green) with an implementation kickoff that lists the phase-1 test paths in `files_out_of_scope` and passes them to the close checker as `protected_test_paths`. Both dispatches live in the producing department's orchestrator session. An implementation-worker ESCALATION asserting that a test is wrong routes to a FRESH `test-designer` dispatch (correct the test in the design layer), never to a worker edit of the test.
- **No-touch enforcement, three layers (ADR-016).** (a) `WORKER-ROLE.md` gains a universal-convention bullet: the implementation worker never creates or edits test files; if it believes a test is wrong it returns `RETURN: ESCALATION` (the sanctioned channel), it does not edit the test. (b) The Orchestrator lists the surface's test paths in the implementation kickoff's `files_out_of_scope`, using the existing kickoff mechanism (no kickoff-drafter or kickoff-checker change). (c) New `worker-close-checker` rule W3: FAIL if any path matching the Orchestrator-supplied `protected_test_paths` input appears in the report's "Files touched" section. W3 fires ONLY when `protected_test_paths` is non-empty (implementation closes); it is inert on test-design closes and on tasks with no protected tests. Wire W3 through all touchpoints in both `worker-close-checker.md` and `WORKER-CLOSE-CHECKER-SPEC.md`: the Inputs table (new `protected_test_paths` input), a new Phase for the W3 scan, the severity rubric, the report schema, and an invocation example, plus a revision-history entry in the spec.
- **The Orchestrator verify-against-disk backs W3.** `ORCHESTRATOR-ROLE.md` "Dispatched-worker flow" step 6 already says re-derive the worker's claims against disk; add a note there that for an implementation close the Orchestrator re-derives the no-touch check against `git diff` (since a report could under-report Files touched), and update step 5 to pass `protected_test_paths` to the close checker.
- **Reuse the existing checkers; author no new checker agents.** The test-design kickoff and report flow through the SAME `worker-prelaunch-checker` (W1) and `worker-close-checker` (W2) as any worker run. W3 is added to the existing close checker. W1 is unchanged. Do not author new checker agents.
- **Naming and metadata.** Agent name: `test-designer`. Display role name: "Test Designer Agent". Agent-file `color`: `cyan` (a distinct color; `worker-agent` is green, the checkers are yellow). The spec header mirrors `WORKER-AGENT-SPEC.md` (Status: Implemented; Created: 2026-06-12; Purpose; Lineage referencing ADR-016 and the `worker-agent` it parallels).
- **Consistency sweep.** Add a `TEST-DESIGNER-ROLE.md` row to the `docs/README.md` "This tree" navigation table. Keep the worker-fleet cross-references coherent (`WORKER-ROLE.md` "Checker dispatch" and `ORCHESTRATOR-ROLE.md` "Dispatched-worker flow" / "Kickoff drafting convention"). Reference ADR-016; do not restate its content.

## Deliverables

- NEW `./.claude/agents/test-designer.md`: the agent definition. `model: opus`, `color: cyan`, a description with usage examples mirroring the shape of `worker-agent.md`'s description, adopting `TEST-DESIGNER-ROLE.md`, with bootstrap reads (`TEST-DESIGNER-AGENT-SPEC.md` and `TEST-DESIGNER-ROLE.md`) and the Identity / Core principles / Capabilities / Pipeline position / Input-output / Quality-checks sections adapted for test design.
- NEW `./docs/ai-orchestration/roles/TEST-DESIGNER-ROLE.md`: the full standalone role doc that mirrors `WORKER-ROLE.md` end to end, adapted for test design; the model-tier section pins Opus and states the asymmetry with `worker-agent`.
- NEW `./.claude/agents/specs/TEST-DESIGNER-AGENT-SPEC.md`: the full agent spec mirroring `WORKER-AGENT-SPEC.md` (Overview, Agent Purpose, Tool Access including Write/Edit for test files, Inputs, Workflow Phases, Return Schema, Style Rules, Error Handling, Invocation Examples, Design Rationale including why Opus, Revision History).
- EDIT `./docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md`: add the "TDD two-phase surface flow" subsection adjacent to "Dispatched-worker flow"; add the `protected_test_paths` note to Dispatched-worker flow step 5 and the git-diff no-touch re-derivation note to step 6; add a note in "Kickoff drafting convention" that an implementation kickoff in the TDD flow lists the surface's test paths under files out of scope.
- EDIT `./docs/ai-orchestration/roles/WORKER-ROLE.md`: add the no-touch universal-convention bullet (the implementer never creates or edits test files; escalate, do not edit); update "Checker dispatch (Orchestrator-run)" to note W3 conditionally joins W2.
- EDIT `./.claude/agents/worker-close-checker.md`: add the W3 rule and the `protected_test_paths` input across the Identity, Capabilities, Input/Output, and Severity sections.
- EDIT `./.claude/agents/specs/WORKER-CLOSE-CHECKER-SPEC.md`: add the `protected_test_paths` input, the W3 workflow phase, the severity-rubric entry, the report-schema update, an invocation example, and a revision-history entry.
- EDIT `./docs/README.md`: add a `TEST-DESIGNER-ROLE.md` row to the "This tree" table.
- STATUS hygiene plus the named STATUS deltas in `./ai-infrastructure/project-manager/STATUS.md` (see "STATUS deltas").

## Files in scope

- `./.claude/agents/test-designer.md`
- `./docs/ai-orchestration/roles/TEST-DESIGNER-ROLE.md`
- `./.claude/agents/specs/TEST-DESIGNER-AGENT-SPEC.md`
- `./docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md`
- `./docs/ai-orchestration/roles/WORKER-ROLE.md`
- `./.claude/agents/worker-close-checker.md`
- `./.claude/agents/specs/WORKER-CLOSE-CHECKER-SPEC.md`
- `./docs/README.md`
- `./ai-infrastructure/project-manager/STATUS.md` (universal hygiene plus the named STATUS deltas)

## Files out of scope

- `./ai-infrastructure/project-manager/decisions/ADR-016-testing-strategy-test-designer-agent.md` (accepted; implement it, do not edit)
- `./.claude/agents/kickoff-drafter.md` and `./.claude/agents/specs/KICKOFF-DRAFTER-SPEC.md` (no change; the out-of-scope listing uses the existing files_out_of_scope mechanism)
- `./.claude/agents/kickoff-checker.md` and `./.claude/agents/specs/KICKOFF-CHECKER-SPEC.md` (no change)
- `./.claude/agents/worker-agent.md` and `./.claude/agents/specs/WORKER-AGENT-SPEC.md` (the implementer's no-touch convention lives in `WORKER-ROLE.md`, which the worker reads; no agent-file change)
- `./.claude/agents/worker-prelaunch-checker.md` and `./.claude/agents/specs/WORKER-PRELAUNCH-CHECKER-SPEC.md` (W1 unchanged)
- the `app/` tree (the actual test files, the pytest harness, and the compose test service are backend-api's API-T-001, not this task)
- `./ai-infrastructure/project-manager/tasks/` (task transitions are Orchestrator-only)

## References

Read these in the order given. The first three are the structural precedents you mirror; the rest are the edit targets and the lineage decisions.

- `./.claude/agents/worker-agent.md` (the agent file `test-designer.md` mirrors structurally: frontmatter, Bootstrap, Identity, Core principles, Capabilities, Pipeline position, Input/output, Quality checks)
- `./.claude/agents/specs/WORKER-AGENT-SPEC.md` (the spec `TEST-DESIGNER-AGENT-SPEC.md` mirrors: Overview, Agent Purpose, Tool Access, Inputs, Workflow Phases, Return Schema, Style Rules, Error Handling, Invocation Examples, Design Rationale, Revision History)
- `./docs/ai-orchestration/roles/WORKER-ROLE.md` (the role doc `TEST-DESIGNER-ROLE.md` mirrors end to end; also the site of the new no-touch universal-convention bullet and the "Checker dispatch" W3 update)
- `./ai-infrastructure/project-manager/decisions/ADR-016-testing-strategy-test-designer-agent.md` (the binding decision this task implements: TDD, the test-designer, the two-phase flow, the three enforcement layers; reference, do not restate)
- `./.claude/agents/worker-close-checker.md` (the close-checker agent gaining W3 and the `protected_test_paths` input)
- `./.claude/agents/specs/WORKER-CLOSE-CHECKER-SPEC.md` (the close-checker spec gaining W3 and `protected_test_paths` across all touchpoints: Inputs, a new Phase, severity rubric, report schema, an invocation example, revision history)
- `./docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md` (sections "Dispatched-worker flow" and "Kickoff drafting convention", where the two-phase flow, the step-5/6 notes, and the out-of-scope note land)
- `./docs/README.md` (the navigation index gaining the new role-doc row in "This tree")
- `./ai-infrastructure/project-manager/decisions/ADR-028-worker-as-dispatched-subagent.md` (the dispatched-subagent model the test-designer also follows: leaf node, return-and-re-dispatch, model override)
- `./ai-infrastructure/project-manager/decisions/ADR-023-dispatch-loop-day-zero.md` (the checker rule lineage; W3 joins the W1/W2 family in the worker-close-checker)

## Related tasks and ADRs

- COR-T-035 (this task)
- ADR-016 (the decision this task implements: TDD strategy and the test-designer agent)
- COR-T-015 (the structural precedent: authored `worker-agent` plus its spec, added the Dispatched-worker flow to `ORCHESTRATOR-ROLE.md`, reframed `WORKER-ROLE.md`, repointed the checkers; this task mirrors that shape)
- ADR-028 (the dispatched-subagent model the test-designer inherits: leaf, return-and-re-dispatch, model override)
- ADR-023 (the dispatch-loop checkers; W3 is added to the `worker-close-checker` rule family alongside W1 and W2)
- ADR-021 (the test-design department is deferred to a promotion trigger; the test-designer is authored now as universal shared infrastructure, not department-owned)

## STATUS deltas

Beyond universal hygiene (bump `last_updated`, append a `recent_updates` entry), apply this task-specific edit to `./ai-infrastructure/project-manager/STATUS.md`:

- Reword the "Current phase" narrative clause that currently reads (paraphrase) "P2-2 is gated on COR-T-035, which authors the universal test-designer agent and wires the two-phase test-design-then-implement flow that backend-api's API-T-001 will follow." Replace it with a statement that the universal test-designer agent and the two-phase TDD flow are now in place, so backend-api can run P2-2 (API-T-001) as a test-design dispatch followed by an implementation dispatch. Leave the rest of the narrative intact. Locate the exact wording in the file before editing; the clause above is a paraphrase, not a literal string to match.

No roadmap milestone status change: COR-T-035 is enabling AI-infrastructure work, not a roadmap milestone.

## Hard rules

- **Reference ADR-016; do not restate it.** The new role doc and spec point at ADR-016 for the binding rationale (TDD, the two-phase flow, the enforcement layers); they do not copy its decision tables or reasoning into themselves.
- **Mirror structure, do not copy verbatim.** `TEST-DESIGNER-ROLE.md`, `test-designer.md`, and `TEST-DESIGNER-AGENT-SPEC.md` follow the section structure of their `worker-agent` counterparts but carry test-design content (FAILING-tests-against-contract, owns-only-test-files, red-on-purpose, Opus tier). Do not leave `worker`/Sonnet/implementation language in the test-designer artifacts where the test-design delta applies.
- **W3 is conditional and inert by default.** W3 fires only when `protected_test_paths` is non-empty. On a test-design close and on any task with no protected tests, W3 must not fire. Make this explicit in both the agent file and the spec so the checker does not regress the existing W2-only PASS path.
- **W1 and the kickoff drafter/checker are untouched.** Do not edit `worker-prelaunch-checker` (W1 unchanged) or the kickoff-drafter/kickoff-checker pair; the test-design kickoff flows through them unchanged, and the out-of-scope listing uses the existing `files_out_of_scope` mechanism.
- **Path convention.** Files under `./docs/ai-orchestration/` and the repo-root `.claude/` tree use repo-root-relative `./` paths in their bodies, consistent with the existing `worker-agent` artifacts you are mirroring. (Note that `./ai-infrastructure/project-manager/`-internal docs use a different bare-path convention per that workspace's own CLAUDE.md, but the artifacts in scope here are root-tree artifacts and use `./`.)

## Worker pointer

You are the dispatched `worker-agent` (ADR-028). Universal worker conventions, the six-section report shape, and the dual-channel report-to-file rule live in `./docs/ai-orchestration/roles/WORKER-ROLE.md`. Write the closing report to `./.claude/artifacts/handoffs/COR-T-035-KICKOFF-REPORT.md` per `WORKER-ROLE.md`, section "Report shape".
