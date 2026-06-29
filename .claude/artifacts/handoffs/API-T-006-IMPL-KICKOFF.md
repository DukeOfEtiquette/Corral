# API-T-006 (items 1 and 3): api devex hardening, single tracked app/.env.example + compose env wiring, and formalize gen-admin-hash.sh

## Target

This is **web-app** work (domain 1, ADR-005): operability hardening of the `app/` stack, directed by the backend-api department. You are executing **items 1 and 3 of API-T-006 only**. Item 2 (a fail-fast pytest in `./app/api/tests/`) is a separate test-designer dispatch and is not part of this kickoff; you must not create or edit any file under `./app/api/tests/`.

The work has two threads:

- **Item 1**: replace the two scattered, unused `.env.example` templates with a single tracked template at the compose project directory (`./app/.env.example`), and wire the currently-unwired environment variables into the compose `api` service so that template genuinely drives the stack.
- **Item 3**: formalize the already-committed helper `./app/api/gen-admin-hash.sh` as an owned deliverable by adding a documentation note to its header comment. No behavioral change to the script.

Every decision below is pinned by the Orchestrator. You make no design decisions; execute the specified changes exactly.

## Decisions resolved by the Orchestrator

- **Single tracked template, at the compose project directory.** The repo currently has two scattered, unused templates: `./app/api/.env.example` and `./app/db/.env.example`. Nothing consumes either one: `./app/docker-compose.yml` has no `env_file:` directive, and the only references to `.env.example` anywhere are exclusion lines in `./app/api/.dockerignore` and `./app/db/.dockerignore`. Docker compose auto-reads `./app/.env` (the compose project directory) for `${VAR}` interpolation. The fix is therefore a single tracked template at `./app/.env.example`. Rationale: one source of truth, co-located with the file compose actually reads.

- **`./app/.env.example` content is fixed.** Create the file with exactly this content (secrets are variable-names-only per ADR-006; the commented optional-override defaults are the existing public dev defaults already present in tracked `./app/docker-compose.yml` and `./app/api/settings.py`, so reproducing them exposes no new secret):

  ```
  # Environment for the Corral app stack. Copy this file to app/.env (gitignored;
  # ADR-006) and fill in the required values, then run the stack with
  #   docker compose -f app/docker-compose.yml up
  # which reads app/.env automatically for ${VAR} interpolation. Never commit app/.env.
  #
  # Generate ADMIN_PASSWORD_HASH with the helper (argon2id-hashes via the api image,
  # no host Python needed):
  #   app/api/gen-admin-hash.sh --email you@example.com --password your-password

  # Required: the api refuses to start until these are set (no safe default).
  ADMIN_EMAIL=
  ADMIN_PASSWORD_HASH=

  # Optional overrides (defaults shown; uncomment a line to change it).
  #DATABASE_URL=postgresql://corral:devpassword@postgres:5432/corral
  #API_HOST_PORT=8123
  #API_DOCS_ENABLED=true
  #SESSION_COOKIE_NAME=session
  #SESSION_LIFETIME_SECONDS=604800
  #SESSION_COOKIE_SECURE=false
  ```

  Note on one character: the Orchestrator's source comment for the `# Required` line used an em dash after the word "Required". Em dashes are forbidden in tracked files (`./CLAUDE.md`), so the line above uses a colon after "Required" instead. Reproduce the block exactly as shown here, with the colon; do not introduce an em dash anywhere in the file. Every other line is verbatim from the pinned content.

