---
schema_version: 1
department: "{{DEPT_SLUG}}"
last_updated: "{{DATE}}"
recent_updates:
  - "{{DATE}}: Department workspace created via /create-department."
---

# Status

Single source of truth for current progress in the `{{DEPT_NAME}}` department. Update at the end of any session that makes progress.

## Current phase

**Newly created.** The `{{DEPT_NAME}}` department workspace has been scaffolded. No work has been dispatched yet. The department's scope is: {{DEPT_SCOPE}}

## Next step

File the first task in `ai-infrastructure/{{DEPT_SLUG}}/tasks/backlog/` with a `{{DEPT_TASK_PREFIX}}-T-001` ID and route it through the `/{{DEPT_SLUG}}-orchestrator` dispatched-worker flow.

## Blocked on

Nothing. The workspace is ready for work.
