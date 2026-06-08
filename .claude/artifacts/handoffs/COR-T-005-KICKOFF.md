# Resolve ADR-011: auth and session mechanism

## Target

This is web-app work (ADR-005): the artifact is a decision record that governs the web app's browser authentication, sessions, password hashing, invite tokens, and the credential the MCP server uses to reach the REST API. No application code, SQL, or migration is written by this task. It is the same classification as the COR-T-004 ADR-013 run: an ADR resolution plus a small, named doc-propagation edit.

The procedure is the same one COR-T-002 (ADR-012), COR-T-003 (ADR-010), and COR-T-004 (ADR-013) followed. You resolve the pending ADR in place per `./decisions/README.md`:

- Expand "Alternatives considered" with honest selected/rejected reasoning across every dimension this ADR closes (browser session model, build approach, password hash, invite-token mechanics, MCP-to-API credential).
- Fill the stubbed `Decision` section declaratively.
- Fill the stubbed `Consequences` section.
- Flip frontmatter `status` from `pending` to `accepted` and set frontmatter `date` to the work date `2026-06-08`.
- Remove the `> Pending:` blockquote callout directly under the H1. That callout is a status marker, not decision content; it is removed when the ADR goes accepted. The append-only rule (`./decisions/README.md`) still forbids deleting the existing Context or the Option A / Option B / Option C framing: you expand that framing, you do not delete it.

## Decisions resolved by the Orchestrator

Every dimension below is already decided. Encode each as ADR text (the pinned answer plus the rationale to record). Do not re-open any of these or present them as options for a reader to choose between.

- **Frontmatter on resolve.** Set `status: "accepted"`, `date: "2026-06-08"`, and `related_adrs: [6, 7, 10, 12, 13, 20]`. The current value is `[6, 7, 10]`; the new Consequences cite ADR-012 (auth schema boundary), ADR-013 (the `issue_claim` actor), and ADR-020 (the claim-lease coupling), so add `12, 13, 20`. This is reference bookkeeping per `./decisions/README.md`, not a new decision.

- **Browser session model: server-side sessions with HTTP-only cookies (ADR-011 Option A, selected).** An opaque, high-entropy random session identifier is stored in an HTTP-only, SameSite cookie (Secure when served over HTTPS); session state is persisted server-side and is therefore directly revocable. Rationale to record: the React client is same-origin behind the compose network, nothing requires statelessness, and instant revocation matters for an invite-only tool. Option B (JWT bearer tokens) is the rejected alternative: stateless tokens add revocation machinery (a denylist, or short expiry plus refresh) that a single same-origin app does not need.

- **Build approach: hand-rolled on vetted primitives (ADR-011 Option C, resolved toward minimal).** Use trusted crypto and session primitives (argon2-cffi for password hashing; a server-side session store such as a sessions table keyed by the opaque cookie id, or Starlette session middleware backed server-side), but hand-write the small number of flows: admin seed, login, invite redemption. No full auth framework (for example fastapi-users). Rationale to record: the surface is deliberately narrow (invite-only, no self-registration, no password-reset email per ADR-007), so a framework's main value-adds go unused while it adds dependency weight and opinionated models.

