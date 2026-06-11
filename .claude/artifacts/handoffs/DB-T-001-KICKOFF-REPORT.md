# DB-T-001-KICKOFF-REPORT

Worker: worker-agent (Sonnet), attempt 1
Kickoff: ./.claude/artifacts/handoffs/DB-T-001-KICKOFF.md
Task: DB-T-001 (Postgres schema, P2-1)
Date: 2026-06-11

## Deliverables completed

All four kickoff deliverables shipped:

1. **Alembic project at `./app/db/`** - complete:
   - `./app/db/alembic.ini`: Alembic config; `sqlalchemy.url` is blank (set dynamically in env.py from `DATABASE_URL`)
   - `./app/db/alembic/env.py`: reads `DATABASE_URL` from environment (ADR-006: no credentials hardcoded); `target_metadata = None` (no ORM, no autogenerate, ADR-014)
   - `./app/db/alembic/script.py.mako`: standard Alembic revision template
   - `./app/db/requirements.txt`: `alembic==1.13.3`, `psycopg2-binary==2.9.10`
   - `./app/db/Dockerfile`: `python:3.12-slim`, installs requirements, copies project
   - `./app/db/.env.example`: variable names only (`DATABASE_URL=`), no values (ADR-006)

2. **Baseline migration `0001`** at `./app/db/alembic/versions/0001_baseline_schema.py`:
   - Builds all eleven tables in `upgrade()`: `users`, `agent_credentials`, `issues`, `labels`, `issue_labels`, `views`, `view_labels`, `issue_comments`, `issue_events`, `invites`, `sessions`
   - DDL exactly per kickoff pinned spec (ADR-012, ADR-025, ADR-011, ADR-026)
   - Seven named indexes (`ix_{table}_{col}` convention) created explicitly
   - `downgrade()` drops all tables and indexes in reverse dependency order
   - No native Postgres ENUMs (ADR-012), no DB-level epic invariants or machine/human invariants (ADR-010/ADR-025), no seed data, no triggers or cross-table CHECKs

3. **`./app/docker-compose.yml`**: `postgres:16` service with health check; one-shot `migrate` service built from `./db` context, runs `alembic upgrade head`, depends on postgres healthy

4. **Verification** (compose-only per ADR-003): migration applied cleanly; all eleven tables confirmed via `\dt`; all four CHECK constraints confirmed via `pg_constraint`; all seven named indexes confirmed via `pg_indexes`; downgrade/upgrade round-trip clean. Evidence captured under "Build / verification status" below.

## Decisions made

The kickoff stated zero design decisions remain. One mechanical choice exercised:

- **Alembic API style**: used `op.create_table(...)` with explicit `sa.Column()` arguments throughout (rather than `op.execute(...)` with raw SQL strings). The kickoff named both as implementation-equivalent; `op.create_table` was chosen for readability and because it produces Alembic-introspectable metadata, with no effect on the generated DDL.

## Surprises

- **`./app/` did not exist**: the directory was entirely absent from the repo (this is the first domain-1 code). The kickoff anticipated this ("Because this is the first web-app code") so it is not a conflict; noted here as a state observation.
- **Orphan container warning from Docker**: `docker compose up migrate` emitted a warning about an orphan container `app-app-1` from a prior compose run. This is a pre-existing compose artifact unrelated to this task; it did not affect the migration run or verification. No action taken (out of scope).

## Follow-ups

- **Orphan compose container `app-app-1`**: a stale container from a prior compose session showed up as an orphan warning during verification. The Orchestrator should triage whether to run `docker compose down --remove-orphans` at close or note it as a cleanup item. [triage to orchestrator]
- **`requirements.txt` pinned to current stable (2026-06-11)**: `alembic==1.13.3` and `psycopg2-binary==2.9.10` were the current stable releases at time of authoring. A future devops department pass should confirm or update these pins. [COR-T candidate: devops/dependency hygiene pass]
- **No `.dockerignore` for `./app/db/`**: the Docker build context includes all files under `./app/db/`, which is fine for now but may become relevant when the backend-api department adds more files to `./app/`. A `.dockerignore` is a non-precluding future refinement. [COR-T candidate: devops/dockerfile hygiene]
- **Compose service naming**: the compose project is named `app` (from the directory name). When other departments (backend-api, mcp, frontend) extend `./app/docker-compose.yml`, the service names will share this project namespace. No conflict now; the devops department should document naming conventions when extending compose. [triage to orchestrator]

