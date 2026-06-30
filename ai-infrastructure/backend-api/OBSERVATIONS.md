# Observations

Append-only log of recurring patterns, friction points, and notable one-offs seen while working in the `Backend API` department. Convention inherited from the coordinator workspace (see `ai-infrastructure/project-manager/OBSERVATIONS.md`).

## Conventions

- Stable IDs: `API-NN`, monotonically increasing, never reused.
- Lifecycle: **seen-once** (handled ad hoc, not yet logged) -> **logged** (an entry below, with context) -> **promoted** (canonicalized into a rule, template, role doc, or ADR; the entry records where it went).
- Entries are never edited after the fact except to update their lifecycle state and promotion pointer.

## Entry format

```markdown
### API-NN: short title
- date: YYYY-MM-DD
- state: logged | promoted -> <where>
- context: what happened, where
- pattern: why this might recur / what to do about it
```

## Log

### API-01: a deferred backlog task's premise drifts when later tasks edit the shared surface
- date: 2026-06-30
- state: logged
- context: API-T-005 (filed 2026-06-15 off the API-T-002 report) describes its target cost as the FastAPI lifespan firing per test because the `client` fixture "builds the ASGI app per test." Verified against disk 2026-06-30: the app is imported once at module scope in `app/api/tests/conftest.py` (`from app.api.main import app as fastapi_app`; `app = create_app()` runs once at import); the `client` fixture only wraps that one app in a fresh httpx `ASGITransport` per test; and plain `ASGITransport` does not run the lifespan (no `LifespanManager` / `asgi-lifespan` in the suite, so `app/api/main.py`'s lifespan `seed_admin()` does not fire through the test client). The real per-test seed cost is the explicit `seed_admin()` calls inside individual test fixtures (`test_auth_login.py:51`, `test_sessions.py:53`, `test_admin_seed.py`) plus the autouse `reset_auth_tables` TRUNCATE. The suite is now 30 `test_` functions across 5 files, up from the ~19 the task cites. Likely cause of the drift: API-T-004/006 edited the api test harness (including fail-fast seed tests) after API-T-005 was filed.
- pattern: a backlog task's diagnosis can silently go stale when later tasks edit the same shared surface (here, the api test harness). Re-verify a deferred task's stated premise against current disk at pickup time, before drafting its kickoff, and re-anchor `decisions_resolved` on the verified cost source rather than the originally-filed one.
