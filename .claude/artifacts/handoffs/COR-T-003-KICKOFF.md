# COR-T-003: Resolve ADR-010 - API shape and MCP data path

## Target

This is **web-app** domain work (ADR-005): the artifact is a decision record about the web app's HTTP API and the MCP server's data path. No application code exists yet and none is written by this task. You are taking `./decisions/ADR-010-api-shape-and-mcp-data-path.md` from `pending` to `accepted` in place, then propagating its two downstream effects into `./README.md` (roadmap), `./docs/architecture/OVERVIEW.md` (one mcp bullet), and `./STATUS.md` (next-step list).

ADR-010 is one of the blocking Phase 1 ADRs. A fresh ADR-013 author (MCP tool surface) and a Phase 2 API implementer must be able to bind to ADR-010 without asking questions once you are done.

## Decisions resolved by the Orchestrator

Every choice below is pinned. You encode these answers; you do not re-deliberate them and you do not open any option back up.

- **API shape is REST, not GraphQL (user call 2026-06-05).** The resource model is deliberately narrow (issues, labels, views per ADR-001/ADR-012); GraphQL's tooling weight is not justified, and FastAPI's native idiom is REST with OpenAPI generation. ADR-010 Option C (GraphQL) is rejected on these grounds.
- **The MCP server calls the HTTP API; it never touches Postgres directly (ADR-010 Option A, confirmed with user 2026-06-05).** One enforcement seam: the house rules ADR-013 will define are enforced in the API layer and bind the web client and LLM agents identically, preserving ADR-004's guardrail intent. Accepted costs: a network hop inside the compose network, the MCP server needs service credentials, and the API must be built before the MCP server can function. ADR-010 Option B (direct DB access) is rejected: house rules would need correct application in two write paths, the dual-enforcement drift ADR-004 argues against.
- **Build-order inversion and roadmap swap (user call 2026-06-05).** Choosing the API data path inverts the README roadmap's current phase order (Phase 2 "MCP + DB core" before Phase 3 "API"). The swap is pinned: Phase 2 becomes **"API + DB core"** (Postgres schema, FastAPI endpoints with house rules, auth/sessions, invite tokens, migrations per ADR-014, admin seeding per ADR-006; milestone: first moment the app can store an issue). Phase 3 becomes **"MCP server"** (FastMCP server as an authenticated API client per ADR-004/ADR-010; milestone: the agent seam goes live). Only rows 2 and 3 of the roadmap table change; all other rows and all other README content stay untouched. The existing citations in those rows must survive the swap in the correct row: migrations (ADR-014), auth/sessions, invite tokens, and admin seeding all travel with the API phase.
- **API versioning: all routes carry a `/api/v1` path prefix (Orchestrator pin).** Cheap, standard, and explicitly distinct from MCP contract versioning, which ADR-019 (pending) owns. The ADR must state that the two versioning concerns are separate.
- **Resource model at entity level only (Orchestrator pin).** REST resources map 1:1 onto the accepted ADR-012 schema: issues, labels, views, issue comments, issue events, and the minimal users reference. ADR-010 records the resource list; the full endpoint table (verbs, routes, payloads) is implementation work in the API phase, not ADR content. Error envelope and pagination conventions are likewise implementation conventions, explicitly out of ADR scope; the ADR says so in one sentence rather than omitting the topic.
- **MCP-to-API authentication: ADR-010 names the requirement and defers the mechanism (Orchestrator pin).** The ADR states that the MCP server is an ordinary authenticated API client holding service credentials. The token shape and session model are deferred to ADR-011 (pending). Do not resolve ADR-011.
- **Shared Python package clarification (Orchestrator pin).** ADR-002's consequences anticipated a shared package for "models and house-rules validation". Under this decision the shared package carries models/types only; house-rules enforcement consolidates in the API layer and is not duplicated in the MCP server. ADR-010's Consequences must record this clarification of ADR-002's phrasing. ADR-002 itself is not edited.
- **Resolve mechanics per `./decisions/README.md` (same procedure as the ADR-012 run).** Edit ADR-010 in place: fill the stubbed Decision and Consequences sections, expand "Alternatives considered" with honest selected/rejected reasoning for Options A, B, and C, flip frontmatter `status` to `"accepted"`, set the frontmatter `date` to the work date `"2026-06-05"`. The append-only rule forbids deleting the existing framing; the `pending` blockquote callout under the H1 (the line beginning `> Pending:`) is a status marker, not decision content, and is removed.

