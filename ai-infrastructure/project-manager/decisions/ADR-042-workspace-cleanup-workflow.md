---
schema_version: 1
adr: 42
title: "End-of-session workspace cleanup check and its session trigger"
status: "pending"
date: "2026-06-15"
related_adrs: [3, 23, 24, 28, 30, 35, 39, 40, 41]
supersedes: []
superseded_by: null
---

# ADR-042: End-of-session workspace cleanup check and its session trigger

> Pending: frames the open questions for an end-of-session "workspace cleanup" workflow. No decision is taken yet. Body Alternatives carry leanings (clearly marked) to support deliberation; Decision and Consequences stay pending until taken up. Do not implement before this ADR is accepted.

## Context

A session sometimes ends with work the operator did not realize was unfinished: an uncommitted or untracked file under a workspace, a task left in `in-progress/`, a kickoff with no sibling report, leftover `tmp/` scratch, or a derived surface that has drifted out of sync. Today the safety net is downstream: a concurrent or subsequent session in the same workspace sees the residue and (correctly) refuses to touch it without operator approval. That net works, but it is reactive. It catches the residue only on the next session, and it surfaces the problem to a session that did not create it rather than to the operator who did.

The wanted capability is a proactive, workspace-scoped "cleanup" check the operator can run at the end of a session, before exiting, that scans for unfinished or out-of-sync state and surfaces it for resolution while the originating context is still live. The operator's stated ideal was for this to run automatically as part of `/exit` and to abort the exit if something needs attention, scoped to only the workspace the session was working in (e.g. a `/project-manager-orchestrator` session checks the project-manager workspace, not every workspace in the repo).

This sits alongside the existing derived-surface and consistency-check lineage. The dashboard ETL already carries owned-but-advisory consistency checks for phase/epic/task drift (the COR-03 to COR-08 lineage, canonicalized in ADR-041; the fully-derived surfaces in ADR-039 and ADR-040). The dispatch loop already establishes the precedent of a standing checker fleet that lints work products (ADR-023). The cleanup check is a third member of that family: a lint over end-of-session workspace state rather than over a kickoff or a dashboard.

A hard platform constraint shapes the trigger question, verified against the Claude Code hooks documentation 2026-06-15:

- A `SessionEnd` hook fires when the session is already terminating and is strictly informational. It cannot block or cancel the exit (exit code 2 only prints to stderr; execution continues to termination).
- A `Stop` hook can force the agent to continue, but it fires on every turn (whenever the agent finishes responding, not at exit) and is capped after 8 consecutive blocks. It is not tied to exit intent.
- No hook can directly read which slash command was invoked earlier in the session. Workspace scoping for a hook therefore requires session-scoped state, idiomatically a marker file written when the orchestrator command runs and read by the hook.
- Hooks configured in `.claude/settings.json` fire for every session in the project; there is no built-in "only when command X is active" matcher.

The consequence: the literal "abort `/exit` until resolved" is not achievable. The design space is everything short of a hard exit-block. This is also the first hook in this repo (not yet independently verified), so adopting one is a new automation surface worth recording.

Open dimensions:

- **Trigger mechanism.** How the check is invoked: explicit operator command, a non-blocking `SessionEnd` backstop, a blocking `Stop` hook, or a combination.
- **Workspace scope semantics.** What "the workspace I am done with" resolves to for a coordinator session that holds write authority over sibling departments.
- **Surface-only vs auto-fix.** Whether the workflow reports and proposes, or also resolves (commits, deletes scratch, moves tasks).
- **Check composition and reuse.** Whether the phase/epic/task-sync portion reuses the existing ETL consistency checks or reimplements them.
- **Where the check logic lives and how it runs.** A standalone script, a dashboard-style compose service, or logic embedded in the orchestrator command, given the ADR-003 compose-only run policy applies to the app and the existing ETL precedent for AI-infra tooling.
- **Generality across departments.** Whether cleanup is a shared capability every orchestrator inherits (like the shared checker fleet) or a project-manager-only tool.

## Alternatives considered

The dimensions below are independent; the eventual decision selects one option per dimension.

### Dimension 1: Trigger mechanism

**Option 1A: Manual command only.** A dedicated invocation (an arg to the orchestrator command, e.g. `cleanup`, or a standalone skill) the operator runs deliberately before exiting.

