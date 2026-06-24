---
schema_version: 1
adr: 13
title: "MCP tool surface and server-enforced house rules"
status: "accepted"
date: "2026-06-07"
related_adrs: [4, 8, 10, 12, 17, 18, 19, 20, 25, 26]
supersedes: []
superseded_by: null
---

# ADR-013: MCP tool surface and server-enforced house rules

## Context

ADR-004 commits to an MCP server as the sole LLM seam. This ADR decides what that server exposes and enforces. The proven reference is rogue's `ghtask` surface: `task_list`, `task_get`, `task_create`, `task_claim`, `task_move`, `task_comment`, `task_label`, `task_link`, with server-side house rules (required label families, exactly-one-status, priority labels, auto-created sanctioned labels).

## Alternatives considered

### Option A: Mirror the ghtask tool set, renamed for this domain

`issue_list/get/create/claim/move/comment/label/link` plus `view_list`. Familiar to the existing agent fleet; proven ergonomics.

**Selected and narrowed.** The v1 surface is eight base tools, renamed from ghtask's `task_*` to this domain's `issue_*`: `issue_list`, `issue_get`, `issue_create`, `issue_claim`, `issue_move`, `issue_comment`, `issue_label`, plus `view_list`. These map directly onto the accepted ADR-012 schema (issues, issue_labels, views, issue_comments, issue_events, the minimal users reference). A ninth tool, `issue_import`, is added for the ADR-008 dogfood import path (see "Open house-rule dimensions" below). Rationale: the `issue_*` set is familiar to the existing agent fleet, carries proven ergonomics from ghtask, and provides a 1:1 fit with the accepted ADR-012 schema.

Three ghtask tools were considered and deliberately excluded:

- `task_link` is dropped. In ghtask it appends `- [ ] #child` under a `## Tracked work` body section, a markdown workaround for GitHub Issues' lack of native epic support. Corral will support epics natively (see ADR-025), so the body-convention link tool is not needed.
- `task_check` is dropped. It ticks markdown checklist items in an issue body, the same body-convention family as `task_link`, and is likewise a GitHub workaround Corral does not need.
- `task_lint` is deferred. It conformance-checks issues against house rules, but the house-rule specifics (label families) are not yet pinned, and rules are enforced at write time by the API layer. A separate lint tool can be added later if needed.

### Option B: Leaner v1 surface

Only `issue_list/get/create/move/comment`; add claim/label/link when an agent workflow actually needs them.

**Rejected.** The ADR-012 schema includes `assignee_id` and the label relation as first-class columns, and `view_list` is required for the headline multi-board use case (ADR-001). Deferring `issue_claim` and `issue_label` would make the MCP surface immediately incomplete against the accepted schema and the existing agent fleet's expectations. The cost of including them in v1 is low; the cost of a surface gap against a committed schema is higher.

### Open house-rule dimensions

Which invariants are server-enforced: required label families (e.g. exactly one `dept:*`?), priority required or optional, who may create labels (relates to ADR-018), valid status transitions (relates to ADR-017), and an importer/migration tool for the ADR-008 dogfood milestone.

**Resolved:**

