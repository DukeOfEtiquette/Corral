# Decisions

Architectural Decision Records (ADRs) for GHIssuesClone. Append-only.

## Filenames

`ADR-NNN-kebab-case-title.md`, where `NNN` is a monotonically increasing zero-padded integer (`ADR-001`, `ADR-002`, ...). `ADR-000-template.md` is reserved as the starting template and is not a real decision.

## Frontmatter schema

Each ADR begins with YAML frontmatter:

```yaml
---
schema_version: 1
adr: NNN
title: "Short, declarative summary of the decision"
status: "pending"          # pending | draft | proposed | accepted | superseded | rejected
date: "YYYY-MM-DD"          # date of last status change
related_adrs: []            # other ADR numbers this references
supersedes: []              # ADR numbers superseded by this one
superseded_by: null         # ADR number that superseded this one, or null
---
```

## Status values

- `pending`: the decision is queued; the ADR file frames the question but no decision has been made yet. Body sections (Alternatives, Decision, Consequences) are stubs to be filled in when the ADR is taken up. Used for ADRs that exist to reserve a number and capture the question dimensions ahead of authoring.
- `draft`: actively being authored; not yet submitted for review.
- `proposed`: submitted for review; awaiting decision.
- `accepted`: decision is in force.
- `superseded`: replaced by a later ADR. The `superseded_by` field points to the replacement.
- `rejected`: considered and declined. Kept as historical record.

## Body convention

Each ADR body covers:

1. **Context**: what was true when the decision came up; what problem prompted it.
2. **Alternatives considered**: the options on the table, with honest reasoning for why each was or was not selected. Even rejected alternatives belong here.
3. **Decision**: the choice, stated declaratively.
4. **Consequences**: what changes once this decision is in force, including downsides accepted as part of the choice.

## Append-only

ADRs are not deleted, even after they are superseded. A superseded ADR keeps its `accepted` content but flips its `status` to `superseded` and sets `superseded_by` to point to the replacement. The replacement ADR sets `supersedes` to point back. Both stay in the directory.

## Starting point

Copy `./ADR-000-template.md` as `./ADR-NNN-your-title.md`, fill in the frontmatter, and write the body.
