# API-T-004 test-design report (phase 1, red): failing test for GET /healthz

## Deliverables completed

- Authored the new test file `./app/api/tests/test_healthz.py` (the only file written), specifying the pinned `GET /healthz` contract. Three failing tests:
  - `test_healthz_returns_200_and_ok_body` (test_healthz.py:36): the two pinned minimum assertions, `status_code == 200` and `resp.json() == {"status": "ok"}`.
  - `test_healthz_is_unauthenticated` (test_healthz.py:50): locks the unauthenticated-liveness property: the fresh `client` carries no session cookie (asserted via `not client.cookies`) and the route still returns 200 with the exact body.
  - `test_healthz_is_top_level_not_under_api_v1` (test_healthz.py:69): guards the ADR-010 top-level placement: `/healthz` answers 200 with the exact body, and `/api/v1/healthz` returns 404 (not part of the contract).
- All tests reuse the existing async `client` fixture from `./app/api/tests/conftest.py` verbatim; no fixture was added, modified, or duplicated, and the conftest was not edited.

## Decisions made

- **Edge-case coverage beyond the pinned minimum (test designer judgment per the kickoff).** The kickoff fixed status 200, body `{"status": "ok"}`, and the unauthenticated property, and left further edge cases to my judgment. I added one extra test (`test_healthz_is_top_level_not_under_api_v1`) asserting `/api/v1/healthz` returns 404, to lock the pinned top-level placement against an implementer accidentally mounting the route under the API prefix. Rationale: ADR-010's top-level-vs-prefix placement is a load-bearing, pinned contract property; a test that pins it is the cheapest way to keep the implementation honest.
- **Async style: `@pytest.mark.asyncio` + `async def` using `await client.get(...)`.** Matches the existing API-T-002 tests verbatim (verified `test_auth_login.py` uses `@pytest.mark.asyncio` on every async test). No new style introduced.

## Surprises

(none) Observed state matched the kickoff exactly: `app/api/main.py` exposes only `/api/v1/*` routes (login, logout, me) and no `/healthz`, so the route returns 404 today and the suite collects cleanly via the successful app import.

## Follow-ups

(none) The `/healthz` route implementation in `./app/api/main.py` and the `app/docker-compose.yml` api healthcheck block are explicitly named as phase-2 (implementation executor) deliverables in the kickoff, not out-of-scope discoveries surfaced by me.

## Files touched

- `./app/api/tests/test_healthz.py` (NEW, test file, authored this session)
- `./.claude/artifacts/handoffs/API-T-004-TEST-DESIGN-KICKOFF-REPORT.md` (this report, dual-channel write)

All files touched are a test file and the report. No non-test file was created or edited.

## Build / verification status

- Not run by the test designer: the compose-only run path (ADR-003) via the `api-test` one-shot service is exercised in phase 2 and by the orchestrator, not here.
- Expected outcome is RED: `GET /healthz` does not exist yet, so it returns 404; the status (`== 200`) and body (`== {"status": "ok"}`) assertions in all three tests fail, and the `/api/v1/healthz == 404` assertion in the third test passes today but is paired with the failing top-level assertions in the same test. Redness comes from the 404/status/body assertions, NOT from a collection-time or import error: the app import (`from app.api.main import app as fastapi_app` in conftest.py:55) succeeds, so the suite collects cleanly.
- Phase-2 verification expectation: after the executor implements the top-level `/healthz` route returning `{"status": "ok"}`, all three tests go green under the `api-test` compose service.
