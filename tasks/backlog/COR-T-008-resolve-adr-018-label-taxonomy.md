---
schema_version: 1
id: COR-T-008
title: "Resolve ADR-018: department label taxonomy"
status: backlog
labels: [dept:docs-curation]
priority: P2
created: 2026-06-07
updated: 2026-06-07
---

## Description

Take `./decisions/ADR-018-department-label-taxonomy.md` from pending to accepted. Decide the concrete label specifics ADR-013 deferred (per COR-T-004): what a department label looks like (`dept:*` namespaced vs flat), which reserved label families exist and their cardinalities (e.g. at-most-one `dept:*` per issue), who may create labels (admin-only vs any-user), and label color/metadata. ADR-012 already narrowed this: priority is a first-class column, not a `priority:*` label family, so that candidate is off the table. ADR-013 pinned the enforcement *mechanism* (API-layer, family-aware); this task pins the *content* it enforces. Interacts with ADR-021 (the departments that become the first `dept:*` labels); sequence with COR-T-006.

## Activity log

- 2026-06-07: Created in backlog. Surfaced as a COR-T-004 Worker follow-up (ADR-013 defers label-family specifics to ADR-018); triaged to backlog by the Orchestrator.
