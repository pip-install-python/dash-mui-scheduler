# Divergences from the template

Every DELIBERATE difference between this repo and
dash-documentation-boilerplate, with its reason. This file is the
boundary between design and drift:

- Template syncs read this file FIRST and must not "restore" anything
  recorded here.
- A difference not recorded here is treated as drift and will be
  synced away.
- Record the divergence in the SAME commit that creates it — one
  line: what differs, why, and what the template would otherwise do.
- An empty list is a statement too: it means this repo intends to
  match the template exactly.

## This repo's divergences

1. **This repo is a component LIBRARY as well as a docs site.** It
   carries `src/lib/components/` (React), `package.json`,
   `webpack.config.js`, the committed bundle and generated wrappers
   under `dash_mui_scheduler/`, and a third workflow —
   `.github/workflows/release.yml`, a tag-driven PyPI publish over
   OIDC trusted publishing (`RELEASING.md`). The template documents
   components it does not ship, so it has no equivalent for any of
   this. A sync must not read these as drift, and `release.yml` is a
   third encoding of the interpreter — `tests/test_python_version.py`
   pins it alongside `ci.yml` and `cd.yml`.

2. **Render's DOCKER runtime, so `render.yaml` declares no
   `PYTHON_VERSION`.** The template deploys on Render's native
   `runtime: python`, where `PYTHON_VERSION` is the platform's
   interpreter declaration and must agree with the image. This
   service is `runtime: docker`: Render ignores `PYTHON_VERSION`
   entirely, so declaring one would add a second, INERT Python that
   nothing enforces and nothing serves — precisely the drift spec
   1.6.27 item 5 exists to prevent, with no way for the battery to
   see it. The image IS the runtime declaration here, and
   `tests/test_python_version.py::test_render_yaml_leaves_the_python_to_the_image`
   inverts the template's render.yaml pin to keep it that way. If
   this service ever moves to the native runtime, that pin fails on
   purpose and says what to do.

3. **The Dockerfile's `HEALTHCHECK` is a python-urllib probe, not
   the template's `curl`.** This image installs no apt packages at
   all — no node toolchain (the bundle is committed) and therefore
   no curl — so the template's block would need an apt layer added
   to run one probe. Same contract: `${PORT:-8598}` defaulted at the
   point of use, and `docker inspect` reports a real verdict, which
   is what ci.yml's health-verdict step asserts.

4. **This site has no `home.md`.** `pages/home.py` is a hand-written
   DMC landing page, and the root machine-lane prose is the
   `llms_doc=` string in `run.py`. Spec 1.6.22-27 item 4's two-lane
   pin therefore reads `run.py` where upstream reads
   `pages/home.py` — same contract (whatever the docs lane
   substitutes, the home lane substitutes too), different file.
   `run.py`'s `llms_doc` runs through `lib.versions.substitute_versions`
   for exactly that reason.

5. **`block_ai_training=False` — this host does not disallow the AI
   training crawlers.** Most satellites run `True`. These are
   MIT-licensed component docs whose whole point is being read; the
   robots artifact therefore carries no training-bucket `Disallow`,
   and both batteries PIN the divergence rather than tolerate it
   (`scripts/network_smoke.py` and `scripts/smoke_live.py` fail if a
   `ClaudeBot` stanza ever appears). See `run.py`'s `configure_seo`
   call for the reasoning in full.
   RE-MEASURED 2026-08-29 at the dash-improve-my-llms 2.8.0 floor: the
   STATUSES are unchanged (200 on `/`, `/llms.txt` and `/healthz` for
   ClaudeBot and GPTBot alike — see the Posture block below), but the
   DOCUMENT on `/` moved. 2.8's lane assignment follows the package's
   vendor registry, so both vendors now receive the prerendered crawler
   document where they previously got the app shell. That is the allow
   posture working, not a regression: the training crawlers are not
   refused here, and what they now read is this site's prose rather
   than a JavaScript stub.

