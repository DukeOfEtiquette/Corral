# API-T-004 (phase 2, implementation): the api GET /healthz liveness route + the api compose healthcheck

## Target

This is web-app domain work (ADR-005). It is phase 2 (green) of the ADR-016 two-phase TDD flow for API-T-004: the phase-1 test-design dispatch already authored the failing specification at `app/api/tests/test_healthz.py`, and your job is to implement against it until that spec passes. The artifacts in scope are exactly two: the FastAPI `app` in `app/api/main.py` (where you add a top-level `GET /healthz` route) and the `api` service in `app/docker-compose.yml` (where you add a `healthcheck` block). You drive three currently-red tests green without touching any test file.

## Decisions resolved by the Orchestrator

- **The route.** Implement a top-level `GET /healthz` in `app/api/main.py` that returns HTTP 200 with a JSON body EXACTLY `{"status": "ok"}`. No authentication, no database access (pure process-liveness). Author it in the existing route-decorator style of the file: an `@app.get("/healthz")` decorator on a function that returns the dict literal `{"status": "ok"}`. FastAPI serializes a returned dict to JSON with a 200 by default, which satisfies the contract; do not hand-build a `JSONResponse` for this route. Rationale: the existing `@app.get("/api/v1/me")` route in the same file returns a plain dict, so this matches the file's convention.

- **Top-level placement, NOT under /api/v1.** The route path is `/healthz`, mounted at the root, NOT under the ADR-010 `/api/v1` prefix. ADR-010 scopes `/api/v1` to the API contract surface; `/healthz` is an infrastructure liveness probe target, so it sits at the root. The phase-1 test `test_healthz_is_top_level_not_under_api_v1` asserts that `/api/v1/healthz` returns 404, so do NOT mount the route under the prefix. Rationale: pinned by ADR-010 and the phase-1 test, cited in the References below.

- **The compose healthcheck.** Add a `healthcheck` block to the `api` service in `app/docker-compose.yml`, mirroring the `postgres` service's `CMD-SHELL` pattern. Use this EXACT probe command and timing, verbatim:

  ```yaml
  healthcheck:
    test: ["CMD-SHELL", "python -c \"import urllib.request; urllib.request.urlopen('http://localhost:8000/healthz')\""]
    interval: 2s
    timeout: 5s
    retries: 10
  ```

  Rationale (pinned, not for re-deciding): `urllib` ships in the python image, so there is no `curl` dependency; `urlopen` raises on a non-200 response (non-zero exit, treated as unhealthy) and returns on 200 (exit 0, treated as healthy). The interval/timeout/retries values mirror the `postgres` healthcheck verbatim. The api process listens on `0.0.0.0:8000` (port 8000 is published in the `api` service), so `http://localhost:8000/healthz` is the correct in-container probe target.

- **Scope is exactly two edits.** The route in `app/api/main.py` and the `healthcheck` block on the `api` service in `app/docker-compose.yml`. Do NOT add healthchecks to any other compose service; do NOT modify `api-test`, `postgres`, `migrate`, `test`, `test-roundtrip`, or any other service. Do NOT alter the existing routes in `app/api/main.py`.

- **The tests are the specification; you may not touch them.** The three tests in `app/api/tests/test_healthz.py` were authored in phase 1 and are the pinned specification (ADR-016 no-touch rule). You may NOT create or edit any test file. If you believe a test assertion is wrong, return `RETURN: ESCALATION` describing the conflict; do not edit the test. Test corrections are routed to a fresh test-designer dispatch, never to an executor edit. Rationale: ADR-016 establishes the design-implementation separation; editing a test to make it pass inverts the TDD cycle.

- **Acceptance gate.** The full api test suite passes under the compose one-shot. Run it verbatim with `docker compose -f app/docker-compose.yml run --rm --build api-test`. The `--build` is required because the `api-test` image COPYs the api source and tests in at build time (`app/api/Dockerfile.test`), so it must rebuild to pick up both the new `/healthz` route and the phase-1 test file. Expect the three `test_healthz.py` tests to go from red to green and the existing API-T-002 tests (`test_admin_seed.py`, `test_auth_login.py`, `test_sessions.py`) to remain green.

## Deliverables

