---
schema_version: 1
phase: 1
phase_title: "AI infrastructure: role docs, agents, blocking ADRs"
last_updated: "2026-06-08"
recent_updates:
  - "2026-06-08: COR-T-005 executed: ADR-011 accepted (server-side cookie sessions; hand-rolled on vetted primitives; argon2id hashing, closing ADR-006; invite-token mechanics pinned, closing ADR-007; MCP-to-API static service API key with a single shared service identity, closing ADR-010 Consequence #3; auth schema delta owned per ADR-012 Consequence #3); per-agent MCP identity deferred to a future ADR; OVERVIEW.md line-25 \"pending\" annotation dropped."
  - "2026-06-07: Queued COR-T-008 (resolve ADR-018 label taxonomy) and COR-T-009 (resolve ADR-025 native epics), triaged from COR-T-004 Worker follow-ups."
  - "2026-06-07: COR-T-004 executed: ADR-013 accepted (nine-tool MCP surface: issue_list/get/create/claim/move/comment/label/view_list/import; free status transitions; priority required at create; label-governance mechanism pinned, specifics deferred to ADR-018/ADR-021); ADR-025 queued pending (native epics); OVERVIEW.md mcp-bullet clause updated."
  - "2026-06-05: COR-T-007 executed: ADR-024 accepted (kickoff/report handoffs git-tracked in .claude/artifacts/handoffs/, tmp/ stays gitignored scratch); four existing COR-T-002/003 artifacts adopted; path/classification sweep across CLAUDE.md, role docs, commands, agents, specs."
  - "2026-06-05: COR-T-003 executed: ADR-010 resolved from pending to accepted (REST API, /api/v1 prefix, MCP server as authenticated API client); README roadmap rows 2 and 3 swapped; OVERVIEW.md mcp bullet updated."
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

Work the remaining Phase 1 backlog: COR-T-006 (departments, ADR-021) is the near-term candidate for the kickoff/worker workflow. COR-T-008 (label taxonomy, ADR-018) and COR-T-009 (native epics, ADR-025) are queued for later resolution.

## Blocked on

Nothing. All remaining Phase 1 tasks are actionable.
