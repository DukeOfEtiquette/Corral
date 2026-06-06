## Deliverables completed

- [x] `./decisions/ADR-010-api-shape-and-mcp-data-path.md` resolved from `pending` to `accepted`:
  - Frontmatter: `status: "accepted"`, `date: "2026-06-05"`, `related_adrs: [2, 4, 11, 12, 13, 14, 19]`
  - `> Pending:` blockquote removed
  - All three alternatives expanded with selected/rejected reasoning
  - Decision section filled (REST, `/api/v1`, entity-level resource model bound to ADR-012, MCP server as authenticated API client that never touches Postgres)
  - Consequences section filled with all six required items
- [x] `./README.md` roadmap rows 2 and 3 swapped and retitled (Phase 2 "API + DB core", Phase 3 "MCP server"); all citations travel on the correct row
- [x] `./docs/architecture/OVERVIEW.md` mcp bullet updated; diagram and `(data path per ADR-010)` annotation unchanged
- [x] `./STATUS.md`: `last_updated` already current; `recent_updates` entry prepended; task-specific "Next step" edit applied

## Decisions made

No Worker-made decisions. All choices were pinned in the kickoff:
- REST API with `/api/v1` prefix (Orchestrator pin)
- MCP server calls HTTP API, never Postgres directly (Orchestrator pin, user call 2026-06-05)
- Build-order inversion: API phase before MCP phase (Orchestrator pin, user call 2026-06-05)
- Entity-level resource model bound 1:1 to ADR-012 schema (Orchestrator pin)
- ADR-011 owns MCP-to-API credential mechanism; not resolved here (Orchestrator pin)
- ADR-002 shared-package clarification: models/types only, no enforcement (Orchestrator pin)
- ADR-019 owns MCP contract versioning; separate from `/api/v1` path versioning (Orchestrator pin)

## Surprises

(none)

## Follow-ups

- COR-T candidate: ADR-004's Consequences item 2 still reads "Whether the MCP server calls the HTTP API or the database directly is a pending decision (ADR-010)." Now that ADR-010 is accepted, this sentence is stale. A future task that updates accepted ADRs for cross-reference accuracy should patch ADR-004's Consequences item 2 to reflect the resolved decision. Target: triage to orchestrator.

## Files touched

- `./decisions/ADR-010-api-shape-and-mcp-data-path.md`
- `./README.md`
- `./docs/architecture/OVERVIEW.md`
- `./STATUS.md`
- `./.claude/artifacts/tmp/COR-T-003-KICKOFF-REPORT.md` (this file)

## Build / verification status

No application code exists; no build or compose verification applies to this task. The deliverables are document edits only. Acceptance-gate items verified by reading the final file state:
- ADR-010 frontmatter: `status: "accepted"`, correct date, `related_adrs` covers ADR-011 and ADR-014 and ADR-019 (newly cited in Consequences)
- `> Pending:` blockquote absent; Context and all three expanded options present
- Decision section: all pinned choices encoded
- Consequences section: all six required items present
- README rows 2 and 3: swapped and retitled; ADR-014 citation on row 2 (API phase); ADR-004/ADR-010 citations on row 3 (MCP phase)
- OVERVIEW mcp bullet: updated; diagram and annotation unchanged
- STATUS.md: new recent_updates entry present; COR-T-003 dropped from "Next step"

User is expected to review staged changes (`git diff --cached`) before committing. No compose verification required for this task.
