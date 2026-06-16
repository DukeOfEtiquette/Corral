# API-T-004-IMPL-KICKOFF-REPORT

## Deliverables completed

- [x] `GET /healthz` route added to `app/api/main.py` (line 80): decorator `@app.get("/healthz")` on a function returning `{"status": "ok"}`, no auth, no DB access, matches existing dict-returning decorator style.
- [x] `healthcheck` block added to the `api` service in `app/docker-compose.yml` (after `ports`, before `depends_on`): exact pinned `CMD-SHELL` probe using `urllib.request.urlopen`, with `interval: 2s`, `timeout: 5s`, `retries: 10`, mirroring the `postgres` service pattern.
- [x] All 22 tests pass under `docker compose -f app/docker-compose.yml run --rm --build api-test`: the three `test_healthz.py` tests are green (red-to-green), and all 19 existing API-T-002 tests remain green.

## Decisions made

No open decisions were needed. All decisions were pinned by the Orchestrator in the kickoff:

- Route path `/healthz` at root (not `/api/v1/healthz`), per ADR-010 and the `test_healthz_is_top_level_not_under_api_v1` test.
- Returned plain dict `{"status": "ok"}` (not a hand-built `JSONResponse`), per the kickoff's convention note referencing `@app.get("/api/v1/me")`.
- Exact probe command and timing for the compose healthcheck, verbatim from the kickoff.

## Surprises

(none)

## Follow-ups

- COR-T candidate: downstream compose services (e.g., a future frontend service) can now gate on `depends_on: { api: { condition: service_healthy } }` - triage to orchestrator when the frontend service is introduced.

## Files touched

- `/home/adam/src/corral/app/api/main.py` (added `/healthz` route at line 80)
- `/home/adam/src/corral/app/docker-compose.yml` (added `healthcheck` block to `api` service)
- `/home/adam/src/corral/.claude/artifacts/handoffs/API-T-004-IMPL-KICKOFF-REPORT.md` (this report)

## Build / verification status

Verified: `docker compose -f app/docker-compose.yml run --rm --build api-test` completed with 22 passed in 2.80s. All three `test_healthz.py` tests (previously red) are now green. All 19 existing API-T-002 tests remain green. No manual post-session verification required.
