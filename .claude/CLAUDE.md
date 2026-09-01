# dash-mui-scheduler — project guide

A **Dash ≥4.2 component library + documentation site** for the **MUI X Scheduler**: the
`dash_mui_scheduler` package (five wrappers: `EventCalendar`, `EventCalendarPremium`,
`EventTimeline`, `RadialLineChart`, `RadialBarChart` — the three *radial doc pages* are named
Radial Lines/Bars/Axes, but there is no `RadialAxes` component) and its docs (14 scheduler + 3
radial pages with live examples).

This repo was refocused from the original 2plot.ai monolith (2026-07 network split — the
execution packet is `.claude/migration/`): the petri-dish evolution game moved to the
`2plotxyz` repo (2plot.xyz) and the hub pages to `2plotai` (2plot.ai). This repo is now ONLY
the component + docs, destined for PyPI (`pip install dash-mui-scheduler`).

## ⚠️ Read before running anything
- **No LLM/image cost traps remain in the code** — the game's Gemini/Anthropic call sites left
  with the game. `.env` may still hold real keys; blanking them is harmless here.
- **The MUI X license key is NOT a cost trap — leave it set.** Perpetual *license* key (not
  metered). Docs examples read it as `licenseKey=os.environ.get("MUI_X_LICENSE_KEY", "")`;
  locally `.env` stores it as `MUI_PRO_API_KEY` plus an `MUI_X_LICENSE_KEY=${MUI_PRO_API_KEY}`
  alias line (render.yaml sets `MUI_X_LICENSE_KEY` directly). Blank just degrades Premium
  components to a watermark.
- **Backends:** `lib/backend.resolve_backend()` honors `DASH_BACKEND` > `BACKENDS` > `BACKEND`.
  Verify behavior on flask (`DASH_BACKEND=flask PORT=8598 python run.py`), and separately
  confirm the fastapi build: `DASH_BACKEND=fastapi python -c "import run; print('ok')"`.
- **Restart to see changes:** server is `debug=False`. `pkill -9 -f run.py` + free the port:
  `for pid in $(lsof -ti:8598); do kill -9 $pid; done`.
- **Don't commit/push unless asked.** Branch first if on the default branch. Commit footer: use
  the CURRENT harness's required footer.
- **Keep `CHANGELOG.md` accurate as a LEDGER (owner rule):** every shipped feature/fix gets a
  product-voice entry under `[Unreleased]` in the SAME change set; `[Unreleased]` holds ONLY
  uncommitted working-tree work — cut a dated release section once shipped.

## Component build
The React sources live in `src/lib/components/`; the **built bundle + generated Python wrappers
are COMMITTED** (`dash_mui_scheduler/*.min.js` + `*.py`), so `pip install -e .` works without
npm. Changing anything under `src/` requires `npm install && npm run build` and committing the
regenerated artifacts. `setup.py` reads `package.json` for the version — keep them in sync
(currently 1.0.0). **PyPI publishing is tag-driven** — push a `v*` tag and
`.github/workflows/release.yml` verifies, tests, builds, gates and publishes via OIDC trusted
publishing; see `RELEASING.md`. (PyPI holds 0.1.0, uploaded by hand before that existed; 0.1.1
shipped to the docs site only.)

## Layout
- `dash_mui_scheduler/` — the built package (5 wrappers + bundles). `src/lib/` — React sources.
- `docs/<page>/<page>.{md,py}` — each doc page: markdown frontmatter (`name`, `endpoint`,
  `category`, `icon`, `lastmod`, optional `tier`/`llms_public`/`schema_type`) +
  `.. exec::docs.<page>.<page>` runs the `.py` (which sets `component = ...` and registers
  callbacks). **`lastmod` is a REAL content date** — it is emitted verbatim as the sitemap
  `<lastmod>`; never script it from mtimes.
- `lib/` — site plumbing: `backend.py` (backend resolution), `constants.py`,
  `analytics_tracker.py`, `asgi_middleware.py`/`asgi_routes.py` (fastapi), `directives/*`
  (kwargs/source/toc renderers), `clerk_webhook.py`, `versions.py` (the `{{VERSION:...}}`
  substitution both content lanes run).
