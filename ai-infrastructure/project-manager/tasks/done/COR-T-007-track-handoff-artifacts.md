---
schema_version: 1
id: COR-T-007
title: "Git-track kickoff and report handoff artifacts (ADR-024)"
status: done
labels: [dept:agent-development]
priority: P2
created: 2026-06-05
updated: 2026-06-05
---

## Description

Reverse the artifact-location trade-off accepted in `./decisions/ADR-023-dispatch-loop-day-zero.md`: kickoff and worker-report handoff artifacts become git-tracked so handoff history is preserved. Decisions resolved with the user 2026-06-05:

- Tracked location: `./.claude/artifacts/handoffs/`. `./.claude/artifacts/tmp/` stays gitignored for genuinely scratch files (status snapshots, intermediate analyses).
- Commit timing: handoff artifacts ride along in the existing resolve-time commit gate. No new mid-task commit points; Workers still never commit.
- The four existing artifacts (COR-T-002/003 kickoff+report pairs) are moved and tracked retroactively.
- ADR-023 stays accepted and untouched (it also carries the dispatch-loop decision, which is unchanged); new `./decisions/ADR-024-git-tracked-handoff-artifacts.md` records the amendment.

Deliverables: ADR-024 authored as accepted; artifacts moved and tracked; `.gitignore` comment rescoped; documentation sweep across `./CLAUDE.md`, both role docs, `./docs/README.md`, both slash commands, all four agent definitions and specs; STATUS hygiene.

## Activity log

- 2026-06-05: Created in backlog.
- 2026-06-05: Claimed by the Orchestrator session; moved to in-progress. Process-architecture work executed directly per role clusters 4 and 5.
- 2026-06-05: Done. ADR-024 accepted, artifacts migrated and adopted, full path/classification sweep verified. Commit de073fa.
- 2026-06-10: Relabeled dept:ai-infra -> dept:agent-development per ADR-018 (COR-T-008): ai-infra is a domain not a department (ADR-021), so dept:ai-infra was invalid taxonomy. Label-only edit; task otherwise unchanged.
