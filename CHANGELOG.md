# Changelog

All notable changes to **dash-mui-scheduler** — the Plotly Dash wrapper for the
MUI X Scheduler (EventCalendar, EventCalendarPremium, EventTimeline) and its
Radial chart components (RadialLineChart, RadialBarChart) — are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/).

> The petri-dish evolution game this component grew up alongside now lives in its
> own project (2plot.xyz); its 0.4.x–0.5.x history moved with it.

## [Unreleased]

## [2026-08-23] — one headline per page, and a health probe that answers

*Documentation site only; the `dash_mui_scheduler` package is unchanged —
PyPI still carries 1.0.0. Shipped as `d0f4068` and deployed the same
evening.*

### Fixed
- **Every page served crawlers two headlines instead of one.** The
  no-JavaScript block in the page shell opened with its own `<h1>`, and
  crawlers — which run no JavaScript — parse that block, so alongside each
  page's real heading they read a second, site-wide one competing with it.
  The block now starts a level down, and a new sweep checks every published
  page for exactly one headline rather than trusting the shell.
- **The AI/LLM copy of a page can no longer be broken by a code sample that
  quotes the docs' own syntax.** Inlining an example file is triggered by a
  directive; a directive shown *inside* a fenced code block — teaching the
  syntax rather than using it — used to be inlined anyway, which closed the
  fence early and turned the rest of the sample into headings. Fenced
  examples are now left as the documentation they are. No page in this repo
  had one yet; the fix lands before the first one does.
- **`/healthz` answers per request, and says more.** It now reports which
  satellite answered and — where the guardrail package supports it — whether
  geo-blocking is configured, how many countries are on the list (a count,
  never the list itself), and which country the request resolved to. Two
  things had to change for those answers to be true rather than merely
  present: the probe used to be computed once when the app started, so
  anything configured afterwards would have been reported wrong forever, and
  the country a request resolves to has to be read from *that* request —
  which the FastAPI build this site runs in production cannot do unless the
  route hands its own headers along.

### Changed
- **The AI/SEO package floor rises to dash-improve-my-llms 2.7.1.** It buys
  the fix for the duplicate headline the prerendered copy used to inject, a
  deduplicated `/llms.txt` link in the page footer, hardening against a page
  that merely *mentions* the prerender marker silently losing its prerender,
  and the llms.txt v2 discovery relations — `rel="alternate"` /
  `rel="describedby"` plus matching `Link` headers — that give an agent a
  machine-readable route from any page to that page's prose.
- **Automated dependency checks, aimed at the packages that matter.** The
  repo now runs a weekly check, and it proposes version upgrades only for
  the Dash/Plotly stack, grouped into a single review. The other floors in
  `requirements.txt` record minimum-compatibility facts (a CVE, a rendering
  guarantee) that a mechanical raise would erase, so they are left alone.
  Security updates arrive through their own channel and are unaffected.
- **The deploy gate waits long enough for the slowest build.** Raising a
  dependency floor deliberately rebuilds the whole image, so the most
  important deploy is also the slowest one; the wait is now sized for it,
  and a deploy that nothing actually triggered says so loudly instead of in
  passing.

## [2026-08-22] — the interactive sign-in gate, shipped dark

*Documentation site only; the `dash_mui_scheduler` package is unchanged —
PyPI still carries 1.0.0. Merged as PR #8 and deployed the same evening;
the Clerk 1.0.2 section below shipped earlier the same day and this
supersedes it.*

### Added
- **A sign-in gate, shipped dark.** Every documentation page can now be put
  behind a Clerk sign-in card, and none of them is: every tier ships
  `public`, so the site reads exactly as it did. What changed is that gating
  became a setting rather than a project — `PAGE_DEFAULT_TIER=auth` closes
  the interactive site, setting it back opens it, and neither touches a line
  of code. Pages can also declare their own tier in frontmatter.
- **A control board at `/admin/control-board`** for hiding or gating
  individual pages live, without a deploy. It fails closed: with the auth
  layer unavailable, nobody gets in rather than everybody.
- **Machine surfaces stay open on purpose.** `/llms.txt`, the tiered corpus
  documents and each page's own `/<page>/llms.txt` are governed by a second,
  independent axis — so gating the site for people never silently closes the
  window agents read through. A new `/api/agent-key` turns a signed-in
  browser session into a key that a copied `llms.txt` link carries with it,
  because the assistant you paste that link into has no cookie.
- **Real dates in the sitemap.** Every documentation page now declares the
  date its content actually last changed, taken from this repository's own
  history, and that date is published verbatim. The home page declares none:
  it is a standing index, and any single date would be a guess.

### Changed
- **The Clerk auth hook rises 1.0.2 → 1.0.5 — this one is a security fix.**
  On 1.0.2 signing out never told the server: the browser cleared its own
  session while the server kept honouring the identity cookie it had already
  issued, for up to seven days. Anyone who signed out on a shared machine
  stayed signed in as far as this site was concerned. 1.0.5 revokes properly,
  fixes the sign-in return trip (you now land back on the page you started
  on, signed in, instead of on a stale card), and — specific to this
  service's FastAPI backend — makes the authentication endpoints answerable
  at all: before it, every one of them rejected every request.
- **Sharper icons, and a complete set.** The favicon set was regenerated from
  this site's own artwork and now includes the sizes that were missing, so
  browsers, phone home screens and search results all resolve a real icon
  instead of falling back to a generic globe.
