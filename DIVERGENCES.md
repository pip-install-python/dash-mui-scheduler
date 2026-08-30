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

8. **`scripts/network_smoke.py`'s default UA names the BROWSER lane;
   the template's is a bare `2plot-internal/1.0 (...) network-smoke`.**
   Ahead of the template, not behind it, and measured here first:
   dash-improve-my-llms 2.8.0 classifies by its vendor registry, and a
   UA carrying no browser identity is the CRAWLER lane. Every
   default-UA check in the battery then measured the prerendered
   crawler document instead of the app shell — `installable_as_an_app`
   reported "no manifest link" against a host that serves one, and
   `social_card_real_pixels` reported two `og:image` tags. Both went
   red on this repo's own suite the moment the floor moved. The fix
   prefixes a real Chrome token and keeps the internal-traffic token
   after it, so the analytics contract is untouched; `CRAWLER_UA` is
   unchanged and still names Googlebot. Same class as the template's
   own 1.6.34 fix to `tests/test_proxy_scheme.py` (a UA-less request
   receiving the crawler document), applied one file further out.
   Reported to the ops seat as a fleet pushback — every fork's battery
   ships this UA. Retire this entry when the template adopts the same
   default.

9. **`components/header.py` keeps three pieces of this fork's identity
   that the template hardcodes in the same file.** Sync item 16 (1.6.38)
   makes navbar/header/footer cargo-eligible "once a fork carries the
   constants block" — and this fork does: `WORDMARK`, `GITHUB_URL`,
   `CATEGORY_ORDER`, `UPSTREAM`, `API_PACKAGES` and `resources()` are all
   in `lib/constants.py` now, and `components/navbar.py` and
   `components/footer.py` came across byte-identical. `header.py` did not,
   and the reason is in the TEMPLATE's copy, not this one: it still names
   `get_asset_url('ddb.png')`, `c="#03c7e5"` and `visibleFrom="xs"` on the
   wordmark inline. This host's logo is `assets/dms_logo.svg` (an SVG —
   the template's fixed `width: 36px` is wrong for it), its accent is
   `#3399ff` (the `brand` ramp in components/appshell.py), and its
   wordmark is `visibleFrom="md"` because "dash-mui-scheduler" is
   seventeen characters and crowds the burger and search at xs. One more
   difference is this fork's own: `create_link()` takes a `visible_from`
   breakpoint so the GitHub icon drops on phone widths. A byte-copy of
   the template's header would therefore ship this site the template's
   logo and colour. Retire this entry when the template lifts the logo
   asset, the wordmark colour and the wordmark breakpoint into
   `lib/constants.py` — reported to the ops seat as the evidence item
   16's reclass asked for.

## Retired

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

RE-MEASURED on the wire 2026-08-30 (sync item 15's acceptance), build
4a4ef49, with the real vendor UAs — ClaudeBot/1.0 and GPTBot/1.2, not a
UA-less curl, which the package classifies separately:

    /          ClaudeBot 200   GPTBot 200
    /llms.txt  ClaudeBot 200   GPTBot 200
    /healthz   ClaudeBot 200   GPTBot 200

and `robots.txt` carries no `Disallow` for either — no training stanza
at all, which is the shape `block_ai_training=False` produces (they fall
under `User-agent: *`). Item 15's flip is therefore `already-present`
here: this host has allowed since it was built, and the numbers below
are its measurement, not the hub's seeded table. The same six were read
on 2026-08-29 and reproduced in-process on the 2.8.0 wheel this round
ships — the STATUSES do not move at 2.8.0; the DOCUMENT on `/` does,
because the lane now follows the package's vendor registry, so both
vendors get the prerendered crawler prose where they used to get the app
shell. A browser gets 200 on all three paths too, so on this host the
fence has no asymmetry to record — which is itself the posture. Wire
minus in-process is zero here: no edge wall, consistent with the owner's
2026-08-30 finding that no Cloudflare AI-bot rule exists on this plan.

```yaml posture
ai_bots: {"/": 200, "/llms.txt": 200, "/healthz": 200}
healthz: full
runtime: docker
deploy: release-branch
```
