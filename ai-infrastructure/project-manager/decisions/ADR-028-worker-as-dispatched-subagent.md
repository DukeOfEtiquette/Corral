---
schema_version: 1
adr: 28
title: "Worker as an orchestrator-dispatched subagent; retire the /corral-worker session"
status: "accepted"
date: "2026-06-09"
related_adrs: [9, 23, 24, 35]
supersedes: []
superseded_by: null
---

# ADR-028: Worker as an orchestrator-dispatched subagent

## Context

Corral's orchestration layer (authored in COR-T-001 under ADR-009 and ADR-023) splits work
between two paired slash commands:

- `/corral-orchestrator` (Opus): surveys state, resolves anticipated decisions with the user, and
  drafts a self-contained kickoff (via the `kickoff-drafter` / `kickoff-checker` loop, ADR-023).
- `/corral-worker` (Sonnet): consumes the kickoff in a separate session and executes it, ending
  with the six-section closing report written dual-channel (chat + `-REPORT.md`, ADR-024).

The handoff is **session-mediated by the human**: the orchestrator writes a kickoff, the user opens
a second session, runs `/corral-worker` against it, and carries the report back. The user sits in
the middle of every handoff.

The exemplar Corral derives its conventions from (`~/rogue/ai-workspaces/project-manager`, per
ADR-009) has since moved past this shape. Rogue's ADR-025 ("Worker as a universal
orchestrator-dispatched subagent") promotes the worker into the same orchestrator-dispatched-subagent
model that ADR-023's checker fleet already uses: the orchestrator dispatches the worker directly via
the Task tool, the user interacts only with the orchestrator, and the man-in-the-middle handoff is
removed. Rogue validated the mechanics with a throwaway spike (rogue #146) and cut the dispatched
path over to standard on 2026-06-08.

Corral has not yet executed any work through the parallel-session worker in anger; the
`/corral-worker` command exists but the project is still in Phase 1 (AI infrastructure). This ADR
adopts rogue's reshaped pattern now, while there is no installed base of parallel-session habits to
unwind.

## Alternatives considered

### Option A: Adopt the dispatched-subagent worker; retire `/corral-worker` (selected)

The orchestrator dispatches a universal `worker-agent` subagent (Task tool, `model: sonnet`,
foreground) to execute a drafted kickoff, with explicit context pass-down. The user interacts only
with the orchestrator. The `/corral-worker` slash command is deleted, not kept as a fallback.

**Selected because:** it removes the user from every handoff (the primary goal), and it is a natural
extension of ADR-023, which already makes the orchestrator a dispatcher-and-synthesiser of subagents
for the checkers. The mechanics are already validated on Corral's own exemplar (rogue spike #146 and
the rogue cutover), so Corral inherits a proven design rather than re-spiking. Retiring
`/corral-worker` outright (rather than keeping it as rogue did) is correct for Corral specifically:
Corral never operated the parallel-session worker in production, so there is no installed base that
needs a fallback, and a single execution path is cleaner to maintain and document.

### Option B: Adopt the dispatched path but keep `/corral-worker` as a manual fallback

This is what rogue did at its cutover (the dispatched path is default; `/project-manager-worker` is
retained for manual/debug runs). **Rejected for Corral:** rogue kept the command because it had live
sessions and habits built on it; Corral does not. Carrying a second, unused execution path forward
is maintenance and documentation cost with no offsetting installed base. The command can be
re-introduced from git history if the dispatched path ever proves insufficient.

### Option C: Status quo (parallel human-driven worker sessions)

**Rejected:** keeps the user as the man-in-the-middle on every handoff, which is the friction this
ADR exists to remove.

### Option D: Agent teams / in-place resume (SendMessage)

**Rejected for now**, mirroring rogue ADR-025's Alternative B. Rogue's spike found SendMessage gated
behind an experimental agent-teams feature whose teammates are heavyweight full sessions with a
documented no-in-process-resumption limitation. Corral parks this; a future ADR can revisit it if
the primitive matures.

## Decision

Corral adopts the worker-as-orchestrator-dispatched-subagent pattern, on the reshaped
(return-and-re-dispatch) branch that rogue ADR-025's spike validated. Concrete elements:

> Forward pointer (ADR-032, accepted 2026-06-12): the agent this ADR names `worker-agent` is renamed `executor`, its role doc `WORKER-ROLE.md` becomes `EXECUTOR-ROLE.md`, and its spec `WORKER-AGENT-SPEC.md` becomes `EXECUTOR-AGENT-SPEC.md`. The dispatch mechanics in this Decision are unchanged in substance (leaf node, return-and-re-dispatch, `model` override, foreground); only the names change. ADR-032 establishes the cross-department agent tier in which `executor` is the general execution agent alongside specialist executors like `test-designer`. The rename cascade is COR-T-036. Read `worker-agent` below as `executor`.

1. **Dispatch mechanism.** After drafting and checking a kickoff, the orchestrator dispatches a
   universal `worker-agent` subagent (Task tool, `model: sonnet`, foreground) to execute it, rather
   than handing it to a separate human-driven session. The worker returns one of two verdict-lined
   results: `RETURN: COMPLETED` (+ the six-section report, written dual-channel) or
   `RETURN: ESCALATION` (+ a four-part block).

