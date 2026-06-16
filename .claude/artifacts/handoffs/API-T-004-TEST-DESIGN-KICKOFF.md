# API-T-004 (phase 1, test design): failing test for the api GET /healthz liveness route

## Target

This is web-app domain work (ADR-005), phase 1 (red) of the ADR-016 two-phase TDD flow for API-T-004. The surface is a new HTTP liveness route on the api FastAPI app, `GET /healthz`. You author a failing test that specifies its contract; you do NOT implement the route. The application already exists at `app/api/main.py` (built by API-T-002), so the suite collects cleanly; the test you write is RED because the route does not exist yet and currently returns 404. The test file you author is the specification the phase-2 implementation executor satisfies, and under the ADR-016 no-touch rule that executor may not edit it.

## Decisions resolved by the Orchestrator

- **Contract pinned: `GET /healthz` returns HTTP 200 with JSON body exactly `{"status": "ok"}`, requires NO authentication (no session cookie), and performs NO database access (pure process-liveness).** These three properties ARE the specification the test asserts. Rationale: the orchestrator pinned the liveness contract; the test encodes it, it does not re-derive it.
- **The route is at the top level (`/healthz`), NOT under the `/api/v1` prefix.** ADR-010 scopes `/api/v1` to the API contract surface; `/healthz` is an infrastructure liveness probe target (the future docker-compose healthcheck), so it sits at root by design. The test MUST assert `GET /healthz`, never `/api/v1/healthz`. This is a deliberate, pinned exception, not an oversight. Source: `./ai-infrastructure/project-manager/decisions/ADR-010-api-shape-and-mcp-data-path.md`.
- **The test must be RED when authored, via the 404 assertion, NOT via a collection-time failure.** The FastAPI app already exists in `./app/api/main.py` (unlike API-T-002's phase 1, where the app import failed at collection), so the app import succeeds and the suite collects cleanly. Redness comes from `GET /healthz` currently returning 404 and the status/body assertions failing. Do NOT author the test in any way that depends on collection failure or on the route's absence breaking import.
- **Reuse the EXISTING async `client` fixture in `./app/api/tests/conftest.py`.** It is an httpx `AsyncClient` over `ASGITransport` (in-process, no network listener). The test is an `async def` using `await client.get("/healthz")`, matching the existing async test style. Do NOT add, modify, or duplicate any fixture; the conftest is out of scope.
- **Minimum required assertions (pinned): status code `== 200`, and `resp.json() == {"status": "ok"}`.** Additionally lock the unauthenticated contract: assert the route returns 200 with no session cookie present, since "unauthenticated liveness" is a load-bearing property of a healthcheck probe target. Enumerating further edge cases is your judgment as test designer, but the body and status above are fixed and not optional.
- **Run path is compose-only (ADR-003); you run nothing.** The test runs under the existing `api-test` compose service, which supplies `DATABASE_URL` (required by the conftest's session-scoped `db_url` fixture and the autouse `reset_auth_tables` TRUNCATE, even though `/healthz` itself touches no DB). You do not run the suite; phase 2 and the orchestrator verify via compose. Source: `./ai-infrastructure/project-manager/decisions/ADR-003-docker-compose-runtime.md`.
- **Scope is the failing test ONLY.** Do NOT implement the `/healthz` route in `./app/api/main.py`, and do NOT add the compose healthcheck block. Both are phase-2 (implementation executor) deliverables.

## Deliverables

- A new test file `./app/api/tests/test_healthz.py` containing failing test(s) that specify the `GET /healthz` contract above: status 200, body exactly `{"status": "ok"}`, and the unauthenticated property (200 returned with no session cookie present). The file is the specification phase 2 implements against; per the ADR-016 no-touch rule the phase-2 executor may not edit it.

## Files in scope

- `./app/api/tests/test_healthz.py` (NEW FILE to author; the only file you write)

## Files out of scope

- `./app/api/main.py` (the `/healthz` route lives here, authored in phase 2; do not touch)
- `./app/docker-compose.yml` (the api healthcheck block is added in phase 2; do not touch)
- `./app/api/tests/conftest.py` (existing shared fixtures including the `client` fixture to REUSE; do not modify)
- `./app/api/tests/test_admin_seed.py` (existing API-T-002 test; do not touch)
- `./app/api/tests/test_auth_login.py` (existing API-T-002 test; do not touch)
- `./app/api/tests/test_sessions.py` (existing API-T-002 test; do not touch)

## References

- `./app/api/tests/conftest.py` (the async `client` fixture, an httpx `AsyncClient` over `ASGITransport`, to reuse verbatim; also the autouse `reset_auth_tables` TRUNCATE and the session-scoped `db_url` fixture that requires `DATABASE_URL`)
- `./app/api/main.py` (current FastAPI app shape and the existing `/api/v1` routes; read for context, do not edit; confirms `/healthz` does not yet exist, so it currently returns 404)
- `./ai-infrastructure/project-manager/decisions/ADR-016-testing-strategy-test-designer-agent.md` (the TDD two-phase flow, the test-file no-touch rule, API-level tests over a real Postgres, no DB mocking)
- `./ai-infrastructure/project-manager/decisions/ADR-010-api-shape-and-mcp-data-path.md` (the `/api/v1` prefix scope; the basis for placing `/healthz` at the top level instead)
- `./ai-infrastructure/project-manager/decisions/ADR-003-docker-compose-runtime.md` (compose-only run path; the `api-test` service that runs the suite)

## Related tasks and ADRs

- API-T-002 (done): stood up the api FastAPI app (`./app/api/main.py`), the conftest fixtures (including the async `client` and the autouse TRUNCATE), and the red/green TDD pattern this test mirrors. The new test reuses that conftest verbatim.
- ADR-016: the two-phase TDD flow and the test-file no-touch rule that protects this test in phase 2.
- ADR-010: scopes `/api/v1` to the API contract; the rationale for `/healthz` being top-level.
- ADR-003: compose-only run path (the `api-test` service runs the suite).

## Hard rules

- Assert `GET /healthz`, never `/api/v1/healthz`. The top-level placement is pinned.
- The test must be RED via the 404 / status / body assertions failing, never via a collection-time or import error. The app import must continue to succeed.
- Reuse the existing async `client` fixture; do not add, modify, or duplicate any fixture, and do not edit `./app/api/tests/conftest.py`.
- Author the failing test only; do not implement the route in `./app/api/main.py` and do not add the compose healthcheck block.
- You run nothing. The compose-only run path (ADR-003) is exercised in phase 2 and by the orchestrator, not by you.

## Executor pointer

You are the dispatched `test-designer` (ADR-016 phase 1). Universal conventions (the writing rules and Agent Discipline in `./CLAUDE.md`, the compose-only run policy, git boundaries, and the pinned six-section report shape) live in `./docs/ai-orchestration/roles/EXECUTOR-ROLE.md`. Write your closing report to `./.claude/artifacts/handoffs/API-T-004-TEST-DESIGN-KICKOFF-REPORT.md` per EXECUTOR-ROLE.md, section "Report shape".
