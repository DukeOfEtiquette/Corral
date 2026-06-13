---
schema_version: 1
id: COR-T-029
title: "Dashboard: derive current_phase and next_step from milestone statuses"
status: done
labels: []
priority: P2
created: 2026-06-11
updated: 2026-06-11
epic: COR-E-004
---

## Description

The project-manager dashboard derives each roadmap phase's CURRENT/UPCOMING/DONE badge from a single hand-maintained `phase` field in `STATUS.md` frontmatter (`etl.py:280`, fed into `derive_roadmap_status`). That field drifted: it stayed `phase: 1` after Phase 2 work began (COR-T-023 departments, DB-T-001 / P2-1), so the live dashboard showed Phase 1 CURRENT and Phase 2 UPCOMING despite all P1 milestones being done and P2-0/P2-1 complete. The `## Next step` prose section has the same class of drift (it is hand-maintained and had already decayed into a self-contradictory paragraph). The per-milestone DONE badges, by contrast, are always correct because they are authored per milestone.

Fix the root cause: make the dashboard derive both the current phase and the next step from the milestone statuses that are already in the data, eliminating the hand-maintained pointers. Directed by the user during the COR-T-028 session after spotting the stale phase badge on the live dashboard.

Coordinator/agent-development presentational-pipeline deliverable; routes through the `/project-manager-orchestrator` dispatched-worker flow. Decisions are pinned in the kickoff (derivation rule, next_step format, removal of the now-dead frontmatter fields and the `## Next step` section). The "Next step panel" design fork was resolved with the user: derive it from milestones.

## Activity log

- 2026-06-11: Created and picked up (directed work; user instruction during the COR-T-028 session). Moved straight to in-progress; routing through the dispatched-worker flow. Decisions resolved with the user: derive current_phase as the lowest not-fully-done phase; derive next_step as the first non-done milestone of the current phase; remove the dead `phase`/`phase_title` frontmatter fields and the `## Next step` prose section from STATUS.md. Unlabelled per ADR-031.
- 2026-06-11: Executed via dispatched worker-agent and closed. Kickoff drafter+checker PASSed on iteration 1 (0 findings); prelaunch W1 PASS, close W2 PASS. etl.py gains derive_current_phase/derive_current_phase_title/derive_next_step; extract_next_step retired; JSON-contract docstring updated; STATUS.md phase/phase_title frontmatter and the ## Next step section removed. Independently verified against disk: coordinator object + meta use the derived values, the only residual fm.get("phase") reads are department entries (which legitimately keep their own field), and the compose-rebuilt data.json shows current_phase=2, badges 0/1 done / 2 current / 3-5 upcoming, next_step "P2-2: FastAPI endpoints with house rules". Derived current_phase_title is the roadmap title "API + DB core" (shorter than the removed phase_title; accepted as the cleaner, consistent form). Visually confirmed by the user. Committed in f59e4eb (deliverable + kickoff/report pair). Follow-up: the PHASE-column dead field and the milestone-status drift surface were surfaced in the close review (filed/logged separately).
