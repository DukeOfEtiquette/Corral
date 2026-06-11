# Author the Postgres schema and baseline migration (P2-1) in the database department

## Target

This is web-app work (domain 1, ADR-005): the first domain-1 code in the repo. You are executing task DB-T-001, roadmap milestone P2-1, inside the `database` department. The artifact in scope is the Alembic project at `./app/db/` plus the compose topology at `./app/docker-compose.yml`: a single baseline migration that builds the complete v1 Postgres schema, and the minimal compose services that apply and verify it. Because this is the first web-app code, the web-app conventions weigh heaviest, and the placement you establish here is the seam later web-app departments (backend-api, mcp, frontend) extend.

Every schema decision is already pinned in accepted coordinator ADRs and in the "Decisions resolved by the Orchestrator" section below. You implement those decisions; you do not re-decide them and you do not invent columns the ADRs do not name. The references give you the exact column lists and rationale; cite them by path when you need the authority, but the pinned DDL below is the binding specification for what you build. You make zero design decisions: where a line below offers an implementation choice, it states explicitly that the alternatives are equivalent and the choice is yours only mechanically.

## Decisions resolved by the Orchestrator

**Migration tooling (ADR-014).** Alembic with HAND-WRITTEN migrations. No SQLAlchemy ORM is adopted; autogenerate is OFF. Author the SQL by hand. You may render each object through either `op.execute(...)` with explicit SQL or `op.create_table(...)` with explicit columns; these two Alembic APIs are implementation-equivalent and produce the same schema, so the choice between them is mechanical, not a design decision, and either is accepted. The full v1 schema lands in a SINGLE baseline revision `0001`. `alembic/env.py` reads the database URL from an environment variable (for example `DATABASE_URL`); no credentials are hardcoded (ADR-006: secrets via env only).

**Auth scope is FULL.** The baseline migration `0001` creates the COMPLETE v1 schema in one revision: eleven tables, `users`, `agent_credentials`, `issues`, `labels`, `issue_labels`, `views`, `view_labels`, `issue_comments`, `issue_events`, `invites`, `sessions`. Column definitions come from the ADRs as pinned below; do not add columns the ADRs do not name.

**`users` (ADR-012 minimal + ADR-011 auth delta + ADR-026 discriminator).**
- `id` bigserial primary key
- `display_name` text not null
- `kind` text not null check (kind in ('human','machine'))
- `email` text unique, NULLABLE (null for machine rows; Postgres UNIQUE ignores nulls)
- `password_hash` text, NULLABLE (null for machine rows)
- `created_at` timestamptz not null

The argon2id hashing itself is application-layer (ADR-011); this column only stores the resulting hash.

**`agent_credentials` (ADR-026, a SEPARATE table).**
- `user_id` bigint primary key references users(id)
- `api_key_hash` text not null
- `created_at` timestamptz not null

One credential row per machine user (rotation is a config change plus restart, ADR-026). The API key is stored HASHED at rest (ADR-026 / ADR-011 hashed-at-rest posture); NEVER store a plaintext key. `api_key_hash` lives only here, not on `users`.

**`issues` (ADR-012 DDL + ADR-025 epic columns, folded into the baseline CREATE).** Because this is the first migration there is no separate `ALTER`; the `type` and `parent_id` columns are part of the `CREATE TABLE`.
- `id` bigserial primary key (doubles as the human-facing issue number; no separate counter)
- `title` text not null
- `body` text
- `status` text not null check (status in ('backlog','in-progress','blocked','done'))
- `priority` text not null check (priority in ('P0','P1','P2','P3'))
- `type` text not null default 'task' check (type in ('task','epic'))
- `parent_id` bigint references issues(id) (nullable self-reference)
- `assignee_id` bigint references users(id) (nullable)
- `external_ref` text unique (nullable; carries the COR-T-NNN id for the ADR-008 idempotent dogfood import)
- `created_at` timestamptz not null
- `updated_at` timestamptz not null