- **Password hashing: argon2id (via argon2-cffi).** Used for the admin bootstrap credential (this closes ADR-006's bcrypt-vs-argon2 open question) and for user passwords set at invite redemption. The operator's local hash-generation step (ADR-006; README getting-started step 1) uses argon2id. Rationale to record: greenfield project with no legacy hashes to honor; argon2id is the current OWASP first choice and is memory-hard. bcrypt is the rejected alternative (72-byte silent truncation, with no offsetting benefit here).

- **Invite-token mechanics (this closes ADR-007's deferral of token generation, expiry, and single-use enforcement).** Pin these properties: tokens are high-entropy random (CSPRNG), email-bound, single-use (consumed and invalidated on redemption), time-limited (an expiry exists), stored hashed at rest (never persisted in plaintext), and admin-revocable (mint, list, revoke on the ADR-006 admin page). Redemption verifies the token, then lets the invitee set a password (argon2id-hashed). The rejected alternatives are plaintext-token-at-rest and no-expiry. Exact token byte-length and expiry window are implementation-phase, not ADR content (consistent with ADR-010's altitude, which deferred endpoint specifics).

- **MCP-to-API authentication: a static service API key, single shared service identity.** The MCP server authenticates to the REST API with a long random bearer secret held in the MCP server's gitignored `.env` (the ADR-006 secret convention), verified by the API. It is one shared service identity for all agents. Rationale to record: minimal moving parts, it matches the `.env` secret convention, and the agent fleet currently shares one seam (ADR-004). This closes ADR-010 Consequence #3 ("the token shape and session model are deferred to ADR-011"). The rejected v1 alternatives are service-account-login (which would couple MCP auth to the browser session model) and per-agent tokens (premature before the MCP surface is built). Per-agent identity is explicitly deferred to a future pending ADR; do not create that ADR in this task.

- **Single-identity to claim-lease coupling (record as a Consequences note citing ADR-013 and ADR-020).** Because all agents share one MCP service identity, `issues.assignee_id` set via ADR-013's `issue_claim` resolves to that single service user, so claim-as-lease cannot distinguish one agent from another. ADR-020 (pending) leans toward "assignee-as-lease so agents avoid contention by convention" (its Option C); per-agent identity is the prerequisite for agent-vs-agent claim contention. Record this as the rationale the deferred per-agent-identity ADR will carry. ADR-020 stays pending and is not decided here; this is a non-preclusion and deferral note, not a concurrency decision.

- **Auth schema delta owned by ADR-011 (per ADR-012 Consequences #3, accepted).** ADR-012 deliberately scoped the `users` table to `id` plus `display_name` and handed the full auth schema (password hash, invite tokens, session management) to ADR-011. At decision altitude, record that ADR-011 owns: `users` gains `email` (unique; the identity anchor per ADR-007) and `password_hash`; plus an `invites` concept (email, token-hash, expiry, consumed marker, created-by) and a `sessions` concept (opaque session id, user, expiry), or an equivalently capable signed-session store. Exact DDL, column names, and types are implementation-phase and ADR-014 migration work, not ADR-011 content. State this as the schema boundary and cite ADR-012 Consequence #3 and the `assignee_id` FK seam.

- **Named, not decided (out of scope: name them and stop).** Exact session lifetime, cookie-attribute specifics (for example, toggling the Secure flag for local HTTP dev), token byte-length and expiry windows, and the concrete DDL are implementation-phase. MCP contract versioning (ADR-019) and the multi-user concurrency model (ADR-020) are not touched beyond the claim-lease non-preclusion note. Name these in the ADR and stop; do not resolve them.

## Deliverables

1. `./decisions/ADR-011-auth-session-mechanism.md` resolved in place:
   - Frontmatter: `status: "accepted"`, `date: "2026-06-08"`, `related_adrs: [6, 7, 10, 12, 13, 20]`.
   - The `> Pending:` blockquote callout under the H1 removed.
   - "Alternatives considered" expanded with Option A selected, Option B rejected, and Option C resolved toward hand-rolled, plus the resolved password-hash, invite-token, and MCP-credential dimensions.
   - "Decision" filled declaratively: cookie sessions, hand-rolled on vetted primitives, argon2id, the invite-token mechanics, the static MCP service API key with a single shared service identity, and the auth schema delta.
   - "Consequences" filled: closes ADR-006 (hash algorithm), ADR-007 (token mechanics), ADR-010 Consequence #3 (MCP credential), and ADR-012 Consequence #3 (auth schema boundary); the single-identity to claim-lease deferral note; per-agent identity deferred to a future ADR; and the implementation-phase items named.

2. `./docs/architecture/OVERVIEW.md` line-25 parenthetical updated. Line 25 currently reads, in its trailing clause: `users, invites (schema pending, ADR-011).` Rewrite the parenthetical from `(schema pending, ADR-011)` to `(schema ADR-011)`, dropping the word `pending` only, and keep the rest of line 25 intact. Nothing else in OVERVIEW.md changes (see Files out of scope).

3. `./STATUS.md` updated per the STATUS deltas section below (universal hygiene plus the named task-specific edits).

## Files in scope

- `./decisions/ADR-011-auth-session-mechanism.md` (resolve in place).
- `./docs/architecture/OVERVIEW.md` (the line-25 parenthetical only).
- `./STATUS.md` (task-specific delta plus universal hygiene).

## Files out of scope

- Every other ADR. ADR-006, ADR-007, ADR-010, ADR-012, and ADR-013 (all accepted) are cited in ADR-011's Consequences but are never edited; ADRs are append-only. ADR-019 and ADR-020 stay pending and unedited.
- Do not create a new pending ADR for per-agent MCP identity. That is an Orchestrator follow-up, not this task. Surface it under "Follow-ups" in your report if you wish, but do not author it.
- The `./tasks/` tree, including `./tasks/in-progress/COR-T-005-resolve-adr-011-auth.md`. Task transitions are Orchestrator-only. Read the task file for context if you need it; never move, edit, or create anything under `./tasks/`.
- Any application code, auth code, SQL or migration files, OpenAPI or tool-schema files, compose files, and `.env` / `.env.example`. No secrets, password hashes, or `.env` contents in any tracked file (`./CLAUDE.md`, ADR-006). Concrete DDL, endpoint wiring, and crypto parameter values are implementation or future-ADR work, not authored here.
- `./README.md`. Roadmap row 1 (which lists auth / ADR-011 as a Phase-1 blocking ADR) stays an accurate historical deliverable list after resolution, matching how the ADR-010 and ADR-013 runs left it. Getting-started step 1 ("Generate an admin password hash locally") does not name an algorithm and stays accurate. Not edited.
- `./docs/architecture/OVERVIEW.md` line 26, the diagram, and all other bullets. Line 26 ("**api**: FastAPI... enforces auth (ADR-011)...") already reads correctly and is not edited.

## References

Read these in this order.

- `./decisions/ADR-011-auth-session-mechanism.md`: the target; read first. Carries the Context and the Option A / Option B / Option C framing you expand.
- `./decisions/README.md`: ADR conventions: frontmatter schema, status values, the four-section body convention, the append-only rule, and how a pending ADR is taken to accepted.
- `./decisions/ADR-006-admin-bootstrap-env-hash.md`: the admin env-hash bootstrap; the hash algorithm (argon2id) closes its deferral, and its `.env` secret convention is reused for the MCP service key.
- `./decisions/ADR-007-invite-only-tokens-no-smtp.md`: the invite model; ADR-011 owns generation, expiry, and single-use enforcement; redemption sets the password; the admin page mints, lists, and revokes.
- `./decisions/ADR-010-api-shape-and-mcp-data-path.md`: accepted REST plus MCP-as-authenticated-API-client; Consequence #3 defers the MCP token shape here; the single enforcement seam.
- `./decisions/ADR-012-issue-label-view-schema.md`: accepted schema; Consequence #3 hands the auth schema (password hash, invite tokens, sessions) to ADR-011; the `users` table is minimal (`id` plus `display_name`); the `assignee_id` FK is the seam.
- `./decisions/ADR-013-mcp-tool-surface-house-rules.md`: `issue_claim` sets `issues.assignee_id`; read for the actor in the single-identity claim-lease note.
- `./decisions/ADR-020-multi-user-concurrency-model.md`: pending; the assignee-as-lease leaning (its Option C) that the coupling note references without deciding.
- `./docs/architecture/OVERVIEW.md`: carries the line-25 clause that is in scope; line 26 is read-only context.

## Related tasks and ADRs

- COR-T-005 (`./tasks/in-progress/COR-T-005-resolve-adr-011-auth.md`): this task's tracking file; read for context, do not edit.
- COR-T-002 (`./tasks/done/COR-T-002-resolve-adr-012-schema.md`): delivered the accepted schema whose deferred auth fields ADR-011 now owns.
- COR-T-003 (`./tasks/done/COR-T-003-resolve-adr-010-api-shape.md`): delivered the data path; its Consequence #3 defers the MCP credential here.
- COR-T-004 (`./tasks/done/COR-T-004-resolve-adr-013-mcp-surface.md`): delivered the MCP surface; the `issue_claim` actor relates to the single-identity note.
- ADR-006 / ADR-007: accepted; their deferrals (hash algorithm; invite-token mechanics) close in ADR-011.
- ADR-010 (Consequence #3): the MCP service-credential deferral that closes here.
- ADR-012 (Consequence #3): the auth schema boundary ADR-011 owns; the `assignee_id` FK seam.
- ADR-013 / ADR-020: the `issue_claim` actor and the concurrency model the single-identity coupling note references; neither is decided here.

## STATUS deltas

Beyond universal STATUS hygiene (bump `last_updated` to `2026-06-08` and append a `recent_updates` entry, per WORKER-ROLE.md), apply these task-specific edits to `./STATUS.md`:

- Under "Next step", the line currently reads: "Work the remaining Phase 1 backlog: COR-T-005 (auth, ADR-011) and COR-T-006 (departments, ADR-021) are the near-term candidates for the kickoff/worker workflow. COR-T-008 (label taxonomy, ADR-018) and COR-T-009 (native epics, ADR-025) are queued for later resolution." Remove the "COR-T-005 (auth, ADR-011) and" clause and fix the grammar so it reads that COR-T-006 (departments, ADR-021) is the near-term candidate (singular). Leave the COR-T-008 / COR-T-009 sentence intact.

- The `recent_updates` entry should note: ADR-011 accepted (server-side cookie sessions; hand-rolled on vetted primitives; argon2id hashing, closing ADR-006; invite-token mechanics pinned, closing ADR-007; MCP-to-API static service API key with a single shared service identity, closing ADR-010 Consequence #3; auth schema delta owned per ADR-012 Consequence #3); per-agent MCP identity deferred to a future ADR; OVERVIEW.md line-25 "pending" annotation dropped.

- The "Blocked on" section stays "Nothing." Do not change it.

## Hard rules

- Resolve the ADR in place; do not create a second ADR file or a copy. The append-only rule means you expand the existing Context and Alternatives framing, you never delete it. The only deletion permitted is the `> Pending:` status-marker blockquote under the H1.
- No secrets, password hashes, token values, or `.env` contents in any tracked file. The ADR describes mechanisms and properties (argon2id, CSPRNG tokens, a static bearer key in `.env`); it never contains an actual hash, token, or key.
- Keep the ADR at decision altitude. Concrete DDL, column types, byte-lengths, expiry windows, cookie-attribute toggles, and endpoint wiring are implementation-phase or future-ADR work. Name them as deferred; do not specify them.
- Do not decide ADR-019 or ADR-020. The claim-lease coupling note is a non-preclusion and deferral, not a concurrency decision.

## Worker pointer

The Worker session is `/corral-worker`. Universal worker conventions live in `./docs/ai-orchestration/roles/WORKER-ROLE.md`. The closing report is written to `./.claude/artifacts/handoffs/COR-T-005-KICKOFF-REPORT.md` per WORKER-ROLE.md, section "Report shape".