## Files touched

New files created (all under `./app/`, which is the new web-app domain-1 root):
- `/home/adam/src/corral/app/db/alembic.ini`
- `/home/adam/src/corral/app/db/alembic/env.py`
- `/home/adam/src/corral/app/db/alembic/script.py.mako`
- `/home/adam/src/corral/app/db/alembic/versions/0001_baseline_schema.py`
- `/home/adam/src/corral/app/db/requirements.txt`
- `/home/adam/src/corral/app/db/Dockerfile`
- `/home/adam/src/corral/app/db/.env.example`
- `/home/adam/src/corral/app/docker-compose.yml`

STATUS hygiene (department STATUS only, per kickoff STATUS deltas):
- `/home/adam/src/corral/ai-infrastructure/database/STATUS.md` (prepended one `recent_updates` entry; `last_updated` was already `2026-06-11`)

Report file (dual-channel):
- `/home/adam/src/corral/.claude/artifacts/handoffs/DB-T-001-KICKOFF-REPORT.md`

No commits made (staging-not-committing rule, WORKER-ROLE.md universal conventions).

## Build / verification status

**Verified** via `docker compose` against the compose Postgres service (ADR-003). Evidence:

**Migration apply (upgrade):**
```
migrate-1  | INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
migrate-1  | INFO  [alembic.runtime.migration] Will assume transactional DDL.
migrate-1  | INFO  [alembic.runtime.migration] Running upgrade  -> 0001, Baseline v1 schema: eleven tables
migrate-1 exited with code 0
```

**Table inventory (`\dt`):**
```
              List of relations
 Schema |       Name        | Type  | Owner
--------+-------------------+-------+--------
 public | agent_credentials | table | corral
 public | alembic_version   | table | corral
 public | invites           | table | corral
 public | issue_comments    | table | corral
 public | issue_events      | table | corral
 public | issue_labels      | table | corral
 public | issues            | table | corral
 public | labels            | table | corral
 public | sessions          | table | corral
 public | users             | table | corral
 public | view_labels       | table | corral
 public | views             | table | corral
(12 rows)
```
Eleven application tables + `alembic_version` = 12 rows. All eleven tables present.

**CHECK constraints (`pg_constraint`):**
```
 issues_priority_check | issues   | CHECK ((priority = ANY (ARRAY['P0','P1','P2','P3'])))
 issues_status_check   | issues   | CHECK ((status = ANY (ARRAY['backlog','in-progress','blocked','done'])))
 issues_type_check     | issues   | CHECK ((type = ANY (ARRAY['task','epic'])))
 users_kind_check      | users    | CHECK ((kind = ANY (ARRAY['human','machine'])))
```
All four CHECK constraints present.

**Named indexes (`pg_indexes` WHERE indexname LIKE 'ix_%'):**
```
 ix_issue_comments_issue_id | issue_comments
 ix_issue_events_issue_id   | issue_events
 ix_issue_labels_label_id   | issue_labels
 ix_issues_assignee_id      | issues
 ix_issues_parent_id        | issues
 ix_issues_status           | issues
 ix_view_labels_label_id    | view_labels
(7 rows)
```
All seven named indexes present with correct `ix_{table}_{col}` naming.

**Alembic version table:**
```
 version_num
-------------
 0001
(1 row)
```

**Downgrade/upgrade round-trip (nice-to-have):**
```
INFO  [alembic.runtime.migration] Running downgrade 0001 -> , Baseline v1 schema: eleven tables
INFO  [alembic.runtime.migration] Running upgrade  -> 0001, Baseline v1 schema: eleven tables
```
Both clean (exit code 0).

Compose stack torn down after verification (`docker compose down`).
