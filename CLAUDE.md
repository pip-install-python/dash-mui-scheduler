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
  Verify behavior on flask (`DASH_BACKEND=flask PORT=8560 python run.py`), and separately
  confirm the fastapi build: `DASH_BACKEND=fastapi python -c "import run; print('ok')"`.
- **Restart to see changes:** server is `debug=False`. `pkill -9 -f run.py` + free the port:
  `for pid in $(lsof -ti:8560); do kill -9 $pid; done`.
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
  `category`, `icon`) + `.. exec::docs.<page>.<page>` runs the `.py` (which sets
  `component = ...` and registers callbacks). See `.claude/rules/docs-pages.md` when editing.
- `lib/` — site plumbing: `backend.py` (backend resolution), `constants.py`,
  `analytics_tracker.py`, `asgi_middleware.py`/`asgi_routes.py` (fastapi), `directives/*`
  (kwargs/source/toc renderers), `auth.py` + `clerk_satellite.py` + `clerk_webhook.py`
  (Clerk plumbing, **OFF at launch** — no CLERK_* env → clean no-op; flip on later by setting
  the satellite env, see `lib/clerk_satellite.py`).
- `components/` — `appshell.py`, `header.py`, `navbar.py` (Scheduler + Radial sections),
  `backend_badge.py`.
- `pages/` — `home.py` (landing), `markdown.py` (docs loader), `not_found_404.py` (plain DMC).
- `run.py` — entrypoint (PORT env). `Dockerfile`/`render.yaml` — fastapi Render deploy at
  **`https://muischeduler.2plot.dev`** (custom domain; the service's own `*.onrender.com` URL
  301s there via `lib/canonical_host.py` once `CANONICAL_HOST_REDIRECT=1`).

## 2plot network standard (retrofit 2026-08-01)
This repo follows the satellite standard
(`pip-docs+/.claude/support_files/subdomain_blueprint/STANDARD.md`):
- **Identity**: `lib/constants.SITE_BRAND` ("dash-mui-scheduler — MUI X scheduling for
  Dash") reaches every surface — `Dash(title=)`, `register_page_metadata(path="/",
  name=SITE_BRAND)`, index.html `<title>`/`og:site_name`, manifest.
  `tests/test_site_identity.py` pins them; don't restate the brand, derive it.
- **App id is `muischeduler` everywhere**: `lib/traffic_report.app_key()`,
  `lib/ad_client.APP_ID`, `lib/bulletin.app_id()` — pinned together in tests.
- **Social card**: `scripts/make_social_card.py` → CDN
  `cdn.2plot.ai/github_assets/muischeduler.2plot.dev.png` (1200×630). Upload is MANUAL
  and gates deploy: og:image points at the CDN, so a 404 there fails
  `social_card_real_pixels` in the live battery — deliberately.
- **Internal traffic**: UAs carrying `2plot-internal` are dropped at write time in
  `lib/analytics_tracker`; every outbound network call sends `internal_ua(caller)`.
- **CI/CD**: `.github/workflows/ci.yml` (lint+actionlint, secretless pytest on
  flask+fastapi, docker build→fingerprints→boot→battery, advisory pip-audit);
  `cd.yml` owns main (sustained health, then `scripts/network_smoke.py` +
  `scripts/smoke_live.py` against the live host). `markdown2dash` installs
  `--no-deps` everywhere (its gunicorn<22 pin vs our >=23 floor).
- **Tests are secretless by design** — `tests/conftest.py` pins every secret empty
  before run.py imports; run `DASH_BACKEND=flask python -m pytest tests -q`.

## Run + verify recipe
```bash
DASH_BACKEND=flask PORT=8560 nohup python run.py >/tmp/srv.log 2>&1 &
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

## .claude/ scaffold
- **`migration/`** — the 2plot network split packet (HANDOFF → MIGRATION-CHECKLIST →
  OWNER-ACTIONS → PLAN). Read HANDOFF.md first if you're picking up split work.
- **`workflows/scheduler-docs-content.js`** — the saved doc-generation workflow
  (`/scheduler-docs-content`): writes doc pages in parallel, one agent per page.
- **`rules/docs-pages.md`** — path-scoped guidance for `docs/**`.
- **`hooks/syntax-check.sh`** + `settings.json` — advisory PostToolUse syntax check.