## Deliverables

1. **`./decisions/ADR-010-api-shape-and-mcp-data-path.md` updated in place.** Specifically:
   - Frontmatter: `status: "accepted"`, `date: "2026-06-05"`. The `related_adrs` list currently reads `[2, 4, 12, 13]`; because the Consequences you write newly cite ADR-011, ADR-014, and ADR-019, add those three numbers so the list reflects the references the body actually makes (mechanical bookkeeping per the `./decisions/README.md` `related_adrs` definition, not a new decision).
   - Remove the `> Pending:` blockquote line directly under the H1.
   - "Alternatives considered": expand the three existing options with honest selected/rejected reasoning. Option A is selected (REST API; MCP server calls the HTTP API). Option B is rejected (REST API; MCP server reads/writes the database directly). Option C is rejected (GraphQL API). Keep the existing option framing as the floor; the append-only rule means you expand and complete it, not replace it.
   - "Decision" section filled, stated declaratively: REST, `/api/v1` path prefix, entity-level resource model bound 1:1 to the ADR-012 schema, MCP server as an authenticated API client that calls the HTTP API and never touches Postgres directly.
   - "Consequences" section filled, covering all six items below:
     1. the build-order inversion and the roadmap swap (note that this task edits README roadmap rows 2 and 3);
     2. the single enforcement seam: ADR-013's house rules will live in the API layer; the MCP server stays thin;
     3. the MCP-to-API service-credential requirement, with the mechanism owned by ADR-011;
     4. the ADR-002 shared-package clarification (models yes, enforcement no);
     5. the `/api/v1` prefix, with endpoint details and error/pagination conventions deferred to API-phase implementation;
     6. ADR-019 separation: MCP contract versioning is independent of API path versioning.
2. **`./README.md` roadmap table: swap and retitle rows 2 and 3** exactly as pinned above (Phase 2 "API + DB core", Phase 3 "MCP server"; citations travel with their phase). No other README change.
3. **`./docs/architecture/OVERVIEW.md` mcp bullet.** The sentence "Whether it calls the api service or postgres directly is pending (ADR-010)." (in the `mcp` bullet) becomes a statement that the MCP server calls the api service over HTTP per ADR-010 and never touches postgres directly. The diagram and its "(data path per ADR-010)" annotation stay as-is: the drawn mcp-to-api arrow already depicts the decided path and the citation remains correct. No other OVERVIEW change.
4. **`./STATUS.md`** per the STATUS deltas section below.

## Files in scope

- `./decisions/ADR-010-api-shape-and-mcp-data-path.md`
- `./README.md` (roadmap table rows 2 and 3 only)
- `./docs/architecture/OVERVIEW.md` (the single mcp-bullet sentence described above)
- `./STATUS.md`

## Files out of scope

- **Every other ADR.** ADR-011, ADR-013, ADR-014, and ADR-019 in particular remain `pending` and unedited; ADR-010's Consequences reference them but never edit them. ADR-002 and ADR-004 (both accepted) are likewise not edited; the ADR-002 shared-package clarification lands in ADR-010's Consequences only.
- **The `./tasks/` tree**, including `./tasks/backlog/COR-T-003-resolve-adr-010-api-shape.md`. Task transitions are Orchestrator-only per `./docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md`. You may read the task file for context; you never move, edit, or create files under `./tasks/`.
- **Any application code, OpenAPI spec files, SQL, migration files, or compose files.** This task writes no code; the endpoint table, error envelope, and pagination conventions are explicitly deferred to the API phase, not authored here.

## References

Read these in the order listed.

- `./decisions/ADR-010-api-shape-and-mcp-data-path.md`: the target; read first. Carries the Context and the three options you expand.
- `./decisions/README.md`: ADR conventions - frontmatter schema, status values, the four-section body convention, the append-only rule.
- `./decisions/ADR-004-mcp-server-as-llm-contract.md`: the guardrail rationale the single-enforcement-seam decision serves.
- `./decisions/ADR-012-issue-label-view-schema.md`: the accepted schema; the source of the entity-level resource model (issues, labels, views, issue_labels, view_labels, issue_comments, issue_events, users).
- `./decisions/ADR-002-tech-stack.md`: stack pins (FastAPI, FastMCP) and the shared-package consequence this ADR clarifies.
- `./decisions/ADR-011-auth-session-mechanism.md`: pending neighbour; owns the MCP service-credential mechanism the Consequences name without resolving.
- `./decisions/ADR-019-mcp-contract-versioning.md`: pending neighbour; owns the MCP contract versioning the Consequences mark as separate from `/api/v1`.
- `./README.md`: carries the roadmap table rows 2 and 3 in scope.
- `./docs/architecture/OVERVIEW.md`: carries the mcp-bullet sentence in scope.

