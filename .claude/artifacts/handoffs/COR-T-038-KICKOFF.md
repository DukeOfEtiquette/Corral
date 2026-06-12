# Author END-GOAL.md (the destination) and extend the README roadmap toward it

## Target

This is AI-infrastructure work (domain 2 per `./ai-infrastructure/project-manager/decisions/ADR-005-two-domains-ai-first.md`), task COR-T-038. You author a new repo-root file `./END-GOAL.md` (the project's final destination) and make matching edits to two existing repo-root files (`./README.md` and `./CLAUDE.md`) so the roadmap points at that destination and the new file is compliant with the documentation-placement rule it sits beside. The conceptual split: `./END-GOAL.md` describes the end state; the roadmap (in `./README.md` and `./ai-infrastructure/project-manager/STATUS.md`) is the incremental path that reaches it. The STATUS.md roadmap frontmatter was already extended with Phases 6-8 orchestrator-direct; this task adds the matching README table rows and authors END-GOAL.md.

## Decisions resolved by the Orchestrator

- **Conceptual split (destination vs path).** `./END-GOAL.md` is the project's final destination; the roadmap is the incremental path that reaches it. END-GOAL.md describes the end state, the roadmap phases are the steps. Rationale: the user wants the "where are we going" recorded as a stable narrative separate from the phase-by-phase "how we get there."
- **END-GOAL.md purpose (the question it answers).** It answers: "what do we do after the kanban issue tracker is fully implemented and integrated into this project?", that is, after the dogfood milestone (ADR-008), once the project tracks itself through the app instead of the markdown trees. Source: ADR-008 defines the dogfood boundary END-GOAL describes "after."
- **END-GOAL.md content (the end state).** The end state is a reusable, portable project-manager extracted as a native Claude Code plugin. Installing it in any project yields, out of the box: `/create-department`, a dashboard that auto-tracks newly created departments, and a config hook pointing issue-tracking at a remote Corral deploy. The plugin carries the generic coordinator machinery (the orchestrator role, the dispatch loop, the checker fleet, the cross-department agents, `/create-department` plus the department template, the dashboard) but NONE of the Corral-specific departments (backend-api, database, mcp-server, frontend-ui, devops) nor Corral's own ADRs/tasks. Corral becomes both the app being built and the first consumer of the plugin extracted from it.
- **Motivation to state in END-GOAL.md.** The user runs many projects with various forks of this system (`~/rogue`, `~/src/wow_ah`, future projects); the end goal is one reusable plugin instead of per-project forks. Render this as the motivation, not as a deferred question.
- **END-GOAL.md closing.** It closes by pointing at the roadmap (`./README.md` and `./ai-infrastructure/project-manager/STATUS.md`) as the incremental path, naming Phases 6-8 as the steps that reach the destination.
- **END-GOAL.md cross-references: cite, do not restate.** Cite the roadmap (`./README.md`, `./ai-infrastructure/project-manager/STATUS.md`); ADR-033 (remote deployment topology, pending, gates Phase 6); ADR-034 (plugin extraction boundary, pending, gates Phase 8); ADR-008 (dogfood milestone, the boundary END-GOAL describes "after"); ADR-021 (the candidate-department menu, the departments the plugin excludes); ADR-032 (the cross-department agent tier the plugin carries). Reference these ADRs by their `./ai-infrastructure/project-manager/decisions/`-rooted paths; do not paraphrase their contents into END-GOAL.md.
- **END-GOAL.md is a concise vision/narrative doc, not an exhaustive spec.** Reference ADRs rather than restating them. Rationale: ADR-033 and ADR-034 already carry the open dimensions; END-GOAL.md states the destination and points at them.
- **Path convention.** Use `./`-prefixed repo-root-relative paths exactly as the existing root `./README.md` and `./CLAUDE.md` do. END-GOAL.md is a repo-root file, so `./`-prefixed paths resolve correctly from it.
- **README roadmap table: add three rows** after the existing "**5. Dogfood milestone**" row, mirroring the STATUS Phase 6-8 titles and deliverables, one sentence per cell (the table was intentionally thinned to one sentence per cell in COR-T-021; preserve that style). The three rows are pinned verbatim:
  - `| **6. Remote deployment & concurrency** | Deploy Corral to a remote server and prove multiple concurrent agent sessions work with no errors. |`
  - `| **7. Repoint ai-infrastructure at the remote** | Switch this project's dashboard and task seam from local markdown to the remote Corral deploy. |`
  - `| **8. Extract the project-manager plugin** | Generalize the project-manager into a portable Claude Code plugin and dogfood Corral with it. |`
- **README END-GOAL pointer, touch (a): Repository layout table.** Add a row to the "Repository layout" table for `./END-GOAL.md` with the one-line description "The project's final destination: the portable project-manager plugin end state". Place it as a sensible row in the existing table (the `./CLAUDE.md` row is the natural neighbour, both being repo-root files).
- **README END-GOAL pointer, touch (b): Roadmap lead-in line.** Add a short lead-in line in the "## Roadmap" section stating the roadmap is the incremental path and `./END-GOAL.md` is the destination. This sits alongside the existing live-status pointer line under the heading; it does not replace it.
- **CLAUDE.md amendment (a): sanctioned-root-files enumeration.** The "Documentation placement" rule enumerates the sanctioned repo-root `.md` files as the literal "the repo-root files (`CLAUDE.md`, `README.md`)". Change that enumeration to include `END-GOAL.md` so the new file is compliant with the rule it sits beside. Rationale: a new sanctioned repo-root file must be named in the rule that governs `.md` placement, or it would read as a violation of that rule.
- **CLAUDE.md amendment (b): north-star pointer line.** Add a north-star pointer line near the top of `./CLAUDE.md` naming `./END-GOAL.md` as where the project's end goal is recorded. "Near the top" means in the opening orientation area (the first heading block), not buried in a later section.
- **Do NOT edit STATUS.md frontmatter.** The roadmap frontmatter extension (Phases 6-8) is already done orchestrator-direct. Your only STATUS.md touch is the universal hygiene append (a `recent_updates` entry plus `last_updated` bump) per `./docs/ai-orchestration/roles/EXECUTOR-ROLE.md`.
- **Do NOT decide or edit the pending ADRs.** ADR-033 and ADR-034 are already authored and stay pending; you cite them from END-GOAL.md but do not edit them.

## Deliverables

- NEW `./END-GOAL.md`: the destination narrative as specified in the decisions above (purpose, end-state description, motivation, closing pointer to the roadmap naming Phases 6-8, and the six cited cross-references). Concise vision/narrative doc; no em dashes; `./`-prefixed paths.
- EDIT `./README.md`: add the three roadmap table rows (6, 7, 8) after the "**5. Dogfood milestone**" row, verbatim per the pinned decision; add the two END-GOAL.md pointers (the Repository-layout table row and the Roadmap-section lead-in line).
- EDIT `./CLAUDE.md`: add `END-GOAL.md` to the documentation-placement sanctioned-root-files enumeration; add the north-star pointer line near the top.

## Files in scope

- `./END-GOAL.md` (new)
- `./README.md`
- `./CLAUDE.md`

## Files out of scope

- `./ai-infrastructure/project-manager/STATUS.md` (roadmap frontmatter already extended orchestrator-direct; touch it only for the universal hygiene append, not as a deliverable edit).
- `./ai-infrastructure/project-manager/decisions/ADR-033-remote-deployment-topology.md` and `./ai-infrastructure/project-manager/decisions/ADR-034-project-manager-plugin-extraction-boundary.md` (already authored; do not edit).
- `./ai-infrastructure/project-manager/CLAUDE.md` (the workspace operating file; the documentation-placement rule being amended lives in the repo-root `./CLAUDE.md`, not this workspace one).
- The dashboard, any code, `./ai-infrastructure/project-manager/OBSERVATIONS.md`, and the `./ai-infrastructure/project-manager/tasks/` tree.

## References

- `./docs/ai-orchestration/roles/EXECUTOR-ROLE.md` (the Executor role and the pinned six-section report shape).
- `./README.md` (the current Roadmap table and Repository layout table to extend; preserve the one-sentence-per-cell style from COR-T-021).
- `./CLAUDE.md` (the documentation-placement rule to amend; the writing-style and path conventions that bind this work).
- `./ai-infrastructure/project-manager/STATUS.md` (the authoritative Phase 6-8 titles and deliverables in the roadmap frontmatter, to mirror in the README table).
- `./ai-infrastructure/project-manager/decisions/ADR-033-remote-deployment-topology.md` (cite from END-GOAL.md; gates Phase 6).
- `./ai-infrastructure/project-manager/decisions/ADR-034-project-manager-plugin-extraction-boundary.md` (cite from END-GOAL.md; gates Phase 8).

## Related tasks and ADRs

- ADR-008 - dogfood milestone; the boundary END-GOAL.md describes "after."
- ADR-033 - remote deployment topology (pending); gates Phase 6.
- ADR-034 - project-manager plugin extraction boundary (pending); gates Phase 8.
- ADR-021 - candidate-department menu; the departments the plugin excludes.
- ADR-032 - cross-department agent tier; the agents the plugin carries.
- COR-T-021 - thinned the README roadmap to one sentence per cell; preserve that style in the new rows.

## STATUS deltas

No task-specific STATUS deltas; universal hygiene only. The roadmap frontmatter extension was done orchestrator-direct, the Current phase stays Phase 2, and there are no phase or "Next step" changes. Apply only the universal hygiene to `./ai-infrastructure/project-manager/STATUS.md` (append a `recent_updates` entry naming this task and its deliverables; bump `last_updated`) per `./docs/ai-orchestration/roles/EXECUTOR-ROLE.md`.

## Hard rules

- No em dashes in any file you write or edit (repo writing rule, `./CLAUDE.md`). Use a regular hyphen, comma, colon, or rephrase.
- END-GOAL.md cites the named ADRs and the roadmap; it does not restate their contents. Keep it a concise vision/narrative doc.
- Preserve the one-sentence-per-cell README roadmap style (COR-T-021); the three new rows match that shape.
- Do not edit the STATUS.md roadmap frontmatter or either pending ADR (ADR-033, ADR-034).
- Use `./`-prefixed repo-root-relative paths throughout, matching the existing `./README.md` and `./CLAUDE.md`.

## Executor pointer

You are the dispatched `executor` (ADR-028). Universal executor conventions, the no-em-dash and `./`-path writing rules, the staging-not-committing policy, and the pinned six-section closing report shape live in `./docs/ai-orchestration/roles/EXECUTOR-ROLE.md`; reference them rather than re-deriving them. Write your closing report to the path derived per `EXECUTOR-ROLE.md`, section "Report shape" (the dual-channel write: print the six sections to chat and write the same content to the report file beside this kickoff).