2. **Explicit context pass-down is the rule.** The orchestrator names the `workspace` and the exact
   `explicit_reads` (the workspace `CLAUDE.md` plus every reference the kickoff names, in order). The
   worker loads exactly those, plus the kickoff and (on re-dispatch) the resume anchor. It does not
   survey, deduce its workspace, or free-explore.

3. **Escalation is return-and-re-dispatch, not in-place resume.** On a genuine gap it must not
   resolve itself, the worker returns `RETURN: ESCALATION` with the question, the context to answer
   it, the progress so far, and a resume anchor (the partial report-to-file). The orchestrator
   answers simple, well-understood cases and re-dispatches a FRESH worker with the answer folded in;
   edge cases (or any second escalation on the same point) surface to the user. Ceiling: at most 2
   escalation round-trips before a mandatory user-surface. Escalations must stay rare; the
   zero-anticipated-decisions discipline (ADR-023) is load-bearing.

4. **The worker is a leaf; checkers stay orchestrator-run.** A dispatched subagent has no Agent/Task
   tool, so the orchestrator (not the worker) runs `worker-prelaunch-checker` before dispatch and
   `worker-close-checker` after the worker returns. This matches ADR-023, which already makes the
   orchestrator the checker-dispatcher.

5. **Verify against disk.** The orchestrator independently re-derives the worker's claimed results
   against disk rather than trusting the report's verification claims (this guards the rogue pilot
   defect where a worker reported a check that did not hold).

6. **Foreground, lower-tier worker.** The worker runs foreground (background subagents cannot get
   interactive permission approvals) and pinned to Sonnet via the Task `model` override, independent
   of the Opus orchestrator, preserving the Opus-plans / Sonnet-executes economics.

7. **`/corral-worker` is retired.** The dispatched `worker-agent` path is the single worker
   execution path. The `/corral-worker` slash command is deleted (recoverable from git history if
   ever needed).

What stays the same (inherited, not changed): the orchestrator/worker role split (orchestrator
decides and plans, worker executes against a tight plan with zero anticipated decisions); the kickoff
as the unit of handoff and the six-section closing report; the dual-channel report-to-file and the
git-tracked handoff location (ADR-024); the checker fleet (ADR-023); and the model-tier intent.

This ADR **partially supersedes** the worker-invocation mechanism established under ADR-009 (the
parallel human-driven `/corral-worker` session), replacing it with the orchestrator-dispatched
subagent. ADR-009's convention-adoption decision, the role split, the report shape, and the handoff
artifacts are all retained, so this is a partial supersede: per Corral's append-only convention the
`supersedes` / `superseded_by` frontmatter fields are left untouched (reserved for full
supersession); ADR-009 and ADR-023 are listed in `related_adrs` and ADR-009 gains a forward-pointer
Status note. It **extends** ADR-023 by promoting the worker into the same
orchestrator-dispatched-subagent model already used for the checkers.

Implementation is tracked as **COR-T-015** (port the `worker-agent` agent and spec, add the
`§Dispatched-worker flow` to `ORCHESTRATOR-ROLE.md`, add the Identity-delta note to
`WORKER-ROLE.md`, wire `/corral-orchestrator`, and delete `/corral-worker`). Per the COR-T-012
restructure (still pending), these files land at their current paths now and the restructure carries
them to their final home.

## Consequences

### Positive

- The user interacts only with the orchestrator; the man-in-the-middle handoff is eliminated.
- A natural extension of ADR-023: the worker joins the checkers in the dispatched-subagent model.
- Reuses existing infrastructure: `WORKER-ROLE.md`, the six-section report, the dual-channel
  report-to-file (ADR-024, now also the escalation resume anchor), the checker fleet, and the
  model-tier pin.
- A single worker execution path: cleaner to document and maintain than two coexisting paths.
- Corral inherits a design already validated on its exemplar (rogue spike #146 + cutover); no
  re-spike needed.

### Negative

- Escalation is lossier and costlier than in-place resume: each escalation is a full re-dispatch
  carrying re-supplied context. Mitigated by keeping escalations rare and by the report-to-file
  resume anchor.
- The orchestrator (higher tier) is engaged supervising the run and fielding escalations, consuming
  budget the parallel-session model left idle.
- Background runs cannot get interactive approvals, so foreground-by-default is a constraint.
- A real `RETURN: ESCALATION` round-trip is proven only synthetically on the exemplar (rogue's
  accepted gap, rogue #160). Corral inherits this gap; the first live escalation hardens the path.

### Neutral

- Corral diverges from rogue by retiring `/corral-worker` rather than keeping it as a fallback,
  justified by Corral having no installed parallel-session base.
- The agent-teams path (Option D) is parked, not foreclosed; a future ADR can revisit it.
- Forward pointer (added 2026-06-12): ADR-035 makes this flow's step-6 verify-against-disk check explicit for deliverable citations, requiring the orchestrator to resolve every repo-relative path cited in the deliverable on disk before close. ADR-035 promotes OBSERVATIONS COR-04/05/06 (the unverified-claim family this step backstops).
