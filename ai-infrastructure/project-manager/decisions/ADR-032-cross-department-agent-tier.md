---
schema_version: 1
adr: 32
title: "Cross-department agent tier: taxonomy, naming, and the agent-feeds-department pattern"
status: "accepted"
date: "2026-06-12"
related_adrs: [16, 21, 23, 28]
supersedes: []
superseded_by: null
---

# ADR-032: Cross-department agent tier: taxonomy, naming, and the agent-feeds-department pattern

## Context

The AI-infrastructure fleet began with a single dispatched execution agent (`worker-agent`, ADR-028) plus the dispatch-loop validators (ADR-023). ADR-016 added `test-designer`, the first specialist execution agent and the first cross-department agent designed to feed a department's backlog (the test-design department, when created). More such agents are anticipated; the next is a documentation reviewer that runs after an executor finishes and files documentation work for a department to pick up.

With the fleet growing past one execution agent, two naming problems compounded:

1. **"Universal" overstates these agents' position.** They were called universal agents, but orchestrators sit above them and dispatch them. They are not above the hierarchy; they are shared across departments below the orchestrator tier. "Universal" reads as a rank these agents do not hold.
2. **"worker-agent" named a category, not a function.** When it was the only execution agent, the category was the function. Next to the function-named `test-designer`, "worker" is undifferentiated: it does not say what the agent does, and every dispatched agent is a "worker" in the loose sense.

This ADR pins the tier taxonomy, the term, the naming of the general executor, the rename of the `docs-curation` department, and the agent-feeds-department pattern, so the ambiguity does not compound as the fleet specializes.

## Alternatives considered

### Naming the general executor: keep `worker-agent`, `implementer`, or `executor`

- **Keep `worker-agent`.** Rejected. It is defensible as "the general one that does the work," but it does not name a function the way the rest of the specializing fleet does, and the asymmetry will worsen as specialists multiply.
- **`implementer`.** Considered. Pairs cleanly with `test-designer` in the TDD flow (designer/implementer). Rejected because it reads as code-only, while the general executor also authors docs, specs, configs, and agent definitions (it authored `test-designer` itself in COR-T-035).
- **`executor` (selected).** Names the function precisely: it executes a kickoff's deliverables, whatever their kind. Its role doc states that "execute" means "carry out the kickoff's deliverables," not strictly code. Chosen by the user over `implementer` for exactly this generality.

### The general-executor-versus-specialist distinction

The `executor` and `test-designer` are not peers. `executor` is the general default: it handles any deliverable no specialist owns. `test-designer` is a specialist: one function carved out of the general scope. The taxonomy records this so future specialists slot in as carve-outs, with the general executor as the fallback, rather than as undifferentiated siblings.

### Department vs cross-department agent: the `docs-curation` case

`docs-curation` on the ADR-021 menu suggested a department that only curates. The intended department owns documentation maintenance, design, and curation as production. Separately, a cross-department documentation reviewer (shared infrastructure, not department-owned) is useful in every executor's close sequence. The two are different things, exactly as `test-designer` (cross-department agent) differs from the test-design department (production owner). Conflating them is the error this ADR removes.

## Decision

### The tier model

Below the human-facing layer, two tiers:

- **Tier 1: Orchestrators.** Per-department coordinators plus the `project-manager` coordinator (ADR-021, ADR-029). They survey, decide, dispatch, and review. They are not dispatched; they are instantiated by their `/<slug>-orchestrator` command.
- **Tier 2: Cross-department agents.** Shared dispatched subagents (the ADR-028 dispatch model) owned by no single department and dispatchable by any orchestrator. Two kinds:
  - **Executors** produce deliverables. The **general executor** (`executor`, formerly `worker-agent`) handles any deliverable no specialist owns. **Specialist executors** own one function: `test-designer` authors tests; a documentation reviewer (future) surfaces documentation work; more may follow.
  - **Validators** are read-only checkers that gate or annotate: `kickoff-checker`, `worker-prelaunch-checker`, `worker-close-checker` (ADR-023).

