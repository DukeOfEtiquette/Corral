# DB-T-006 - unify DATABASE_URL and postgres credentials across compose services from app/.env

## Target

This is web-app work (domain 1, ADR-005): a change to the `app/` stack's compose definition, directed by the Database department (domain 2). The artifacts in scope are the web-app stack's compose definition `app/docker-compose.yml` and its environment template `app/.env.example`; the web-app stack conventions weigh heaviest here, notably the compose-only run policy (ADR-003). Task DB-T-006. Today the `postgres` service credentials and every service's `DATABASE_URL` are independently hardcoded; a change to one can silently desync from the others and break connectivity. This task introduces shared constituent `POSTGRES_*` variables as the single source of truth and assembles every `DATABASE_URL` in-string from them, so the credentials and the connection strings stay in sync by construction.

## Decisions resolved by the Orchestrator

- **Config model: drive constituent `POSTGRES_*` vars, assemble `DATABASE_URL` in-string from them.** Introduce `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` as the single source of truth, each with a compose `${VAR:-default}` dev default (`corral`, `devpassword`, `corral` respectively). Every service's `DATABASE_URL` is assembled in-string from those same three vars, so the `postgres` service credentials and every connection string stay in sync by construction (a desync is structurally impossible). The task's stated failure mode is a `POSTGRES_*` vs `DATABASE_URL` desync breaking connectivity; assembling from shared constituents eliminates it. Compose interpolation supports in-string assembly: `postgresql://${POSTGRES_USER:-corral}:${POSTGRES_PASSWORD:-devpassword}@postgres:5432/${POSTGRES_DB:-corral}`.
- **Host and port stay fixed at `postgres:5432`.** These are the compose-internal service address, not credentials; they are NOT parameterized.
- **Override policy: `migrate` and `api` honor a top-level external `${DATABASE_URL}` override; the three test services do NOT.** `migrate` and `api` use `DATABASE_URL: ${DATABASE_URL:-postgresql://${POSTGRES_USER:-corral}:${POSTGRES_PASSWORD:-devpassword}@postgres:5432/${POSTGRES_DB:-corral}}` so an operator can point the running app (and its migrations) at an external DB via a single `DATABASE_URL` in `app/.env`. The `test`, `test-roundtrip`, and `api-test` services use the assembled form WITHOUT the outer `${DATABASE_URL:-...}` wrapper: `DATABASE_URL: postgresql://${POSTGRES_USER:-corral}:${POSTGRES_PASSWORD:-devpassword}@postgres:5432/${POSTGRES_DB:-corral}`, so they always target the in-stack `postgres` even if `DATABASE_URL` is set in `app/.env`. This preserves the test-isolation intent API-T-006 established when it deliberately pinned `api-test` (a `docker compose run test` must never accidentally hit a non-stack DB).
- **The `postgres` service and its healthcheck both read the constituent vars.** The `postgres` service `environment` block sets `POSTGRES_DB: ${POSTGRES_DB:-corral}`, `POSTGRES_USER: ${POSTGRES_USER:-corral}`, `POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-devpassword}`. The healthcheck currently hardcodes `pg_isready -U corral -d corral`; update it to `pg_isready -U ${POSTGRES_USER:-corral} -d ${POSTGRES_DB:-corral}` so a credential override keeps the healthcheck valid.
- **`api` service: only its `DATABASE_URL` default changes.** The `api` service already reads `DATABASE_URL: ${DATABASE_URL:-postgresql://corral:devpassword@postgres:5432/corral}` (wired by API-T-006). Change ONLY its inline default to the assembled form so the default stays in sync with the postgres creds; leave its `ADMIN_EMAIL`, `ADMIN_PASSWORD_HASH`, `API_DOCS_ENABLED`, `SESSION_*`, `ports`, `healthcheck`, and `depends_on` exactly as they are (settled by API-T-006).
- **`app/.env.example`: add the three new vars as commented optional overrides.** Under the existing "Optional overrides" block, add commented lines `#POSTGRES_USER=corral`, `#POSTGRES_PASSWORD=devpassword`, `#POSTGRES_DB=corral` showing the dev defaults, consistent with the existing commented-override style in that file. Do not uncomment them (they are optional overrides, not required values). Leave the existing `#DATABASE_URL=...` line in place (it remains a valid external override for `api`/`migrate`).

## Deliverables

- `app/docker-compose.yml` edited so that:
  - the `postgres` service drives `POSTGRES_DB` / `POSTGRES_USER` / `POSTGRES_PASSWORD` from `${VAR:-default}`, and its healthcheck uses the `POSTGRES_USER` / `POSTGRES_DB` vars;
  - `migrate` and `api` use `DATABASE_URL: ${DATABASE_URL:-<assembled>}` (the external-override form);
  - `test`, `test-roundtrip`, and `api-test` use the assembled `DATABASE_URL` with no external `${DATABASE_URL}` override;
  - every assembled URL is `postgresql://${POSTGRES_USER:-corral}:${POSTGRES_PASSWORD:-devpassword}@postgres:5432/${POSTGRES_DB:-corral}`.
