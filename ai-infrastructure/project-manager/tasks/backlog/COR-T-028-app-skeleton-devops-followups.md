---
schema_version: 1
id: COR-T-028
title: "app/ skeleton devops follow-ups: dependency policy, .dockerignore, compose naming"
status: backlog
labels: []
priority: P3
created: 2026-06-11
updated: 2026-06-11
---

## Description

Three cross-cutting devops follow-ups surfaced by the DB-T-001 worker (the first `app/` skeleton, committed in `74de6b2`). All are low-severity and non-blocking: the schema/migration deliverable is correct as-is. They concern the shared `app/` foundation that every web-app department (backend-api P2-2, mcp-server Phase 3, frontend Phase 4) will extend, which is devops-domain infrastructure, not database/schema work. They are held here because the `devops` department is not created yet (lazy creation, ADR-021/ADR-027). This is the coordinator acting as the interim catch-all for unassigned cross-cutting work; relocate this task to the devops `tasks/` tree (with that department's prefix) when devops is stood up, mirroring the COR-T-024 -> DB-T-001 relocation precedent (ADR-031).

The three items, grounded in files on disk under `app/`:

1. **Python dependency-management approach for `app/` (`app/db/requirements.txt`).** The file pins `alembic==1.13.3` and `psycopg2-binary==2.9.10`, chosen as "latest stable at authoring time," not against a project-wide policy. There is no lockfile, no hash pinning, and no shared constraints file, so when backend-api adds its own Python deps under `app/` the two can drift or conflict. Decide the approach (a shared constraints/lock file, `uv`/`pip-tools`, or per-service `requirements`), and reconsider `psycopg2-binary` (the `-binary` build is conventionally dev/test; production usually wants `psycopg[c]` or a source build). **ADR candidate:** this is precedent-setting for every web-app service; promote to a pending ADR when devops picks it up.

2. **Add a `.dockerignore` for `app/db/` (and the shared `app/` topology).** `app/db/Dockerfile` ends with `COPY . .` and there is no `.dockerignore`, so the whole directory enters the build context and image. Negligible today (the dir is tiny), but as `app/` fills out this balloons build contexts and risks baking in unwanted files, notably a real `.env` if one ever lands next to `.env.example` (a secret-hygiene risk per ADR-006). Add a `.dockerignore` excluding `.env`, `__pycache__/`, `*.pyc`, VCS dirs, etc.

3. **Explicit compose project/service naming for the shared `app/` topology (`app/docker-compose.yml`).** The compose file sets no `name:`, so Docker derives the project name from the directory (`app`), producing implicit container/network names; this implicit project name is what produced the orphan-container warning the DB-T-001 worker saw. Every web-app department inherits this same file when it adds services, so with no documented convention you get collisions/ambiguity as services multiply. Set an explicit `name:` and document the service/network naming convention for the shared `app/` topology. **ADR candidate:** this is precedent-setting for the shared topology; promote to a pending ADR when devops picks it up.

Source of record: the DB-T-001 closing report (`.claude/artifacts/handoffs/DB-T-001-KICKOFF-REPORT.md`, "Follow-ups") and this task's predecessor discussion. Out of scope: any change to the DB-T-001 schema/migration (done and committed); creating the devops department (a separate lazy-creation step).

## Activity log

- 2026-06-11: Created in backlog. Triaged from the DB-T-001 worker report's Follow-ups (items 2-4; item 1, the orphan container, was already resolved during the close re-run). Held in the coordinator tree as the interim catch-all because the devops department does not exist yet (lazy creation, ADR-021/ADR-027); relocate to the devops tasks tree on creation per the COR-T-024 -> DB-T-001 precedent (ADR-031). P3: all three are low-severity and non-blocking. Items 1 and 3 flagged as pending-ADR candidates (precedent-setting for the shared app/ topology). Unlabelled per ADR-031 (dept:* applied at the dogfood import, not hand-applied here).
