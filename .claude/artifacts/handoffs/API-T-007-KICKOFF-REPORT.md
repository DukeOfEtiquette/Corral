# API-T-007-KICKOFF-REPORT

## Deliverables completed

- `app/api/Dockerfile` line 14: uvicorn CMD `--port` changed from 8000 to 8123. Container now listens on 8123.
- `app/docker-compose.yml` `api` service `ports` entry: changed from `"8000:8000"` to `"8123:8123"`.
- `app/docker-compose.yml` `api` service healthcheck probe URL: changed from `http://localhost:8000/healthz` to `http://localhost:8123/healthz`.
- Runtime verification completed: the `api` service reached `(healthy)` and answered `{"status": "ok"}` on host port 8123. Host port 8000 refuses connections (curl exit 7). Stack torn down cleanly.

## Decisions made

No decisions were deferred to the Executor. All three edits were fully pinned by the kickoff (file paths, exact line values, and the full-move rationale). The Executor applied them verbatim.

## Surprises

(none)

The observed file state matched the kickoff exactly: `app/api/Dockerfile` had `"--port", "8000"` on line 14; `app/docker-compose.yml` had `"8000:8000"` ports and `http://localhost:8000/healthz` in the healthcheck, both in the `api` service block only.

## Follow-ups

(none) -- No adjacent issues surfaced during execution.

## Files touched

- `/home/adam/src/corral/app/api/Dockerfile` (line 14: `8000` -> `8123` in uvicorn CMD)
- `/home/adam/src/corral/app/docker-compose.yml` (api service: ports mapping and healthcheck probe URL, both `8000` -> `8123`)
- `/home/adam/src/corral/.claude/artifacts/handoffs/API-T-007-KICKOFF-REPORT.md` (this report)

## Build / verification status

Verified at runtime via `docker compose -f app/docker-compose.yml up -d --build api` (ADR-003 compose-only run path):

- `docker compose ps` output:
  ```
  NAME             IMAGE    COMMAND                  SERVICE  CREATED          STATUS                    PORTS
  app-api-1        app-api  "uvicorn app.api.mai..."  api      24 seconds ago   Up 21 seconds (healthy)   0.0.0.0:8123->8123/tcp, [::]:8123->8123/tcp
  ```
  The `api` row shows `(healthy)` and port mapping is `8123->8123`.

- `curl -fsS http://localhost:8123/healthz` returned: `{"status":"ok"}`

- `curl -fsS http://localhost:8000/healthz` returned: `curl: (7) Failed to connect to localhost port 8000` (connection refused -- host 8000 no longer serves this api).

- Stack torn down with `docker compose down`; all containers and network removed cleanly.

The string `8000` does not appear anywhere in `app/api/Dockerfile` or in the `api` service block of `app/docker-compose.yml`. No test files were touched. No other compose services were modified.
