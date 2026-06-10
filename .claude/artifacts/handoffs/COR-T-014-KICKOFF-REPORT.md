# COR-T-014 Worker Report (attempt 2 - dark theme corrective pass)

## Deliverables completed

Dark theme applied cohesively to the Corral PM Dashboard via a full rewrite of
`ai-infrastructure/project-manager/dashboard/src/styles.css`. All panels and both
views (LandingView, WorkspaceView) are covered. Specific changes:

- CSS custom properties re-toned: near-black page background (#0f1117), dark surface
  (#1a1d27), elevated surface (#21253a for count-badge/code/table-hover), dark borders
  (#2d3147), near-white text (#e2e4f0), muted slate (#7e86a8), single periwinkle
  accent (#6b8cff).
- Site header: darkened to #0c0e17 with a border-bottom instead of box-shadow only;
  logo color changed to var(--color-accent); title and back-link re-toned.
- All badge palettes converted from light-theme pastels to dark-surface equivalents:
  badge-planned, badge-exists, badge-missing, badge-role, badge-domain, badge-phase,
  badge-roadmap-done/current/upcoming, badge-adr-accepted/pending/superseded.
- Hard-coded selector colors updated:
  - .roadmap-current background: #f0f6ff -> #1a2050
  - .roadmap-upcoming border-left: #ced4da -> #3a3f5c
  - .domain-aiinfrastructure: light purple -> dark purple (#251e38 / #b09ee8)
  - .domain-webapp: light teal -> dark teal (#1a2d3a / #7ec8e8)
  - .count-badge background: #e9ecef -> var(--color-surface-raised)
  - code background: #f1f3f5 -> var(--color-surface-raised)
  - .tc-inprogress: hard-coded #0d6efd -> var(--color-accent)
- Added table row hover on non-planned dept rows for usability on dark surfaces.
- Introduced --color-surface-raised as a third surface tier (depth without clutter).

No JSX file required any changes: grep confirmed zero inline style= attributes and
zero hard-coded hex color literals across all .jsx files.

Layout, DOM structure, component tree, routing, data, and all text content are
unchanged (styling only).

## Decisions made

- Accent color: periwinkle blue (#6b8cff). Distinct from status-done green and
  status-danger red, readable at WCAG-AA contrast on #0f1117, and gives the header
  logo, links, and in-progress task counts a coherent identity thread.
- Near-black (not pure black) for page bg (#0f1117) and header (#0c0e17). Avoids
  harsh contrast halos and is more professional on modern displays.
- Near-white text #e2e4f0 rather than #fff. Reduces eye strain in a dark environment.
- --color-surface-raised (#21253a) added as a third surface tier for count-badge, code
  background, and table row hover. Provides subtle depth without requiring a separate
  design token per component.
- Badge color strategy: tinted dark backgrounds with lightened foreground text (e.g.
  #1a3328 / #5ec98a for done-green; #1a2050 / #8aacff for current-blue; #3a1a1e /
  #f08090 for danger-red). All satisfy approximate WCAG-AA at their respective sizes.

## Surprises

- No surprises. The JSX panels are fully class-name-driven. The report from attempt 1
  was accurate: all styling is centralized in styles.css.

## Follow-ups

- COR-T candidate / triage to orchestrator: Consider adding
  `<meta name="color-scheme" content="dark">` in index.html so browser scrollbars
  and native form controls also adopt a dark appearance. One-line change, outside this
  corrective scope (index.html is listed as out-of-scope).
- COR-T candidate / triage to orchestrator: The .roadmap-upcoming opacity: 0.75 rule
  may look slightly washed on very dark monitors. Consider bumping to 0.85 after the
  Orchestrator's visual QA on the rebuilt container.

## Files touched

- `/home/adam/src/corral/ai-infrastructure/project-manager/dashboard/src/styles.css`
  (full dark-theme rewrite)
- `/home/adam/src/corral/.claude/artifacts/handoffs/COR-T-014-KICKOFF-REPORT.md`
  (this report, dual-channel; overwrites prior attempt-1 report per kickoff instruction)

STATUS.md was NOT touched (status_deltas: none; prior pass already applied COR-T-014
hygiene; kickoff explicitly says do not touch STATUS.md).

## Build / verification status

Static self-verification (all checks passed):

- grep -rn "style=" on all .jsx files: zero hits (no inline style attributes).
- grep -rn hex colors on all .jsx files: zero hits (no hard-coded colors in JSX).
- grep for em/en dashes in styles.css: zero hits.
- All badge class selectors confirmed present in dark-theme rewrite (17 badge variants
  verified by reading the final file against the JSX className usage).
- .roadmap-current background confirmed as #1a2050 (not the prior light #f0f6ff).
- .domain-* selectors confirmed dark-toned.
- code and .count-badge confirmed to reference var(--color-surface-raised).
- No .md files added inside dashboard/.
- No out-of-scope files touched.

Runtime/visual gate delegated to the Orchestrator: rebuild the container and screenshot
the dashboard to confirm the dark theme renders correctly on LandingView (landing) and
WorkspaceView (per-workspace detail). Run with:

```
cd ai-infrastructure/project-manager/dashboard
docker compose up --build
```

Then open http://localhost:8420 and http://localhost:8420/#/workspace/project-manager.