- `app/.env.example` extended with the three commented `#POSTGRES_USER=corral` / `#POSTGRES_PASSWORD=devpassword` / `#POSTGRES_DB=corral` optional-override lines under the existing "Optional overrides" block.

## Files in scope

- `app/docker-compose.yml`
- `app/.env.example`

## Files out of scope

- `app/api/**` (the api image, source, and the `api` service's non-`DATABASE_URL` env were settled by API-T-006; do not touch).
- `app/db/**` (the db image and migration logic are unchanged).
- Any service block field other than the env / healthcheck lines named above; do not alter `build`, `depends_on`, `command`, `working_dir`, `ports`, or service ordering.

## References

- `app/docker-compose.yml` (target: the `postgres` / `migrate` / `test` / `test-roundtrip` / `api` / `api-test` services).
- `app/.env.example` (target: the consolidated env template; add the three commented override lines here).
- `ai-infrastructure/backend-api/tasks/done/API-T-006-api-devex-hardening.md` (origin of the `api`-service `DATABASE_URL` wiring this task completes for the DB-owned services; the source of the `api-test` test-isolation pin).
- `ai-infrastructure/project-manager/decisions/ADR-006-admin-bootstrap-env-hash.md` (deployment secrets live in gitignored `.env` files only; the new `POSTGRES_*` defaults are dev-only, real creds go in `app/.env`).
- `ai-infrastructure/project-manager/decisions/ADR-003-docker-compose-runtime.md` (docker compose is the only sanctioned run path; the verification commands below run through `docker compose`).

## Related tasks and ADRs

- `API-T-006` - origin task; wired the `api` service's `DATABASE_URL` from `app/.env` and deliberately deferred the DB-owned services and pinned `api-test` for test isolation. This task completes that deferral.
- `DB-T-005` - recent DB compose change (made the `test` service depend on `migrate`); context for the current compose service shape.
- `ADR-006` - deployment secrets live in gitignored `.env` files only; the new `POSTGRES_*` vars follow this (defaults are dev-only, real creds go in `app/.env`).
- `ADR-003` - docker compose is the sanctioned runtime and verification path.

## Hard rules

- Change only the env and healthcheck lines named in the resolved decisions. Do not touch any other field of any service block, and do not reorder services.
- Host and port are fixed literals `postgres:5432` in every assembled URL; do not parameterize them.
- The three test services (`test`, `test-roundtrip`, `api-test`) must NOT carry the outer `${DATABASE_URL:-...}` wrapper; only `migrate` and `api` do. This is the test-isolation boundary; preserve it exactly.
- The `POSTGRES_*` defaults are dev-only values that belong in compose interpolation defaults and a commented `.env.example`; do not write real credentials into either tracked file (ADR-006).

## Verification expectations

Run verification through `docker compose` per ADR-003 and quote the rendered evidence in the report's "Build / verification status" section.

- **Default render.** `docker compose -f app/docker-compose.yml config` renders with no interpolation error. With no `app/.env` present (or no overrides set), every service's resolved `DATABASE_URL` equals `postgresql://corral:devpassword@postgres:5432/corral`, and the `postgres` service resolves `POSTGRES_USER=corral`, `POSTGRES_PASSWORD=devpassword`, `POSTGRES_DB=corral`. Quote the relevant rendered lines as evidence.
- **Sync-by-construction.** Render with a throwaway override, for example `POSTGRES_PASSWORD=overridden docker compose -f app/docker-compose.yml config`, and confirm the override appears BOTH in the `postgres` service `POSTGRES_PASSWORD` AND in every assembled `DATABASE_URL`, demonstrating they cannot desync. Quote the evidence.
- **Isolation.** Render with `DATABASE_URL=postgresql://external/db docker compose -f app/docker-compose.yml config` and confirm `migrate` and `api` pick up the external value while `test`, `test-roundtrip`, and `api-test` still resolve to the in-stack `postgresql://corral:devpassword@postgres:5432/corral`. Quote the evidence.

## Executor pointer

The executor is the dispatched `executor` (ADR-028). Universal executor conventions (run policy, git boundaries, file-edit hygiene, the pinned six-section report shape, dual-channel report write) live in `./docs/ai-orchestration/roles/EXECUTOR-ROLE.md`; follow them rather than re-deriving them here. Write the closing report to `./.claude/artifacts/handoffs/DB-T-006-KICKOFF-REPORT.md` per EXECUTOR-ROLE.md, section "Report shape".
