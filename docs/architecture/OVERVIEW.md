# Architecture Overview

The intended runtime shape. Nothing here is built yet (see `../../STATUS.md`); this page records the target so every other doc can point at one picture. Decision rationale lives in `../../decisions/`, not here.

## Runtime shape

Four services under docker compose (ADR-003):

```
                       docker compose
  +-----------------------------------------------------------+
  |                                                           |
  |  [frontend]  ----HTTP---->  [api]  <---SQL--->  [postgres]|
  |   React kanban client       FastAPI                       |
  |                               ^                           |
  |                               | (data path per ADR-010)   |
  |                            [mcp]                          |
  |                         FastMCP server                    |
  +-------------------------------^---------------------------+
                                  |
                         LLM agents (orchestrators,
                         workers) connect ONLY here
```

- **postgres**: owns all tracker data: issues, labels, views (schema ADR-012); users, invites (schema pending, ADR-011).
- **api**: FastAPI. Serves the client, enforces auth (ADR-011), seeds the admin user from `.env` on first boot (ADR-006), mints invite tokens (ADR-007).
- **frontend**: React kanban client. Multiple views over the same database, each with a label filter (ADR-001); build/dev workflow pending (ADR-015).
- **mcp**: FastMCP server, the sole seam for LLM agents (ADR-004). Tool surface and house rules pending (ADR-013). It calls the api service over HTTP per ADR-010 and never touches postgres directly.

## The two domains

Per ADR-005, the repo also contains a second system that never ships in a container: the AI infrastructure (role docs, agent definitions, specs, the task convention in `../../tasks/`) that builds and maintains the four services above.

## Invariants

1. LLM agents touch tracker data only through the mcp service (ADR-004). Until that service exists, the interim seam is the markdown task convention (ADR-008).
2. No secrets in the source tree; deployment credentials arrive via gitignored `.env` (ADR-006).
3. docker compose is the only supported run path (ADR-003).