- **The mobile navigation is a real panel.** It now runs full height from
  under the header, with its own search field — previously phones had no way
  to jump to a page by name, only a long scroll, and the menu could not be
  closed with the button that opened it.
- **The dependency floors move up** to the versions this site actually
  needs: the SEO layer to the release that makes page text visible to
  non-JavaScript readers, and the component library to the release where the
  navigation panel renders as a panel.

### Fixed
- **The deploy check was grading the previous release.** After every push the
  post-deploy verification ran against whichever build happened to be
  answering — in practice the one being replaced. It now waits for the
  release it just shipped and verifies that.
- **A false "MCP unavailable" notice on every boot.** The startup log claimed
  the optional integration needed a newer Dash than the one running, on a
  version that was already new enough. It was wired to the wrong entry point
  and could never have worked; it is now wired correctly and silent unless
  enabled.
- **Stylesheet rules aimed at private internals of the component library**
  were removed — four of them, including two that had already caused visible
  layout bugs on sister sites. They would have broken silently, or started
  restyling something else entirely, on any future upgrade.

## [2026-08-22] — Clerk auth hook 1.0.2

*Shipped to the documentation site only; the `dash_mui_scheduler` package is
unchanged — PyPI still carries 1.0.0.*

### Changed
- **The vendored Clerk auth hook rises 0.9.1 → 1.0.2** ahead of the auth
  flip-on: the avatar menu no longer paints signed-out over a valid session
  (it lost a race against Dash mounting the menu), and 1.0.1's widened
  `clerk-backend-api` cap lets pip resolve `cryptography>=50.0.0`, clearing
  four published advisories (GHSA-537c-gmf6-5ccf, PYSEC-2026-3552/3553/3554)
  from the installed environment.

## [2026-08-18] — network instrumentation deploy

*Shipped to the documentation site only; the `dash_mui_scheduler` package is
unchanged — PyPI still carries 1.0.0.*

### Changed
- **Visitor analytics moved to the network's shared instrumentation** (the
  boilerplate 1.3.x trio). The ledger is now buffered, cross-process locked,
  pruned by a retention window, and written atomically — a busy hour no longer
  rewrites the whole file on every hit, and two workers can no longer silently
  overwrite each other's counts. The hourly rollup this site reports to
  2plot.ai is computed by the same shared code every satellite runs, so the
  network's numbers are finally measured with one rule. The Gen-0 reporter
  (`lib/traffic_report.py`) is retired.
- **A deploy can no longer erase the day's traffic.** The Render blueprint now
  attaches a persistent 1 GB disk and keeps the visitor ledger on it, so a
  mid-day deploy stops resetting the numbers the hub charts.
- **Documentation version claims are derived, never written.** Docs prose can
  state a package version as `{{VERSION:<distribution>}}` and the site
  substitutes the installed version at load — a hardcoded number that drifts
  from the shipped package can no longer appear on any page or llms.txt
  surface. (No page had one; the mechanism now guards all of them.)

### Added
- **Every docs page can declare who may read it.** Pages accept a `tier:` in
  their frontmatter (`public | auth | admin | hidden`), and the two corpus
  documents (`/llms-small.txt`, `/llms-full.txt`) take theirs from
  `LLMS_SMALL_TIER` / `LLMS_FULL_TIER`. Everything is and stays public —
  nothing enforces yet; this records the knobs the network's 402 experiment
  will read.
- **`.env.example`** — the app's whole environment surface documented in one
  file: what turns on when each variable is set, and what the app does
  without it.

### Fixed
- **The AI/SEO package floor rises to dash-improve-my-llms 2.5.1**, picking up
  the crawler-document fixes (the page `<title>` carrying the site name,
  per-page social images reaching crawlers, `/favicon.ico` answered with a
  redirect instead of the app shell).

## [1.0.0] - 2026-08-03

The component API has been stable since the first release and the docs site is
now on the network standard, so this graduates the package out of 0.x. Nothing
in the component itself changed — existing code keeps working untouched.

### Fixed
- **`pip install dash-mui-scheduler` no longer leans on a dependency it never
  declared.** Every component imports `typing_extensions`, which the package
  had been getting for free because current versions of Dash happen to install
  it. Anyone resolving to an older Dash could install this package successfully
  and then have it fail on import. It is now declared outright.

### Added
- **Releasing is now one push of a tag.** Publishing to PyPI used to be a manual
  upload from a laptop. Pushing a `v*` tag now runs the whole test matrix against
  that exact commit, builds the package, proves the built result is a working
  component library, publishes it, and opens a GitHub release whose notes are
  lifted from this file. No PyPI token is stored anywhere — PyPI verifies a
  short-lived identity token that GitHub mints for this repository alone, so
  there is no long-lived secret to leak or rotate. `RELEASING.md` documents the
  flow.
- **Guard rails against the releases that go wrong quietly.** A release stops
  before it can upload if the tag disagrees with the version the package
  declares, if the tagged commit never landed on `main`, or if this changelog
  has no section for the version being cut. The packaging is checked as well:
  both the wheel and the source archive must carry the built component bundle —
  a package that installs cleanly and then renders nothing is otherwise
  indistinguishable from a good one — and that check reads a clean install of
  the built artifact rather than the source tree sitting beside it.

## [0.1.1] - 2026-08-01

*Shipped to the documentation site; superseded on PyPI by 1.0.0, which carries
these changes.*

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