- **The interactive gate** (batch-2 gate wave, 2026-08-22 — shipped DARK): `auth.py` is the
  single source of truth for "is auth on" and owns BOTH wiring halves —
  `register()` before `Dash(...)` and `configure_app(app)` after. Ship one without the other
  and the site LIES (renders signed-in, every server render reads signed-out);
  `tests/test_auth_wiring.py` pins both by AST. Around it: `access.py`, `page_tiers.py`
  (two-axis), `gate_layouts.py`, `auth_demos.py`, `agent_key.py`, `hub_client.py`,
  `page_visibility.py` + `pages/control_board.py`. It replaced the hand-rolled
  `clerk_satellite.py` (retired — its three 0.9.0-era fixups are all upstream now).
  Clerk is **LIVE via env group C**; every page tier is `public`, so nothing is gated.
  The flip is env-only: `PAGE_DEFAULT_TIER=auth`.
- `components/` — `appshell.py`, `header.py` (Clerk avatar + toggle burger), `navbar.py`
  (Scheduler + Radial sections, `create_mobile_content` drawer), `backend_badge.py`.
- `pages/` — `home.py` (landing, plain DMC — this site has no `home.md`), `markdown.py` (docs
  loader, gated registration), `control_board.py` (`/admin/control-board`, fails closed),
  `not_found_404.py` (plain DMC).
- `run.py` — entrypoint (PORT env, default 8598). `Dockerfile`/`render.yaml` — fastapi Render
  deploy at **`https://muischeduler.2plot.dev`** (custom domain; the service's own
  `*.onrender.com` URL 301s there via `lib/canonical_host.py` once
  `CANONICAL_HOST_REDIRECT=1`).

