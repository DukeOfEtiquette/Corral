---
schema_version: 1
phase: 0
phase_title: "Bootstrap: docs, decisions, task convention"
last_updated: "2026-06-05"
recent_updates:
  - "2026-06-05: Project renamed from placeholder GHIssuesClone to Corral (ADR-022); ID prefixes GHI-T/GHI-NN renamed to COR-T/COR-NN."
  - "2026-06-05: Phase 0 executed: repo initialized, ADR-001..009 accepted, ADR-010..021 queued pending, task convention seeded with COR-T-001..006 (as GHI-T at the time)."
---

# Status

Single source of truth for current progress. Update at the end of any session that makes progress.

## Current phase

**Phase 0: bootstrap.** The repo contains documentation only: decision records, the task convention, and orientation docs. No application code, no AI-infrastructure code. See `./README.md` for the full roadmap.

## Next step

Begin Phase 1 (AI infrastructure): work the seeded backlog in `./tasks/backlog/`, starting with COR-T-001 (role docs) and the blocking pending ADRs (COR-T-002 through COR-T-005).

## Blocked on

Nothing. All Phase 1 tasks are actionable.
