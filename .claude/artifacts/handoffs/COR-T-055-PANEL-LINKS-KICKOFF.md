# COR-T-055 refinement: render localhost service addresses in the services panel as new-tab links

## Target

This is AI-infrastructure work (domain 2 per ADR-005). It is a small refinement to the dashboard services panel authored under COR-T-055 Dispatch 2. The panel `./ai-infrastructure/project-manager/dashboard/src/panels/ServicesPanel.jsx` already exists and is already wired into LandingView. This dispatch changes ONLY how service addresses render inside that panel: localhost addresses become clickable links that open in a new tab. Nothing else about the panel changes.

Operator rationale for the refinement: clickable links let a reviewer open each service address directly; a 404 on click is a useful "server is down or buggy" signal either way.

## Decisions resolved by the Orchestrator

- **Scope is link rendering only.** This dispatch changes how the Host:Port and Endpoints cells render their values; it adds no columns, changes no data shape, and alters no other behaviour. The columns, the planned-row styling, and the warning-tooltip behaviour stay exactly as they are today.

- **Host:Port column links when `base_url` is non-null.** For a service entry whose `base_url` is non-null, render the displayed host:port value as an anchor: `<a href={base_url} target="_blank" rel="noopener noreferrer">...</a>`, keeping the existing displayed text. For a service entry whose `base_url` is null (the planned `mcp` and `frontend` services, and `postgres`, all of which have `base_url` null), render the existing plain text with NO anchor. Rationale: only services with a usable base URL can be opened in a browser; the rest stay plain text.

- **Endpoints column links each endpoint when `base_url` is non-null.** For a service entry whose `base_url` is non-null, render each endpoint as an anchor whose `href` is `base_url + endpoint.path`, opening in a new tab with the same `target="_blank"` and `rel="noopener noreferrer"`, keeping the existing display text (the path and the kind). For a service entry whose `base_url` is null, render each endpoint as plain text exactly as today. Rationale: an endpoint link is only meaningful when joined to a real base URL.

- **Every new-tab anchor carries `rel="noopener noreferrer"`.** This is standard security hygiene for `target="_blank"` anchors and is required on every anchor this dispatch adds.

- **Styling is reuse-first.** Reuse existing link/anchor styling. Add minimal CSS to `./ai-infrastructure/project-manager/dashboard/src/styles.css` ONLY if the links are visually indistinguishable from plain text and need a basic style to be recognisable as links. If the existing styling already makes anchors visible, do not touch `styles.css`.

- **The data fields are defined by ADR-045.** The `base_url` field and the `endpoints` list of `{path, kind}` entries this dispatch reads are the fields ADR-045 (accepted) pins for each service entry. Read them off the service objects the panel already receives; do not re-derive or reshape them.

## Deliverables

- `./ai-infrastructure/project-manager/dashboard/src/panels/ServicesPanel.jsx` modified so that, for a service with a non-null `base_url`, the Host:Port value is an anchor to `base_url` and each endpoint is an anchor to `base_url + endpoint.path`, all opening in a new tab with `rel="noopener noreferrer"`; a service with a null `base_url` renders the Host:Port value and each endpoint as plain text, unchanged from today.

## Files in scope

- `./ai-infrastructure/project-manager/dashboard/src/panels/ServicesPanel.jsx` (modify: add the anchors to the Host:Port and Endpoints cells)
- `./ai-infrastructure/project-manager/dashboard/src/styles.css` (modify ONLY if a basic link style is genuinely needed per the styling decision above; otherwise leave untouched)

## Files out of scope

- `./ai-infrastructure/project-manager/dashboard/etl.py` (do not touch)
- `./ai-infrastructure/project-manager/dashboard/src/views/LandingView.jsx` (already wired; do not touch)
- `./ai-infrastructure/backend-api/services.yml`, `./ai-infrastructure/database/services.yml`, `./ai-infrastructure/project-manager/services.yml` (data files; do not touch)
- Any other dashboard panel.

## References

- `./docs/ai-orchestration/roles/EXECUTOR-ROLE.md` (the Executor role and the pinned six-section closing report shape)
- `./ai-infrastructure/project-manager/dashboard/src/panels/ServicesPanel.jsx` (the file to modify; its current Host:Port cell builds `hostPort` and its Endpoints cell builds `endpointPaths`, and these are the cells that get the anchors)
- `./ai-infrastructure/project-manager/decisions/ADR-045-service-endpoint-inventory-structured.md` (the services schema: `base_url` and `endpoints` as a list of `{path, kind}` are the fields rendered here as links)

## Related tasks and ADRs

- COR-T-055 - the parent task; this dispatch refines the services panel authored under its Dispatch 2.
- ADR-045 - defines the `base_url` and `endpoints` fields that this dispatch renders as links.

## Hard rules

- No behavioural change beyond link rendering. Do not change the columns, the data shape, the planned-row styling, or the warning-tooltip behaviour.
- Every anchor this dispatch adds opens in a new tab (`target="_blank"`) and carries `rel="noopener noreferrer"`.
- A service whose `base_url` is null renders its Host:Port value and its endpoints as plain text, unchanged from today (no anchor).
- The rendered panel is a visual surface. Verification expectations for this task:
  - A grep over the modified `ServicesPanel.jsx` confirms the new anchors carry both `target="_blank"` and `rel="noopener noreferrer"`.
  - A service with a non-null `base_url` (for example `api`, `dashboard`) shows a linked Host:Port and linked endpoints; a service with a null `base_url` (for example `postgres`, `mcp`, `frontend`) shows plain text with no anchors.
  - The rendered panel requires the Orchestrator's user-facing visual confirmation via docker compose. The closing report states that the links render pending that visual check; it does not assert the visual result, which only the user-facing compose render can confirm.

## Executor pointer

The executor is the dispatched `executor` (ADR-028). Universal executor conventions, including the compose-only run policy and the file-edit hygiene rules, live in `./docs/ai-orchestration/roles/EXECUTOR-ROLE.md`. The closing report is written to the derived path next to this kickoff per `./docs/ai-orchestration/roles/EXECUTOR-ROLE.md`, section "Report shape" (dual-channel).
