---
task: COR-T-036
kickoff: COR-T-036-KICKOFF.md
attempt: 1
completed: "2026-06-12"
---

# COR-T-036 Worker Report: ADR-032 rename cascade

## Deliverables completed

All rename and term-sweep changes from the kickoff have been applied:

1. **Three git mv renames** (history-preserving):
   - `.claude/agents/worker-agent.md` -> `.claude/agents/executor.md`
   - `docs/ai-orchestration/roles/WORKER-ROLE.md` -> `docs/ai-orchestration/roles/EXECUTOR-ROLE.md`
   - `.claude/agents/specs/WORKER-AGENT-SPEC.md` -> `.claude/agents/specs/EXECUTOR-AGENT-SPEC.md`

2. **Three exact-string global replacements** in all in-scope files:
   - `worker-agent` -> `executor`
   - `WORKER-ROLE` -> `EXECUTOR-ROLE`
   - `WORKER-AGENT-SPEC` -> `EXECUTOR-AGENT-SPEC`

3. **Prose role-concept renames** (Worker/worker -> Executor/executor where referring to the agent role):
   - Applied throughout all in-scope files: EXECUTOR-ROLE.md, EXECUTOR-AGENT-SPEC.md, executor.md, ORCHESTRATOR-ROLE.md, test-designer.md, TEST-DESIGNER-ROLE.md, TEST-DESIGNER-AGENT-SPEC.md, kickoff-drafter.md, KICKOFF-DRAFTER-SPEC.md, KICKOFF-CHECKER-SPEC.md, worker-prelaunch-checker.md, WORKER-PRELAUNCH-CHECKER-SPEC.md, worker-close-checker.md, WORKER-CLOSE-CHECKER-SPEC.md, and all orchestrator commands.

4. **Bounded "universal" -> "cross-department" sweep** for agents-as-a-class descriptions:
   - "universal worker" -> "cross-department executor" and "cross-department dispatched" in CLAUDE.md files, EXECUTOR-AGENT-SPEC.md design rationale, TEST-DESIGNER-AGENT-SPEC.md lineage section, TEST-DESIGNER-ROLE.md checker dispatch section.
   - "universal conventions", "universal hygiene", "universal rule W1/W2", "universal kickoff conventions", "universal minimum" left unchanged throughout.

5. **`docs-curation` -> `docs`** in `ai-infrastructure/project-manager/dashboard/etl.py` DEPARTMENTS_ROSTER only.

6. **Checker names preserved**: `worker-prelaunch-checker` and `worker-close-checker` filenames and `name:` frontmatter unchanged. Internal references to the executor/executor role updated within those files.

7. **Append-only trees**: no edits to `.claude/artifacts/handoffs/`, `tasks/`, `OBSERVATIONS.md`, STATUS history, or accepted ADR bodies.

## Decisions made

- The revision history entries in `EXECUTOR-AGENT-SPEC.md` (v1.0 line "Ported from rogue's `worker-agent`" and v2 line "renamed from `WORKER-AGENT-SPEC.md`") were left as-is. These are accurate historical records: one refers to rogue's external agent (still named `worker-agent` there), and one records the source filename of the rename. Neither is a stale live Corral reference.

- `ORCHESTRATOR-ROLE.md` line 127 contains "the Worker knows which conventions weigh heaviest" (the Name-the-domain bullet). This uses "Worker" as a generic noun, not the agent's proper-noun role name, and in context modifies the kickoff-writing convention. Left as prose variation to avoid awkward reads; the surrounding bullets consistently say "Executor."

## Surprises

None. The in-scope file set matched what the kickoff named. No unexpected "worker-agent" references were found in non-append-only files beyond the two historical revision-history entries in EXECUTOR-AGENT-SPEC.md (documented above).

## Follow-ups

- COR-T candidate: once the `docs` department is created (per ADR-032 follow-on), verify the `docs` slug in `etl.py` DEPARTMENTS_ROSTER resolves correctly against the new department's `STATUS.md` path.
- Phase: P2 (low-priority; this is a consistency verification at department-creation time, not blocking anything now).

## Files touched

### Renamed (git mv)
- `/home/adam/src/corral/.claude/agents/executor.md` (was `worker-agent.md`)
- `/home/adam/src/corral/docs/ai-orchestration/roles/EXECUTOR-ROLE.md` (was `WORKER-ROLE.md`)
- `/home/adam/src/corral/.claude/agents/specs/EXECUTOR-AGENT-SPEC.md` (was `WORKER-AGENT-SPEC.md`)

