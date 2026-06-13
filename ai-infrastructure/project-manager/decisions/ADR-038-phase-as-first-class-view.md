---
schema_version: 1
adr: 38
title: "Phase as a first-class work item: a View entity plus a phase:* label family"
status: "accepted"
date: "2026-06-13"
related_adrs: [1, 8, 12, 17, 18, 25, 36, 37]
supersedes: []
superseded_by: null
---

# ADR-038: Phase as a first-class work item: a View entity plus a phase:* label family

> Accepted 2026-06-13. Revisits the Phase representation that ADR-036 mapped to a bare label and ADR-025 left a level short of the taxonomy. Amends ADR-036's import mapping (Phase: label -> View + phase:* label), amends ADR-018 (adds phase:* as a second reserved family), and amends ADR-012 (view ordering) via this later ADR per the ADR-024 precedent. Resolved alongside ADR-037 (the markdown storage representation), which targets this model.

## Context

ADR-036 pinned the work-item taxonomy as a strict, uniform containment hierarchy: Phase contains Epics, Epic contains Tasks, with uniform rollup and a `>= 2` cardinality convention at each level. But its dogfood import mapping (ADR-008/ADR-025) sent Epic to a first-class issue (`type = epic`) and Phase to a bare label. That is an incoherence: ADR-036 gave Phase *container* semantics (it contains epics, has a derived rollup status, a cardinality minimum, a standalone-versus-contained distinction) while storing it as a *label*, which is a filter, not a container. The containment chain is then implemented by two different mechanisms: a structural edge below the epic (`parent_id`) and a label-match above it.

ADR-025 is the deeper root: it built a flat, one-level parent relation (epic -> task) and explicitly deferred deeper nesting ("epics are not nested in v1"). ADR-036 then made the taxonomy genuinely three-level, leaving the app model one level shallower than the taxonomy it serves.

ADR-037 (markdown storage representation) surfaced the practical cost. Its goal is an importer that is a reader, not an interpreter. If a Phase becomes a markdown file with bottom-up linkage (mirroring `parent_id`) but the app stores Phase as a bare label, the asymmetry removed from inside the markdown reappears at the markdown-to-app seam: epic-file -> issue, phase-file -> label, by different rules. True end-to-end isomorphism requires Phase to be first-class in the app, not just in the markdown.

A design conversation (2026-06-13) worked the alternatives with the operator and selected the View model below.

## Alternatives considered

### Option A: Phase stays a bare label (status quo, ADR-036 import mapping)

Phase is a `phase:N` label string and nothing else; "containment" is a label query, rollup is computed, no entity carries the phase's identity, description, or order.

Rejected: this is the incoherence itself. A label is not a container, has no identity to hang a name/description/order on, and leaves the import asymmetric. It treats Phase as second-class despite the taxonomy declaring it a peer band above Epic.

### Option B: Phase as a first-class issue (a `type = phase` node, or a three-level parent chain)

Extend ADR-025 so a Phase is an issue (or a third level of `parent_id`), giving one uniform structural mechanism for the whole chain.

Rejected: a Phase is not a kanban citizen. The app's primary surface is the board (ADR-015/017, fixed global status columns, no nesting); a phase issue is never claimed, moved by hand, or commented on, and its status is purely derived. An issue that is never directly worked is a smell, and this reopens ADR-025's deliberate no-nesting decision and complicates board rendering for no gain over Option C.

### Option C: Phase as a View entity plus a reserved phase:* label family (selected)

Model a Phase exactly the way a Department is already modeled: a reserved label family for membership (`phase:*`, peer to ADR-018's `dept:*`) plus a first-class View (ADR-012 `views`) for its board (peer to ADR-001's one-board-per-department).

Selected: a View in Corral (ADR-012: `views(id, name)` plus a `view_labels` filter, MCP-addressable per ADR-004) is precisely a named, durable, saved board over the issues carrying its labels. Because views filter only on labels, "Phase as a View" forces a `phase:*` label for the View to filter on, which is the same label-plus-board pattern departments already use. Phase becomes a real, governed entity without becoming an issue: it is a board over its epics, not a card on a board.

## Decision

**Option C selected.** A roadmap Phase is realized in the Corral app as a **View entity plus a reserved `phase:*` label family**, the same first-class treatment a Department receives (`dept:*` family in ADR-018 plus a department-board View in ADR-001).

### Membership

- **A reserved `phase:*` label family** (`phase:<n>`, for example `phase:2`) marks an issue's phase membership, peer to ADR-018's `dept:*` family. This amends ADR-018 item 2 ("`dept:*` only in v1") to add a second reserved family.
- **`phase:*` cardinality is at most one per issue (0 or 1).** An epic belongs to zero or one phase (a standalone epic carries no phase label). Enforced API-side, mirroring the at-most-one of `dept:*` (ADR-018) and `parent_id` (ADR-025).
- **`phase:*` applies to `type = epic` issues only.** A Phase contains only Epics (ADR-036 strict containment), so only epics carry a phase label; a Task is never a direct phase member. A task's phase is transitive through its epic's `parent_id`. This mirrors ADR-025's "only a task may carry `parent_id`, and it may point only to an epic."

