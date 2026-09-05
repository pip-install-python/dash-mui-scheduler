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
- `/healthz` build == HEAD **of `release`** is the deploy proof on a
  release-branch host — and this host is one; see the fuller trap
  below and read that one before acting on this line. Written
  unqualified here until 1.6.44 item 14, which is the same
  contradiction clerkhook found on the template: two lines about the
  same question a hundred lines apart, and a reader who met this one
  first was sent to the wrong ref — `main` ahead of `release` then
  reads as drift instead of what it is, an uncertified push pending.
  A missing geo block on dimll ≥2.7 means the cache trap fired (unless
  DIVERGENCES.md says this host's healthz is deliberately minimal).
  The general form, since this file is long enough to contain its own
  contradictions: when a trap is later corrected, AMEND THE ORIGINAL —
  a correction that only appends leaves the wrong answer in the place
  a reader looks first.
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
  TIMING (leaflet, 1.6.43; concrete form 1.6.44 item 17).
  `main == release == wire` at every step of a promote tells you
  nothing — both configurations produce the same three shas. STRONG
  EVIDENCE, NOT PROOF: the canonical discriminator is still the first
  push that goes RED on main, with `release` unmoved and the wire
  unchanged. Four hosts declined to call their `deploy:` fence row
  proven on a green push; that refusal is the standard, and this host
  was one.
  RUN `scripts/promote_sampler.py`, DO NOT RE-DERIVE IT LIVE. Three
  things a hand-written watcher gets wrong, each earned by a host that
  got it wrong:
  SAMPLE THE WIRE AND THE RUN STATE IN THE SAME LOOP — **eight samples
  at 45** s, one timeline (pannellum). Two separate reconstructions
  invite exactly the arithmetic error the measurement exists to avoid.
  pannellum's live pair: push 21:55:44Z · promote 21:58:20Z · wire
  still OLD at 21:58:47Z · wire NEW at 21:59:33Z — 73 s after the
  promote, 183 s after the push. The old-then-new bracket AROUND the
  promote is the whole evidence; a single "new" sample proves nothing,
  because it cannot say what it followed, and the sampler refuses to
  report a bracket it did not observe.
  TIME AGAINST THE PROMOTE STEP'S `completed_at`, NEVER THE DEPLOY
  JOB'S (emojimart). The job CONTAINS the build-match wait, so it
  completes after the swap BY CONSTRUCTION and the arithmetic reads
  "swap before promote" every time — emojimart measured a 9 s
  impossible ordering before catching it. A measurement that cannot
  produce a sane answer is worse than none, because the number looks
  like data.
  AND THE SAMPLER MUST RETRY: three attempts per sample, recording
  `unreadable` as a state DISTINCT from "old" (emojimart). The
  container restart lands exactly where the bracket needs its sample,
  so an un-retried loop is systematically blind at the only moment that
  matters — and collapsing unreadable into old invents a bracket nobody
  observed.
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
- PRINT THE RESOLVED VERSION BESIDE THE RESULT, and say which tool
  produced it (1.6.44 item 10). An acceptance is a claim about a tree
  AT A VERSION: "suite green" is not a result, "467 passed, 2 skipped,
  exit 0, dimll 2.8.0 imported from
  .venv/lib/python3.12/site-packages/dash_improve_my_llms/__init__.py"
  is. Resolve it by IMPORTING and printing `mod.__file__` — never by
  reading requirements.txt, which states the INTENT rather than the
  fact, and never by parsing source, which truncates (see the regex
  and substring traps above). The gap this closes is real and was
  measured on excalidraw 2026-09-01: `llms_version` 2.9.4 on the wire
  while its suite ran 2.8.0, so CI and production disagreed about
  whose behaviour was being accepted and every green tick certified
  the older one. THIS HOST HAS THE SAME GAP TODAY and it is a `>=`
  floor, not a pin: the venv here resolves 2.8.0 while production's
  image resolved something with route-level HEAD (measured item 2 —
  local 11/15 pairs, wire 15/15). Until the 1.6.45 pin lands, every
  acceptance from this seat is a statement about 2.8.0 and must say so.
- NAME THE TOOLS WHOSE LOCAL INVOCATION IS NOT CI'S, in the same
  sentence as the result. `actionlint` without shellcheck on PATH
  skips every `run:` block's shell analysis, so a local "actionlint
  clean" is a weaker statement than the CI job's — and a local ABSENCE
  of the binary is weaker still. Both are the case in this sandbox:
  neither `actionlint` nor `shellcheck` is installed, so workflow
  changes from this seat are reported as "ci.yml parses as YAML
  (yaml.safe_load), actionlint NOT RUN — not installed here", never as
  lint-clean. The general form: when the check you ran differs from
  the check CI runs, say which one you ran.
- PARSE IT, OR STRIP COMMENTS **AND STRINGS** (1.6.44 item 13). A
  source detect that greps raw text reports the defect that the
  documentation of its absence describes. STRIPPING COMMENTS IS NOT
  THE FIX — it is the half-measure that looks like the fix, because a
  docstring is a string, not a comment. Both halves happened inside
  this repo's own 1.6.44 build: item 9 added a module docstring to
  `lib/asgi_middleware.py` explaining why there is no
  `HeadAsGetMiddleware`, and the grep-based guard asserting the shim
  was absent went RED on a tree that has no shim in it. The
  progression to copy is raw grep, comment strip, `ast.parse`, and
  only the third is right: walk for `ClassDef`/`FunctionDef` names and
  `Name`/`Attribute` ids, then assert the parse found definitions at
  all, so an unreadable file cannot pass as a clean one. The reason
  the class recurs is worth naming — a good comment explains the
  ABSENCE of the thing a detect hunts, so the better the code is
  documented, the more reliably a raw grep reports the defect it is
  documenting the absence of. The detects most likely to be wrong are
  the ones on the best-explained code.
  PROSE detects have the same disease in a different costume, and it
  is FORMATTING-bound: flatten whitespace before matching (a phrase
  that WRAPS across two lines is one string to a reader and two to a
  regex), strip markdown emphasis (`**measured on a GREEN\npush**`
  carries `**` inside the phrase), and strip an indented blockquote's
  `> ` markers. Read case-INSENSITIVELY: the SYNC-1.6.43 item-3
  detects all read 1 on this tree flattened and case-folded, and all
  read 0 against the capitalised literal — the phrases are here, and a
  case-sensitive grep would report them missing.

<!-- Merged from dash-documentation-boilerplate at 1.6.44 item 14. This
     fork's section was 14 entries against the template's 28; every entry
     below is a FLEET-class trap this repo never received, taken whole
     rather than summarised, because a trap loses its teeth when its
     measurement is dropped. Entries this fork had already ADAPTED were
     amended in place, never pasted over — `scripts/kit_traps.py` matches
     on token overlap for exactly that reason. Items 18 and 19 add their
     own two traps with those items. -->
- Always GET, never HEAD — and the mechanism, measured 2026-08-27
  after two rounds of wrong diagnoses: on the ASGI backends HEAD is
  answered by NOTHING AT ALL. Werkzeug derives a HEAD rule from
  every GET rule; FastAPI's `APIRoute` does not, so a route declared
  `@router.get(...)` returns 405, and every ASGI host in the network
  was 405ing HEAD on every route — `/healthz`, `/robots.txt`,
  `/sitemap.xml` included. Get the LAYER right (corrected 1.6.33,
  after this text and two seats' drops all said "Starlette", and
  three probes went looking in the wrong package):
  `starlette.routing.Route` DOES add HEAD wherever GET is present —
  `self.methods.add("HEAD")`, the same courtesy Werkzeug does — and
  FastAPI's `APIRoute` is the one that takes `methods` literally.
  A HEAD probe therefore tells you about
  the router's method table and never about the document. GET is
  never wrong, which is the whole reason to have one rule.
  Do NOT "verify" the trap on one host and conclude HEAD is fine:
  excalidraw measured twice and was right about its own Flask host
  and wrong about the fleet. Do not verify it on `HEAD /` either —
  a crawler-UA `HEAD /` is answered by the prerender middleware
  before routing, so it returns 200 on a host that 405s everything
  else, and that one case is how this repo's 1.6.31 in-process
  probe cleared the app code. Earlier text here said the ASGI hosts
  DROP the `Link` headers on HEAD: a 405 carries no `Link`, so the
  observation was true and the diagnosis was not. Fixed in the
  template at 1.6.32 (a HEAD→GET ASGI middleware, because the
  package's own adapter declares its routes GET-only); the fleet's
  two ASGI forks consume it as spec item 11, and the hub plus four
  second-ring hosts had the same defect — if you serve a non-Flask
  backend, assume you have it until you have probed a route that is
  NOT `/`. The middleware stayed after dimll 2.7.2 fixed the
  package's own routes, because `/` is Dash's page catch-all and every
  Dash route is an `APIRoute` too — and it is RETIRED at 1.6.44, on the
  pin to dimll 2.9.4, where the package walks the router itself and adds
  HEAD wherever GET is allowed, Dash's lifespan-registered catch-all
  included. Amended here rather than appended below, because the version
  is the whole content of the claim and a reader who met "the middleware
  stays" first would keep a shim that now MASKS the fix it was standing
  in for: converting HEAD to GET above the router made every HEAD look
  correct whatever the router did, so it would have hidden a regression
  in the package's pass exactly as well as it hid the original defect.
  Measured before removing (5 paths x 3 UAs, FastAPI lane, in-process):
  15 of 15 HEAD/GET status pairs matched WITHOUT it, `/` to a browser UA
  included — the one case the old text said would 405. The disable was
  proved non-vacuous first by asserting the middleware stack contained
  the class in one run and not the other. If your floor is below 2.9.4,
  the shim is still load-bearing: this retirement is gated on the pin,
  not on the date.
- Any throwaway Python probe a session writes against a production
  host needs the certifi SSL context AND a retry guard. Fixing the
  shipped tools does not cover the next ad-hoc script: the template
  seat hit `CERTIFICATE_VERIFY_FAILED` in a hand-written CD watcher
  one hour after shipping that exact fix inside both live tools,
  and the ops seat hit it plus an `IncompleteRead` on a chunked
  response in the same session. It is a seat habit, not a repo
  contract, which is what this file is for.
- SUPERSESSION: cd.yml's build-match wait cannot tell "not deployed
  yet" from "already replaced" — both look like a live build that
  is not the sha it wants. A bot-merged PR (any GITHUB_TOKEN merge)
  is one road in: it lands with ZERO workflow runs on the merge sha
  (anti-recursion) yet still reaches production, because the deploy
  hook builds branch HEAD — so an in-flight CD run ships the merge
  while its own wait holds out for the superseded release sha
  (observed live on 4a1d430, 2026-08-25). It is NOT the only road,
  and taking the bot actor off main does not close the class: two
  human pushes inside one deploy window, or hook dispatch lag,
  produce exactly the same state. Since 1.6.25 the wait fails FAST
  when the live build is a DESCENDANT of the wanted sha (compare
  API) instead of going red at timeout — that is the diagnosis, and
  it works whoever merged. The policy — actions PRs: human merge
  when green, never a bot actor on main — removes the most common
  road, not the trap.
- Anonymous api.github.com is 60 requests/hour. With no `gh` and no
  token, read a run ONCE after CI's own jobs report complete — a
  blind 20 s poll loop spends the whole budget reading rate-limit
  bodies as "not done yet" (modelviewer, 2026-08-26).
- A GitHub API JSON body WITHOUT the field you asked for
  (`workflow_runs` absent, not empty) is a rate-limit error body,
  never an empty result — check the field exists before trusting
  the answer.
- `git fetch` before any audit: the fan-out pushes to these repos
  now, and a checkout current yesterday is 2–3 merges behind
  origin/main today (three pilot sessions, same day, 2026-08-26).
- A failed STEP is not a failed RUN. A job with
  `continue-on-error: true` (pip-audit here) reports its step red
  and the RUN still concludes `success`; the reverse also bites —
  a green-looking job list under a run whose conclusion is
  `failure`. Read the run's `conclusion`, then the annotations;
  never infer either one from the other.
- Never round-trip JSON through zsh `echo` — it interprets the
  `\n` inside a multi-line commit message and hands the parser
  real control characters (a broken API read on the template, then
  the same hour on the ops seat). Pipe curl straight into
  `python3`, or use `printf '%s'`.
- Repeated HTTP headers survive only if you keep them: both
  `dict(resp.headers)` and `{k: v for k, v in resp.headers.items()}`
  keep the LAST value per name, and dimll emits several `Link`
  headers (muicharts, 2026-08-26). Iterate the items, or ask for
  `resp.headers.get_all(name)`; in curl, `-D -` and read the raw
  block.
- Name the crawler UA when you probe the machine lane. Which
  document a host serves is decided by the package's UA
  classification, not by the absence of a UA: on the template
  today, curl's default `curl/8.x` receives the SAME crawler
  document as Googlebot (18,779 bytes, byte-identical) while a
  Chrome UA gets the 148 KB app shell. One host (muicharts) reported
  a UA-less probe classified the other way; treat that as
  UNCONFIRMED — muischeduler filed the same observation and then
  RETRACTED it (its report had the two documents swapped), leaving
  one unreproduced sighting, and a trap carrying an unreproducible
  fact spends somebody's afternoon. The advice does not depend on
  it: either lane can be the one you did not mean to test, so send
  `-A "<a real crawler UA>"` and confirm from the body which
  document came back.
- Headless browsers are CRAWLER-lane from dash-improve-my-llms 2.9.0
  (measured on the wheel, 2026-08-29: `HeadlessChrome/…` and a
  Playwright UA classify `lane: crawler, bot_type: monitor,
  vendor_key: headless`; 2.8.0 said browser). A host that screenshots
  ITSELF for social cards — Playwright, Puppeteer, a headless Chrome
  in a job — now receives the crawler document, not the app shell,
  unless the screenshot service sends its own non-headless UA. If a
  card went blank or textual after a floor bump, look here before
  the template. Same class as the two lane traps above: name the UA,
  confirm from the body which document answered.
- And the same family one turn later, MEASURED TWICE — this seat and
  clerkhook hit it independently within the hour, so it is a property of
  the technique and not one seat's slip: extracting a package constant with
  `re.search(r"EVENT_FIELDS = \((.*?)\)", src, re.S)` truncated at a `)`
  inside a COMMENT in the middle of the tuple, printed eight of sixteen
  fields, and reported `'ua' present: False` — confidently, with a
  number beside it. Caught only because eight looked too few. When you
  parse a language construct out of source with a regex, check the count
  against something independent (the file, `python -c "from … import X;
  print(len(X))"`, the CHANGELOG) before you believe a negative.
- A shell's CWD can shadow an installed package, and it produces the most
  convincing wrong answer of the family: measuring `EVENT_FIELDS` across
  two dimll versions, this seat ran the comparison with the cwd inside an
  unpacked 2.9.4 wheel, so `import dash_improve_my_llms` resolved from
  the CURRENT DIRECTORY rather than site-packages — and two readings of
  ONE wheel were reported as two versions agreeing, in a CHANGELOG and a
  shipped spec (2026-09-01, corrected the same day). The load-bearing
  half was true and the supporting detail was invented. When comparing
  versions, `print(mod.__file__)` and assert it is the path you meant, or
  set PYTHONPATH explicitly and import in a fresh process per version;
  and print the unpacked file count before the read (note 88 applied to
  the check itself, leaflet). Note also that parsing the constant out of
  source is not the safe alternative: the regex form truncated on a `)`
  inside a comment (measured twice — this seat and clerkhook), and an AST
  form written to replace it agreed with the wrong answer until the
  import settled it. IMPORT THE THING.
- NAME THE CHECK THAT ACTUALLY RAN, not the one you meant to run (1.6.44
  item 7). `.flake8` excludes `docs/*/`, so for a year "flake8 is clean"
  was reported as covering the exec'd examples a documentation site
  RENDERS, and it never read one of them: a file in `docs/` containing
  `def broken(:` leaves `flake8 docs/` at exit 0 with zero output —
  measured again here 2026-09-04, alongside `py_compile` exiting 1 with
  the SyntaxError on the same file. The general form of the reporting
  rule: a report says which invocation produced the number, over how
  many files, and with what exit code, because "lint passed" is a claim
  about a command and everyone reads it as a claim about the code. CI
  runs the sweep as its own step (`py_compile sweep of docs/`) and fails
  when the corpus is EMPTY, since a sweep of nothing is the same green
  as a sweep of something clean.
- A CD LANE THAT CALLS ci.yml MUST NOT ALSO LET ci.yml RUN ITSELF on a
  push to main (1.6.44 item 12, clerkhook 44c0c27). Both runs resolve to
  the concurrency group `ci-${{ github.ref }}` with
  `cancel-in-progress: true`, so one is killed at random; when the
  standalone run wins, CD's `test` job is CANCELLED, `deploy` skips,
  `release` never moves — and `main` ahead of `release` then reads as an
  ordinary pending push instead of as the accident it is. Detect:
  `ci.yml` declares `push: branches: [main]` AND `cd.yml` has
  `uses: ./.github/workflows/ci.yml`. Acceptance: a `workflow_call`
  creates NO run of its own, so the next push to main adds ZERO rows to
  the CI workflow list and the matrix appears exactly once, as `ci / *`
  jobs INSIDE the CD run. The template has the correct shape
  (pull_request + workflow_dispatch + workflow_call) and the pin is in
  `tests/test_cd_promotes_release.py` so it cannot drift back.
  Sub-trap, met while writing that pin: PyYAML parses an unquoted `on:`
  key as the BOOLEAN `True`, so `workflow["on"]` raises KeyError on
  every workflow file in this repo. A test that reads triggers must try
  both keys — one that catches the KeyError and moves on asserts
  nothing at all.
- A FORK'S TRAPS SECTION DRIFTS BEHIND THE TEMPLATE'S SILENTLY (1.6.44
  item 14, emojimart 166e33a). The kit is contract-class, so the sync
  never copies it, and nothing printed the gap: emojimart carried 7
  entries against the template's 22, and its HEAD trap still held the
  diagnosis 1.6.32 had corrected — a fork can be reading, and acting
  on, a fact the fleet retired months ago. Detect, printed as a PAIR:
  `python3 scripts/kit_traps.py <fork>/.claude/CLAUDE.md` reports
  `fork N / template M` and names what is missing. Matching is by
  token overlap of each trap's opening sentence, not by exact text,
  because a fork is EXPECTED to merge a trap into its own wording —
  the check exists to find a trap that never arrived, never to police
  prose, and a strict check would train forks to paste over their own
  adaptations. MERGED, NEVER INSTALLED OVER, in both directions.
- A VERIFY VERDICT IS METERING EVIDENCE, NEVER SOLE AUTHORISATION
  (1.6.44 item 18; the security incident of 2026-09-02, hub 0.26.0 →
  0.26.1, 2plot.dev `5ca793c`). The hub gated two admin-data routes on
  its own `/api/agent-key/verify`, whose all-unknown-tier fallback
  answered "allow" WITHOUT READING THE KEY. A verdict fetched from the
  hub says what the hub believes about a key; it does not by itself say that the caller may
  read the page. Any route that consults `hub_client.verify` FOR
  ACCESS must NAME the host-held secret beside it — here
  `CROSS_APP_WEBHOOK_SECRET`, which signs the POST the verdict travels
  on, and without which `enabled()` is False and `verify` answers
  "gated" without asking anyone. A route that does not name one is
  metering-only and must say so in words. The trust chain is: a secret
  this host holds, THEN a verdict — never a verdict alone, and never
  one an unauthenticated caller could have induced.
  SOURCE-PIN THE CLOSED FALLBACKS, do not merely exercise them. A
  behavioural suite cannot see a restored default that pre-empts its
  own guard: change one `return "gated"` to `return "allow"` on the
  no-secret path and every test that configures a secret stays green.
  `tests/test_access.py` parses `verify` and asserts every literal
  return in it is `gated`; the mutation was run both ways.
  AND PIN THE GOOD ROWS BESIDE THE BYPASS ROWS, or the restriction
  tests pass on a route that denies everything.
  REJECT CASE AND WHITESPACE LOOKALIKES OF A TIER, NOT ONE LITERAL —
  and this was LIVE on this host, not hypothetical. `lib/access.check`
  compared the hub's RAW ceiling against three lowercase literals, so a
  ceiling published as "Auth", "ADMIN" or " hidden " matched none of
  them and the machine lane opened on a page the NETWORK had
  restricted. Every other comparison in the tier stack already
  normalised (`page_tiers.register`, `more_restrictive`); that one
  comparison was the gap. A satellite may loosen its own declaration
  and may never loosen the hub's.
- A PROXIED robots.txt IS NOT YOUR robots.txt (1.6.44 item 19; the
  2plot.dev proxy canary). An edge can inject, rewrite or replace
  `/robots.txt` in perfectly valid syntax with no tell beyond a comment
  marker, and a grep for `User-agent:` sails straight past it. To learn
  what the APP declares you must GENERATE it in process through the
  package's own `generate_robots_txt` with the app's registered
  `RobotsConfig` — a reimplementation compares the edge against your
  beliefs about the config, not against the app. To learn what the
  WORLD is told, fetch it. WHEN THEY DIFFER, THE DIFFERENCE IS THE
  FINDING; same family as "verify the artifact the claim is about".
  TWO SHAPES, and only one of them is visible to a directive diff: an
  INJECTED stanza adds directives the app never wrote, and a MARKER
  WITH NOTHING UNDER IT adds none at all — an edge that has claimed the
  file and happens to be passing it through today. Both are pinned in
  `tests/test_network_smoke.py`, and the second is asserted to be
  caught by the marker scan specifically, or it is not being tested.
  AND THE ROW MUST BE ABLE TO RUN. `ai_bot_posture` SKIPS where the app
  cannot be generated beside the script, which is right — a comparison
  with one side is not a comparison — but a row that skips on every
  deploy reads exactly like a row that passed. cd.yml's verify job
  therefore installs the requirements before the battery, and a test
  pins the ordering. A check that cannot run is not a check that
  passed.
