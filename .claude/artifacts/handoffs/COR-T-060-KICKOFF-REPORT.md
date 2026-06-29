# COR-T-060 Executor Report

Kickoff: `.claude/artifacts/handoffs/COR-T-060-KICKOFF.md`
Worktree/branch: `cor-t-060-impl` (stacked on `cor-t-059-impl`)
Attempt: 1

## Deliverables completed

- [x] `docs/ai-orchestration/roles/EXECUTOR-ROLE.md` - 3 changes:
  - (a) **Gap-2a**: "Stage, do not commit." bullet rewrote to "Commit on the feature branch; never push; never integrate." (line 58). New text names the worktree workflow explicitly: commits stay on the feature branch, never reach `master`, executor never runs `bin/git-integrate`, integration stays the orchestrator's gate.
  - (b) **Gap-1**: New "Worktree handling (dispatched executor)" section added after "Universal conventions" (lines 64-82). Gives the canonical `git worktree add` procedure, absolute-path editing rule, commit-on-branch instruction, leave-on-disk rule, and the prohibition on calling `EnterWorktree` / `ExitWorktree` or running `bin/git-integrate`.
  - (c) **Gap-2b**: "Path derivation" paragraph in "Dual-channel: print to chat AND write to file" updated (line 145) to note that under the worktree workflow `<kickoff-dir>` resolves inside the worktree, so the report file is written inside the worktree and committed on the feature branch.

- [x] `docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md` - 2 changes:
  - (a) **Gap-2b**: "Resolve-gate worktree (Gap-2b)" sub-note added to step 7 of "Dispatched-worker flow" (line 210). Documents the resolve procedure: create a short-lived resolve worktree from `master`, copy the untracked kickoff into it, `git add` it alongside the task-tree move, commit there, integrate with `bin/git-integrate`. Notes that the executor's report is already in the executor's worktree (Gap-2b cross-link). Gate stays unconditional.
  - (b) **Gap-1**: "Dispatched executors use plain `git worktree add` commands" note appended to "Spike-grounded mechanics" paragraph (line 212). States the harness tools are refused in subagent context, points to `EXECUTOR-ROLE.md` "Worktree handling" section as canonical, and notes kickoffs no longer need a bespoke GIT HANDLING block.

- [x] `GIT_WORKFLOW.md` - 1 addition (ADD only, no COR-T-059 content touched):
  - Step 2 expanded with a two-path note (lines 10-12): "Interactive sessions" subpath uses `EnterWorktree` / `ExitWorktree {action: "keep"}`; "Dispatched executor subagents" subpath uses `git worktree add` / leave-on-disk. Both paths satisfy the same unconditional gate. Cross-reference to `EXECUTOR-ROLE.md` "Worktree handling (dispatched executor)" added.

- [x] `CLAUDE.md` - 1 change:
  - Hard-gate sentence in "Git workflow" section broadened (line 47): "(via `EnterWorktree`...)" replaced with "(via `EnterWorktree` for interactive sessions, or via `git worktree add` for dispatched executor subagents, both branched from local `master` HEAD)". Gate wording ("MUST happen inside a dedicated worktree, never in the main checkout on `master`") unchanged.

- [x] `COR-T-060-KICKOFF-REPORT.md` - This file, written inside the worktree at `.claude/artifacts/handoffs/COR-T-060-KICKOFF-REPORT.md`, dogfooding the Gap-2b report-into-worktree behavior.

## Decisions made

No new decisions. All three gaps and the hard-gate mechanism broadening were pinned in the kickoff. One implementation choice was made silently and is recorded here:

- For the "Worktree handling" section in EXECUTOR-ROLE.md, the kickoff said "a short subsection." It was implemented as a `##` section (peer to "Universal conventions", "Failure modes", etc.) rather than a `###` subsection within "Universal conventions". Rationale: the procedure is a distinct enough concept to warrant its own top-level section for findability; making it a peer gives it a section header visible in a ToC or search, whereas a `###` inside "Universal conventions" would have been nested inside an already-long block. The kickoff did not prohibit this placement.

## Surprises

None. All four files were at the expected paths on the base branch `cor-t-059-impl`. The worktree created cleanly. COR-T-059's 9-step Flow content (steps 6 and 9: `ExitWorktree {action: "keep"}`, exact teardown commands) was intact exactly as the kickoff described.

One observation: the `COR-T-059-KICKOFF.md` and `COR-T-059-KICKOFF-REPORT.md` files are not present in the worktree's `.claude/artifacts/handoffs/` directory - they exist only as untracked files in the main checkout. This is precisely the Gap-2b scenario this task documents: those files must be committed through a resolve worktree per the new ORCHESTRATOR-ROLE.md procedure.

## Follow-ups

- **COR-T candidate: update the agent `executor.md` and `EXECUTOR-AGENT-SPEC.md` to reference the new "Worktree handling (dispatched executor)" section.** The dispatch system prompt for the executor agent currently notes the worktree constraint informally; a cross-reference to the new canonical section would complete the documentation triangle. Triage to Orchestrator.

## Files touched

- `/home/adam/src/corral/.claude/worktrees/cor-t-060-impl/docs/ai-orchestration/roles/EXECUTOR-ROLE.md` (3 edits, committed on branch `cor-t-060-impl`)
- `/home/adam/src/corral/.claude/worktrees/cor-t-060-impl/docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md` (2 edits, committed on branch `cor-t-060-impl`)
- `/home/adam/src/corral/.claude/worktrees/cor-t-060-impl/GIT_WORKFLOW.md` (1 edit, committed on branch `cor-t-060-impl`)
- `/home/adam/src/corral/.claude/worktrees/cor-t-060-impl/CLAUDE.md` (1 edit, committed on branch `cor-t-060-impl`)
- `/home/adam/src/corral/.claude/worktrees/cor-t-060-impl/.claude/artifacts/handoffs/COR-T-060-KICKOFF-REPORT.md` (this file, dual-channel report write, committed on branch `cor-t-060-impl`)

## Build / verification status

No code changes; no compose run per kickoff.

Cross-file consistency verified:

- **Three Gap-1 surfaces agree on `git worktree add` mechanism**: EXECUTOR-ROLE.md "Worktree handling" section, GIT_WORKFLOW.md step 2 dispatched-path note, and CLAUDE.md broadened gate sentence all name `git worktree add <abs-path>/.claude/worktrees/<branch> -b <branch> <base>` as the dispatched-subagent worktree-creation command. All three surfaces also agree that `EnterWorktree` / `ExitWorktree` are refused in subagent context.
- **Gap-2b resolve procedure consistent**: ORCHESTRATOR-ROLE.md step 7 "Resolve-gate worktree" note says the executor's report is already committed in the executor's worktree (per EXECUTOR-ROLE.md) and that only the untracked kickoff needs the copy step. EXECUTOR-ROLE.md "Dual-channel" subsection says the report resolves inside the worktree and is committed on the feature branch. These are mutually consistent.
- **Hard gate stays unconditional**: CLAUDE.md "Git workflow" section retains "MUST happen inside a dedicated worktree, never in the main checkout on `master`" and all "no exception" language. GIT_WORKFLOW.md step 2 keeps "same gate" for both paths. No exception added to either file.
- **COR-T-059 content in GIT_WORKFLOW.md unchanged**: Step 6 (`ExitWorktree {action: "keep"}` with `remove` caution) and step 9 (exact teardown commands with `remove` caution) are verbatim from the base branch. Only step 2 was modified.
- **No em dashes in any of the four edited files**: grep -P check returned no matches.
- Branch: `cor-t-060-impl`; commit hash: (see commit below)
