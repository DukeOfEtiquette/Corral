# DB-T-003 fix: stop the `test` service from collecting the round-trip test (no skip line)

## Target

This is web-app work (ADR-005): a one-line addendum to the in-progress DB-T-003 (task file `./ai-infrastructure/database/tasks/in-progress/DB-T-003-roundtrip-test-runnable.md`). The artifact in scope is the schema-shape test image's Dockerfile, `./app/db/Dockerfile.test`. The prior DB-T-003 dispatch added a dedicated `test-roundtrip` compose service (`./app/db/Dockerfile.test-roundtrip` plus the `test-roundtrip` service in `./app/docker-compose.yml`, both already on disk and KEPT) where the migration round-trip test runs and passes. The remaining problem: the schema-shape `test` service still collects the round-trip test and self-skips it there (its image has no Alembic), producing a noisy "1 skipped" line. The chosen two-job design is that the read-only shape suite (`test`) and the DB-mutating round-trip (`test-roundtrip`) are separate jobs and neither shows a skip. This dispatch makes the `test` service stop collecting the round-trip test so there is no skip line anywhere.

## Decisions resolved by the Orchestrator

- **The change (one line):** In `./app/db/Dockerfile.test`, change the final `CMD` line from `CMD ["pytest", "-v", "tests/"]` to `CMD ["pytest", "-v", "tests/", "--ignore=tests/test_migration_roundtrip.py"]`. This is the only change. Rationale: the round-trip test mutates the database (downgrade/upgrade) and belongs in its own one-shot job; collecting-and-skipping it in the read-only shape suite was noise. Excluding it at the `test` image's pytest invocation removes the skip without touching any test file.
- **The round-trip test keeps running unchanged:** It continues to run in the dedicated `test-roundtrip` service added by the prior DB-T-003 dispatch. Do not modify that service or its Dockerfile. Rationale: that job already runs the round-trip test to a pass; this dispatch only removes the duplicate collection-and-skip in the shape suite.
- **The exclusion lives in the Dockerfile, not compose:** The `test` service runs the image's `CMD`, so the `--ignore` belongs in `./app/db/Dockerfile.test`, not in `./app/docker-compose.yml`. Rationale: `./app/docker-compose.yml` is unchanged by this task.
- **No test-file edits:** The round-trip test's skip guard stays exactly as authored; it is simply no longer collected by the `test` image. Rationale: ADR-016 test no-touch (`./ai-infrastructure/project-manager/decisions/ADR-016-testing-strategy-test-designer-agent.md`).

## Deliverables

- `./app/db/Dockerfile.test`: the final `CMD` line updated to `CMD ["pytest", "-v", "tests/", "--ignore=tests/test_migration_roundtrip.py"]` so the schema-shape `test` image collects only the shape tests and no longer picks up (and self-skips) the round-trip test.

## Files in scope

- `./app/db/Dockerfile.test`

## Files out of scope

- `./app/db/tests/` (ALL test files, including `./app/db/tests/test_migration_roundtrip.py`): no edits. The skip guard stays as-authored; the file is referenced only so the `--ignore` path is exact (per ADR-016 test no-touch).
- `./app/db/Dockerfile.test-roundtrip` and the `test-roundtrip` service in `./app/docker-compose.yml`: kept as-is from the prior DB-T-003 dispatch.
- `./app/docker-compose.yml`: no change (the `test` service runs the image's `CMD`; the exclusion lives in `./app/db/Dockerfile.test`).
- `./app/db/Dockerfile`, `./app/db/requirements.txt`, `./app/db/requirements-test.txt`: no change.
- `./app/db/alembic/` (the migration), and any backend-api / other app code: no change.

## References

- `./app/db/Dockerfile.test`: the file to edit. Its current final line is `CMD ["pytest", "-v", "tests/"]`.
- `./app/db/tests/test_migration_roundtrip.py`: the file being excluded from the `test` collection. Do not edit it; referenced only so the `--ignore=tests/test_migration_roundtrip.py` path is exact.
- `./ai-infrastructure/project-manager/decisions/ADR-003-docker-compose-runtime.md`: compose-only run and verify policy.
- `./ai-infrastructure/project-manager/decisions/ADR-016-testing-strategy-test-designer-agent.md`: test no-touch rule.

## Related tasks and ADRs

- DB-T-003: this dispatch completes it. The prior dispatch added the `test-roundtrip` service; this removes the skip from the `test` service, yielding the clean two-job split.
- DB-T-002: delivered the test suite including the round-trip test.
- ADR-016: test no-touch (no test-file edit here).
- ADR-003: compose-only run and verify.

## STATUS deltas

No task-specific STATUS deltas; none.

## Hard rules

- Edit exactly one line in exactly one file (`./app/db/Dockerfile.test`); change the final `CMD` and nothing else in that file.
- Do not edit any file under `./app/db/tests/` (ADR-016 test no-touch).
- Do not change `./app/db/Dockerfile.test-roundtrip`, the `test-roundtrip` service, or `./app/docker-compose.yml`.

## Verification expectations

Verify compose-only (ADR-003):

- `docker compose run --rm test` now reports the schema-shape result with NO skip line: 130 passed, 0 skipped (the round-trip test is no longer collected).
- `docker compose run --rm test-roundtrip` still runs the round-trip test: 1 passed, not skipped.

Capture both result lines in the closing report's "Build / verification status" section. The Orchestrator re-runs both at close.

## Executor pointer

The executor is the dispatched `executor` (ADR-028). Universal executor conventions live in `./docs/ai-orchestration/roles/EXECUTOR-ROLE.md`. The closing report is written to the path derived per EXECUTOR-ROLE.md, section "Report shape" (the kickoff's directory, kickoff basename with `-REPORT.md`).