### Term: "cross-department agent"

"Cross-department agent" is the canonical term for a tier-2 shared agent, replacing the informal "universal agent". These agents are usable across all departments but sit below the orchestrator tier; "cross-department" states that precisely while "universal" implied a rank they do not hold. The canonical definition lives here; role-doc prose adopts it as those docs are touched.

### Naming: `worker-agent` becomes `executor`

The general execution agent is renamed `worker-agent` to `executor`. Its role doc `WORKER-ROLE.md` becomes `EXECUTOR-ROLE.md` and its spec `WORKER-AGENT-SPEC.md` becomes `EXECUTOR-AGENT-SPEC.md`. The dispatched-subagent model is unchanged in substance (leaf node, return-and-re-dispatch escalation, `model` override, foreground); only the agent, role-doc, and spec names change. This amends ADR-028, which named the agent `worker-agent`.

### Rename: `docs-curation` department becomes `docs`

The ADR-021 menu entry `docs-curation` is renamed `docs`, with orchestrator command `/docs-orchestrator`, reflecting that the department owns documentation maintenance, design, and curation as production, not curation alone. This amends the ADR-021 menu. The department remains lazily created (ADR-021/ADR-027); this ADR renames the menu entry, it does not create the department.

### The agent-feeds-department pattern

A cross-department agent (shared infrastructure) can surface work that a department (production) then owns. The worked example is `test-designer` (ADR-016): the agent authors tests across web-app surfaces; the test-design department, when created, owns the sustained test backlog. The documentation reviewer follows the same split: a cross-department documentation-review agent, dispatched in the executor close sequence, diffs an executor's changes, cross-references the affected docs, and files `dept:docs` issues into the `docs` department's backlog; the `docs` department handles them. The agent surfaces; the department produces. The agent can exist before its department does (shared infrastructure first, lazy department later), as `test-designer` does today.

### Scope: what this ADR does not build

- The documentation-review agent is not authored here; it is a follow-on, authored when wanted, as `test-designer` was authored by COR-T-035.
- The `docs` department is not created here (lazy creation, ADR-021/ADR-027).
- The implementation cascade (the `executor` rename across the live fleet, the ADR-021/ADR-028 forward-pointer notes, the term sweep in the primary role docs) is a follow-on task, COR-T-036.

## Consequences

- **ADR-028 amended (executor rename).** `worker-agent` becomes `executor`; `WORKER-ROLE.md` becomes `EXECUTOR-ROLE.md`; `WORKER-AGENT-SPEC.md` becomes `EXECUTOR-AGENT-SPEC.md`. The dispatch mechanics are unchanged. A forward-pointer note is added to ADR-028.

- **ADR-021 amended (docs rename).** The `docs-curation` menu entry becomes `docs` with command `/docs-orchestrator`. A forward-pointer note is added to ADR-021. The other menu entries are unchanged.

- **ADR-016 is the worked precedent.** The agent-feeds-department pattern this ADR generalizes was first instantiated by `test-designer` (ADR-016). The documentation reviewer is the second instance.

- **The "worker-" prefixed checkers keep their names for now.** `worker-prelaunch-checker` and `worker-close-checker` validate every executor (the close checker already validates both `worker-agent` and `test-designer` reports), so their `worker-` prefix is now legacy rather than precise. Renaming them to drop the producer prefix is a candidate follow-up, not decided here, to keep the COR-T-036 cascade bounded.

- **Implementation cascade filed as COR-T-036.** The mechanical rename across `.claude/agents/`, `docs/ai-orchestration/roles/`, `.claude/agents/specs/`, and all cross-references, plus the two forward-pointer notes and the targeted term sweep, is a dispatched-worker task. The general executor renames itself.

- **Future specialists slot in cleanly.** New cross-department agents are added as specialist executors (carve-outs from the general `executor`) or validators, named for their function, dispatched by orchestrators, optionally feeding a department's backlog. The taxonomy gives each new agent a defined place rather than another undifferentiated "worker".
