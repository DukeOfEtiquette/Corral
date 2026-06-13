---
schema_version: 1
id: COR-T-008
title: "Resolve ADR-018: department label taxonomy"
status: done
labels: [dept:docs-curation]
priority: P2
created: 2026-06-07
updated: 2026-06-10
epic: COR-E-002
---

## Description

Take `./decisions/ADR-018-department-label-taxonomy.md` from pending to accepted. Decide the concrete label specifics ADR-013 deferred (per COR-T-004): what a department label looks like (`dept:*` namespaced vs flat), which reserved label families exist and their cardinalities (e.g. at-most-one `dept:*` per issue), who may create labels (admin-only vs any-user), and label color/metadata. ADR-012 already narrowed this: priority is a first-class column, not a `priority:*` label family, so that candidate is off the table. ADR-013 pinned the enforcement *mechanism* (API-layer, family-aware); this task pins the *content* it enforces. Interacts with ADR-021 (the departments that become the first `dept:*` labels); sequence with COR-T-006.

## Activity log

- 2026-06-07: Created in backlog. Surfaced as a COR-T-004 Worker follow-up (ADR-013 defers label-family specifics to ADR-018); triaged to backlog by the Orchestrator.
- 2026-06-10: Executed orchestrator-direct (ADR/STATUS/task-edit coordination surface). Stale-reference sweep over ADR-018's related_adrs (1/12/13/21) plus ADR-025: confirmed priority and status are first-class ADR-012 columns (not label families) and surfaced ADR-021's exactly-one leaning as a contradicted decision. Decisions resolved with the user: dept:* cardinality at-most-one (0 or 1); creation rights admin/auto-sanctioned for dept:* and any-user for free-form; relabel the off-menu dept:ai-infra tasks now. ADR-018 set pending -> accepted; ADR-021 forward-pointer note added; COR-T-007 and COR-T-015 relabeled dept:ai-infra -> dept:agent-development; tasks/README.md label example corrected; STATUS hygiene applied. Deliverable committed as 4d8187f. Moved to done.