6. **`scripts/smoke_live.py` is a PORT of the template's, never a
   byte-copy.** Spec 1.6.22-1.6.29 item 6 reclassed the file
   contract-class at template 1.6.29 for a different reason (fork-owned
   test stubs pin its interface); here there is a second, harder reason:
   two checks in the list are this host's. The robots block asserts the
   `ChatGPT-User` / `PerplexityBot` rows and the ABSENCE of a `ClaudeBot`
   stanza — divergence 5 — where the template asserts
   `ClaudeBot -> Disallow: /`, so a byte-copy of the template's file
   fails on a correctly-configured host. The second is a non-fatal WARN
   when the hub bulletin is unwired, which the template does not carry.
   Everything else — the wake loop, the retry ladder, the SSL context,
   the crawler/browser identity parity block — tracks the template
   verbatim and should be ported whenever it moves, with one addition:
   the Clerk bootstrap token that gates the auth probe is a named
   constant, `CLERK_BOOTSTRAP_MARKER`, where the template inlines the
   string. `tests/test_auth_wiring.py` imports it and pins it against
   the branch `lib/auth.py` actually emits — spec item 7's class, whose
   render-with-fake-config half remains open. The path is fenced
   `byte-owned` below so no fan-out can decide otherwise.

7. **`scripts/network_smoke.py` passes a certifi SSL context to
   `urlopen`; the template still calls it bare.** Ahead of the template,
   not behind it: directed fleet-wide by the ops seat on 2026-08-26,
   the same fix `smoke_live.py` already carried. Without it, any Python
   without OS trust-store integration (macOS — the fleet's whole
   local-dev half) fails every https handshake and the battery reports
   a healthy host as DOWN, every check zero. Linux CI cannot see it and
   no wired test can (they patch the transport), so
   `tests/test_network_smoke.py::test_the_batterys_urlopen_carries_the_ssl_context`
   holds the line from the source. Retire this entry when the template
   adopts the same context.

8. **`templates/index.html` declares ONE canonical, as the literal token
   `__PAGE_URL__`; the template declares none.** Recorded 2026-08-30 after
   the ops seat read it as drift — it has been pinned by
   `tests/test_config.py::test_the_only_canonical_is_the_per_request_token`
   and explained in that pin's docstring since before this repo carried a
   DIVERGENCES.md, and never written down here. That omission is the whole
   reason it looked like drift, which is this file's rule proving itself.
   The reason it exists: the template lets the package inject a canonical,
   which reaches the CRAWLER document only. This app instead ships the token
   in the shell and `run.py`'s `@dash.hooks.index()` hook (`run.py:357`)
   replaces it with the REQUESTED page's URL on every response, so a client
   that reads HTML without running JavaScript already has the right
   canonical rather than the home page's. Deleting the line would leave the
   browser lane with NO canonical in the server response: `grep -rn
   'rel="canonical"'` over the tree finds exactly two emitters — this one,
   and `run.py:555`, which is inside `_augment_crawler_html` and guarded, so
   it fires on the crawler lane only. The URL-sync script at
   `templates/index.html:167` is not a third: its `head()` helper is
   find-or-create and runs on client-side navigation, so it cannot help a
   JS-less reader of the first response. MEASURED 2026-08-30 by parsing
   ELEMENTS rather than counting substrings — `/`, `/quickstart` and
   `/changelog`, both lanes: exactly ONE `<link rel="canonical">` each,
   carrying that page's own URL. A substring grep reads 2 on the browser
   lane because the sync script's selector mentions the tag; that artifact
   is what produced this repo's own false report of a duplicate, and it is
   the same trap the template hit on its note-63 probe. Count elements.

9. **`pages/markdown.py` expands `.. kwargs::` into the prose, so the props
   reach the MACHINE lane; the template's does not.** Ahead of the template
   and measured here first, on spec 1.6.42's amended highlight 7 (the fourth
   empty-props mechanism). A markdown2dash directive that renders Dash
   components puts its output in the React tree ONLY — the machine lane, the
   dimll prerender and the crawler HTML are all built from the markdown
   SOURCE, where the directive line is stripped, and the renderer returns
   None on empty so a broken spec renders as silence. Measured on this host
   2026-08-31, before the fix: `/event-calendar/llms.txt` carried the prose
   and NOT ONE of `EventCalendar`'s 33 props; the same was true of the
   prerender and the app-shell markup. On a component-documentation site that
   is the whole point of the page. The fix follows the `.. source::`
   treatment already in this file — the same fence-aware walker, so a
   directive shown inside a fenced block is still documentation and not a
   command — and resolves the component through `lib/directives/kwargs.py`'s
   own `_PACKAGE_MAP` and `parse_dash_kwargs`, ONE shared parse, so the two
   lanes cannot describe the same component differently. An unresolvable
   spec emits a visible marker rather than nothing, because silence is what
   let this survive. `tests/test_kwargs_lane_parity.py` pins ROWS and row
   CONTENT in all three curl-visible artifacts (never a section heading — a
   heading pin passes on an empty table) and is MUTATION-CHECKED: disabling
   the expansion turns four of its pins red. The template carries no
   equivalent; retire this entry if it adopts one.

