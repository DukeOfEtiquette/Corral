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

Pick up the first `dept:{{DEPT_SLUG}}`-tagged task from the shared task pool at `ai-infrastructure/project-manager/tasks/` and route it through the `/{{DEPT_SLUG}}-orchestrator` dispatched-worker flow.

## Blocked on

Nothing. The workspace is ready for work.