## 2plot network standard (retrofit 2026-08-01)
This repo follows the satellite standard
(`pip-docs+/.claude/support_files/subdomain_blueprint/STANDARD.md`):
- **Identity**: `lib/constants.SITE_BRAND` ("dash-mui-scheduler — MUI X scheduling for
  Dash") reaches every surface — `Dash(title=)`, `register_page_metadata(path="/",
  name=SITE_BRAND)`, index.html `<title>`/`og:site_name`, manifest.
  `tests/test_site_identity.py` pins them; don't restate the brand, derive it.
- **App id is `muischeduler` everywhere**: `lib/satellite_reporter.app_key()`
  (env `SATELLITE_APP_KEY`), `lib/ad_client.APP_ID`, `lib/bulletin.app_id()` —
  pinned together in tests.
- **Social card**: `scripts/make_social_card.py` → CDN
  `cdn.2plot.ai/github_assets/muischeduler.2plot.dev.png` (1200×630). Upload is MANUAL
  and gates deploy: og:image points at the CDN, so a 404 there fails
  `social_card_real_pixels` in the live battery — deliberately.
- **Internal traffic**: UAs carrying `2plot-internal` are dropped at write time in
  `lib/analytics_tracker`; every outbound network call sends `internal_ua(caller)`.
- **CI/CD**: `.github/workflows/ci.yml` (lint+actionlint, secretless pytest on
  flask+fastapi, docker build→fingerprints→boot→health verdict→battery, advisory pip-audit);
  `cd.yml` owns main (sustained health, then `scripts/network_smoke.py` +
  `scripts/smoke_live.py` against the live host). `markdown2dash` installs
  `--no-deps` everywhere (its gunicorn<22 pin vs our >=23 floor).
- **Tests are secretless by design** — `tests/conftest.py` pins every secret empty
  before run.py imports; run `DASH_BACKEND=flask python -m pytest tests -q`.
- **One fleet Python**: `python:3.14-slim` in the Dockerfile is the single declaration;
  the CI matrix, cd.yml's verify job and `/healthz`'s `python` field follow it, and
  `tests/test_python_version.py` holds them together. This service is Render's DOCKER
  runtime, so `render.yaml` carries no `PYTHON_VERSION` — the image is the runtime
  (recorded in `DIVERGENCES.md`).

## Run + verify recipe
```bash
DASH_BACKEND=flask PORT=8598 nohup python run.py >/tmp/srv.log 2>&1 &
# then: curl the doc pages / drive with headless Playwright
DASH_BACKEND=fastapi python -c "import run; print('ok')"   # build check
```
In a sandbox that blocks sockets, render in-process instead:
`run.app.server.test_client().get('/')`.

## Conventions / gotchas
- **`prevent_initial_call`/duplicate outputs:** `allow_duplicate=True` needs
  `prevent_initial_call` set.
- Doc-page `.py` files must set `component = ...`; the `.. exec::` directive imports the module
  at page load, so import-time errors break the whole site — self-validate by importing.
- The `.. kwargs::dash_mui_scheduler.<Component>` directive renders the prop table from the
  generated wrapper docstrings; `PROPS_TO_EXCLUDE` in `lib/constants.py` filters style props.
- **Version claims are never typed.** Prose writes `{{VERSION:<distribution>}}` and
  `lib/versions.substitute_versions` fills it from the installed package — in the docs lane
  (`pages/markdown.py`) *and* on the root `llms_doc` in `run.py`, which is this site's
  home-lane equivalent. A hardcoded number is a lie waiting for the next release.
- `MUI_X_LICENSE_KEY` flows to examples via `licenseKey` — never hard-code a license string.
- **Host moves:** change `APP_BASE_URL` only — never a literal host in code/template. Order:
  attach the domain in Render → DNS CNAME verified → confirm it serves → flip `APP_BASE_URL`
  → set `CANONICAL_HOST_REDIRECT=1`. Flipping the redirect early strands every visitor.
- **SEO/URLs:** `lib/constants.BASE_URL` (from `APP_BASE_URL`) is the ONLY source of absolute
  URLs — canonical, `og:*`, sitemap, robots, llms, JSON-LD. `templates/index.html` uses
  `__BASE_URL__` / `__PAGE_URL__` / `__VERSION__` tokens that `run.py` substitutes; never
  hard-code a host there, and never add a static `description`/`og:*`/`twitter:*` tag (Dash
  emits those per page from `register_page`). Dash replaces **every** occurrence of a
  `{%…%}` placeholder — including inside HTML comments. Crawlers get
  dash-improve-my-llms' own prerendered HTML, not the SPA shell; `run.py` patches canonical
  and `og:image` into it.

## Local scaffold under `.claude/`
Only the shipped kit is tracked (`.gitignore` allow-lists `CLAUDE.md`, `settings.json` and
`skills/`). Everything else here is local to a clone:
- **`migration/`** — the 2plot network split packet (HANDOFF → MIGRATION-CHECKLIST →
  OWNER-ACTIONS → PLAN). Read HANDOFF.md first if you're picking up split work.
- `.pypirc` — the PyPI upload credential. Never committable; the allow-list is what
  guarantees that structurally.

---

## Network role & the behavioral contract

This repo is a member of the 2plot network — either the template
itself (dash-documentation-boilerplate) or a fork of it serving one
component's documentation. **Identity derives from the repo, never
from this file**: the app key comes from `SATELLITE_APP_KEY` and
run.py's fork point, the host from `lib/constants.py`'s `BASE_URL`,
the deliberate differences from the template from `DIVERGENCES.md`
at the repo root. If those disagree with anything written here,
they win.

### The contract — every session, every prompt

1. **Check the prompt against this tree before executing.** Prompts
   are written from the template's perspective and your fork may
   legitimately differ — floors, backends, payload shapes, page
   sets. A prompt step that doesn't fit this repo is a finding to
   return, not an instruction to force.
2. **Corrections are your job, not scope creep.** If a prompt's
   reference list doesn't match its steps, if its assumed state is
   wrong, or if executing it as written would produce a
   green-but-vacuous result, say so and propose the corrected
   version before running it.
3. **Verify your own deploy on the wire before reporting.** A push
   is not a result. Run `/wire-verify` (or its manual equivalent)
   against production and paste what came back. If your sandbox
   cannot reach your own domain, say exactly that — an unverified
   claim marked as unverified is honest; the same claim unmarked is
   not.
4. **Report observed versus expected, with evidence.** Paste the
   JSON, the status code, the test count. "Should work" and summary
   claims without artifacts are not reports.
5. **Divergence is legitimate when written down.** Before syncing
   template changes, read `DIVERGENCES.md`; never let a sync
   "restore" a recorded deliberate difference. When you deliberately
   diverge, record it there in the same commit — an unrecorded
   divergence is indistinguishable from drift and will be treated
   as drift.
6. **Never touch**: environment variable VALUES, hosting dashboards,
   secrets, other repos' trees, or anything the prompt didn't put in
   scope. Enumerate what you cannot do (closing PRs, dashboard
   steps) for the owner instead of claiming it done.

### Verification traps (fleet-learned, keep them)

- A `>=` floor can never pull a new release through a Docker cache
  hit — the requirements line changing IS the cache bust, and floors
  live in several encodings (requirements, run.py's boot floor,
  tests, CI): grep the number, move every one.
- `/healthz` build == HEAD is the deploy proof; a missing geo block
  on dimll ≥2.7 means the cache trap fired (unless DIVERGENCES.md
  says this host's healthz is deliberately minimal).
- Probe with GET, not HEAD — HEAD responses omit the Link headers.
- Run-watchers keyed on a commit sha can match Dependabot's runs on
  the same sha — key on the workflow path (cd.yml) instead.
- The browser lane and the machine lane are different documents;
  a fix proven on one is unproven on the other.
- There is ONE classifier: `dash_improve_my_llms.classify()`. Never
  add a User-Agent list to this app — the tracker had one for a year
  (`lib/analytics_tracker.py`, until the 2.8.0 floor), it filed
  ClaudeBot as *search* (it is Anthropic's training crawler; the
  package's registry and this repo's own `run.py` comment both said so
  six lines from where the list ignored them), it still named the
  retired `anthropic-ai` / `claude-web` tokens, and it counted every
  UA-less or library client as a human. Every host in the fleet
  reported those numbers. A token the registry lacks is a pushback to
  the package seat, not a list here; `tests/test_analytics_classifier.py`
  greps the module for the old tokens and goes red if one comes back.
- `build == HEAD` on `/healthz` means HEAD of **`release`**, not main
  (1.6.35). Render deploys `release`; only cd.yml's `deploy` job writes
  it, fast-forward, after the CI matrix is green. `main` ahead of
  `release` is an uncertified push pending — its CD run is red or still
  running — never "drift" and never a reason to deploy by hand or to
  write `release` yourself (a non-fast-forward push fails the next run
  on purpose). Compare the wire against `git rev-parse origin/release`.
  On a service Render manages from its DASHBOARD rather than the
  Blueprint, `render.yaml`'s `branch:` is documentation and the Branch
  field is the switch — the first promoted run cannot tell the two
  apart, because main and release then hold the same sha.
- A bot-merged PR — any GITHUB_TOKEN merge — lands with ZERO
  workflow runs on the merge sha (anti-recursion) yet still reaches
  production: the deploy hook builds branch HEAD, so an in-flight
  CD run ships the merge while its own build-match wait holds out
  for the superseded release sha. Observed live on 4a1d430
  (2026-08-25). Since 1.6.25 the wait fails FAST on this (live
  build a descendant of the wanted sha, via the compare API)
  instead of going red at timeout, and the remedy is policy —
  actions PRs: human merge when green; never a bot actor on main.
- WHICH BRANCH RENDER BUILDS CAN BE **measured on a GREEN push**, by
  TIMING (leaflet, 1.6.43). `main == release == wire` at every step of
  a promote tells you nothing — both configurations produce the same
  three shas. Sample `/healthz` every ~45 s from the push and time the
  swap against the **promote**, not the push: leaflet measured
  build+swap at 2m03s from its promote, where a Render reacting to the
  PUSH would have put that build live ~1m52s earlier. STRONG EVIDENCE,
  NOT PROOF. The canonical discriminator is still the first push that
  goes RED on main, with `release` unmoved and the wire unchanged.
  Four hosts declined to call their `deploy:` fence row proven on a
  green push; that refusal is the standard, and this host was one.
- VERIFY THE ARTIFACT THE CLAIM IS ABOUT, AND SAY WHICH ONE. It runs
  both ways. A props table absent from the crawler document is a defect
  of the SITE, not of the harness — pannellum moved that assertion to
  the lane that passed and the pin held for a fortnight over a corpus
  serving zero props. WHEN A LANE DISAGREES, THAT IS THE FINDING. And
  the inverse, which is worse because it sends someone hunting a bug
  that does not exist: `curl https://…/ | grep -c skip-link` returns
  **0** on a host where the skip link ships and works (excalidraw),
  because it is a Dash component in `app.layout` and never in the
  served markup. This repo's own version: a substring count of
  `rel="canonical"` read 2 on a page carrying exactly ONE canonical
  element, because the URL-sync script names the tag in a selector —
  and that number nearly deleted a load-bearing tag.
- ASSERT THE CORPUS IS NON-EMPTY BEFORE TRUSTING ANY NEGATIVE, and
  print the count beside the result. A sweep that found nothing and a
  sweep that swept nothing produce the same green. Measured on the
  template 2026-09-01: its `.flake8` excludes `docs/*/`, so
  `flake8 docs/` exits 0 with a file containing `def broken(:` — the
  linter is not passing the file, it is not reading it; `py_compile`
  sees it immediately. Same family: `pytest … | tail -2 && git commit`
  takes the pipe's exit status from `tail`, so a red suite commits.
  Here it was a row regex that counted a page's own hand-written
  tables as prop rows, and a wire probe that grepped for a prop name I
  had invented and duly reported the 0.
