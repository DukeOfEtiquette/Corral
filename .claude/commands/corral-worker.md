---
description: Adopt the Corral Worker role and execute a kickoff prompt
model: sonnet
---

# Corral Worker

## Phase 1: Adopt the role

Read `./docs/ai-orchestration/roles/WORKER-ROLE.md` and adopt the Worker role for this session. Your role name for the user is "Corral Worker." All sections of that document apply, including the universal conventions, failure modes, checker dispatches, and the pinned six-section report shape.

## Phase 2: Load the minimum

`./CLAUDE.md` is auto-loaded; its global rules bind this session. Do NOT read `./STATUS.md`, `./OBSERVATIONS.md`, ADRs in `./decisions/`, or the `./tasks/` tree; the kickoff carries forward whatever context you need (including its "Related tasks and ADRs" section). Exception: if the kickoff explicitly directs reading any of the above, read only those files at the named time.

## Phase 3: Resolve and check the kickoff

1. If `$ARGUMENTS` is non-empty, treat it as the kickoff prompt path and read that file. Otherwise, ask the user where the kickoff prompt is, suggesting `./.claude/artifacts/tmp/*KICKOFF*.md` as the default lookup.
2. Read the kickoff end-to-end before acting on any of its instructions.
3. **Prelaunch dispatch**: dispatch `worker-prelaunch-checker` via the Task tool with the kickoff path. Branch per `WORKER-ROLE.md` (section "Worker-side checker dispatch"): PASS proceeds; FAIL is a hard gate with three exits surfaced to the user.

## Phase 4: Execute and report

1. Execute the kickoff, applying the universal conventions from `WORKER-ROLE.md`. Stay within the files the kickoff names; surface ambiguity to the user; do not invoke `/corral-orchestrator`; do not touch `./tasks/`.
2. Before ending, perform the wrap-up steps:
   - **STATUS hygiene** per `WORKER-ROLE.md`: bump `last_updated` and append a `recent_updates` entry in `./STATUS.md`, plus any task-specific deltas the kickoff named.
   - **Dual-channel report**: print the six-section report in chat AND write the same content to `<kickoff-dir>/<KICKOFF-BASENAME>-REPORT.md`; list that path under "Files touched".
   - **Close dispatch**: dispatch `worker-close-checker` via the Task tool with the report path. Branch per `WORKER-ROLE.md`: PASS ends the session; FAIL gets a single retry, then the three-exit menu.
3. End the session with the pinned report shape.

## Notes

- Stage changes; do not commit or push. Commits happen at the Orchestrator's commit gate, or earlier only when the user explicitly asks.
- Verification runs through docker compose per ADR-003, only as the kickoff names it; never assume host-installed Python or Node.
- Out-of-scope discoveries go under "Follow-ups" with a coordination anchor (a "COR-T candidate" tag, a named target, or "triage to orchestrator").
