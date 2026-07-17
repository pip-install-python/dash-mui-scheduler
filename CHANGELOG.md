# Changelog

All notable changes to **dash-mui-scheduler** — the Plotly Dash wrapper for the
MUI X Scheduler (EventCalendar, EventCalendarPremium, EventTimeline) and its
Radial chart components (RadialLineChart, RadialBarChart) — are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/).

> The petri-dish evolution game this component grew up alongside now lives in its
> own project (2plot.xyz); its 0.4.x–0.5.x history moved with it.

## [Unreleased]

## [0.1.0] - 2026-07-16

First public release — the component library on PyPI (`pip install
dash-mui-scheduler`) and its documentation site, split out of the 2plot.ai
monolith.

### Added
- **Five Dash components** wrapping MUI X: `EventCalendar`,
  `EventCalendarPremium`, `EventTimeline`, `RadialLineChart` and
  `RadialBarChart` — with recurrence, drag & resize, inline editing, resources,
  preferences, localization/timezones, and MUI X Premium features via a
  `licenseKey` prop.
- **The full 2plot network in the sidebar** — the "2plot network" section now
  lists every application and tool in the network: 2plot.xyz (the game),
  2plot.ai (the hub), 2plot.media (videography), PiratesBargain (commerce), and
  ai-agent.buzz (the infinite AI canvas).
- **`skills.md`** — an agent-facing usage guide for the component library
  (component picker, the events/`lastAction` data boundary, prop cheat sheets,
  radial chart patterns, gotchas). Ships inside the PyPI source distribution
  alongside the README.
- **Documentation site** with live examples: 14 scheduler pages (Quickstart,
  Event Calendar, Playground, Events, Resources, Views, Navigation, Responsive,
  Drag & Resize, Editing, Preferences, Recurrence, Event Timeline,
  Localization & Timezones) and 3 radial chart pages, each with an LLM-friendly
  `/llms.txt` mirror, sitemap, and social cards.
- **Pluggable Dash 4.2 backends** — runs on Flask or FastAPI (`DASH_BACKEND`);
  the FastAPI build ships `/healthz`, `/api/backend`, `/api/pages`, and Swagger UI.
- **Optional sign-in, off by default** — the site runs fully public; setting the
  Clerk environment variables later flips on 2plot-network sign-in with no code
  change.

### Changed
- **Professional README** — rewritten with a centered header, badges, community
  links, and a fuller tour (overview, quick start, data boundary, Premium
  licensing, recurrence and radial chart samples, selected prop reference).
- **Repo hygiene** — the local `.claude/` agent scaffold is no longer tracked
  in git.

### Fixed
- **Chart image export no longer fails.** Exporting a radial chart to PNG (or
  printing it) made the bundle fetch a code-split chunk the package never
  registered with Dash, so the request came back a 500 and the export died. The
  chunk is now registered and served on demand.
- **The header no longer types out "Petri Dish."** A leftover animation script
  from the departed evolution game overwrote the "dash-mui-scheduler" brand text
  in the header on every page load.
- **Premium license key now reaches every live example.** The docs read
  `MUI_X_LICENSE_KEY`, but the environment only provided `MUI_PRO_API_KEY` — so
  every Premium demo (recurrence, timeline, radial charts) rendered the
  "Missing license key" watermark. `.env` now aliases the key and the Render
  blueprint supplies `MUI_X_LICENSE_KEY` directly.
- **Loading screen no longer 404s** — its logo still pointed at the departed
  2plot artwork; it now uses the dash-mui-scheduler logo, and the console is
  clean on every docs page.
- **Render blueprint URL corrected** — `APP_BASE_URL` said
  `dash-mui-scheduler.onrender.com` while the service name resolves to
  `dash-mui-scheduler-docs.onrender.com`; sitemap/llms/social links would have
  pointed at a dead host.

