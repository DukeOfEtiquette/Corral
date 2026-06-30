---
schema_version: 1
id: COR-T-061
title: "Worktree-workflow doc polish: resolve-gate move-not-copy + dispatched-executor cross-references"
status: in-progress
labels: []
priority: P3
created: 2026-06-30
updated: 2026-06-30
---

## Description

Two small follow-ons surfaced while landing COR-T-059/060 (the worktree-workflow fixes). Both are doc polish on the worktree workflow; orchestrator-direct by user direction (not dispatched).

1. **Resolve-gate: move, not copy.** The Gap-2b resolve procedure written into `docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md` ("Dispatched-worker flow" step 7, "Resolve-gate worktree" note) says to COPY the untracked kickoff from the main checkout into the resolve worktree. That leaves the untracked original in the main checkout, which makes `bin/git-integrate` abort with "untracked working tree files would be overwritten by merge" when the branch adds the same path as a tracked file. Observed live during the COR-T-059/060 resolve. Fix: prescribe MOVE (`mv`, not copy) so no untracked original remains, with the failure mode named.

2. **Dispatched-executor worktree cross-references.** The new canonical procedure lives in `docs/ai-orchestration/roles/EXECUTOR-ROLE.md` section "Worktree handling (dispatched executor)" (COR-T-060), but the executor agent definition (`.claude/agents/executor.md`) and its spec (`.claude/agents/specs/EXECUTOR-AGENT-SPEC.md`) do not reference it at all, so a dispatched executor reading only its bootstrap docs would not know to create its worktree with `git worktree add`. Fix: add a cross-reference in each so the documentation triangle (role doc + agent file + spec) is complete. Promoted from the COR-T-060 executor report Follow-up.

### Deliverables

- `docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md`: reword the Gap-2b resolve-gate note from copy to move (`mv`), naming the untracked-files-would-be-overwritten abort as the reason.
- `.claude/agents/executor.md`: add a core-principle pointer to `EXECUTOR-ROLE.md` section "Worktree handling (dispatched executor)" (create the worktree with `git worktree add`; harness `EnterWorktree`/`ExitWorktree` are refused in a subagent; leave the worktree on disk for the Orchestrator).
- `.claude/agents/specs/EXECUTOR-AGENT-SPEC.md`: add the same cross-reference at the point execution begins (Phase 3).

Out of scope: any change to the merge-lock, hooks, `bin/git-integrate`, or the substance of the COR-T-059/060 fixes; only the resolve note and the two cross-references.

## Activity log

- 2026-06-30: Created and picked up (in-progress) by the project-manager orchestrator, handled orchestrator-direct by user direction (do it myself, not dispatched). Two doc-polish follow-ons from the COR-T-059/060 landing: the resolve-gate copy-vs-move abort (caught live during this session's resolve) and the missing dispatched-executor cross-references in the executor agent file and spec (COR-T-060 report Follow-up). P3: pure doc polish, non-blocking. Standalone (no epic), worktree-workflow family (COR-T-057/058/059/060).
