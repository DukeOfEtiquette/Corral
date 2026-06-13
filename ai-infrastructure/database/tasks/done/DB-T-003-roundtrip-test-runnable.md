---
schema_version: 1
id: DB-T-003
title: "Make the migration round-trip test runnable in the compose test harness"
status: done
labels: []
priority: P3
created: 2026-06-13
updated: 2026-06-13
epic: DB-E-001
---

## Description

The schema test suite delivered by DB-T-002 includes `app/db/tests/test_migration_roundtrip.py`, which asserts the ADR-014 clean-drop round-trip (after `alembic downgrade base` none of the eleven tables exist; after `alembic upgrade head` all eleven exist). It currently **self-skips** in the delivered harness: the compose `test` service builds from `app/db/Dockerfile.test`, which deliberately copies only `tests/` and excludes `alembic/`, so the test environment has no Alembic and no migration to run. The migrate image has Alembic but no pytest. As a result, neither service can execute the round-trip pytest test, and it skips in both the test-designer's red check and the orchestrator's green run (1 of 131 tests never actually runs in the suite).

The round-trip **behavior** is already validated (DB-T-001 verified it at delivery, and the DB-T-002 close re-validated it manually via the migrate image: `upgrade head` -> 11 tables, `downgrade base` -> 0, `upgrade head` -> 11). So this is purely about closing the **automated coverage** gap, not a suspected defect.

Make the round-trip test runnable in the compose harness. Pin the approach at pickup; likely options to weigh then: an Alembic-capable test image variant (or job) that has both pytest and the Alembic project/migration available, or a dedicated round-trip compose job. The test file's self-skip guard may need adjusting so it runs (not skips) in whatever environment is provided; if a test-file edit is required, that routes to a `test-designer` dispatch (the executor may not edit test files, ADR-016), otherwise the harness change is a plain executor dispatch. P3, non-blocking.

Out of scope: any change to the schema/migration (DB-T-001, validated) or to the schema-shape test assertions (DB-T-002, all passing); the round-trip behavior itself (already validated).

## Activity log

- 2026-06-13: Done. Harness-only change (no test-file edit; ADR-016 no-touch verified by the close checker W3). Executed in two dispatches through the dispatched-worker flow: (1) added app/db/Dockerfile.test-roundtrip (alembic + pytest + the project) and an additive `test-roundtrip` one-shot compose service that runs the round-trip test; (2) after the user chose the clean two-job split (option B) over a single suite, added --ignore=tests/test_migration_roundtrip.py to the `test` image CMD so the read-only shape service stops collecting (and skipping) the DB-mutating round-trip test. Orchestrator green validation: `test` (migrated) = 130 passed / 0 skipped / 0 failed, `test-roundtrip` = 1 passed -- all 131 tests run, nothing skips anywhere. (The fix executor's report claimed 116 failures; that was it running `test` without `migrate` first, the by-design red state, annotated as resolved in the FIX report.) Completes epic DB-E-001 (DB-T-001 + DB-T-002 + DB-T-003 all done). Deliverable + both kickoff/report pairs + department STATUS committed in 18b895e.
- 2026-06-13: Picked up; moved to in-progress via /database-orchestrator. Orchestrator doing homework (reading the round-trip test's skip guard + DB-state handling and the test harness) to pin the approach and decide the dispatch type (harness-only -> executor; test-file edit -> test-designer per ADR-016).
- 2026-06-13: Created in backlog by the database orchestrator. Surfaced during the DB-T-002 green-validation gate: the round-trip pytest test self-skips because the `test` image excludes `alembic/`, so it is structurally un-runnable in the delivered compose harness. The round-trip behavior was validated manually at the DB-T-002 close (11 -> 0 -> 11). Linked to DB-E-001 (the schema-and-tests epic) as the remaining test-coverage item. P3 polish.
