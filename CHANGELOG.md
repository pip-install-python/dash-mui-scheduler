# Changelog

All notable changes to **dash-mui-scheduler** — the Plotly Dash wrapper for the
MUI X Scheduler (EventCalendar, EventCalendarPremium, EventTimeline) and its
Radial chart components (RadialLineChart, RadialBarChart) — are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/).

> The petri-dish evolution game this component grew up alongside now lives in its
> own project (2plot.xyz); its 0.4.x–0.5.x history moved with it.

## [Unreleased]

## [0.1.1] - 2026-08-01

### Added
- **The docs site is now on the 2plot network standard**, the baseline proven on
  2plot.ai, 2plot.dev and the other satellite documentation sites:
  - **A test suite and CI/CD pipeline, from zero.** Every pull request now runs a
    secretless test suite on both the Flask and FastAPI builds, lints the code and
    the workflows themselves, builds the real production image, checks the shipped
    dependency versions inside it, boots it, and runs the same smoke battery that
    later checks the live site. Merging to `main` deploys and then verifies the
    live domain — waiting for *sustained* health before calling the deploy good.
  - **One identity on every surface.** The site now states what it is —
    *dash-mui-scheduler — MUI X scheduling for Dash* — identically in the browser
    tab, in search results, in shared-link previews, in the machine-readable
    `/llms.txt` index, in its app manifest and atop the README, and a test pins
    each surface so none of them can silently drift.
  - **A proper share card.** Links shared to Slack, Discord, X or LinkedIn will
    unfurl with a purpose-drawn 1200×630 card served from the network CDN (so a
    sleeping free-tier container never blanks a preview) instead of an upscaled
    favicon.
  - **The network bulletin.** The hub's tips and announcements now render in the
    documentation's llms.txt viewer once `NETWORK_BULLETIN_URL` is set on the
    service, so network-wide news reaches this site's readers without a deploy.
  - **Honest analytics.** The network's own machinery — health sweeps, smoke
    batteries, this site's calls to the hub — now identifies itself and is
    dropped from visitor analytics before it is ever written down — however the
    marker is capitalised — and every
    outbound call this site makes carries the same marker for the far side. The
    site reports to the hub under its one short id, `muischeduler`, everywhere.
  - `/healthz` on every backend (previously FastAPI-only), answering the hub's
    hourly health sweep and gating deploys.
  - **The cross-host network directory** — `/llms.txt` now lists the sibling
    documentation sites and the hub, so an agent landing here can discover the
    rest of the network.

- **Walkthrough video** — a video tour of the calendar, resource timeline, and
  radial charts now sits near the top of the Quickstart page **and on the
  documentation home page**, so a reader landing on the docs can watch it
  without going to GitHub first. The README header carries a clickable
  thumbnail linking to the same walkthrough. Both embeds use YouTube's
  no-cookie player, so nothing is set until you press play.
- **Richer search-result data** — the site now describes itself to search
  engines as what it is: an MIT-licensed Python source library with a
  repository, a PyPI download page, a version number read straight from the
  package, and the walkthrough video attached.
- **The docs site now reports its traffic to 2plot.ai**, the analytics home for
  the whole 2plot network. Once an hour it sends a signed daily rollup — page
  hits split human/bot, unique visitors, sessions, median session length, top
  pages and visitor countries — so the network dashboard shows how the
  documentation is actually being read. Reporting only happens when the shared
  network secret is configured; without it the site behaves exactly as before
  and makes no outbound calls.

### Changed
- **The maintainer's home is now [2plot.dev](https://2plot.dev).** Every link
  that pointed at the retired `pip-install-python.com` domain — in the README,
  the sidebar, the site's structured data and the cross-host directory — now
  points at 2plot.dev, and the README opens with the 2plot banner.
- **Fresher, safer dependencies.** The AI/SEO layer (`dash-improve-my-llms`) now
  installs from PyPI at ≥ 2.3.4 instead of a vendored 2.0.0 snapshot; the
  `gunicorn` web server is floored at ≥ 23 (clearing two request-smuggling
  CVEs its old pin was stuck on); and the optional Clerk auth package moves to
  0.9.1, the release that fixes the account chip on satellite domains.
- **The documentation has its own home: [muischeduler.2plot.dev](https://muischeduler.2plot.dev).**
  Everything the site publishes about itself — search-engine addresses, shared-link previews,
  the sitemap, the machine-readable pages — now points there, and the README and the PyPI
  listing send readers to the docs rather than back to the repository. The old
  `onrender.com` address keeps working and forwards to the new one, so existing links and
  bookmarks survive the move and search engines are told where the pages went.

### Fixed
- **The browser-tab and home-screen icons now show the actual logo.** Every
  favicon size, the app-install icons and the iOS home-screen icon are drawn
  fresh from the vector logo instead of the blurry upscale they were before.
- **A bad analytics-ledger path can no longer take the whole site down.**
  Pointing `TRAFFIC_ANALYTICS_FILE` at a persistent-disk path before the disk
  existed crashed every worker at boot, so the deploy never went live and the
  old build kept serving. The tracker now creates the directory when it can,
  and when the path is truly unwritable it disables itself with a clear log
  line — the site serves either way, and a test pins both behaviours.
- **Search engines were being told this site is a copy of a site that does not
  exist.** The page template still carried the URL it was built with
  (`dash-mui-scheduler.onrender.com`) rather than the address the docs actually
  live at, and it claimed that one address for all 17 pages at once — the
  fastest way for a site to fall out of the index entirely. Every page now
  declares its own correct address, kept in step as you navigate, and every
  link the site publishes about itself is built from a single setting.
- **Every page was announcing itself as the home page.** The template carried
  its own copy of the title, description and social tags, which overrode the
  per-page ones — so a search result or shared link for, say, *Recurrence*
  showed the site blurb instead of the page's. The per-page text now wins
  everywhere, including for search-engine and link-preview crawlers, and shared
  links unfurl with the project logo and the right page's title.
- **Visitor counts and countries are now measured at the edge, not at the
  proxy.** Behind Render/Cloudflare every request looked like it came from the
  same address, which collapsed all visitors into one and mislabelled where
  readers came from; the site now reads the forwarded client address and the
  edge country header. Visitor geography also no longer costs a lookup on the
  request path.
- **The visitor ledger no longer grows without limit** — it is capped (default
  20,000 hits) so a long-running deployment doesn't slow every page view down.

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

