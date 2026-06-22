# COR-T-055 Panel Links - Executor Report

## Deliverables completed

- `./ai-infrastructure/project-manager/dashboard/src/panels/ServicesPanel.jsx` modified so that:
  - For a service with a non-null `base_url`, the Host:Port cell renders as `<a href={svc.base_url} target="_blank" rel="noopener noreferrer">` wrapping the existing `hostPort` text.
  - For a service with a non-null `base_url`, each endpoint in the Endpoints cell renders as `<a href={svc.base_url + ep.path} target="_blank" rel="noopener noreferrer">` with the existing `{ep.path} ({ep.kind})` display text, comma-separated via wrapping `<span>` elements.
  - For a service with a null `base_url`, the Host:Port cell and all endpoint entries render as plain text, unchanged from before this dispatch.
  - All columns, planned-row styling, and warning-tooltip behaviour are unchanged.

## Decisions made

- **No `styles.css` changes needed.** The existing global rule `a { color: var(--color-accent); text-decoration: none; }` and `a:hover { text-decoration: underline; }` (styles.css lines 31-32) already make anchors visually distinguishable on the dark background using accent blue (`#6b8cff`). The styling decision in the kickoff ("add minimal CSS only if links are visually indistinguishable") did not trigger.

- **Endpoint comma separation via `<span key={ep.path}>`** rather than `.join(', ')`. Because the endpoints cell now conditionally renders anchors (React elements, not strings), the plain-string `.join(', ')` approach no longer works for the mixed case. The chosen pattern wraps each endpoint in a `<span>` that prepends `', '` for `i > 0`. This preserves the same visual output (comma-separated list) while keeping the React key hygiene correct.

## Surprises

- None. The file was at the expected path and matched the kickoff's description of the `hostPort` and `endpointPaths` variables. The `endpointPaths` variable (a string built by `.join(', ')`) was replaced by `endpointsCell` (a React fragment built by `.map()`), which required restructuring that cell's rendering path. This was an anticipated consequence of adding conditional anchors, not a surprise.

## Follow-ups

- **Visual confirmation pending user-facing docker compose render (COR-T candidate / triage to orchestrator).** The kickoff hard rule states: "The rendered panel requires the Orchestrator's user-facing visual confirmation via docker compose. The closing report states that the links render pending that visual check; it does not assert the visual result." The link rendering is therefore pending compose verification.

- **Key uniqueness on endpoint path (triage to orchestrator).** The `<span key={ep.path}>` approach assumes endpoint paths are unique per service. If the data could ever have duplicate paths within a service (for example, a path exposed under two kinds), React would warn on duplicate keys. The current `services.yml` data does not duplicate paths per service, but this is worth noting if the schema evolves.

## Files touched

- `./ai-infrastructure/project-manager/dashboard/src/panels/ServicesPanel.jsx`
- `./.claude/artifacts/handoffs/COR-T-055-PANEL-LINKS-KICKOFF-REPORT.md` (this report)

## Build / verification status

Grep verification (kickoff-specified):

- Both new anchors carry `target="_blank"` and `rel="noopener noreferrer"` (confirmed by grep; both appear on lines 49 and 61 of the modified file).
- The `hasBaseUrl` guard (`!!svc.base_url`) ensures services with a null `base_url` render plain text in both cells.

Visual verification pending docker compose render by the Orchestrator/user. No build was run (compose-only run policy per ADR-003; no host-installed Node assumed). The dashboard is a Vite/React app; it requires `docker compose up` to render.