**Option 1B: Manual command plus a non-blocking `SessionEnd` backstop.** The manual command is primary; additionally a `SessionEnd` hook, gated by a session marker file so it fires only for the relevant workspace's orchestrator sessions, runs the same check and prints unresolved items to stderr as the session exits. Cannot block, but catches the "forgot to run it" case the operator described.

**Option 1C: Blocking `Stop` hook.** A `Stop` hook keyed to the session marker forces the agent to continue when the workspace is dirty.

**Selected / rejected because:** {pending}. Leaning: **1B**. It delivers the proactive end-of-session notice the operator wants without depending on memory, while staying within the platform constraint (no exit-block is possible). 1C is a poor fit: it interrupts every turn during active work and hits the 8-block cap, and exit cannot be blocked regardless. 1A alone re-introduces the "I forgot" failure mode this is meant to solve. The existing next-session refusal remains the hard net under any option.

### Dimension 2: Workspace scope semantics

**Option 2A: Invoked workspace directory plus shared handoffs.** The check covers `ai-infrastructure/<dept>/` for the invoking orchestrator plus the shared `.claude/artifacts/handoffs/` and `tmp/` trees (where orphan kickoffs and scratch live).

**Option 2B: Whole AI-infrastructure tree.** The check covers everything the coordinator can write, reflecting the project-manager's cross-department write authority.

**Option 2C: Parameterized.** Scope defaults to 2A but accepts an explicit wider target.

**Selected / rejected because:** {pending}. Leaning: **2A** as the default, given the operator framed scoping as a feature ("only the workspace I am done with"). The coordinator's write authority over sibling departments (per the workspace `CLAUDE.md`) makes 2B defensible for a coordinator session specifically; this is the dimension most in need of the operator's call.

### Dimension 3: Surface-only vs auto-fix

**Option 3A: Surface-only.** The workflow reports unresolved state and proposes resolutions; it commits nothing, deletes nothing, and moves no tasks.

**Option 3B: Guided auto-fix.** The workflow offers to resolve some classes (delete consumed scratch, move a clearly-done task) on confirmation.

**Selected / rejected because:** {pending}. Leaning: **3A**. Resolution decisions (commit, delete scratch, promote an observation, transition a task) are orchestrator-and-operator judgment under the repo's existing discipline: only the orchestrator transitions tasks, commits happen only on operator authorization (the commit gate), and scratch is not deleted unless the operator asks. Surface-only also keeps the `SessionEnd` backstop safe to run unattended.

### Dimension 4: Check composition and reuse

**Option 4A: Reuse the ETL consistency checks.** The phase/epic/task-sync portion calls or shares the owned-but-advisory checks already in the dashboard ETL (ADR-041 lineage) rather than growing a parallel implementation.

**Option 4B: Standalone reimplementation.** The cleanup workflow implements its own sync checks independently.

**Selected / rejected because:** {pending}. Leaning: **4A**. A parallel copy of the drift checks is exactly the duplication the COR-03 to COR-08 lineage warns against; two implementations of the same check will themselves drift. The non-sync checks (uncommitted/untracked files, orphan kickoffs per ADR-024, stuck in-progress tasks, leftover scratch) are new to this workflow.

### Dimension 5: Where the check logic lives and how it runs

**Option 5A: Standalone script** (shell or Python) reading git status and the markdown trees, invoked by the command and/or hook.

**Option 5B: Compose service**, mirroring the dashboard ETL's packaging under ADR-003.

**Option 5C: Logic inline in the orchestrator command / skill**, with no separate executable artifact.

**Selected / rejected because:** {pending}. Note: ADR-003's compose-only run policy governs the app; AI-infra tooling such as the ETL already runs in its own compose service, so either packaging has precedent. The reuse decision (Dimension 4) constrains this one: sharing the ETL checks pulls toward the ETL's packaging.

### Dimension 6: Generality across departments

**Option 6A: Shared capability.** Every orchestrator (project-manager and each department per the ADR-030 create-department recipe) inherits cleanup, like the shared checker fleet and the shared `executor`.

**Option 6B: Project-manager only.** Cleanup is a coordinator-only tool initially.

**Selected / rejected because:** {pending}. Leaning: **6A** in shape but **6B** in rollout: design the check to take a workspace target so it generalizes, but it is acceptable to wire it into the project-manager orchestrator first and extend to the department scaffold (ADR-030) once proven, rather than blocking on full generality.

## Decision

{Pending.}

## Consequences

{Pending.}
