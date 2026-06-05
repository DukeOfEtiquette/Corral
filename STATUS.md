---
schema_version: 1
phase: 1
phase_title: "AI infrastructure: role docs, agents, blocking ADRs"
last_updated: "2026-06-05"
recent_updates:
  - "2026-06-05: COR-T-002 executed: ADR-012 resolved from pending to accepted (issues/labels/views/comments/events schema pinned); OVERVIEW.md line 25 corrected to attribute users/invites to ADR-011."
  - "2026-06-05: COR-T-001 executed: orchestrator/worker role docs authored, full drafter+checker dispatch loop ported from rogue (ADR-023), /corral-orchestrator and /corral-worker commands created."
  - "2026-06-05: Project renamed from placeholder GHIssuesClone to Corral (ADR-022); ID prefixes GHI-T/GHI-NN renamed to COR-T/COR-NN."
  - "2026-06-05: Phase 0 executed: repo initialized, ADR-001..009 accepted, ADR-010..021 queued pending, task convention seeded with COR-T-001..006 (as GHI-T at the time)."
---

# Status

Single source of truth for current progress. Update at the end of any session that makes progress.

## Current phase

**Phase 1: AI infrastructure.** The orchestration layer now exists: orchestrator and worker role docs (`./docs/ai-orchestration/roles/`), the drafter+checker dispatch loop with four universal subagents (ADR-023), and the `/corral-orchestrator` and `/corral-worker` commands. Remaining Phase 1 work: resolve the blocking pending ADRs and the department structure. See `./README.md` for the full roadmap.

## Next step

Work the remaining Phase 1 backlog: COR-T-003 (API shape, ADR-010), COR-T-004 (MCP surface, ADR-013), COR-T-005 (auth, ADR-011), COR-T-006 (departments, ADR-021). These are the first candidates for the new kickoff/worker workflow.

## Blocked on

Nothing. All remaining Phase 1 tasks are actionable.
