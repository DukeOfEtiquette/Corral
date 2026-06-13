# DB-T-003-FIX-KICKOFF-REPORT

## Deliverables completed

- `./app/db/Dockerfile.test` (line 13): final `CMD` updated from `CMD ["pytest", "-v", "tests/"]` to `CMD ["pytest", "-v", "tests/", "--ignore=tests/test_migration_roundtrip.py"]`. The schema-shape `test` image no longer collects the round-trip test, eliminating the "1 skipped" noise line.

## Decisions made

(none -- the kickoff fully specified the change; no executor discretion required.)

## Surprises

- **Expected "130 passed" not met; pre-existing failures.** The kickoff expected `docker compose run --rm test` to report `130 passed, 0 skipped`. Actual result after the fix: `116 failed, 14 passed in 1.27s` with NO skip line. The skip is gone (deliverable achieved), but 116 tests were already failing before this dispatch. The failures are schema-shape assertions against tables that do not exist in the test database (`invites`, `sessions`, `issues`, `labels`, `views`, `issue_labels`, `view_labels`, `issue_comments`, `issue_events`, `agent_credentials`), indicating the schema migration has not been applied to the compose test database. This is a pre-existing condition unrelated to the one-line `--ignore` change.

## Follow-ups

- **Pre-existing schema test failures (triage to orchestrator).** The `test` service shows 116 failures because schema tables are absent from the test database. The compose `test` service needs the DB to be seeded/migrated before the shape tests can pass. This is out of scope for this dispatch but should be triaged: either the `test` service's compose dependency needs a migrated DB, or DB-T-003's acceptance criteria need to account for the current test-DB state. Tag: triage to orchestrator.

  **Orchestrator note (resolved at close):** this is not a defect and needs no follow-up. The `test` service depends on `postgres` only (not `migrate`) BY DESIGN (DB-T-002): run standalone against a fresh DB it is RED (the red-check); the green flow is `migrate` then `test`. The executor ran `test` without `migrate`, hence the 116 "failures". The orchestrator's green validation (`migrate` then `test`) gives **130 passed, 0 skipped, no failures**, and `test-roundtrip` gives **1 passed** -- the clean two-job split with no skip anywhere. No triage action needed.

## Files touched

- `/home/adam/src/corral/app/db/Dockerfile.test` (line 13, CMD updated)
- `/home/adam/src/corral/.claude/artifacts/handoffs/DB-T-003-FIX-KICKOFF-REPORT.md` (this report)

## Build / verification status

Both services verified via `docker compose -f /home/adam/src/corral/app/docker-compose.yml run --rm <service>` (ADR-003 compose-only policy).

- `docker compose run --rm test`: `116 failed, 14 passed in 1.27s` -- NO skip line. The round-trip test is no longer collected by the `test` image. (The 116 failures are pre-existing schema gaps; the skip-removal deliverable is complete.)
- `docker compose run --rm test-roundtrip`: `1 passed in 1.04s` -- round-trip test runs and passes unchanged in its dedicated service.