### Edited
- `/home/adam/src/corral/.claude/agents/test-designer.md`
- `/home/adam/src/corral/.claude/agents/worker-prelaunch-checker.md`
- `/home/adam/src/corral/.claude/agents/worker-close-checker.md`
- `/home/adam/src/corral/.claude/agents/kickoff-drafter.md`
- `/home/adam/src/corral/.claude/agents/specs/TEST-DESIGNER-AGENT-SPEC.md`
- `/home/adam/src/corral/.claude/agents/specs/KICKOFF-DRAFTER-SPEC.md`
- `/home/adam/src/corral/.claude/agents/specs/KICKOFF-CHECKER-SPEC.md`
- `/home/adam/src/corral/.claude/agents/specs/WORKER-PRELAUNCH-CHECKER-SPEC.md`
- `/home/adam/src/corral/.claude/agents/specs/WORKER-CLOSE-CHECKER-SPEC.md`
- `/home/adam/src/corral/docs/ai-orchestration/roles/ORCHESTRATOR-ROLE.md`
- `/home/adam/src/corral/docs/ai-orchestration/roles/TEST-DESIGNER-ROLE.md`
- `/home/adam/src/corral/docs/README.md`
- `/home/adam/src/corral/.claude/commands/project-manager-orchestrator.md`
- `/home/adam/src/corral/.claude/commands/backend-api-orchestrator.md`
- `/home/adam/src/corral/.claude/commands/database-orchestrator.md`
- `/home/adam/src/corral/.claude/commands/create-department.md`
- `/home/adam/src/corral/ai-infrastructure/project-manager/CLAUDE.md`
- `/home/adam/src/corral/ai-infrastructure/project-manager/README.md`
- `/home/adam/src/corral/ai-infrastructure/backend-api/CLAUDE.md`
- `/home/adam/src/corral/ai-infrastructure/database/CLAUDE.md`
- `/home/adam/src/corral/ai-infrastructure/project-manager/templates/department/CLAUDE.md`
- `/home/adam/src/corral/ai-infrastructure/project-manager/templates/department/orchestrator-command.md`
- `/home/adam/src/corral/ai-infrastructure/project-manager/dashboard/etl.py`
- `/home/adam/src/corral/ai-infrastructure/project-manager/STATUS.md`

### Report (dual-channel)
- `/home/adam/src/corral/.claude/artifacts/handoffs/COR-T-036-KICKOFF-REPORT.md`

## Build / verification status

**Grep 1: residual `worker-agent` outside append-only trees**

Command: `grep -rn "worker-agent" --include="*.md" --include="*.py" --include="*.json" . | grep -v ".git/" | grep -v ".claude/artifacts/handoffs/" | grep -v "ai-infrastructure/project-manager/decisions/" | grep -v "ai-infrastructure/project-manager/STATUS.md" | grep -v "OBSERVATIONS.md" | grep -v "tasks/"`

Result: one hit -- `EXECUTOR-AGENT-SPEC.md:279` ("Ported from rogue's `worker-agent`"). This refers to rogue's external agent, not Corral's renamed agent, and is an accurate revision-history provenance note. Zero live Corral references.

**Grep 2: residual `WORKER-ROLE` outside append-only trees**

Command: same filter set, term `WORKER-ROLE\b`

Result: zero hits.

**Grep 3: residual `WORKER-AGENT-SPEC` outside append-only trees**

Command: same filter set, term `WORKER-AGENT-SPEC\b`

Result: one hit -- `EXECUTOR-AGENT-SPEC.md:280` ("renamed from `WORKER-AGENT-SPEC.md`"). Accurate historical record of the source filename. Zero live Corral references.

**Grep 4: checker names still present**

Command: `grep -c "worker-prelaunch-checker" .claude/agents/worker-prelaunch-checker.md && grep -c "worker-close-checker" .claude/agents/worker-close-checker.md`

Result: 3 hits each. Both checker files exist and carry their names.

**No em dashes** introduced (writing rule enforced throughout).

**STATUS hygiene applied**: `last_updated` remains "2026-06-12"; one new `recent_updates` entry prepended.
