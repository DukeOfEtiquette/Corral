# Thin the README roadmap to stable orientation; STATUS frontmatter owns the detail

## Target

This is **ai-infrastructure** work (ADR-005): the deliverable is the repo-root human orientation document, `./README.md`, and editing it is AI-infrastructure documentation maintenance. The task (COR-T-021) thins the README's "## Roadmap" section so it carries only stable, slow-changing human orientation. The live and detailed roadmap (per-phase status, sub-milestones) is already owned by the `roadmap:` frontmatter in `./ai-infrastructure/project-manager/STATUS.md`, which the project-manager dashboard renders live (since COR-T-020). The README roadmap currently duplicates phase titles and granular deliverable prose from that frontmatter, the duplication is drift-prone, and it has already drifted: the README carries a stale "(this iteration)" marker on Phase 0 even though the project is in Phase 1.

## Decisions resolved by the Orchestrator

The user chose direction "#1": the README keeps only STABLE human orientation; the STATUS frontmatter and the dashboard own the live and detailed roadmap. Status and milestones must NEVER live in the README. The following are pinned:

- **Edit exactly one section.** Change ONLY the "## Roadmap" section of `./README.md` (currently a phase table, roughly lines 49-58). Every other README section stays byte-for-byte unchanged: Why, Status, Architecture at a glance, Tech stack, Getting started, Repository layout, How decisions are recorded.
- **Keep the table, keep the 6 rows.** The roadmap stays a table (it is human-skimmable on GitHub) with the 6 phase rows, 0 through 5, in order. Do not drop rows, add rows, or change the table format.
- **Remove the granular detail from each cell.** Strip the deliverable enumerations, the inline ADR citations (for example "(ADR-012)", "(ADR-014)"), and the "(this iteration)" status marker on Phase 0. No per-phase status, no milestone rows, and no status markers of any kind remain in the README roadmap.
- **Each cell becomes one concise sentence of phase intent.** Use the substance and altitude below. You may refine the wording to match the README's voice, but keep this substance and this altitude (one sentence, intent only, no deliverable lists, no ADR refs, no status):
  - 0. Bootstrap: "Docs, decision records, and the task convention."
  - 1. AI infrastructure: "Orchestrator and worker role docs, the dispatch loop, the blocking ADRs, and the department structure."
  - 2. API + DB core: "Postgres schema, FastAPI endpoints, auth and sessions, migrations, and admin seeding; the first point the app can store an issue."
  - 3. MCP server: "The FastMCP server goes live as the authenticated agent seam."
  - 4. Kanban UI: "The React multi-view board with per-view label filters, plus the admin page."
  - 5. Dogfood milestone: "Import the markdown tasks into the app via the MCP server; the project tracks itself and the markdown tasks freeze."
- **Add one pointer line.** Under the "## Roadmap" heading, before the table, add one short lead-in line directing the reader to `./ai-infrastructure/project-manager/STATUS.md` for live phase and milestone status (the single source of truth) and to the project-manager dashboard (`./ai-infrastructure/project-manager/dashboard/`) for the rendered live roadmap. This reinforces what README lines 13 and 42 already say. Do not contradict or remove those existing pointers; the new line stays consistent with them.
- **No em dashes** (global rule, `./CLAUDE.md`). Use a comma, colon, semicolon, or rephrase.

## Deliverables

- The "## Roadmap" section of `./README.md` thinned per the pinned scope: 6 phase rows kept, each cell a one-line statement of phase intent, all granular deliverable enumerations / inline ADR refs / the "(this iteration)" marker removed, plus one lead-in pointer line under the heading directing readers to `./ai-infrastructure/project-manager/STATUS.md` and the project-manager dashboard for live status. No other README section is touched.
- Universal STATUS hygiene only (see STATUS deltas below).

## Files in scope

- `./README.md` (repo root): only the "## Roadmap" section changes.
- `./ai-infrastructure/project-manager/STATUS.md`: universal hygiene only (bump `last_updated` if needed, append one `recent_updates` entry). The `roadmap:` frontmatter block in this file is OUT of scope (see below).

## Files out of scope

- The `roadmap:` frontmatter block in `./ai-infrastructure/project-manager/STATUS.md`: this is the structured single source of truth and is NOT edited. Do not mirror the README thinning into it; do not add or remove milestones or statuses there.
- The dashboard code under `./ai-infrastructure/project-manager/dashboard/`: the README points to it; it is not changed.
- `./ai-infrastructure/project-manager/docs/architecture/OVERVIEW.md` and every ADR: not touched.
- The `./ai-infrastructure/project-manager/tasks/` tree: Orchestrator-owned; never edited by the Worker.
- All README sections other than "## Roadmap" (Why, Status, Architecture at a glance, Tech stack, Getting started, Repository layout, How decisions are recorded): byte-for-byte unchanged.

## References

- `./README.md`: the file to edit. The "## Roadmap" section is the only edit target (a phase table, roughly lines 49-58). The "## Status" section (lines 11-13) and the Repository layout row (line 42) already point live status to `./ai-infrastructure/project-manager/STATUS.md` as the single source of truth; keep them and make the new pointer line consistent with them.
- `./ai-infrastructure/project-manager/STATUS.md`: read the `roadmap:` frontmatter to confirm the phase titles and order to stay consistent with, and to see the granular deliverables the README must NOT duplicate. Do NOT edit the roadmap frontmatter; the only edit to this file is the universal `recent_updates` hygiene entry.
- `./ai-infrastructure/project-manager/dashboard/`: the dashboard directory is the rendered live roadmap the README pointer names. It has no README of its own; you do not need to read its code to author the pointer line.

## Related tasks and ADRs

- COR-T-014: built the project-manager dashboard, which renders the roadmap from the STATUS frontmatter.
- COR-T-017: added roadmap sub-milestone granularity to the dashboard; this live detailed view is why the README no longer needs to carry granular roadmap detail.
- COR-T-020: made the dashboard live (it auto-renders STATUS roadmap changes), reinforcing the STATUS frontmatter plus dashboard as the home of the live roadmap.
- ADR-008: the dogfood-milestone seam, context for the Phase 5 one-liner.

## STATUS deltas

No task-specific STATUS deltas; universal hygiene only. Apply the universal hygiene per `./docs/ai-orchestration/roles/WORKER-ROLE.md` (section "Wrap-up STATUS hygiene"): bump `last_updated` and append one `recent_updates` entry naming this task and what it delivered. Do not touch the `roadmap:` frontmatter while doing so.

## Hard rules

- Touch only the "## Roadmap" section of `./README.md`. Read the file before editing and match its existing formatting; do not reflow or reword any other section.
- Do not edit the `roadmap:` frontmatter in `./ai-infrastructure/project-manager/STATUS.md`. The README thinning is one-directional and is NOT mirrored into the frontmatter.
- No em dashes anywhere in the edits (`./CLAUDE.md`).

## Worker pointer

The worker is the dispatched `worker-agent` (ADR-028). Universal worker conventions live in `./docs/ai-orchestration/roles/WORKER-ROLE.md`, including the repo writing rules, the no-edits-outside-scope rule, and the closing report shape. The closing report is written to `./.claude/artifacts/handoffs/COR-T-021-KICKOFF-REPORT.md` per `WORKER-ROLE.md`, section "Report shape".
