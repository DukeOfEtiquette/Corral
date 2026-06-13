---
schema_version: 1
id: COR-T-038
title: "Author END-GOAL.md (the destination) and extend the roadmap toward it"
status: done
labels: []
priority: P2
created: 2026-06-12
updated: 2026-06-12
epic: COR-E-005
---

## Description

Capture the project's post-dogfood trajectory. The roadmap (README table + STATUS frontmatter) is the incremental path; a new repo-root `END-GOAL.md` is the final destination. Domain: AI-infrastructure (a domain-2 documentation deliverable). The deliverable portion routes through the dispatched-worker flow; the ADRs and STATUS roadmap frontmatter were orchestrator-direct.

Resolved with the user:

- **Conceptual split.** `END-GOAL.md` = the destination (the portable project-manager plugin end state). The roadmap = the incremental path. The first three post-dogfood goals become roadmap Phases 6-8; the final end state is the END-GOAL.md narrative.
- **END-GOAL.md content.** The reusable plugin end state: install in any project (`~/rogue`, `~/src/wow_ah`, future ones), immediately get `/create-department`, a dashboard that auto-tracks new departments, and a config hook pointing issue-tracking at the remote Corral deploy; no Corral-specific departments travel with it. Closes by pointing at the roadmap as the path that gets there.
- **Seed pending ADRs now** (done, orchestrator-direct): ADR-033 (remote deployment topology, gates Phase 6) and ADR-034 (project-manager plugin extraction boundary, gates Phase 8).
- **Roadmap Phases 6-8** (STATUS frontmatter done, orchestrator-direct; README table is the executor's job): Phase 6 Remote deployment & concurrency, Phase 7 Repoint ai-infrastructure at the remote, Phase 8 Extract the project-manager plugin.
- **CLAUDE.md is more than a pointer.** Its "Documentation placement" rule enumerates the sanctioned repo-root `.md` files (`CLAUDE.md`, `README.md`); END-GOAL.md must be ADDED to that enumeration so the new file is compliant with the rule it sits beside, plus a north-star pointer.

Orchestrator-direct portion (DONE before dispatch): ADR-033 + ADR-034 seeded as pending; STATUS.md roadmap frontmatter extended with Phases 6-8; this task filed; STATUS hygiene entry added.

Dispatched-worker deliverable (the kickoff): create `END-GOAL.md`; extend the README.md roadmap table with Phases 6-8 + an END-GOAL.md pointer; edit CLAUDE.md (add END-GOAL.md to the sanctioned-root-files enumeration + a north-star pointer).

Out of scope: deciding the pending ADRs (they stay pending until their phases); STATUS.md frontmatter (orchestrator-direct, already done); any dashboard/code change; the OBSERVATIONS or decisions trees.

## Activity log

- 2026-06-12: Created and picked up (moved straight to in-progress). Design decisions resolved with the user (END-GOAL = destination, roadmap = path; seed pending ADRs now; extend roadmap to Phases 6-8). Orchestrator-direct portion done: ADR-033 + ADR-034 seeded pending, STATUS roadmap extended with Phases 6-8, STATUS hygiene entry added. Allocated ID 38 (.next-task-id -> 39). Deliverable portion (END-GOAL.md + README + CLAUDE) routes through the dispatched-worker flow next. P2 documentation deliverable. Unlabelled per ADR-031.
- 2026-06-12: Done. Deliverable executed via the dispatched-worker flow (drafter -> checker PASS -> prelaunch PASS -> executor COMPLETED -> close-checker PASS). Orchestrator verify-against-disk caught two fabricated ADR filenames in END-GOAL.md citations (ADR-008/ADR-021, never read by the executor) and corrected them; all 7 END-GOAL.md path links re-verified. User visually confirmed END-GOAL.md. Committed as 68279f2 (END-GOAL.md, README.md, CLAUDE.md, ADR-033, ADR-034, STATUS.md, .next-task-id, the COR-T-038 kickoff/report pair). Moved to done.