## Retired

- ~~**`components/header.py` keeps three pieces of this fork's identity.**~~
  RETIRED 2026-08-31, by adoption. Recorded at item 16 as the evidence that
  file could not be cargo: the TEMPLATE's copy hardcoded `ddb.png`,
  `c="#03c7e5"` and `visibleFrom="xs"` on the wordmark, so a byte-copy would
  have shipped this site the template's logo and colour. Template 1.6.41
  lifted all of it into `lib/constants.py` — `LOGO_ASSET`, `LOGO_STYLE`,
  `WORDMARK_COLOR`, `WORDMARK_VISIBLE_FROM` — and adopted this fork's
  `create_link(visible_from=)` parameter besides. `components/header.py` is
  now BYTE-IDENTICAL to the template at 4ac02e0 and holds no fork content;
  the identity lives in the constants block where a fork edits it. This is
  the loop closing on a divergence that was always a template gap rather
  than a real difference.

- ~~**`scripts/network_smoke.py`'s default UA names the BROWSER lane.**~~
  RETIRED 2026-08-30, by adoption. Recorded here on 2026-08-29 as ahead of
  the template and measured here first: at dash-improve-my-llms 2.8.0 a UA
  with no browser engine token is crawler-lane, so the battery's bare
  `2plot-internal/1.0 (...) network-smoke` made every default-UA check read
  the prerendered crawler document — `installable_as_an_app` reported "no
  manifest link" against a host that serves one, and
  `social_card_real_pixels` reported two `og:image` tags. Both would have
  gone red in CD's verify job. Template 1.6.40 (8ceca5c) adopts the fix in
  the shape shipped here — a Chrome/AppleWebKit token first, the internal
  token after it, `CRAWLER_UA` untouched — as sync item 17, so this repo now
  carries the template's `BROWSER_UA` constant verbatim and there is no
  difference left to record. `tests/test_network_smoke.py::
  test_the_batterys_default_ua_is_browser_lane_and_still_internal` holds it
  from both ends: the default is browser-lane AND still carries the internal
  token, which is the pair that makes the fix safe.

- ~~**`dependabot.yml` runs no `npm` ecosystem.**~~ RETIRED
  2026-08-26. The reason was real and still holds — this repo has a
  genuine `package.json` (the template deleted its own), but the JS
  bundle is rebuilt and committed BY HAND, so a lockfile PR would
  arrive with no regenerated artifact and nothing in CI could
  validate it. It is retired as a *divergence* because template
  1.6.24 removed the pip ecosystem and ships no npm entry either, so
  this repo now carries `.github/dependabot.yml` byte-identical to
  the template and there is no difference left to record. Kept, not
  deleted: the template's own DIVERGENCES.md still cites
  "muischeduler's no-npm dependabot scope" as a live fleet
  precedent, and a sync that adds an npm ecosystem here would still
  be wrong.

## Byte-owned paths

Paths this fork owns byte-for-byte. The F3b fan-out never overwrites
a path listed here; everything else in the spec's `sync-verbatim`
block is the template's to update mechanically. Prose above explains
divergences; this block is the machine answer.

Repo-relative paths, one per line, `#` comments, no `..`; exactly one
block. An EMPTY block means "the template owns every sync-verbatim
path here" — present so the absence is a statement. When the block
exists it is authoritative; a fork without it gets the conservative
mention heuristic (over-flags, never restores).

Audited 2026-08-26 against the three specs' `sync-verbatim` blocks
(the three kit skills, `tests/test_claude_kit.py`,
`.github/dependabot.yml`, `tests/test_auth_demos.py`): every one of
those paths is byte-identical to template 1.6.27 here, and no
divergence above makes a byte-level claim on any of them. Divergence
1 names `release.yml` and divergence 2 names
`tests/test_python_version.py` — neither is a sync-verbatim path
(both are session-class by their specs), so neither becomes an
entry.

