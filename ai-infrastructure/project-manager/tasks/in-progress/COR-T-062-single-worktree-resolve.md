---
schema_version: 1
id: COR-T-062
title: "Single-worktree task resolve: fold the resolve-gate commit into the deliverable branch"
status: in-progress
labels: []
priority: P1
created: 2026-06-30
updated: 2026-06-30
---

## Description

The ADR-046 worktree workflow, as refined by COR-T-060, routes a task's resolve-gate commit (the untracked kickoff plus the in-progress-to-done task-tree move) through a SEPARATE short-lived "resolve worktree" created from `master` after the deliverable is integrated (the "Gap-2b" procedure, in `ORCHESTRATOR-ROLE.md` "Dispatched-worker flow" step 7 and ADR-046 forward-pointer item 11c). For a dispatched task this produces **two worktrees and two merges per task**: the executor's deliverable worktree (merge 1) and the orchestrator's resolve worktree (merge 2).

Verified live on DB-T-006 (session `13d596a8-a094-4020-8fe6-a22762c13998`), 2026-06-30: branch `db-t-006` (deliverable, merged `0dc5e70`) and branch `db-t-006-resolve` (resolve, merged `91e979a`) -- two worktrees, two integrates for one task. The operator flagged the second worktree as a hard block on all other work.

The second worktree is structurally unnecessary. ADR-046 Gap-2b itself notes the executor's report is already committed on the feature branch; only the untracked kickoff and the task-tree move remain, and both can land on that same branch before a single integrate. This is the COR-11 friction family (each real firing of the worktree workflow surfaces one more friction).

**Decision (user-confirmed, 2026-06-30): fold the resolve-gate commit into the deliverable's own feature branch.** One worktree, one `bin/git-integrate`, one teardown per task. Captured in ADR-047.

### Deliverables

- `ai-infrastructure/project-manager/decisions/ADR-047-single-worktree-task-resolve.md`: new accepted ADR recording the decision; amends ADR-046's Gap-2b resolve-gate procedure (does not change worktree-per-session or the merge lock).
- `ai-infrastructure/project-manager/decisions/ADR-046-...md`: append forward-pointer item 12 to ADR-047 (append-only; the Gap-2b decision text is left intact per the append-only convention).
- `docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md`: rewrite the "Resolve-gate worktree (Gap-2b)" note (Dispatched-worker flow step 7) to the single-worktree procedure; add a pointer from the Task-lifecycle Resolve bullet.
- `GIT_WORKFLOW.md`: update the dispatched-executor step so the Orchestrator adds the resolve-gate commit onto the same feature branch before a single integrate; add ADR-047 to the footer reference.
- `docs/ai-orchestration/roles/EXECUTOR-ROLE.md`: note in "Worktree handling" that the Orchestrator adds the resolve commit onto the executor's branch before integrating (leave the worktree intact).

Out of scope: any change to the merge lock, the hooks, `bin/git-integrate`, the worktree-per-session decision itself, or the COR-T-057/058/059/060/061 fixes.

## Activity log

- 2026-06-30: Created and picked up (in-progress) by the project-manager orchestrator, handled orchestrator-direct by user direction (this exact resolve-gate-doc family was handled orchestrator-direct in COR-T-060/061; user wants it ASAP as a hard block). Root-caused from DB-T-006 session `13d596a8` (two worktrees / two merges for one task). Design confirmed with user: fold the resolve-gate commit onto the deliverable feature branch (single worktree, single integrate). P1: flagged a hard block on all other work. Standalone (no epic), worktree-workflow family (COR-T-057/058/059/060/061, COR-11). Dogfoods its own fix: this task's deliverable and resolve land on one branch (`cor-t-062`), one merge.
