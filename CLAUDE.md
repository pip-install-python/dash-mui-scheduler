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
(currently 0.1.0; PyPI publish is an owner step in `.claude/migration/OWNER-ACTIONS.md`).

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
- `run.py` — entrypoint (PORT env). `Dockerfile`/`render.yaml` — fastapi Render deploy on the
  default `*.onrender.com` URL.

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

## .claude/ scaffold
- **`migration/`** — the 2plot network split packet (HANDOFF → MIGRATION-CHECKLIST →
  OWNER-ACTIONS → PLAN). Read HANDOFF.md first if you're picking up split work.
- **`workflows/scheduler-docs-content.js`** — the saved doc-generation workflow
  (`/scheduler-docs-content`): writes doc pages in parallel, one agent per page.
- **`rules/docs-pages.md`** — path-scoped guidance for `docs/**`.
- **`hooks/syntax-check.sh`** + `settings.json` — advisory PostToolUse syntax check.