**Invariants are API-enforced, not DB-enforced (ADR-025, ADR-010).** The epic invariants (at-most-one parent, children are tasks / parents are epics, epics not nested in v1, `type` backfills to 'task') and the machine-versus-human column invariants are enforced in the HTTP API layer (ADR-010 is the single enforcement seam), NOT in the DDL. Do NOT add triggers, cross-table CHECKs, or any other DB-level enforcement for these. The DDL provides only the columns, the CHECK constraints explicitly named above, and the FKs.

**`labels` / `issue_labels` / `views` / `view_labels` / `issue_comments` / `issue_events` (exactly the ADR-012 DDL blocks).**
- `labels`: id bigserial pk, name text unique not null, color text, description text
- `issue_labels`: issue_id bigint not null references issues(id), label_id bigint not null references labels(id), primary key (issue_id, label_id)
- `views`: id bigserial pk, name text unique not null
- `view_labels`: view_id bigint not null references views(id), label_id bigint not null references labels(id), primary key (view_id, label_id)
- `issue_comments`: id bigserial pk, issue_id bigint not null references issues(id), author_id bigint not null references users(id), body text not null, created_at timestamptz not null
- `issue_events`: id bigserial pk, issue_id bigint not null references issues(id), actor_id bigint not null references users(id), event_type text not null, payload jsonb not null, created_at timestamptz not null

The label taxonomy and reserved families (ADR-018) are NOT modeled in DDL; `labels` is storage only.

**`invites` (ADR-011 invite-token mechanics).**
- `id` bigserial primary key
- `email` text not null
- `token_hash` text not null (HASHED at rest, never plaintext)
- `expires_at` timestamptz not null
- `consumed_at` timestamptz (nullable; null = unconsumed; single-use is enforced API-side on redemption)
- `created_by` bigint references users(id)
- `created_at` timestamptz not null

**`sessions` (ADR-011 server-side session store).**
- `session_id` text primary key, storing the opaque session identifier HASHED at rest (the session id is an equivalent bearer secret to the invite token and API key, so it follows the same ADR-011 hashed-at-rest posture; the server hashes the cookie value to look up the row)
- `user_id` bigint not null references users(id)
- `expires_at` timestamptz not null
- `created_at` timestamptz not null

Revocation is a row delete (ADR-011).