## Related tasks and ADRs

- **COR-T-004** (`./tasks/backlog/COR-T-004-resolve-adr-013-mcp-surface.md`): ADR-013's tool surface binds to this data path; resolving ADR-010 unblocks it.
- **COR-T-005** (`./tasks/backlog/COR-T-005-resolve-adr-011-auth.md`): ADR-011 owns the MCP service-credential mechanism this ADR names, plus the auth/sessions work now in roadmap Phase 2.
- **COR-T-002** (`./tasks/done/COR-T-002-resolve-adr-012-schema.md`): delivered the accepted schema this API binds to.
- **ADR-004**: the MCP-as-sole-seam contract the single-enforcement-seam choice preserves.
- **ADR-002**: tech stack; its shared-package consequence is clarified (not edited) by this ADR.
- **ADR-014**: migrations tooling, pending; cited in the roadmap row that moves to Phase 2.
- **ADR-019**: MCP contract versioning, pending; explicitly separate from the `/api/v1` path versioning.

## STATUS deltas

Beyond universal STATUS hygiene (which `/corral-worker` and `WORKER-ROLE.md` define), apply this task-specific edit:

- In `./STATUS.md`, under "Next step", the line currently reads: `Work the remaining Phase 1 backlog: COR-T-003 (API shape, ADR-010), COR-T-004 (MCP surface, ADR-013), COR-T-005 (auth, ADR-011), COR-T-006 (departments, ADR-021)...`. Drop the `COR-T-003 (API shape, ADR-010)` entry from the list; leave the COR-T-004, COR-T-005, and COR-T-006 entries and the rest of the line intact.

## Hard rules

- **Append-only ADR discipline.** You expand and complete the existing ADR-010 body; you do not delete its Context or its option framing. The only removed line is the `> Pending:` status-marker blockquote, which is a status signal and not decision content (per the Decisions resolved section).
- **No new decisions.** The seven pinned decisions above are the whole decision content. Do not resolve ADR-011 (auth/credential mechanism), do not resolve ADR-019 (MCP contract versioning), do not author the endpoint table or the error/pagination conventions. Where the ADR touches those, it names the owning ADR or the deferring phase and stops there.
- **Scoped edits only.** README changes are confined to roadmap table rows 2 and 3; OVERVIEW changes are confined to the single mcp-bullet sentence (the diagram and its annotation are correct and stay). Do not regress adjacent content while editing.

## Acceptance gate

One gate: ADR-010 reads as an accepted ADR that a fresh ADR-013 author or a Phase 2 API implementer could bind to without asking questions. Concretely:

- ADR-010 frontmatter is `status: "accepted"` with `date: "2026-06-05"` and a `related_adrs` list that covers every ADR the body cites.
- The `> Pending:` blockquote is gone; Context and the three expanded options remain.
- The Decision section encodes all pinned choices (REST, `/api/v1`, entity-level resource model bound to ADR-012, MCP server as authenticated API client that never touches Postgres).
- The Consequences section contains all six required items.
- `./README.md` roadmap rows 2 and 3 are swapped and retitled as pinned, with citations on the correct rows and no other README change.
- `./docs/architecture/OVERVIEW.md` mcp-bullet sentence is updated and the diagram/annotation are unchanged.
- `./STATUS.md` carries the task-specific next-step edit plus universal hygiene.

## Worker pointer

The Worker session is `/corral-worker`. Universal worker conventions (verify-before-asserting, the writing rules in `./CLAUDE.md`, the compose-only run policy, git boundaries, and the pinned six-section report shape) live in `./docs/ai-orchestration/roles/WORKER-ROLE.md`. Write your closing report to `./.claude/artifacts/tmp/COR-T-003-KICKOFF-REPORT.md` per WORKER-ROLE.md, section "Report shape".