- A top-level `GET /healthz` route in `app/api/main.py`: returns 200, body exactly `{"status": "ok"}`, unauthenticated, no DB access, in the file's existing decorator style.
- A `healthcheck` block on the `api` service in `app/docker-compose.yml` using the exact pinned `CMD-SHELL` probe and timing above, so downstream services can gate on `depends_on: { api: { condition: service_healthy } }`.
- All tests under `app/api/tests/` passing under `docker compose -f app/docker-compose.yml run --rm --build api-test`: the three `test_healthz.py` tests red-to-green, the existing API-T-002 tests still green.

## Files in scope

- `app/api/main.py` (ADD the top-level `/healthz` route; match the existing decorator style; do not alter existing routes)
- `app/docker-compose.yml` (ADD a `healthcheck` block to the `api` service ONLY)

## Files out of scope

- `app/api/tests/test_healthz.py` (PROTECTED phase-1 specification, ADR-016 no-touch; do NOT create or edit)
- `app/api/tests/conftest.py` (existing shared fixtures; do not touch)
- `app/api/tests/test_admin_seed.py`, `app/api/tests/test_auth_login.py`, `app/api/tests/test_sessions.py` (existing API-T-002 tests; do not touch)
- Every compose service other than `api`: `postgres`, `migrate`, `test`, `test-roundtrip`, `api-test`. Do NOT add healthchecks to them or otherwise modify them.

## References

Read these in order before editing.

- `app/api/main.py` (the FastAPI `app` and the existing `@app.get` / `@app.post` route-decorator style to match; existing routes live under `/api/v1`, and `@app.get("/api/v1/me")` is the dict-returning pattern to mirror for `/healthz`)
- `app/docker-compose.yml` (the `api` service to edit; the `postgres` service's `healthcheck` block at the top of the file is the `CMD-SHELL` pattern and timing to mirror)
- `app/api/tests/test_healthz.py` (the phase-1 specification the route must satisfy: 200, body `{"status": "ok"}`, unauthenticated, `/healthz` top-level with `/api/v1/healthz` returning 404; READ it to confirm the contract, do NOT edit it)
- `app/api/Dockerfile.test` (the api-test image: COPYs source and tests, `CMD pytest -v app/api/tests/`; this is why `--build` is required on the acceptance run)
- `ai-infrastructure/project-manager/decisions/ADR-016-testing-strategy-test-designer-agent.md` (the two-phase TDD flow and the no-touch rule on test files)
- `ai-infrastructure/project-manager/decisions/ADR-010-api-shape-and-mcp-data-path.md` (the `/api/v1` prefix scope; the basis for `/healthz` being top-level)
- `ai-infrastructure/project-manager/decisions/ADR-003-docker-compose-runtime.md` (the compose-only run path; the `api-test` one-shot service that runs the suite)

## Related tasks and ADRs

- API-T-004 phase 1 (test-design dispatch): authored `app/api/tests/test_healthz.py`, the failing spec this implementation drives green. Report at `./.claude/artifacts/handoffs/API-T-004-TEST-DESIGN-KICKOFF-REPORT.md`.
- API-T-002 (done): stood up the api service, the `api-test` compose one-shot, and the compose patterns; its tests (`test_admin_seed.py`, `test_auth_login.py`, `test_sessions.py`) must stay green.
- ADR-016: the no-touch rule protecting `test_healthz.py`.
- ADR-010: scopes `/api/v1` to the API contract; the basis for `/healthz` being top-level.
- ADR-003: the compose-only run path (the `api-test` service runs the suite).

## Hard rules

- Do NOT create or edit any file under `app/api/tests/`. The three `test_healthz.py` tests are the specification; if one looks wrong, return `RETURN: ESCALATION` rather than editing it (ADR-016 no-touch rule).
- Edit only the two in-scope files. Do not alter the existing `/api/v1` routes in `app/api/main.py`, and do not modify any compose service other than `api`.
- Run verification through docker compose only (ADR-003); do not assume host-installed Python. The single acceptance command is `docker compose -f app/docker-compose.yml run --rm --build api-test`, run from the repo root. The `--build` flag is required (the `api-test` image bakes in source and tests at build time).

## Executor pointer

The executor is the dispatched `executor` (ADR-028). Universal executor conventions (the writing rules and Agent Discipline in `./CLAUDE.md`, the compose-only run policy, git boundaries, the no-touch test rule, the pinned six-section report shape) live in `./docs/ai-orchestration/roles/EXECUTOR-ROLE.md`; follow them there rather than expecting them restated here. Write the closing report to `./.claude/artifacts/handoffs/API-T-004-IMPL-KICKOFF-REPORT.md` per EXECUTOR-ROLE.md, section "Report shape".