**Column and type conventions.** Every id primary key is `bigserial`. Every timestamp column is `timestamptz not null`. `status` / `priority` / `type` use `text` + `CHECK` (NO native Postgres ENUM types, per ADR-012's explicit choice). All FK references are explicit. `external_ref` UNIQUE applies to non-null values only (standard Postgres null semantics).

**Indexes (pinned exactly).** Create exactly these seven explicit indexes, and no others, beyond the indexes that the PK and UNIQUE constraints create automatically:
- `issues(status)`
- `issues(assignee_id)`
- `issues(parent_id)`
- `issue_labels(label_id)`
- `view_labels(label_id)`
- `issue_comments(issue_id)`
- `issue_events(issue_id)`

This named set IS the complete set: do NOT add any additional index, and do NOT omit any from this list. Name each explicitly-created index `ix_{table}_{column}` (for example `ix_issues_status`, `ix_issue_labels_label_id`). For the PK, FK, UNIQUE, and CHECK constraints, use the database's default generated constraint names; do NOT hand-name those. The index set and the naming convention are both pinned here; no index-set or naming choice is left to you.

**`downgrade()`.** The baseline revision's `downgrade()` drops every object it created, in reverse dependency order (a clean teardown; ADR-014 Consequence 5: the baseline downgrade is a clean drop).

**App skeleton and placement.** The Alembic project lives at `./app/db/`: `alembic.ini`, `alembic/env.py`, `alembic/script.py.mako`, `alembic/versions/0001_<slug>.py`. Introduce `./app/docker-compose.yml` now with a `postgres` service (pin an explicit image, for example `postgres:16`) and a one-shot `migrate` service that runs `alembic upgrade head` against the postgres service. The migrate service needs Alembic plus a Postgres driver (psycopg); provide them via a minimal `./app/db/requirements.txt` (pin current stable versions) and a minimal `./app/db/Dockerfile` (for example `python:3.12-slim`, then `pip install -r requirements.txt`). A future devops department may refactor this compose topology later; this minimal version is non-precluding, and other web-app departments extend the same `./app/docker-compose.yml` when their phases begin.

**Secrets (ADR-006).** No secrets, password hashes, or `.env` contents in any tracked file. `env.py` and compose read credentials from environment variables. Non-secret local-dev defaults for the verification path are acceptable (for example a throwaway `POSTGRES_PASSWORD` for the local compose postgres), but no real or production secret is committed. A committed `./app/db/.env.example` is optional and may document variable NAMES only, no values.

**No seed data.** The migration creates SCHEMA ONLY. No admin user row, no data inserts. Admin seeding (ADR-006 / ADR-014, P2-4) and seed logic are out of scope for this task.

## Deliverables

1. The Alembic project under `./app/db/`: `alembic.ini`, `alembic/env.py` (reads the DB URL from an env var), `alembic/script.py.mako`, and `alembic/versions/0001_<slug>.py`.
2. The baseline migration `0001` building the full eleven-table v1 schema per the pinned DDL above, with `upgrade()` creating all tables, constraints, and indexes, and `downgrade()` dropping them in reverse dependency order.
3. `./app/docker-compose.yml` with a pinned-image `postgres` service and a one-shot `migrate` service running `alembic upgrade head`; plus `./app/db/requirements.txt` and `./app/db/Dockerfile` supporting the migrate service.
4. Verification that the migration applies cleanly against the compose Postgres service, with the evidence named under "Verification" in "Hard rules" captured in your closing report.

## Files in scope

- `./app/db/alembic.ini`
- `./app/db/alembic/env.py`
- `./app/db/alembic/script.py.mako`
- `./app/db/alembic/versions/0001_<slug>.py`
- `./app/db/requirements.txt`
- `./app/db/Dockerfile`
- `./app/db/.env.example` (optional; variable names only)
- `./app/docker-compose.yml`
- `./ai-infrastructure/database/STATUS.md` (wrap-up hygiene only; see "STATUS deltas")

## Files out of scope

Do NOT create or edit:

- Any FastAPI endpoint or backend-api code (P2-2, backend-api department)
- The MCP server (Phase 3)
- Admin seeding or any seed/data inserts (P2-4)
- `./ai-infrastructure/project-manager/STATUS.md` (the Orchestrator-owned coordinator surface; already updated this session)
- Anything under `./ai-infrastructure/database/tasks/` (task transitions are the Orchestrator's job)
- The coordinator ADRs (read-only references)
- The project-manager dashboard's own compose/etl (unrelated AI-infra tooling)

## References

Read these for the exact column lists and rationale; cite them by path in your report where a claim leans on them.

- `./ai-infrastructure/project-manager/decisions/ADR-014-db-migrations-tooling.md`: the accepted Alembic / hand-written / single-baseline tooling this task implements.
- `./ai-infrastructure/project-manager/decisions/ADR-012-issue-label-view-schema.md`: the core-table DDL blocks (issues, labels, issue_labels, views, view_labels, issue_comments, issue_events, minimal users).
- `./ai-infrastructure/project-manager/decisions/ADR-025-native-epics.md`: the `issues.type` and `parent_id` epic columns and their API-enforced invariants.
- `./ai-infrastructure/project-manager/decisions/ADR-011-auth-session-mechanism.md`: the auth-schema delta (users.email/password_hash, invites, sessions) and the hashed-at-rest posture.
- `./ai-infrastructure/project-manager/decisions/ADR-026-per-agent-mcp-identity.md`: machine users via a separate `agent_credentials` table plus the `kind` discriminator on `users`.
- `./ai-infrastructure/database/tasks/in-progress/DB-T-001-postgres-schema.md`: the task this kickoff serves (read for context; do not edit it).

## Related tasks and ADRs

- ADR-014: accepted this session; pins the Alembic / hand-written-migration / single-baseline tooling this task implements.
- ADR-012: the core schema DDL source (tables and the status/priority text+CHECK columns).
- ADR-025: the epic columns (`issues.type`, `parent_id`), folded into the baseline CREATE; invariants are API-enforced.
- ADR-011: the auth schema delta (users.email/password_hash, invites, sessions) and the hashed-at-rest secret posture.
- ADR-026: machine identity via a separate `agent_credentials` table plus a `kind` discriminator on `users`.
- ADR-003: compose is the only supported run/verification path; the migration is verified against a Postgres compose service.
- ADR-006: secrets via env only; no secrets, hashes, or `.env` contents in tracked files.
- ADR-008: the dogfood import is why `issues.external_ref` exists (the idempotent COR-T-NNN anchor).
- ADR-010: the HTTP API is the single invariant-enforcement seam, which is why the epic and machine/human invariants are NOT DB-enforced.
- DB-T-001: the task being executed.

## STATUS deltas

The STATUS hygiene target for this task is REDIRECTED from the coordinator STATUS to the department STATUS. Apply the universal wrap-up STATUS hygiene to `./ai-infrastructure/database/STATUS.md` (the DEPARTMENT STATUS), NOT to `./ai-infrastructure/project-manager/STATUS.md`.

Rationale: DB-T-001 is a database-department task with its own task tree (ADR-031), and the department STATUS is its single source of truth. `WORKER-ROLE.md` names the coordinator STATUS only because it predates per-department trees; this kickoff redirects the hygiene target. The coordinator STATUS is the Orchestrator's surface and is already updated for this task; do not touch it.

Apply exactly these two hygiene steps against the department STATUS (`./ai-infrastructure/database/STATUS.md`):

1. Bump `last_updated` to today's date.
2. Prepend a `recent_updates` entry naming the delivered artifact (the `./app/db` Alembic baseline migration `0001` and the `./app/docker-compose.yml` verification path) and the task (DB-T-001).

No further task-specific STATUS edits. The Orchestrator finalizes the department "Current phase" / "Next step" wording and the roadmap P2-1 milestone transition at close; do not reword those.

## Hard rules

- **Schema only, eleven tables, one revision.** The migration creates exactly the eleven tables named above with exactly the columns, CHECK constraints, FKs, and indexes pinned above. No extra columns, no extra tables, no extra indexes beyond the seven pinned, no native ENUM types, no DB-level enforcement of the API-enforced invariants (no triggers, no cross-table CHECKs), and no data inserts.
- **Hashed-at-rest for every bearer secret.** `password_hash`, `agent_credentials.api_key_hash`, `invites.token_hash`, and `sessions.session_id` store HASHED values only; never persist a plaintext password, key, token, or session id. The hashing itself is application-layer; the columns only store the result.
- **No secrets in tracked files (ADR-006).** `env.py` and compose read credentials from environment variables. A throwaway local-dev `POSTGRES_PASSWORD` for the compose postgres is acceptable as a non-secret local default; no real or production secret is committed. An optional `./app/db/.env.example` documents variable NAMES only.
- **Verification is compose-only (ADR-003).** Verify the baseline migration by applying it against the Postgres compose service via `./app/docker-compose.yml`, NOT a host-installed Postgres. Capture this evidence in the closing report: Alembic output showing revision `0001` applied cleanly, plus a table inventory (for example `psql \dt` or an `information_schema` query) confirming all eleven tables and the named CHECK constraints exist. A clean `alembic downgrade base` then `upgrade head` round-trip is a nice-to-have if cheap, not required.

## Worker pointer

You are the dispatched `worker-agent` (ADR-028). Universal worker conventions (the staging-not-committing rule, the compose-only run policy, the file-edit hygiene, and Agent Discipline) live in `./docs/ai-orchestration/roles/WORKER-ROLE.md` and the global `./CLAUDE.md`; follow them without their being re-emitted here. Write your closing report in the pinned six-section shape to `./.claude/artifacts/handoffs/DB-T-001-KICKOFF-REPORT.md` per `WORKER-ROLE.md`, section "Report shape".
