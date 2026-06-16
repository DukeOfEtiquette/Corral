# API-T-007: move the api service off port 8000 onto 8123 (full move)

## Target

This is web-app work (ADR-005): the FastAPI `api` service in the compose stack. Another project on the developer's machine consistently binds host port 8000 and collides with the api's published port. This task moves the `api` service fully off port 8000 onto 8123: not just the host-side publish, but the container-internal listen port too, so the string `8000` appears nowhere in the api setup afterward. The artifacts in scope are `app/api/Dockerfile` (the uvicorn listen port) and `app/docker-compose.yml` (the `api` service `ports` mapping and healthcheck probe URL).

## Decisions resolved by the Orchestrator

- **Full move, not a host-only remap.** The container-internal listen port changes to 8123 as well as the host-side publish. A host-only remap (`8123:8000`) was considered and rejected by the user in favor of a full move, so that `8000` appears nowhere in the api setup afterward. Rationale: the developer's machine collides on host 8000; the user chose to retire 8000 from the api entirely.
- **Exactly three edits, across two files, all values pinned below.** Make these three changes and no others.

  1. `app/api/Dockerfile`, line 14 (the uvicorn CMD). The line currently ends `"--port", "8000"]`. Change `8000` to `8123` so the container listens on 8123. Everything else on the line is unchanged. The result is exactly:

     ```
     CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8123"]
     ```

  2. `app/docker-compose.yml`, the `api` service `ports` entry (currently `"8000:8000"`). Change it to `"8123:8123"` (host:container, both 8123 for the full move).

  3. `app/docker-compose.yml`, the `api` service `healthcheck` test. The probe URL is currently `http://localhost:8000/healthz`. Change only the port to 8123. The `/healthz` URL path is unchanged (`/healthz` is a route path, not a port). The interval, timeout, and retries are unchanged. The result is exactly:

     ```
     test: ["CMD-SHELL", "python -c \"import urllib.request; urllib.request.urlopen('http://localhost:8123/healthz')\""]
     ```

- **Do not change the `/healthz` route in `app/api/main.py`.** It is port-independent; leave it untouched.
- **Do not change any other compose service.** Leave `postgres`, `migrate`, `test`, `test-roundtrip`, and `api-test` exactly as they are. Do not touch any test file. The `api-test` one-shot does not use the `api` service's port mapping, so the pytest suite is unaffected by this change.

## Deliverables

- The api container listening on 8123: `app/api/Dockerfile` uvicorn CMD ends `"--port", "8123"]`.
- The `api` compose service publishing `8123:8123` and its healthcheck probing `http://localhost:8123/healthz`: `app/docker-compose.yml`.
- Runtime confirmation (see "Build / verification expectations" below) that the `api` service reaches `healthy` and answers `{"status": "ok"}` on host port 8123.

## Files in scope

- `app/api/Dockerfile` (change the uvicorn CMD `--port` from 8000 to 8123).
- `app/docker-compose.yml` (the `api` service `ports` mapping and the `api` service healthcheck probe URL only).

## Files out of scope

- `app/api/main.py` (the `/healthz` route is port-independent; do not touch).
- `app/api/tests/` and every test file (the suite does not exercise ports; do not touch).
- Every compose service other than `api` in `app/docker-compose.yml`: `postgres`, `migrate`, `test`, `test-roundtrip`, `api-test`. Do not modify them.

## References

- `app/api/Dockerfile` (line 14: the uvicorn CMD with `--port 8000`, the value to change to 8123).
- `app/docker-compose.yml` (the `api` service: the `ports` mapping `"8000:8000"` and the `healthcheck` block probing `localhost:8000`, both touched by API-T-004; these are the two lines to re-port).
- `ai-infrastructure/project-manager/decisions/ADR-003-docker-compose-runtime.md` (compose-only run path; the verification commands all run through compose).

## Related tasks and ADRs

- API-T-004 (done): added the `api` compose healthcheck probing `localhost:8000` and established the `api` service shape this task re-ports. Its report is at `./.claude/artifacts/handoffs/API-T-004-IMPL-KICKOFF-REPORT.md`.
- API-T-002 (done): stood up the `api` service; the uvicorn CMD on 8000 and the `8000:8000` mapping originate here.
- ADR-003: compose-only run path; verification is via `compose up` + `ps` + `curl`.

## Hard rules

- Make exactly the three pinned edits above and nothing else. After the edits, the string `8000` must not appear anywhere in the api setup (`app/api/Dockerfile` and the `api` service block of `app/docker-compose.yml`).
- Do not modify any compose service other than `api`, and do not touch `app/api/main.py` or any test file.

## Build / verification expectations

Verification is at runtime; the pytest suite does not exercise ports, so a green suite is not the gate here. Per ADR-003, run all verification through docker compose. The `api` service depends on `postgres` and `migrate`, which compose starts automatically; the admin env (`ADMIN_EMAIL`, `ADMIN_PASSWORD_HASH`) is supplied from `app/.env`, already present. Run these commands verbatim:

1. Start the service (builds the re-ported image and brings up its dependencies):

   ```
   docker compose -f app/docker-compose.yml up -d --build api
   ```

2. Confirm the `api` service reaches the `healthy` state (the healthcheck on 8123 succeeds):

   ```
   docker compose -f app/docker-compose.yml ps
   ```

   The `api` row must show `(healthy)`.

3. Confirm the api answers on the new host port:

   ```
   curl -fsS http://localhost:8123/healthz
   ```

   It must return `{"status": "ok"}` on host port 8123. Also confirm nothing still answers on host port 8000 for this service.

4. Tear down when done:

   ```
   docker compose -f app/docker-compose.yml down
   ```

Record in the closing report whether the `api` service reached `healthy`, whether `curl http://localhost:8123/healthz` returned `{"status": "ok"}`, and that host 8000 no longer serves this api.

## Executor pointer

The executor is the dispatched `executor` (ADR-028). Universal executor conventions (the writing rules and Agent Discipline in `./CLAUDE.md`, the compose-only run policy, git boundaries, the pinned six-section report shape) live in `./docs/ai-orchestration/roles/EXECUTOR-ROLE.md`; follow them rather than expecting them restated here. Write the closing report to `./.claude/artifacts/handoffs/API-T-007-KICKOFF-REPORT.md` per EXECUTOR-ROLE.md, section "Report shape".