- **Status transitions:** Free within the ADR-012 CHECK set. `issue_move` accepts any of the four statuses (`backlog`, `in-progress`, `blocked`, `done`) and permits any-to-any transition; the ADR-012 column CHECK constraint confines the value set. Every move is recorded in `issue_events` (ADR-012). This matches GitHub's reopen-anything model, keeps the lifecycle a convention rather than a hard graph, and precludes nothing (a transition graph can be added later). A server-enforced transition graph is the rejected alternative.
- **Priority:** Required at create time. ADR-012 makes `issues.priority` NOT NULL with a CHECK of `P0 | P1 | P2 | P3`, so `issue_create` requires a `priority` argument confined to that set. This is a server-enforced house rule that is mechanical from ADR-012, not a new choice.
- **Label governance mechanism:** The API server enforces (a) reserved-label-family invariants and (b) label-creation rights, exposed through `issue_label` and `issue_create`. ADR-013 pins the enforcement mechanism; it does not pin the concrete families, their cardinalities, or the creation-rights table. Those specifics are owned by ADR-018 (department label taxonomy, pending) and ADR-021 (candidate departments, pending). Flat labels with no families is not the choice; families exist, their content is deferred. **Forward pointer (COR-T-053, 2026-06-24):** ADR-018 (accepted 2026-06-10) and ADR-021 (accepted 2026-06-08) have since been accepted; read both "(pending)" references above as accepted. See `./ADR-018-department-label-taxonomy.md` and `./ADR-021-candidate-departments.md`.
- **ADR-008 dogfood importer:** A ninth MCP tool, `issue_import`, mirrors ghtask's `task_migrate`. It is idempotent via the `external_ref` unique column from ADR-012 (which carries the `COR-T-NNN` task id), so re-running the import does not duplicate issues. Rationale: the dogfood import (ADR-008) is agent-run, and ADR-004 makes the MCP server the only sanctioned agent path, so the importer must live on the MCP surface; it also exercises the seam end-to-end, which is the dogfood milestone's purpose.
- **Surface evolution:** How the tool surface is versioned as it grows is owned by ADR-019 (MCP contract versioning, pending). ADR-013 names it and stops.
- **Enforcement location:** All house rules are enforced in the HTTP API layer (ADR-010's single enforcement seam); the MCP server calls the API and does not re-implement rules. Consistent with ADR-010.

## Decision

The v1 MCP tool surface comprises nine tools:

| Tool | Purpose |
|---|---|
| `issue_list` | List issues, filterable by status, labels, and assignee |
| `issue_get` | Read one issue in full (metadata, labels, comments, events) |
| `issue_create` | Create an issue; `priority` (P0-P3) required; labels optional |
| `issue_claim` | Set `issues.assignee_id`; mirrors ghtask `task_claim` with its `force` option |
| `issue_move` | Transition status to any of the four ADR-012 CHECK values; records an event |
| `issue_comment` | Append a comment to an issue |
| `issue_label` | Mutate labels within server-enforced families |
| `view_list` | List kanban views stored in the database |
| `issue_import` | Idempotent import of markdown tasks via `external_ref`; the ADR-008 dogfood path |

Status transitions are free within the four-value ADR-012 CHECK set (`backlog`, `in-progress`, `blocked`, `done`); `issue_move` permits any-to-any transition. Every move is recorded in `issue_events`.

Priority is required at `issue_create` time; `issue_create` refuses a call that omits `priority` or supplies a value outside `P0 | P1 | P2 | P3`.

The API server enforces reserved-label-family invariants and label-creation rights; the MCP server stays thin and calls the API per ADR-010. The concrete label families, their cardinalities, and creation-rights rules are owned by ADR-018 and ADR-021.

All house rules are enforced in the HTTP API layer per ADR-010. The MCP server is an authenticated API client and does not duplicate enforcement logic.

## Consequences

1. **ADR-008 dogfood importer.** `issue_import` is on the MCP surface because the import is agent-run and ADR-004 makes the MCP server the only sanctioned agent path. The `external_ref` unique column (ADR-012) makes re-runs idempotent. The importer exercises the full seam end-to-end, which is the dogfood milestone's explicit purpose.

2. **Label-governance boundary.** ADR-013 pins the enforcement mechanism (API-layer, family-aware); it does not pin the concrete `dept:*` family members, their at-most-one cardinality, or who may create labels. Those specifics are owned by ADR-018 (department label taxonomy, pending) and ADR-021 (candidate departments, pending). Until those ADRs resolve, `issue_label` and `issue_create` enforce whatever families the API implements; the tool interface is stable regardless. **Forward pointer (COR-T-053, 2026-06-24):** ADR-018 (accepted 2026-06-10) and ADR-021 (accepted 2026-06-08) have since both resolved; read both "(pending)" references above as accepted. See `./ADR-018-department-label-taxonomy.md` and `./ADR-021-candidate-departments.md`.

3. **ADR-020 claim non-preclusion.** Including `issue_claim` (sets `issues.assignee_id`; mirrors ghtask `task_claim` with its `force` option) does not decide the multi-user concurrency model. Whether claim acts as a lease, and last-write-wins vs optimistic versioning, are owned by ADR-020 (pending). The tool exists; its concurrency semantics are deferred. **Forward pointer:** the identity `issue_claim` resolves `assignee_id` to is now per-agent, not the single shared service user, per ADR-026 (accepted); the tool signature is unchanged. See `./ADR-026-per-agent-mcp-identity.md`.

4. **ADR-019 surface-evolution ownership.** How the tool surface is versioned as it grows (for example, adding epic tools additively per ADR-025) is owned by ADR-019 (MCP contract versioning, pending). ADR-013 names it and stops.

5. **ADR-025 epics (resolved); dropped `issue_link` rationale.** Native epics (parent-child issue grouping) are now resolved by ADR-025 (accepted), which amends ADR-012's schema (a `type` column plus a nullable `parent_id` self-FK) via a later ADR per the ADR-024 precedent, and adds three tools to this surface additively: `epic_create`, `epic_attach`, `epic_detach`. The additive addition leaves the nine-tool table above unchanged (the epic tools live in ADR-025). `issue_link` is deliberately not ported because Corral supports epics natively rather than via the body-convention workaround. See `./ADR-025-native-epics.md`.

6. **Single enforcement seam.** Consistent with ADR-010: house rules live in the API layer only. The MCP server never re-implements house-rule logic. The web client and LLM agents share the same enforcement path.