RE-AUDITED 2026-08-26 at template 1.6.29, and the block is no longer
empty. `scripts/smoke_live.py` rode the block for exactly one release
(1.6.28) before 1.6.29 pulled it back out; the fence entry below is
belt-and-braces, and it is the one path here where a byte-copy is
KNOWN to land red rather than merely suspected — divergence 6 has the
proof. Nothing else changed: the six paths above remain the
template's to update mechanically.

```yaml byte-owned
# Contract-class, not verbatim (spec item 6): the transport half is the
# template's and gets ported when it moves, but the CHECK LIST carries
# divergence 5's robots posture — a byte-copy asserts a ClaudeBot
# stanza this host deliberately does not emit and fails a healthy site.
- scripts/smoke_live.py
```

## Posture

What this host ANSWERS, as measured — never as intended. The hub's F4
battery seeded these per-host postures from its own table, which is a
copy of a measurement somebody took once; this block homes them in the
repo that can keep them true, and the hub reads it instead.

Four keys, all optional. An EMPTY block means "the template defaults" —
present, so the absence is a statement. `tests/test_claude_kit.py`
validates the shape (and holds `runtime:` against render.yaml, where the
repo declares one); nothing validates the numbers but a probe, so
re-measure when you change what this host serves:

    ai_bots   the status an AI-crawler UA receives per path, measured
              with a real vendor UA (ClaudeBot, GPTBot — NOT a UA-less
              curl, which is classified separately). ALL 200 here, and
              that is divergence 5, not an oversight: these are
              MIT-licensed component docs and this host does not refuse
              the training crawlers. The template answers 403 on `/`.
    healthz   `full` — the fleet payload (ok, app, backend, build,
              python, dash_version, geo).
    runtime   `docker` — divergence 2. Render ignores PYTHON_VERSION on
              this service; the image is the interpreter declaration.
    deploy    `release-branch` — Render deploys `release`, which only CD
              writes after a green matrix (1.6.35, sync item 13);
              `build` on /healthz is HEAD of `release`, and `main` ahead
              of it is an uncertified push pending. ABSENT reads as
              `main`.

RE-MEASURED on the wire 2026-08-30 at build 4e8c00c — the build this
round shipped, running the dash-improve-my-llms 2.8.0 floor — and read
TWICE by two seats independently rather than transcribed once: this repo
at 17:33Z and the ops seat at ~17:45Z, both sending
`Accept: text/html,*/*;q=0.8` and the real vendor UAs (ClaudeBot/1.0 and
GPTBot/1.2, never a UA-less curl, which the package classifies
separately). Both reads agree on all nine cells:

               /      /llms.txt   /healthz
    ClaudeBot  200       200        200
    GPTBot     200       200        200
    Chrome 120 200       200        200

and `robots.txt` carries ZERO `Disallow` lines — not merely none for
those two vendors, none at all. That is the shape `block_ai_training=False`
produces: no training stanza exists and they fall under `User-agent: *`.
So item 15's flip is `already-present` here, and these numbers are this
host's own measurement rather than the hub's seeded table.

The browser row is in the table on purpose. On most satellites it is the
row that differs — a blocked vendor gets 403 on the browser document
while the agent surfaces stay open, and that asymmetry IS their posture.
Here there is no asymmetry, and recording the identical third row is how
this fence says so rather than leaving it to be inferred.

What moved at the 2.8.0 floor is the DOCUMENT, not the status: the lane
now follows the package's vendor registry, so ClaudeBot and GPTBot get
the prerendered crawler prose on `/` where they used to get the app
shell. Wire minus in-process is zero — no edge wall — consistent with the
owner's 2026-08-30 finding that no Cloudflare AI-bot rule exists on this
plan at all.

`deploy: release-branch` was declared with sync item 13 and is now backed
by a green promote: CD run 33318542986 (attempt 3) ended `success`, and
`origin/release` == `origin/main` == the /healthz build == 4e8c00c. Note
what that does and does not prove. A GREEN push shows the road works; it
cannot show Render is watching `release`, because both refs hold the same
sha and the two configurations are indistinguishable from the wire. The
discriminating observation is the next push that goes RED on `main`:
`release` must not move and the wire must not change.

```yaml posture
ai_bots: {"/": 200, "/llms.txt": 200, "/healthz": 200}
healthz: full
runtime: docker
deploy: release-branch
```
