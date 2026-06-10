# Live auto-rebuilding dashboard: watch sources and refresh the page

## Target

This is AI-infrastructure work (ADR-005). The project-manager dashboard is a domain-2 AI-infrastructure tooling artifact (ADR-027 Fork E, the project-manager insight dashboard), not web-app code. The task makes the existing dashboard live: a source-of-truth markdown edit (STATUS, tasks, decisions, OBSERVATIONS) should auto-regenerate `data.json` AND the open browser page should reflect it, with no manual container rebuild and no manual browser refresh. The artifacts in scope are the dashboard's ETL (`etl.py`), its container build (`Dockerfile`), and its SPA root (`src/App.jsx`), all under `./ai-infrastructure/project-manager/dashboard/`. The design is grounded in the rogue exemplar named in References; you mirror the proven patterns, you do not invent a new design.

## Decisions resolved by the Orchestrator

- **Goal.** Make the dashboard live end to end: a watched markdown edit re-runs the build (regenerating `data.json` in the served directory), and the open page picks up the new data within a few seconds. No new manual steps for the user.
- **Server watch lives in `etl.py`.** Add a `--watch` mode via argparse (a `--watch` `store_true` flag). The default behavior (no flag) stays exactly the one-shot build that exists today: run `run_etl` once and exit, unchanged. With `--watch`: run the build once, then start a watchdog observer over the ETL's source tree under `REPO_ROOT`, and re-run the build (writing `data.json` to `SERVED_DIR`) on each relevant change.
- **Observer: `PollingObserver`, not the default Observer.** Use `from watchdog.observers.polling import PollingObserver`. Rationale (pinned): the watcher runs in a container over a read-only Docker bind mount (`/repo`); `PollingObserver` is bind-mount safe on any host (Linux or Docker Desktop), where inotify is not. This deliberately diverges from rogue, which watches a native filesystem and uses the default `Observer`. Mirror rogue's watch structure (debounce, event filtering, recursive schedule); swap only the observer class and the watched trees.
- **Watch mechanics (mirror rogue's `run_watch`).** Debounce rebuilds at roughly 350ms using a cancel/restart `threading.Timer` (mirror rogue's `schedule_rebuild` / `do_rebuild` pair, `threading.Timer(0.35, ...)`). Filter to content-change events only: react only to `modified`, `created`, `deleted`, `moved`; ignore directory events (`event.is_directory`). This is required, not cosmetic: watchdog 4.0+ emits open/close events for every file open, including the reads the build itself does, which causes a feedback loop without this filter. Restrict triggering to the files the ETL actually reads (an allowlist of the documented source set; rogue's `is_watched` / `WATCH_PATTERNS` is the model). Schedule the observer recursively over these trees under `REPO_ROOT`: `ai-infrastructure/` and `.claude/commands/`. `data.json` is written to `SERVED_DIR` (a separate directory from the watched `/repo`), so the output never self-triggers; keep the content-change-event filter regardless, for the build's own read events.
- **Build call adapts to Corral.** Where rogue's watch calls `build()`, yours calls Corral's `run_etl(repo_root, served_dir)` (the existing build function). Read `REPO_ROOT` and `SERVED_DIR` the same way the existing `__main__` block does. Wrap the rebuild in try/except and log failures to stderr (mirror rogue's `do_rebuild`); a failed rebuild must not kill the watch loop.
- **Process model: single container.** Change the `Dockerfile` so the container entrypoint: (1) runs `etl.py` once for the initial build, (2) launches `python etl.py --watch` in the BACKGROUND, then (3) runs `python -m http.server 8420 --directory /served --bind 0.0.0.0` in the FOREGROUND (the container stays attached to the server). The watcher must be non-fatal: if the background watch process dies, the container keeps serving. A small copied `entrypoint.sh` is acceptable if it is cleaner than an inline CMD; either is fine as long as the http server is the foreground process. `docker-compose.yml` is NOT changed; the single-service topology stays.
- **Dependency: add `watchdog` to the serve stage.** The serve-stage pip install is currently `pip install --no-cache-dir PyYAML==6.0.2`. Add `watchdog`, pinned to a current stable version in the same pinned style (for example `watchdog==4.0.2`, or the current stable equivalent). Keep `PyYAML==6.0.2` pinned as-is.
- **Client poll lives in `src/App.jsx`.** Add a poller that every 5000ms fetches `./data.json` with `{ cache: 'no-store' }`, reads `meta.generated_at` from the fresh payload, and if it differs from the currently-rendered `meta.generated_at`, calls `setData(fresh)` to soft-re-render. This is preferred over rogue's full `location.reload()`: no flash, and it preserves the hash route and scroll position. Keep the existing initial fetch on mount unchanged. Clear the interval on unmount (a `useEffect` cleanup that returns `clearInterval`). A transient poll fetch error must NOT replace the current view with the error screen or clear data: swallow and log poll errors and keep showing the last good data. Only the initial-load failure shows the error screen, exactly as today.
- **`meta.generated_at` is the change key; the contract is unchanged.** The ETL's `data.json` already carries `meta.generated_at` (set in `run_etl`). The poller keys on it. Do not change the `data.json` shape. Note the Corral contract nests it under `meta` (`data.meta.generated_at`); rogue's exemplar keys on a top-level `generated_at`, so adapt the key path when mirroring rogue's poller.

## Deliverables

- `./ai-infrastructure/project-manager/dashboard/etl.py`: a `--watch` mode (argparse `store_true` flag) using watchdog `PollingObserver`, debounced at roughly 350ms via a cancel/restart `threading.Timer`, filtered to content-change events only (`modified`/`created`/`deleted`/`moved`, directory events skipped), allowlisted to the documented ETL source set, recursively watching `ai-infrastructure/` and `.claude/commands/` under `REPO_ROOT`, and re-running the existing `run_etl(repo_root, served_dir)` on each relevant change with failures logged non-fatally. The one-shot default (no flag) is unchanged.
- `./ai-infrastructure/project-manager/dashboard/Dockerfile`: `watchdog` added to the serve-stage pip install (pinned, same style as `PyYAML==6.0.2`); the entrypoint changed to the single-container model (initial build, background `python etl.py --watch`, foreground `http.server`; background watch failure non-fatal to serving). A new `entrypoint.sh` in the dashboard directory is acceptable if you choose a script over an inline CMD.
- `./ai-infrastructure/project-manager/dashboard/src/App.jsx`: a 5000ms `data.json` poller keyed on `meta.generated_at`, with a soft `setData(fresh)` re-render on change, interval cleanup on unmount, and poll-error tolerance (no error-screen takeover, last-good data preserved). The initial on-mount fetch is preserved.
- `./ai-infrastructure/project-manager/dashboard/entrypoint.sh` (new): only if you choose a script over an inline CMD.
- STATUS hygiene: universal only (see STATUS deltas).

## Files in scope

- `./ai-infrastructure/project-manager/dashboard/etl.py`
- `./ai-infrastructure/project-manager/dashboard/Dockerfile`
- `./ai-infrastructure/project-manager/dashboard/src/App.jsx`
- `./ai-infrastructure/project-manager/dashboard/entrypoint.sh` (new file, only if you choose a script over an inline CMD)
- `./ai-infrastructure/project-manager/STATUS.md` (universal hygiene only, per WORKER-ROLE.md)

## Files out of scope

- `./ai-infrastructure/project-manager/dashboard/docker-compose.yml`. The single-container approach needs no compose change; do NOT add services or volumes.
- The `data.json` JSON contract and shape. It is unchanged; the poller only reads the existing `meta.generated_at`.
- The other React panels and views under `./ai-infrastructure/project-manager/dashboard/src/`. Only `App.jsx` changes. No new UI panels, no styling churn, no "auto-refreshes" hint in this task.
- Every ADR under `./ai-infrastructure/project-manager/decisions/` and the `./ai-infrastructure/project-manager/tasks/` tree. These are Orchestrator-owned; do not touch them.

## References

- `~/rogue/ai-workspaces/project-manager/dashboard/build.py`: the exemplar watch implementation. Read `run_watch` and `is_watched` (around lines 1452-1525) and the argparse `--watch` wiring (around lines 1527-1546). Mirror the debounce (`threading.Timer(0.35, ...)` cancel/restart), the `CONTENT_CHANGE_EVENTS` filter, the `event.is_directory` skip, and the recursive `observer.schedule` over a `watch_dirs` list. Adapt: use `PollingObserver`, watch Corral's `REPO_ROOT` trees (`ai-infrastructure/` and `.claude/commands/`), and call Corral's `run_etl`, not rogue's `build()`.
- `~/rogue/ai-workspaces/project-manager/dashboard/static/dashboard.js`: the exemplar client poller. Read around lines 1124-1135 (the `setInterval(..., 5000)`, `fetch('data.json', { cache: 'no-store' })`, `generated_at` compare). Adapt to React: soft `setData` re-render instead of `location.reload()`, and key on `meta.generated_at` (the Corral nesting) rather than the top-level `generated_at` rogue uses.
- `~/rogue/ai-workspaces/project-manager/dashboard/requirements.txt`: shows `watchdog` is the exemplar's watch dependency (PyYAML + watchdog).
- `./ai-infrastructure/project-manager/dashboard/etl.py`: the file to extend. `run_etl(repo_root, served_dir)` (around line 265) is the build function; the `__main__` block (around line 481) reads the `REPO_ROOT` and `SERVED_DIR` env vars and calls `run_etl`. The `--watch` argparse wiring wraps this. The documented ETL source set is in the module docstring (STATUS.md, tasks/, decisions/, OBSERVATIONS.md, department STATUS/decisions/OBSERVATIONS, `.claude/commands`); the allowlist mirrors that set.
- `./ai-infrastructure/project-manager/dashboard/Dockerfile`: the current multi-stage build. The serve stage installs `PyYAML==6.0.2` and the CMD is `python /app/etl.py && python -m http.server 8420 --directory /served --bind 0.0.0.0`. This CMD and the pip install line are what change.
- `./ai-infrastructure/project-manager/dashboard/src/App.jsx`: the SPA root. The existing on-mount `useEffect(() => { fetch('./data.json')... }, [])` (around lines 22-30) is the one-shot fetch the poller augments; `data.meta.generated_at` is the change key, and `setData` (line 18) is the soft-re-render hook.
- `./ai-infrastructure/project-manager/dashboard/docker-compose.yml`: read for context only (the read-only `/repo` bind mount, port 8420). It is NOT edited.

## Related tasks and ADRs

- COR-T-014: built the dashboard (ETL + React SPA + Dockerfile + compose); this task extends that artifact.
- COR-T-017: most recent ETL/contract change (roadmap sub-milestones); confirms the `data.json` contract and the `etl.py` structure.
- COR-T-018: an open backlog task for a standalone one-shot ETL compose target; ADJACENT but separate. The single-container background watch partially overlaps its motivation but does not resolve it; do NOT touch COR-T-018 or `docker-compose.yml` for it.
- ADR-003: docker-compose is the only supported run path; the watch stays inside the existing compose service, no off-compose run path introduced.
- ADR-008: the dogfood seam; the dashboard reads markdown now and repoints to the app then. This watch is a markdown-era convenience.
- ADR-027: the dashboard is ADR-027 Fork E (the project-manager insight dashboard).

## STATUS deltas

No task-specific STATUS deltas; universal hygiene only. (Universal hygiene per WORKER-ROLE.md: bump `last_updated`, append a `recent_updates` entry. No phase change, no "Next step" rewrite, no "Blocked on" edit for this task.)

## Hard rules

- **Mirror, do not redesign.** The watch and poll designs are pinned to the rogue exemplar's proven patterns. Adapt only the named divergences (`PollingObserver` over `Observer`; Corral's `REPO_ROOT` trees; `run_etl` over `build()`; soft `setData` over `location.reload()`; `meta.generated_at` over top-level `generated_at`). Do not introduce a different watch mechanism, a websocket/SSE channel, or a poll interval other than 5000ms.
- **One-shot default stays byte-for-byte equivalent.** With no `--watch` flag, `etl.py` must behave exactly as today: build once, exit. The flag is purely additive.
- **The `data.json` contract is frozen.** Do not change its shape, its keys, or where `meta.generated_at` lives. The poller is a read-only consumer of the existing field.
- **Watcher non-fatal both layers.** A rebuild exception must not kill the watch loop (catch and log to stderr). A dead background watch process must not stop the foreground server.
- **Poll-error tolerance.** A failed poll fetch must never clear data or show the error screen; only the initial-load failure shows the error screen, as today.
- **Verification is compose-only (ADR-003).** If you verify the live behavior, do it through `docker compose` against the existing service; do not assume host-installed Python or Node. Stage changes; do not commit (the Orchestrator commits at the task's resolve gate). The live render is a user-confirmed surface; report what you verified and what the user should confirm in a browser.

## Worker pointer

You are the dispatched `worker-agent` (ADR-028). Universal Worker conventions (the report shape, the dual-channel write, run policy, git boundaries, file-edit hygiene, STATUS hygiene) live in `./docs/ai-orchestration/roles/WORKER-ROLE.md`; follow them rather than re-deriving them here. Write your closing report to `./.claude/artifacts/handoffs/COR-T-020-KICKOFF-REPORT.md` per WORKER-ROLE.md, section "Report shape".
