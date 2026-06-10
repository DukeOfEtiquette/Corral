## Deliverables completed

All four deliverables shipped:

1. `./ai-infrastructure/project-manager/dashboard/etl.py` - `--watch` mode added.
   - `argparse`, `threading`, `time` imports added at the top.
   - `WATCH_PATTERNS` allowlist (two compiled regexes: `ai-infrastructure/.*\.md$` and `.claude/commands/.*\.md$`) and `is_watched(path_str)` predicate added before `__main__`.
   - `run_watch(repo_root, served_dir)` function added: uses `PollingObserver` (bind-mount safe), debounces at 350ms via `threading.Timer(0.35, do_rebuild)` cancel/restart pattern, filters to `CONTENT_CHANGE_EVENTS = {"modified", "created", "deleted", "moved"}`, skips `event.is_directory`, checks `is_watched(src) or is_watched(dest)`, watches `ai-infrastructure/` and `.claude/commands/` under `REPO_ROOT` with `recursive=True`, calls `run_etl(repo_root, served_dir)` and wraps in `try/except` (non-fatal rebuild failures logged to stderr).
   - `__main__` block replaced with an argparse parser (`--watch store_true`); one-shot default unchanged; `run_watch` called only when `--watch` is set.

2. `./ai-infrastructure/project-manager/dashboard/Dockerfile` - watchdog added, entrypoint updated.
   - `pip install` line changed from `PyYAML==6.0.2` to `PyYAML==6.0.2 watchdog==4.0.2`.
   - New `COPY entrypoint.sh /app/entrypoint.sh` and `RUN chmod +x /app/entrypoint.sh` lines added.
   - `CMD` changed from inline shell chain to `CMD ["/app/entrypoint.sh"]`.

3. `./ai-infrastructure/project-manager/dashboard/src/App.jsx` - 5000ms poller added.
   - A second `useEffect` (deps `[]`) adds a `setInterval` at 5000ms.
   - Each tick fetches `./data.json` with `{ cache: 'no-store' }`.
   - Compares `fresh.meta.generated_at` to `current.meta.generated_at`; calls `setData(fresh)` only on a change (soft re-render; no `location.reload()`).
   - Errors in the poll block are swallowed; existing data is never cleared by poll failures.
   - Returns `() => clearInterval(id)` as cleanup so the interval is removed on unmount.
   - Initial one-shot `useEffect` unchanged.

4. `./ai-infrastructure/project-manager/dashboard/entrypoint.sh` (new) - chosen over inline CMD.
   - `set -e` stops the script on error during the initial ETL build.
   - Runs `python /app/etl.py` (initial build; fatal if it fails, per normal start-up contract).
   - Runs `python /app/etl.py --watch &` as a background process.
   - `exec python -m http.server 8420 --directory /served --bind 0.0.0.0` is the foreground process; background watch death does not stop the server.

## Decisions made

- **entrypoint.sh over inline CMD**: the three-step sequence (initial build, background watch, foreground exec) is cleaner as a shell script than a single CMD string. The kickoff explicitly named this as acceptable.
- **`set -e` scope**: `set -e` applies to the initial ETL build and the background-watch launch line. Once `exec python -m http.server` replaces the shell process, `set -e` no longer applies; this is the correct model: the initial build failure is fatal (container should not serve stale/absent data.json), but a background watch crash is not.
- **`setData` functional updater in App.jsx**: the poller uses `setData((current) => ...)` (functional form) rather than closing over the `data` state variable. This avoids a stale closure in the interval callback and ensures the comparison always reads the latest rendered value without adding `data` to the `useEffect` dependency array (which would restart the interval on every data change).
- **watchdog pin `4.0.2`**: the kickoff named this as the current stable equivalent and the pinned-style example. Confirmed as the stable release consistent with the rogue `requirements.txt` constraint (`watchdog>=4.0`).

## Surprises

- The rogue exemplar's `run_watch` calls `build()` and starts the observer before the initial build. Corral's `__main__` block does the initial `run_etl` call first, then optionally calls `run_watch`. This matches the kickoff's intent and is the correct order; no issue, but it is a minor structural divergence from rogue (where the build-then-watch sequence is inside `main()` in that same call site).
- The existing `__main__` block had no argparse at all (just direct `run_etl`). The replacement is fully backward-compatible: `python etl.py` with no args still calls `run_etl` once and exits.

## Follow-ups

- **COR-T candidate: confirm PollingObserver latency in the running container.** `PollingObserver` polls on a 1-second default interval; file changes may see up to ~1.35s latency before the rebuild triggers (1s poll + 0.35s debounce). If the user finds this too slow, the poll interval can be set in `PollingObserver(timeout=N)`. No change needed now; note for runtime observation.
- **COR-T candidate: end-to-end live behavior confirmation.** The browser auto-refresh (markdown edit triggers ETL rebuild and open page soft-re-renders) requires a compose run plus a browser. This is the user-confirmed surface per the kickoff's verification note; the Orchestrator should confirm at the close gate via `docker compose up --build` in `./ai-infrastructure/project-manager/dashboard/`.
- **COR-T-018 (standalone ETL compose target) remains open.** The background watch introduced here partially overlaps COR-T-018's motivation but does not resolve it; the kickoff explicitly called this out as adjacent. No change made to COR-T-018 or docker-compose.yml.

## Files touched

- `./ai-infrastructure/project-manager/dashboard/etl.py` (modified)
- `./ai-infrastructure/project-manager/dashboard/Dockerfile` (modified)
- `./ai-infrastructure/project-manager/dashboard/src/App.jsx` (modified)
- `./ai-infrastructure/project-manager/dashboard/entrypoint.sh` (new)
- `./ai-infrastructure/project-manager/STATUS.md` (universal hygiene: last_updated bumped, one recent_updates entry appended)
- `./.claude/artifacts/handoffs/COR-T-020-KICKOFF-REPORT.md` (this report, dual-channel write)

## Build / verification status

Verified at the code/CLI level:

- `etl.py` parsed cleanly by `python3 -m ast` (syntax OK).
- All key patterns confirmed present in `etl.py` via grep: `PollingObserver`, `threading.Timer(0.35`, `CONTENT_CHANGE_EVENTS`, `event.is_directory`, `recursive=True`, `argparse`, `--watch`, `run_watch`, `run_etl`.
- No em dashes in any written file (grep confirmed).
- `Dockerfile` shows the correct `watchdog==4.0.2` pin and the `CMD ["/app/entrypoint.sh"]` entrypoint.
- `App.jsx` initial fetch unchanged; poller `useEffect` has `setInterval` at 5000ms, `cache: 'no-store'`, `meta.generated_at` key path, functional `setData`, and `clearInterval` cleanup.
- `entrypoint.sh` has `set -e`, initial build, background watch (`&`), and `exec http.server` foreground.
- One-shot default (`python etl.py` with no `--watch` flag): code path is `run_etl(repo_root, served_dir)` then exits; `run_watch` is not called. Unchanged from prior behavior.

Not yet verified (requires compose run + browser):

- End-to-end live behavior: a markdown source edit triggers an ETL rebuild within ~1-2 seconds and the open browser tab soft-re-renders the new data within ~5 seconds. This is the user-confirmed surface; run `docker compose up --build` from `./ai-infrastructure/project-manager/dashboard/` to confirm.
- Container startup: the entrypoint runs the initial ETL, the background watcher starts, and `http.server` serves on port 8420.
