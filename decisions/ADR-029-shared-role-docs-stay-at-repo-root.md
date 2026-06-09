---
schema_version: 1
adr: 29
title: "Shared AI-orchestration role docs stay at the repo root; only docs/architecture/ moves into project-manager"
status: "accepted"
date: "2026-06-09"
related_adrs: [5, 9, 23, 24, 27, 28]
supersedes: []
superseded_by: null
---

# ADR-029: Shared AI-orchestration role docs stay at the repo root

## Context

ADR-027 decided the AI-infrastructure workspace structure and, in its Decision-section tree, placed the entire `docs/` directory (commented `# ai-orchestration/roles/, architecture/OVERVIEW.md`) inside `ai-infrastructure/project-manager/`. COR-T-012 executes that restructure.

While resolving COR-T-012's anticipated decisions, a conflict surfaced against the rogue exemplar that ADR-009 binds Corral to. In rogue, the orchestration role docs live at the repo root (`~/rogue/docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md` and `WORKER-ROLE.md`); rogue's `ai-workspaces/project-manager/` has no `docs/` directory at all. The role docs are treated as shared infrastructure, exactly like the root `.claude/` tree, because every workspace's orchestrator and worker adopt the same `WORKER-ROLE.md` / `ORCHESTRATOR-ROLE.md`. They are universal, not project-manager-specific.

Corral's own design reinforces this: the dispatched `worker-agent` (ADR-028) is a single, universal, root-level `.claude/` agent that bootstraps by reading `./docs/ai-orchestration/roles/WORKER-ROLE.md`. If the role docs move inside `project-manager/`, this shared agent would have to reach into one workspace's subtree (`./ai-infrastructure/project-manager/docs/...`) for a definition that is meant to apply across all workspaces.

`docs/architecture/OVERVIEW.md`, by contrast, is web-app / product-domain content (ADR-005 domain 1). It is not shared orchestration machinery and belongs with the coordinator's planning material until web-app departments are lazily created (the same interim-home pattern ADR-027 Fork C uses for web-app ADRs).

ADR-027 treated `docs/` as a single unit and so did not distinguish these two cases. This ADR makes that distinction. It is a partial amendment of ADR-027's docs/ placement, in the same spirit ADR-027 itself partially amended ADR-009.

## Alternatives considered

### Option A: Keep `docs/ai-orchestration/` at the repo root; move only `docs/architecture/` into the workspace (selected)

`docs/ai-orchestration/` (the role docs) stays at the repo root as shared infrastructure beside `.claude/`. Only `docs/architecture/OVERVIEW.md` moves into `ai-infrastructure/project-manager/docs/architecture/`. `docs/README.md` (the docs navigation index) stays at the root `docs/` and updates its pointer to the moved OVERVIEW.

**Selected because:** it matches the rogue exemplar (ADR-009), keeps the universal `worker-agent`'s bootstrap path stable and domain-appropriate, and treats shared role machinery the same way ADR-027 already treats `.claude/` (shared, root-level, not moved into a workspace). It still achieves ADR-027's core goal of separating the two domains by relocating the product spec (OVERVIEW.md) out of the shared root.

### Option B: Follow ADR-027's literal tree; move all of `docs/` into the workspace (rejected)

**Rejected because:** it couples the shared, universal role docs to one workspace's subtree, forces the root-level `worker-agent` (and any future department's worker) to bootstrap its role definition from a sibling workspace path, and diverges from the rogue exemplar on a load-bearing point. The only thing it buys is literal conformance to ADR-027's tree, which this ADR amends.

### Option C: Keep all of `docs/` at the root for now (rejected)

**Rejected because:** it leaves the web-app product spec (`architecture/OVERVIEW.md`) mixed into the shared root, which is exactly the two-domain entanglement the restructure exists to remove.

## Decision

During the COR-T-012 restructure:

1. **`docs/ai-orchestration/` stays at the repo root** as shared AI-infrastructure, alongside `.claude/`. The role docs (`ORCHESTRATOR-ROLE.md`, `WORKER-ROLE.md`) are universal across workspaces and are not moved into any single workspace.
2. **`docs/architecture/OVERVIEW.md` moves** into `ai-infrastructure/project-manager/docs/architecture/OVERVIEW.md` (the coordinator's interim home for web-app planning material, per the ADR-027 Fork C pattern).
3. **`docs/README.md` stays** at the root `docs/` and updates its navigation pointer to the moved OVERVIEW.
4. **The universal `worker-agent` and the other root `.claude/` agents keep referencing the role docs at their stable root path** (`./docs/ai-orchestration/roles/...`); no rewrite of those bootstrap paths is needed.

This amends ADR-027's Decision-section tree (which placed all of `docs/` under `project-manager/`). Per the partial-amendment convention (ADR-027's own treatment of ADR-009, and ADR-024's precedent), the `supersedes` / `superseded_by` frontmatter fields are left untouched; ADR-027 is listed in `related_adrs` and gains a forward-pointer Status note. ADR-027's other four forks and all its other decisions are unaffected.

## Consequences

- **Two `docs/` locations after the restructure.** Root `docs/` holds `ai-orchestration/` (shared role docs) and `README.md`; `ai-infrastructure/project-manager/docs/` holds `architecture/OVERVIEW.md`. This is intentional: shared orchestration machinery at root, domain planning material in the coordinator workspace.
- **Path conventions.** Root-level `.claude/` files and the thin root `CLAUDE.md` continue to reference the role docs as `./docs/ai-orchestration/roles/...` (repo-root-relative; unchanged). References to the moved OVERVIEW become `./ai-infrastructure/project-manager/docs/architecture/OVERVIEW.md` from root-level files, or workspace-relative `./docs/architecture/OVERVIEW.md` from within `project-manager/`.
- **ADR-027 partial amendment.** ADR-027 remains `accepted` and is not edited beyond a forward-pointer Status note. Readers of ADR-027's tree should read this ADR for the docs/ placement.
- **Future departments.** When the create-department recipe (COR-T-013) lands, a new department's orchestrator/worker reuse the root-level shared role docs by reference, with no per-workspace copy. This ADR makes that the deliberate model.
- **OVERVIEW.md migrates again later.** When a web-app department is lazily created, `OVERVIEW.md` may migrate from the coordinator into that department, mirroring the ADR-027 Fork C web-app-ADR migration. That is deferred, not handled here.
