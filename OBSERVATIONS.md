# Observations

Append-only log of recurring patterns, friction points, and notable one-offs seen while working in this repo. Convention inherited from rogue (ADR-009).

## Conventions

- Stable IDs: `COR-NN`, monotonically increasing, never reused.
- Lifecycle: **seen-once** (handled ad hoc, not yet logged) -> **logged** (an entry below, with context) -> **promoted** (canonicalized into a rule, template, role doc, or ADR; the entry records where it went).
- Entries are never edited after the fact except to update their lifecycle state and promotion pointer.

## Entry format

```markdown
### COR-NN: short title
- date: YYYY-MM-DD
- state: logged | promoted -> <where>
- context: what happened, where
- pattern: why this might recur / what to do about it
```

## Log

(No entries yet.)