### The phase board (View)

- **Each Phase is a `views` row** whose `view_labels` filter is its `phase:<n>` label. The View renders the phase's epics (the issues carrying that label). Tasks are reached through their epic, not shown directly on the phase board, consistent with the epics-only membership above.
- **A phase View introduces no new board column.** It reuses the global status columns (ADR-017's fixed-global-columns leaning, already preserved by ADR-025 for epics); it only filters which epics appear. ADR-017's leaning is untouched.

### Phase order is first-class

- **A Phase carries an explicit order** so the app and the post-Phase-7 dashboard read phase sequence from the data rather than reconstructing it. The carrier is an ordering attribute on the phase View (illustrative DDL below). Exact DDL is deferred to implementation (the ADR-014 migration tooling, the ADR-026 precedent of deferring exact DDL).

### Schema amendment (amends ADR-012 via this later ADR, per the ADR-024 precedent)

The `views` table gains a nullable ordering column; the DDL is illustrative, consistent with ADR-012's decision-record framing:

```sql
alter table views
  add column position int;   -- ordering for sequenced views (phases); null for unordered views
```

No `labels`-table change is needed: `phase:*` is a reserved-family naming rule enforced by the API layer (ADR-010 seam), exactly like `dept:*`, not a new column. Whether phase Views are distinguished from other views by a dedicated marker column or by the presence of a `phase:*` filter label is an implementation detail deferred to the migration.

### Rollup and cardinality (unchanged from ADR-036)

Phase status rolls up over the epics carrying its `phase:*` label (done when all its epics are done; planned when none are started; in-progress otherwise). The `>= 2` epics-per-phase minimum stays a project convention enforced by discipline and a dashboard check, not by schema, exactly as ADR-036 set it. This ADR changes the *mechanism* by which a Phase is represented, not the *semantics* ADR-036 pinned.

### Dogfood import mapping (amends ADR-036 / ADR-008)

At import, a Phase becomes a View (named after the phase, carrying its order) plus its reserved `phase:<n>` label, and each epic in that phase carries the `phase:<n>` label. This refines ADR-036's "Phase -> label" row to "Phase -> View + reserved phase:* label." The importer stays a reader: it creates a view and a label and tags epics, all from data already present in the markdown phase and epic files (ADR-037).

## Consequences

1. **The container-semantics / view-representation incoherence is resolved.** Phase is now honestly a board (a View) over its epics, governed like a department, rather than a container pretending to be a label. The taxonomy's Phase-contains-Epics relation is realized as view-membership (the phase label), not a structural parent edge, and that is stated rather than hidden.

2. **Phase is first-class without being a kanban citizen.** It gains identity, a name, a description, and an order (a View row), and yields a board per phase for free via the existing multi-view mechanism (ADR-001), while never appearing as a never-worked issue card (Option B's smell is avoided).

3. **Amends ADR-018.** `phase:*` becomes a second reserved label family (at-most-one, epic-only, API-enforced) alongside `dept:*`. A forward-pointer note is added to ADR-018; its item 2 "`dept:*` only in v1" is superseded by this addition.

4. **Amends ADR-012.** The `views` table gains a nullable ordering column for sequenced (phase) views. A forward-pointer note is added to ADR-012, consistent with its existing ADR-025 / ADR-026 forward pointers; the ADR-012 DDL block stays as authored.

5. **Amends ADR-036's import mapping.** "Phase -> label" becomes "Phase -> View + reserved phase:* label." Forward-pointer notes are added to ADR-036 and to ADR-008 (whose ADR-036 forward-pointer note said "Phases become labels"). The taxonomy and rollup semantics in ADR-036 are unchanged.

6. **ADR-025 and ADR-017 unchanged.** Phase is orthogonal to the epic/task `parent_id` chain (it rides a label, not the parent relation), so ADR-025's flat one-level model stands; and a phase View reuses the global status columns, so ADR-017's fixed-columns leaning is preserved. Light forward-pointer notes are added to both.

7. **Departments and Phases now share one model.** Both are cross-cutting bands realized as a reserved label family plus a View. This is a deliberate uniformity: the same governance, enforcement, and board mechanism serves both, and the dashboard can treat them with shared machinery.

8. **Schema realization is deferred to the relevant build, not done now.** The `views` ordering column and the `phase:*` family enforcement land in a migration when the dogfood import / phase support is built (roadmap Phase 5, and the Phase 7 dashboard repoint), the same way ADR-025's schema amendment was recorded here and implemented later by DB-T-001. No migration is written by this ADR; the dogfood-import epic references this ADR when it is scoped.

9. **ADR-037 targets this model.** The markdown phase file imports to a View; the markdown epic file's `phase:` field imports to a `phase:<n>` label on the epic issue. The two ADRs together make the markdown representation isomorphic to the app end to end.