- **Wire the unwired vars in the compose `api` service.** Edit the `api` service's `environment:` block in `./app/docker-compose.yml` and only that block. Today it sets a hardcoded `DATABASE_URL`, `ADMIN_EMAIL: ${ADMIN_EMAIL}`, and `ADMIN_PASSWORD_HASH: ${ADMIN_PASSWORD_HASH}`. Change `DATABASE_URL` to be overridable with the dev default, and add the four currently-unwired vars, all using `${VAR:-default}` so behavior is unchanged when `./app/.env` is silent:
  - `DATABASE_URL: ${DATABASE_URL:-postgresql://corral:devpassword@postgres:5432/corral}`
  - `API_DOCS_ENABLED: ${API_DOCS_ENABLED:-true}`
  - `SESSION_COOKIE_NAME: ${SESSION_COOKIE_NAME:-session}`
  - `SESSION_LIFETIME_SECONDS: ${SESSION_LIFETIME_SECONDS:-604800}`
  - `SESSION_COOKIE_SECURE: ${SESSION_COOKIE_SECURE:-false}`

  Leave the `ADMIN_EMAIL` and `ADMIN_PASSWORD_HASH` lines as they are (already `${VAR}`). Leave the `ports:` line `"${API_HOST_PORT:-8123}:8123"` as is (`API_HOST_PORT` is already driven). The default strings above are the contract: the `SESSION_*` defaults come from `./app/api/settings.py` (`get_cookie_name` default `"session"`, `get_session_lifetime_seconds` default `604800`, `get_cookie_secure` default `"false"`), `API_DOCS_ENABLED` default `"true"` (`settings.get_docs_enabled`, ADR-044), and the `DATABASE_URL` default mirrors the current hardcoded compose value verbatim.

- **Delete both scattered templates.** Remove `./app/api/.env.example` and `./app/db/.env.example` with `git rm` so they leave the index, not just the working tree. After deletion the single source of truth is `./app/.env.example`. The now-moot `.env.example` exclusion lines in `./app/api/.dockerignore` and `./app/db/.dockerignore` are left intentionally untouched: they are harmless no-ops because `./app/.env.example` sits above both Docker build contexts, and cleaning them is out of scope. Record this no-op note in the report.

- **Formalize `./app/api/gen-admin-hash.sh` with a documentation-only edit.** The helper is already committed (an Orchestrator-direct one-off filed under this task). Own it as a tracked deliverable by making one change: add a "reseed gotcha" note to the script's header comment block (a shell comment, not a new README; the global docs-placement rule forbids scattering `.md` files into source directories). The note must convey: `seed_admin()` in `./app/api/admin_seed.py` is idempotent (it seeds the admin only if no `users` row with `ADMIN_EMAIL` already exists), so re-running `gen-admin-hash.sh` with a new password and restarting the api does **not** update an already-seeded admin; re-seeding requires a volume reset via `docker compose -f app/docker-compose.yml down -v` followed by bringing the stack back up. You may optionally also add a one-line pointer in the header that `./app/.env.example` is the tracked template for `./app/.env`. Make no functional or behavioral change to the script logic; the edit is comment-only.

- **No smoke test for the helper.** A smoke test is explicitly not in scope: the script's hashing path needs docker plus the built api image, the repo has no shell-test harness, and the cost outweighs the benefit for a dev helper. Do not add one.

## Deliverables

- A new tracked file `./app/.env.example` containing exactly the content pinned above.
- `./app/docker-compose.yml` `api` service `environment:` block edited to add `${VAR:-default}` interpolation for `DATABASE_URL`, `API_DOCS_ENABLED`, `SESSION_COOKIE_NAME`, `SESSION_LIFETIME_SECONDS`, and `SESSION_COOKIE_SECURE`. Only the `api` service is touched.
- `./app/api/.env.example` and `./app/db/.env.example` removed via `git rm`.
- `./app/api/gen-admin-hash.sh` header comment updated with the reseed-gotcha note (and optionally the `./app/.env.example` pointer); no behavioral change.

## Files in scope

- `./app/.env.example` (CREATE)
- `./app/docker-compose.yml` (EDIT, the `api` service `environment:` block only)
- `./app/api/.env.example` (DELETE via `git rm`)
- `./app/db/.env.example` (DELETE via `git rm`)
- `./app/api/gen-admin-hash.sh` (EDIT, header comment only)

## Files out of scope

- `./app/api/tests/**`: the protected test suite. Item 2's fail-fast test is a separate test-designer dispatch (ADR-016). Do not create or edit any test file.
- All compose services other than `api`: `postgres`, `migrate`, `test`, `test-roundtrip`, `api-test`. Do not change their hardcoded `DATABASE_URL`. Unifying `DATABASE_URL` / postgres credentials across those services from `./app/.env` is a deferred database-department follow-up, not this task. `api-test` in particular keeps its fixed `DATABASE_URL` for test isolation.
- `./app/api/settings.py`, `./app/api/main.py`, `./app/api/admin_seed.py`: no code change is needed; these vars are already read by `settings.py`. This task only wires compose, writes the template, and documents the helper.
- `./app/api/.dockerignore`, `./app/db/.dockerignore`: leave the now-moot `.env.example` lines untouched.

