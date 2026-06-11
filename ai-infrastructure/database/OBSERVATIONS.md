# Observations

Append-only log of recurring patterns, friction points, and notable one-offs seen while working in the `Database` department. Convention inherited from the coordinator workspace (see `ai-infrastructure/project-manager/OBSERVATIONS.md`).

## Conventions

- Stable IDs: `DB-NN`, monotonically increasing, never reused.
- Lifecycle: **seen-once** (handled ad hoc, not yet logged) -> **logged** (an entry below, with context) -> **promoted** (canonicalized into a rule, template, role doc, or ADR; the entry records where it went).
- Entries are never edited after the fact except to update their lifecycle state and promotion pointer.

## Entry format

```markdown
### DB-NN: short title
- date: YYYY-MM-DD
- state: logged | promoted -> <where>
- context: what happened, where
- pattern: why this might recur / what to do about it
```

## Log

(No entries yet. Add the first observation when a pattern is worth logging.)
