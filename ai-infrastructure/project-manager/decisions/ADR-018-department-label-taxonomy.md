---
schema_version: 1
adr: 18
title: "Department label taxonomy"
status: "accepted"
date: "2026-06-10"
related_adrs: [1, 8, 12, 13, 21, 25]
supersedes: []
superseded_by: null
---

# ADR-018: Department label taxonomy

> Accepted 2026-06-10 (COR-T-008). Resolves the label-family content ADR-013 deferred; amends ADR-021's exactly-one dept:* leaning to at-most-one.

## Context

The headline use case (ADR-001): one kanban board per department, filtered by a department label. Open: what a department label looks like (`dept:backend` namespaced vs flat names), whether other reserved label families exist (priority? type?), who can create labels (admin only vs any user vs MCP house rules per ADR-013), and label color/metadata. The departments decided in ADR-021 become the first `dept:*` labels at the dogfood milestone.

## Alternatives considered

### Option A: Namespaced families, rogue-style

`dept:*`, `priority:P0..P3`, free-form labels outside reserved families. Server enforces family invariants (e.g. at most one `dept:*`).

**Leaning selected:** matches the conventions the agent fleet already knows.

### Option B: Flat labels, no reserved families

Simplest schema; invariants become convention rather than enforcement, which ADR-004 argues against.

## Decision

Option A (namespaced families, rogue-style), with the specifics below. The shape was already forced by live usage: the markdown task tree, the dashboard ETL prefix-filter (`dashboard/etl.py`), ADR-021, and ADR-013 all assume `dept:*` namespaced labels.

1. **Label shape.** Reserved-family labels are namespaced `<family>:<value>` (e.g. `dept:backend-api`). The colon prefix is the family marker the API recognizes. Free-form labels carry no colon-namespaced family prefix.

2. **Reserved families (v1): `dept:*` only.** `dept:<slug>` is the sole reserved family in v1, with `<slug>` drawn from the ADR-021 roster. Priority and status are NOT label families: ADR-012 makes both first-class columns (`priority` is `P0..P3` NOT NULL; `status` is a CHECK-constrained column), so the `priority:P0..P3` candidate from this ADR's Option A leaning text and any `status:*` family are off the table. Epic/issue-type modeling is deferred to ADR-025 (native epics); if that ADR chooses a label convention over a first-class type, it adds its own reserved family then. This ADR does not pre-decide a `type:*` family.

3. **`dept:*` cardinality: at most one per issue (0 or 1).** An issue belongs to zero or one department. Zero is valid: uncategorized intake and cross-cutting items may sit unlabeled (the ETL prefix-filter already tolerates zero). Two or more `dept:*` on one issue is rejected at the API write path. This amends ADR-021's "exactly one dept:* per task" leaning (ADR-021, "Departments map to filtered boards") to at-most-one; a forward-pointer note is added there. Consequence for the dogfood boards (ADR-008): department boards filter on their `dept:` label; unlabeled issues simply appear on no department board (no mandatory orphan column required).

4. **Free-form labels.** Permitted outside the reserved family, with no cardinality limit. Invariants apply only to reserved families, satisfying ADR-004's enforce-don't-convention stance for the families that carry semantics.

5. **Creation rights.** `dept:*` labels are admin-managed and auto-sanctioned from the ADR-021 roster (the roster is the authority for valid slugs); they are not user-creatable ad hoc, which keeps the department namespace from sprawling outside the blessed menu. Free-form labels may be created by any authenticated user. The API server enforces both rules per the ADR-013 label-governance mechanism (API-layer, family-aware); the MCP server stays thin (ADR-010).

6. **Label color and metadata.** A label carries a name and an optional color (hex). Concrete `dept:*` colors and the rendering palette are deferred to the Kanban UI phase (ADR-015, ADR-017); this ADR fixes only that the storage carries an optional color, consistent with the ADR-012 labels table.

7. **`dept:ai-infra` hygiene.** `ai-infra` is an ADR-005 domain, not a department (ADR-021 deliberately omits it from the menu), so `dept:ai-infra` is invalid taxonomy. The two task files carrying it (COR-T-007, COR-T-015, both done, both agent-tooling work) are relabeled to `dept:agent-development` as part of this task (orchestrator-direct task edits per ADR-021, "ai-infra is a domain, not a department"). No `dept:ai-infra` label remains in the tree.

## Consequences

1. **ADR-013's label-governance mechanism now has content.** The deferred specifics (ADR-013, "Open house-rule dimensions" #2) are pinned: family = `dept:`, cardinality at-most-one, creation rights admin-for-reserved / any-user-for-free-form. The `issue_label` / `issue_create` tool interfaces are unchanged; only the families the API enforces are now defined.

2. **Amends ADR-021.** ADR-021's "exactly one dept:* per task" leaning is superseded by at-most-one; a forward-pointer note is added to ADR-021. ADR-021 remains the authority for the valid `dept:*` slug roster.

3. **Dogfood import (ADR-008).** The importer carries each task's `dept:*` label across as-is; the at-most-one invariant is enforced at the API from the dogfood milestone onward. Tasks with no `dept:*` import unlabeled and appear on no department board.

4. **`dept:ai-infra` retired.** COR-T-007 and COR-T-015 now carry `dept:agent-development`; the orphan bucket the COR-T-014 dashboard work noted is cleared. The dashboard ETL prefix-filter needs no change (it already filters by `dept:` prefix and tolerates zero).

5. **Still deferred.** The concrete `dept:*` color palette and any epic/type family wait on the Kanban UI phase (ADR-015/017) and ADR-025 respectively. Neither blocks Phase 1.
