## Deliverables completed

- `app/docker-compose.yml` edited per all five resolved decisions:
  - `postgres` service environment now uses `${POSTGRES_DB:-corral}`, `${POSTGRES_USER:-corral}`, `${POSTGRES_PASSWORD:-devpassword}` (line 4-7 in the updated file).
  - `postgres` healthcheck updated from hardcoded `pg_isready -U corral -d corral` to `pg_isready -U ${POSTGRES_USER:-corral} -d ${POSTGRES_DB:-corral}` (line 9).
  - `migrate` and `api` use `DATABASE_URL: ${DATABASE_URL:-postgresql://${POSTGRES_USER:-corral}:${POSTGRES_PASSWORD:-devpassword}@postgres:5432/${POSTGRES_DB:-corral}}` (external-override form).
  - `test`, `test-roundtrip`, and `api-test` use `DATABASE_URL: postgresql://${POSTGRES_USER:-corral}:${POSTGRES_PASSWORD:-devpassword}@postgres:5432/${POSTGRES_DB:-corral}` (no outer `${DATABASE_URL:-...}` wrapper; test-isolation boundary preserved).
- `app/.env.example` extended with three commented optional-override lines (`#POSTGRES_USER=corral`, `#POSTGRES_PASSWORD=devpassword`, `#POSTGRES_DB=corral`) under the existing "Optional overrides" block (lines 15-17 in the updated file). The existing `#DATABASE_URL=...` line is left in place.

## Decisions made

(none) - The kickoff resolved all anticipated decisions. The executor made no choices that were not pre-pinned.

## Surprises

(none) - Observed state matched the kickoff exactly. All six service blocks in `app/docker-compose.yml` were at the expected shapes; `app/.env.example` had the expected "Optional overrides" block where the three new lines were inserted.

## Follow-ups

(none) - No out-of-scope issues were found during execution. The kickoff's Related tasks section already captures the upstream context (API-T-006, DB-T-005, ADR-006, ADR-003); no new triage items surfaced.

## Files touched

- `app/docker-compose.yml` (commit f42c797, branch `db-t-006`)
- `app/.env.example` (commit f42c797, branch `db-t-006`)
- `.claude/artifacts/handoffs/DB-T-006-KICKOFF-REPORT.md` (this report; committed on `db-t-006`)

## Build / verification status

All three verification checks from the kickoff passed. Verification run via `docker compose -f app/docker-compose.yml config` per ADR-003 from inside the worktree `/home/adam/src/corral/.claude/worktrees/db-t-006`.

**Check 1 - Default render (no overrides):**

Relevant resolved lines from `docker compose -f app/docker-compose.yml config`:

```
  api:
    environment:
      DATABASE_URL: postgresql://corral:devpassword@postgres:5432/corral
  api-test:
    environment:
      DATABASE_URL: postgresql://corral:devpassword@postgres:5432/corral
  migrate:
    environment:
      DATABASE_URL: postgresql://corral:devpassword@postgres:5432/corral
  postgres:
    environment:
      POSTGRES_DB: corral
      POSTGRES_PASSWORD: devpassword
      POSTGRES_USER: corral
    healthcheck:
      test:
        - CMD-SHELL
        - pg_isready -U corral -d corral
  test:
    environment:
      DATABASE_URL: postgresql://corral:devpassword@postgres:5432/corral
  test-roundtrip:
    environment:
      DATABASE_URL: postgresql://corral:devpassword@postgres:5432/corral
```

No interpolation errors. All services resolve to `postgresql://corral:devpassword@postgres:5432/corral`. PASS.

**Check 2 - Sync-by-construction (`POSTGRES_PASSWORD=overridden`):**

```
grep output (DATABASE_URL and POSTGRES_PASSWORD lines):
  DATABASE_URL: postgresql://corral:overridden@postgres:5432/corral  (api)
  DATABASE_URL: postgresql://corral:overridden@postgres:5432/corral  (api-test)
  DATABASE_URL: postgresql://corral:overridden@postgres:5432/corral  (migrate)
  POSTGRES_PASSWORD: overridden
  DATABASE_URL: postgresql://corral:overridden@postgres:5432/corral  (test)
  DATABASE_URL: postgresql://corral:overridden@postgres:5432/corral  (test-roundtrip)
```

`overridden` appears in all five assembled `DATABASE_URL` values AND in `POSTGRES_PASSWORD`. Desync is structurally impossible. PASS.

**Check 3 - Isolation (`DATABASE_URL=postgresql://external/db`):**

```
  api:
    DATABASE_URL: postgresql://external/db
  api-test:
    DATABASE_URL: postgresql://corral:devpassword@postgres:5432/corral
  migrate:
    DATABASE_URL: postgresql://external/db
  test:
    DATABASE_URL: postgresql://corral:devpassword@postgres:5432/corral
  test-roundtrip:
    DATABASE_URL: postgresql://corral:devpassword@postgres:5432/corral
```

`api` and `migrate` pick up the external URL; `api-test`, `test`, and `test-roundtrip` stay on the in-stack postgres. Test-isolation boundary preserved exactly as API-T-006 established. PASS.

No further operator verification steps required beyond what was run above.
