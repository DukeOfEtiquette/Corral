---
schema_version: 1
id: COR-T-036
title: "ADR-032 implementation cascade: rename worker-agent to executor; docs-curation to docs"
status: done
labels: []
priority: P2
created: 2026-06-12
updated: 2026-06-12
---

## Description

Implement ADR-032 (cross-department agent tier, accepted 2026-06-12): the mechanical rename cascade across the live fleet. The ADR pins the decisions; this task carries them into the files. Analog of COR-T-025 (the ADR-031 implementation cascade). Domain: AI-infrastructure. Routes through the dispatched-worker flow.

Already done by the orchestrator (do NOT redo): the ADR-028 forward-pointer note (executor rename) and the ADR-021 forward-pointer note (docs rename) are in place. ADRs are append-only; the accepted ADR-021 menu and ADR-028 Decision text are not edited in place, they carry forward-pointer notes.

Deliverables:

1. **Rename the general executor agent `worker-agent` to `executor`.**
   - `git mv .claude/agents/worker-agent.md .claude/agents/executor.md`; update the frontmatter `name: executor`, the display role name "Executor Agent", and the body (self-references, bootstrap reads pointing at the renamed spec and role doc).
   - `git mv docs/ai-orchestration/roles/WORKER-ROLE.md docs/ai-orchestration/roles/EXECUTOR-ROLE.md`; retitle "Worker Role" to "Executor Role" and rewrite the role identity throughout ("the Worker" becomes "the Executor"). State that "execute" means "carry out the kickoff's deliverables", not strictly code (per ADR-032's executor-over-implementer rationale).
   - `git mv .claude/agents/specs/WORKER-AGENT-SPEC.md .claude/agents/specs/EXECUTOR-AGENT-SPEC.md`; update title, self-references, and the role-doc pointer.

2. **Update every cross-reference to the renamed agent, role doc, and spec.** Sweep and repoint, in: `ORCHESTRATOR-ROLE.md` (the Dispatched-worker flow, kickoff drafting convention, and elsewhere it cites the worker / `worker-agent` / `WORKER-ROLE.md`); `TEST-DESIGNER-ROLE.md`, `test-designer.md`, `TEST-DESIGNER-AGENT-SPEC.md` (they cite `worker-agent` / `WORKER-ROLE.md` as the sibling and mirror); the four checker agents and specs; `kickoff-drafter` / `kickoff-checker` and their specs; `docs/README.md` (the role-doc nav row); the `.claude/commands/*-orchestrator.md` commands and `create-department` recipe / templates if they name `worker-agent`; and any `CLAUDE.md` mentions.

3. **Preserve the distinction: the agent renames, the checker names do not.** Per ADR-032, `worker-prelaunch-checker` and `worker-close-checker` KEEP their names (their `worker-` prefix is legacy but not renamed in this cascade). Rename references to the worker AGENT (`worker-agent` -> `executor`, "the Worker" -> "the Executor") but do NOT rename the checker agents or their files. Generic uses of the word "worker" inside checker rule prose that refer to the executor's report become "executor"; the checker agent NAMES stay.

4. **Term sweep: "universal agent" -> "cross-department agent"** in the primary role docs (`ORCHESTRATOR-ROLE.md`, `EXECUTOR-ROLE.md`, `TEST-DESIGNER-ROLE.md`) and the specs where the informal "universal" appears for these agents. ADR-032 holds the canonical definition; reference it.

5. **Rename the `docs-curation` department slug to `docs` in the dashboard roster.** Wherever the dashboard pipeline enumerates the ADR-021 department roster (the `DEPARTMENTS_ROSTER` / roster source in `ai-infrastructure/project-manager/dashboard/etl.py`, and any slug literal in the dashboard views), `docs-curation` becomes `docs`. No department workspace exists to rename (lazy creation); this is a roster-label change only.

Out of scope: authoring the cross-department `docs` review agent (a separate follow-on, authored when wanted, as `test-designer` was COR-T-035); creating the `docs` department (lazy, ADR-021/ADR-027); renaming the `worker-` prefixed checkers (ADR-032 keeps their names for now; a candidate follow-up); editing the accepted ADR-021 menu or ADR-028 Decision text in place (forward pointers already carry the renames).

## Activity log

- 2026-06-12: Created in backlog. Implements ADR-032 (accepted 2026-06-12). P2: a clarity/maintainability rename that should land before the next specialist agent (the docs reviewer) is built, so that agent is authored under the executor/cross-department taxonomy. Not blocking P2-2. Unlabelled per ADR-031.
- 2026-06-12: Picked up; moved to in-progress. Routing through the dispatched-worker flow; enumerating live references and resolving the append-only-history scope boundary before drafting the kickoff.
- 2026-06-12: Done (commit 873001a). Dispatched-worker flow ran clean: kickoff drafted+checked (PASS), prelaunch W1 PASS, executor COMPLETED, close W2/W3 PASS, verify-against-disk clean. 3 git mv renames (worker-agent.md/WORKER-ROLE.md/WORKER-AGENT-SPEC.md to executor/EXECUTOR-ROLE/EXECUTOR-AGENT-SPEC) plus 22 edited files; checker names preserved per ADR-032; bounded universal->cross-department sweep; docs-curation->docs slug in etl.py; append-only history untouched. One anchored follow-up (verify the docs roster slug at docs-department-creation time) left surfaced, not filed as a standalone task.