## References

- `./app/docker-compose.yml`: the compose file; edit the `api` service only.
- `./app/api/settings.py`: shows which env vars the api reads and their defaults (the contract for the default values).
- `./app/api/gen-admin-hash.sh`: the helper to formalize (header comment edit).
- `./app/api/admin_seed.py`: the idempotent `seed_admin()` the reseed-gotcha note describes.
- `./ai-infrastructure/project-manager/decisions/ADR-006-admin-bootstrap-env-hash.md`: secrets via env only; admin bootstrap from an env-supplied hash.
- `./ai-infrastructure/project-manager/decisions/ADR-003-docker-compose-runtime.md`: compose is the only run path; verification commands must be compose-based.
- `./ai-infrastructure/project-manager/decisions/ADR-044-api-docs-openapi-endpoint-policy.md`: `API_DOCS_ENABLED` semantics (default true; remote sets false).

## Related tasks and ADRs

- API-T-002 (ADR-016 two-phase build of the auth/admin-seed service): where `gen-admin-hash.sh` and the `.env.example` mismatch were surfaced; the helper was committed as an Orchestrator-direct one-off under API-T-006.
- ADR-006: admin bootstrap from an env-supplied argon2id hash; secrets via env only (governs `./app/.env` and `./app/.env.example`).
- ADR-044: `API_DOCS_ENABLED` policy (one of the newly-wired vars).
- ADR-003: docker compose is the only run path; verification is compose-based.

## Hard rules

- **Touch only the `api` service in compose.** Confirm via `git diff` that no other service's `environment:` block changed. The `ports:` line and the `ADMIN_EMAIL` / `ADMIN_PASSWORD_HASH` lines stay as they are.
- **Remove the old templates from the index, not just the working tree.** Use `git rm`, not a plain filesystem delete.
- **The helper edit is comment-only.** No change to script logic, control flow, or quoting. Verify with `bash -n ./app/api/gen-admin-hash.sh`.
- **No secrets in the template.** `ADMIN_EMAIL` and `ADMIN_PASSWORD_HASH` are present as bare keys with empty values; never fill them in.

## Verification expectations

Verification is compose-based per ADR-003. Run and report each of these:

- `./app/.env.example` exists and is tracked and not ignored: `git ls-files app/.env.example` lists it, and `git check-ignore -q app/.env.example` returns non-zero (the file is NOT ignored).
- `./app/api/.env.example` and `./app/db/.env.example` no longer exist on disk and are removed from the index (confirm via `git status` / `git ls-files`).
- `docker compose -f app/docker-compose.yml config` parses successfully with the edited file. Run it with no `./app/.env` overrides so defaults apply, and confirm the `api` service resolves `DATABASE_URL`, `API_DOCS_ENABLED`, and the `SESSION_*` vars to the documented defaults. If docker is unavailable in your environment, say so explicitly and fall back to confirming the YAML edit is well-formed; do not claim a check you did not run (Agent Discipline, `./CLAUDE.md`).
- `bash -n app/api/gen-admin-hash.sh` reports no syntax error (the header edit is comment-only; no behavior change).
- The `api` service is the only compose service whose `environment:` block changed: confirm via `git diff app/docker-compose.yml` that no other service block was modified.

## Executor pointer

You are the dispatched `executor` (ADR-028). Universal executor conventions (run policy, file-edit hygiene, the no-touch rule for tests, the pinned six-section report shape, dual-channel report write) live in `./docs/ai-orchestration/roles/EXECUTOR-ROLE.md`; follow them rather than re-deriving. Write your closing report to the path derived in `EXECUTOR-ROLE.md`, section "Report shape" (the kickoff's own directory, kickoff basename with `-REPORT.md`). There is one acceptance gate: the deliverables above, confirmed by the verification expectations.
