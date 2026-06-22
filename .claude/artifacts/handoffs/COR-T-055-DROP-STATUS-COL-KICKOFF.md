# COR-T-055 refinement: drop the Status column from the services panel

## Target

This is AI-infrastructure work (domain 2, per ADR-005). It refines the services panel authored under COR-T-055. The artifact in scope is the dashboard React component `ai-infrastructure/project-manager/dashboard/src/panels/ServicesPanel.jsx`, which already exists and renders a Services table. This dispatch removes one column (Status) from that table and nothing else. The operator's direction is that the Status column is redundant and should be dropped, while the underlying `status` field stays in the data and continues to drive the planned-row styling.

## Decisions resolved by the Orchestrator

- **Scope is a single view-only change to one file.** `ServicesPanel.jsx` already renders a Services table; this dispatch ONLY removes the Status column from that table. No ETL, data-shape, or `data.json` change is in scope. Rationale: operator direction is that the Status column is redundant in the rendered view.
- **Remove the Status column entirely.** Delete the `Status` `<th>` header cell and the corresponding status `<td>` body cell. After the change the columns are exactly, in order: Service, Domain, Host:Port, Endpoints, Owner. In the current file the header `<th>Status</th>` is at line 22 and the body cell `<td>{svc.status}</td>` is at line 83; both are removed.
- **Preserve the status-driven planned-row styling unchanged (CRITICAL).** The `status` field stays present in each service object and MUST still drive the planned-row styling. The existing logic that computes `isPlanned` from `svc.status === 'planned'` and applies the `dept-planned` row class (line 30 `const isPlanned = svc.status === 'planned';` and the `rowClass` ternary at lines 32-36, applied via `className={rowClass}` at line 74) stays exactly as-is. Planned services (mcp, frontend) remain visually distinguishable by their muted row even though the Status word is no longer shown in a column. Do NOT remove or alter the status-based row-class logic; only the visible Status column (header cell plus body cell) is removed.
- **Do not change the data path.** The `status` field continues to be emitted by the ETL and read by the component; this is a view-only change removing one column, not a data change.
- **Touch no other file.** Not the ETL, not the `services.yml` data files, not `LandingView.jsx`, not other panels. Reuse existing CSS; no `styles.css` change is expected.

## Deliverables

- `ai-infrastructure/project-manager/dashboard/src/panels/ServicesPanel.jsx` modified so the rendered table no longer has a Status column (the `<th>` header cell and the status `<td>` body cell are both removed), while the status-driven planned-row styling (`isPlanned`, `rowClass`, `dept-planned`) is preserved unchanged. Final columns, in order: Service, Domain, Host:Port, Endpoints, Owner.

## Files in scope

- `ai-infrastructure/project-manager/dashboard/src/panels/ServicesPanel.jsx` (modify)

## Files out of scope

- `ai-infrastructure/project-manager/dashboard/etl.py` (do not touch; the `status` field stays in `data.json`)
- `ai-infrastructure/project-manager/dashboard/src/views/LandingView.jsx` (do not touch)
- `ai-infrastructure/project-manager/dashboard/src/styles.css` (no change expected)
- the `services.yml` data files and all other dashboard panels (do not touch)

## References

- `docs/ai-orchestration/roles/EXECUTOR-ROLE.md` (the Executor role and the pinned six-section closing report shape)
- `ai-infrastructure/project-manager/dashboard/src/panels/ServicesPanel.jsx` (the file to modify; the `Status` `<th>` at line 22 and the `<td>{svc.status}</td>` at line 83 to remove, and the `isPlanned` / `rowClass` / `dept-planned` row-class logic at lines 30-36 and 74 to preserve)

## Related tasks and ADRs

- COR-T-055 - the parent task; this refines its services panel.
- ADR-045 - defines the service schema (the `status` field that drives the row styling).

## Hard rules

- Remove BOTH the Status `<th>` header cell and the status `<td>` body cell. Removing only one leaves the header and body rows with a mismatched column count.
- Do NOT remove or alter the `isPlanned` computation, the `rowClass` ternary, or the `className={rowClass}` application. The `status` field continues to drive the muted planned-row styling even though the Status column is gone.
- This is a single-file, view-only change. No ETL, data, `services.yml`, or `styles.css` edits.

## Verification expectations

- A grep or read of `ServicesPanel.jsx` confirms there is no Status column header and no status data cell remaining in the table, and that the table header row and each body row have a consistent, equal column count: Service, Domain, Host:Port, Endpoints, Owner.
- The status-based planned-row styling logic is still present: `svc.status === 'planned'` still computes `isPlanned`, and planned services still receive the `dept-planned` row class.
- The rendered panel is a visual surface. The Orchestrator obtains user-facing visual confirmation via docker compose; the closing report should state the result renders pending that visual check rather than asserting the render directly.

## Executor pointer

The executor is the dispatched `executor` (ADR-028). Universal executor conventions (the writing rules and Agent Discipline in the repo-root `CLAUDE.md`, the docker-compose-only run policy, git boundaries, the file-edit hygiene rules) live in `docs/ai-orchestration/roles/EXECUTOR-ROLE.md`; follow them rather than re-deriving them here. Write the closing report in the pinned six-section shape per `docs/ai-orchestration/roles/EXECUTOR-ROLE.md`, section "Report shape", to the derived report path next to this kickoff.
