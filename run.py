import inspect
import os
import sys
import dash
from dash import Dash
from components.appshell import create_appshell


def _version(text: str) -> tuple:
    """("4.4.1rc0") -> (4, 4, 1). Trailing rc/dev segments are dropped."""
    parts = []
    for chunk in text.split(".")[:3]:
        digits = ""
        for char in chunk:
            if not char.isdigit():
                break
            digits += char
        if not digits:
            break
        parts.append(int(digits))
    return tuple(parts)


# AI/LLM Integration & SEO — dash-improve-my-llms 2.0
# 2.0 supports Flask, FastAPI, and Quart via a single backend-detecting
# dispatcher. The custom Flask-only routes that used to live in this file
# (`/<page>/llms.txt`, `/<page>/page.json`, `/<page>/llms.toon`) are gone —
# the package owns `/llms.txt` and `/<page>/llms.txt`, and `/page.json` /
# `/llms.toon` were intentionally dropped in 2.0 (Dash 4.3 MCP covers the
# structured-introspection job they were doing).
from dash_improve_my_llms import (
    __version__ as LLMS_PKG_VERSION,
    add_llms_routes,
    LLMSConfig,
    RobotsConfig,
    mark_hidden,
    register_page_metadata,
)

# The version requirements.txt pins. Asserted at boot — see the floors block.
#
# 2.7.1 is the network floor (round-3). Below 2.7.1 the llms.txt v2
# discovery relations are missing on both lanes — rel=alternate /
# rel=describedby plus the matching Link headers — along with the
# `Accept: text/plain` ramp and the representation digest, which is the
# machine route from a page to that page's prose. Below 2.7.0 every page
# serves a DUPLICATE H1 to crawlers (the injected prerender header plus the
# doc body's own), the home footer doubles its /llms.txt link, and a page
# that merely MENTIONS the prerender marker loses its prerender entirely —
# the injector's idempotency probe is a substring match, and that trap
# blanked two hub pages in this fleet. Below 2.6.1 the universal prerender
# ships with a literal `hidden` attribute: every visibility-respecting
# consumer (html-to-text extractors, arguably crawler content-weighting)
# reads "Loading..." where this site's prose should be. Below 2.6.0 the sitemap
# goes back to lying — `register_page_metadata(lastmod=)` is swallowed into
# **kwargs and SILENTLY ignored, so the real dates in the docs frontmatter
# revert to invented build dates. Below 2.5.1 the Tier-B SEO standard
# unwinds: no `configure_seo`, no per-page title/image_url in the crawler
# document, /favicon.ico serves the app shell.
# `configure_seo` is imported AFTER this floor fires so a stale environment
# gets the floor's diagnosis instead of a bare ImportError.
LLMS_PKG_FLOOR = (2, 7, 1)

# THE FORK POINT — claim this app's network identity before any hub-facing
# module imports. Every module that names this app (satellite_reporter,
# ad_client, hub_client, bulletin) carries its own fallback default, and
# after a template sync those defaults can DISAGREE: the byte-copied
# reporter says "boilerplate" while this fork's other modules say
# "muischeduler", so an unset SATELLITE_APP_KEY files this site's traffic
# under the TEMPLATE's hub row (found live on pannellum, 2026-08-21).
# Keeping the reporter byte-identical to the template's is the acceptance
# check for a wave sync, so the identity claim lives HERE instead.
# setdefault: a real env value (Render dashboard, .env) always wins; this
# line only closes the unset gap. FORKS CHANGE THIS ONE STRING.
os.environ.setdefault("SATELLITE_APP_KEY", "muischeduler")

# Analytics tracking
from lib.analytics_tracker import tracker

# Backend selection (flask | fastapi | quart) — see lib/backend.py
from lib.backend import resolve_backend, get_backend_info

scripts = [
    "https://unpkg.com/hotkeys-js/dist/hotkeys.min.js",
]

# ----------------------------------------------------------------------------
# Pluggable backend (Dash 4.1+)
# ----------------------------------------------------------------------------
BACKEND = resolve_backend()
BACKEND_INFO = get_backend_info(BACKEND)
IS_FLASK = BACKEND == "flask"

print(
    f"[muischeduler] Starting Dash {dash.__version__} "
    f"(dash-improve-my-llms {LLMS_PKG_VERSION}) on backend='{BACKEND}'"
)

# ----------------------------------------------------------------------------
# Dependency floors — enforced, not advised.
#
# These were warnings first. That was not enough: an IDE run configuration
# pointing at another project's virtualenv starts this app quite happily
# against whatever versions that environment holds, serves visibly older
# behaviour, and the warning scrolls past above a wall of page-loading logs.
# A version below the floor stops the boot and says what to do, so the app is
# never wrong-but-running. ALLOW_STALE_DEPS=1 downgrades these to warnings if
# you are deliberately testing an older release.
# ----------------------------------------------------------------------------

ALLOW_STALE_DEPS = os.environ.get("ALLOW_STALE_DEPS", "0") == "1"


def _dependency_floor(message: str, fatal: bool) -> None:
    """Print, or refuse to start. Either way, name the interpreter.

    `sys.executable` is the fact that settles which environment is actually
    serving, and it is the one nobody thinks to check first.
    """
    detail = (
        f"{message}\n"
        f"    running from: {sys.executable}\n"
        f"    expected:     "
        f"{os.path.join(os.path.dirname(os.path.abspath(__file__)), '.venv/bin/python')}\n"
        "    fix: point your run configuration at this project's own .venv, "
        "or reinstall with `pip install -r requirements.txt`.\n"
        "    (set ALLOW_STALE_DEPS=1 to start anyway)"
    )
    if fatal and not ALLOW_STALE_DEPS:
        raise RuntimeError("\n[muischeduler] " + detail)
    print("[muischeduler] WARNING: " + detail)


if LLMS_PKG_FLOOR > _version(LLMS_PKG_VERSION):
    _dependency_floor(
        f"dash-improve-my-llms {LLMS_PKG_VERSION} is below the "
        f"{'.'.join(str(n) for n in LLMS_PKG_FLOOR)} floor in requirements.txt. "
        "Below 2.7.1 the llms.txt v2 discovery relations (rel=alternate/"
        "describedby + Link headers), the text/plain Accept ramp and the "
        "representation digest are missing — the machine lane loses its "
        "route from a page to that page's prose. Below 2.7.0 every page "
        "serves a DUPLICATE H1 to crawlers (the injected prerender header "
        "plus the doc body's own), the home footer doubles its /llms.txt "
        "link, and a page that merely MENTIONS the prerender marker loses "
        "its prerender entirely (the marker-in-comment trap). "
        "Below 2.6.1 the universal prerender ships `hidden`, so every "
        "visibility-respecting consumer (text extractors, arguably crawler "
        "content-weighting) reads 'Loading...' instead of the page's prose. "
        "Below 2.6.0 the sitemap goes back to lying: `lastmod=` is accepted "
        "into **kwargs and SILENTLY IGNORED, so every real date stamped in "
        "the docs frontmatter is swallowed and <lastmod> reverts to invented "
        "build dates. Below 2.5.1 the Tier-B SEO standard additionally "
        "unwinds: `configure_seo` does not exist, the crawler <title> drops "
        "back to the bare page name, per-page title/image_url/schema_type "
        "never reach the crawler document, and /favicon.ico serves the app "
        "shell instead of an icon.",
        fatal=True,
    )

# Imported after the floor on purpose: on a pre-2.5.0 package this name does
# not exist, and the floor's diagnosis above beats a bare ImportError. The
# fallback exists only for ALLOW_STALE_DEPS=1 — the floor is fatal otherwise.
try:
    from dash_improve_my_llms import configure_seo  # noqa: E402
except ImportError:  # pragma: no cover — ALLOW_STALE_DEPS with a pre-2.5.0 pkg

    def configure_seo(**_kwargs) -> None:
        print(
            "[muischeduler] WARNING: configure_seo unavailable (pre-2.5.0 "
            "package) — crawler identity tags and root icons not emitted."
        )

# ----------------------------------------------------------------------------
# Clerk satellite auth. MUST run BEFORE Dash(...) — register_clerk_auth
# installs @dash.hooks callbacks that fire during app construction, so calling
# it afterwards silently does nothing.
#
# Fully optional: a no-op with no CLERK_* keys. lib/auth.py is the single
# source of truth and is byte-copied from the network template — it replaced
# this repo's hand-rolled lib/clerk_satellite.py, whose three 0.9.0-era
# satellite fixups are all upstream now (data-clerk-domain in 0.9.1, the
# openSignIn->buildSatelliteRedirect branch in 0.9.2). What the template
# keeps beyond the package is the DELEGATION (a capture-phase listener, so a
# sign-in button Dash renders late still works) and the sign-out shim.
# ----------------------------------------------------------------------------
from lib import auth as _auth  # noqa: E402

CLERK_ENABLED = _auth.register()

if CLERK_ENABLED:
    from dash import hooks as _dash_hooks

    # Dash 4.2 WS-transported callbacks run in a THREAD POOL no HTTP middleware
    # ever touches — the package's WS hooks bind renderer->user at connect so
    # current_user() resolves in WS callbacks too. Since dash-clerk-auth 0.9.0,
    # configure_app registers those hooks ITSELF (with the session_secret
    # pulled from the active config); the old explicit
    # register_websocket_auth() call is gone. Assert with
    # dash_clerk_auth.ws_auth_registered() if in doubt.

    # The package's layout hook prepends dcc.Location(id="url", refresh=False),
    # duplicating the appshell's refresh="callback-nav" Location — which the
    # header search (Output url.href) and the splicer redirect REQUIRE for
    # Pages navigation. Strip the hook's copy: this app-side hook registers
    # after the package's (priority -1 < 0) so it runs second and receives the
    # prepended list. (Verified: exactly one id="url" in the served layout.)
    @_dash_hooks.layout()
    def _strip_clerk_url(layout):
        if isinstance(layout, list) and getattr(layout[0], "id", None) == "url":
            return layout[1:]
        return layout

# ---------------------------------------------------------------------------
# Disable Dash 4.2 websocket-callback transport ENTIRELY (FastAPI/Quart only).
# ---------------------------------------------------------------------------
# We do not use websocket callbacks. But the FastAPI backend ALWAYS advertises
# /_dash-ws-callback (`websocket_capability = True`), so the renderer's
# SharedWorker connects on every page and then drives the socket: on each
# (re)connect it force-starts the app's "persistent" callbacks — every no-input
# /no-output server callback — over the socket. With global websocket callbacks
# OFF (kept off on purpose: global-on routes EVERY callback, incl. the pages
# router, through a thread pool no cookie/ContextVar reaches → the owner
# gate reads anonymous), the server REJECTS any such callback that isn't
# websocket=True, and that rejection (dash backends/_fastapi.py:758 →
# _validate.py:657) is raised UNCAUGHT inside the socket's receive loop, killing
# the connection → the SharedWorker reconnects → re-starts the same callback →
# dies again. The result is an infinite reconnect loop that floods the logs with
# `WebSocketCallbackError` (observed in production 2026-06-13). It is also
# inherently fragile: a no-input/no-output callback is keyed by its source
# `file:line` (dash _utils.create_callback_id), so under our `.. exec::` page
# loader those ids are unstable and can miss the server's callback_map outright.
# Since nothing here needs the socket (the old eco heartbeat was cosmetic; Clerk
# auth is clientside; the match report + PiratesBargain transfer are plain HTTP),
# turn the capability OFF before the app is built: no WS route is registered and
# config.websocket is never emitted, so the SharedWorker never connects and no
# callback can ride the socket. Re-enable deliberately (and make every
# no-input/no-output callback websocket=True) if a real-time feature ever needs it.
try:  # pragma: no cover - FastAPI backend is the prod target; flask has no WS
    from dash.backends import _fastapi as _dash_fastapi_backend
    _dash_fastapi_backend.FastAPIDashServer.websocket_capability = False
except Exception:
    pass

# ----------------------------------------------------------------------------
# Index template
# ----------------------------------------------------------------------------
# templates/index.html carries __BASE_URL__/__PAGE_URL__/__VERSION__ tokens
# instead of hard-coded URLs. BASE_URL (lib/constants, from APP_BASE_URL) is the
# single source of truth for every absolute URL the site emits — the reason a
# host move is one env var, and the reason the template once spent a release
# telling search engines every page was a duplicate of a host that never existed.
from lib.canonical_host import canonical_redirect
from lib.constants import (
    APP_VERSION, BASE_URL, CANONICAL_HOST, CANONICAL_HOST_REDIRECT,
    OG_IMAGE_ALT, OG_IMAGE_HEIGHT, OG_IMAGE_URL, OG_IMAGE_WIDTH,
    PUBLISHER, SAME_AS, SITE_BRAND, SITE_DESCRIPTION, require_owned_base_url,
)
from lib.versions import substitute_versions

# Refuse to boot in production with an unset or platform-generated base URL —
# every canonical/og/sitemap URL would advertise the wrong host, silently.
require_owned_base_url()

_INDEX_TEMPLATE = open('templates/index.html').read()
_index_string = (
    _INDEX_TEMPLATE
    .replace("__BASE_URL__", BASE_URL)
    .replace("__VERSION__", APP_VERSION)
    # __PAGE_URL__ is deliberately left in place — the index hook below fills it
    # with the REQUESTED page's canonical URL on every response.
)

# Dash 4.3+ MCP server: exposes layout, components, pages and (whitelisted)
# callbacks to MCP clients over Streamable HTTP. Off unless DASH_MCP_ENABLED=1,
# because it is a live introspection surface on a public host.
#
# This has to be a CONSTRUCTOR argument — Dash starts the server during
# __init__, so there is no supported way to switch it on afterwards.
# dash-improve-my-llms separately registers each page's prose as a `dash.mcp`
# resource, which is what gives an MCP client the docs alongside the
# introspection.
#
# Passed as **kwargs rather than named arguments, because Dash validates
# unknown constructor keywords by raising TypeError. `enable_mcp` landed in
# 4.3, so naming it unconditionally makes the app refuse to boot on 4.2 with
# an error that says nothing about MCP — over a feature that is off by
# default anyway.
MCP_ENABLED = os.environ.get("DASH_MCP_ENABLED", "0") == "1"
MCP_PATH = os.environ.get("DASH_MCP_PATH", "_mcp")

MCP_KWARGS = {}
if MCP_ENABLED:
    if "enable_mcp" in inspect.signature(Dash.__init__).parameters:
        MCP_KWARGS = {"enable_mcp": True, "mcp_path": MCP_PATH}
    else:
        print(
            f"[muischeduler] DASH_MCP_ENABLED=1 ignored: dash "
            f"{dash.__version__} has no MCP server (needs >= 4.3)."
        )

app = Dash(
    __name__,
    backend=BACKEND,
    suppress_callback_exceptions=True,
    use_pages=True,
    external_scripts=scripts,
    update_title=None,
    prevent_initial_callbacks=True,
    index_string=_index_string,
    # The site identity, stated the same way on every surface (network
    # standard; tests/test_site_identity.py pins it). Feeds the <title>
    # fallback and the "name" in the crawler HTML's JSON-LD; per-page titles
    # come from register_page and are applied by the renderer on navigation.
    title=SITE_BRAND,
    # Belt-and-suspenders: keep the GLOBAL websocket flag off too (see the
    # capability disable above for the full rationale).
    websocket_callbacks=False,
    **MCP_KWARGS,
)

if MCP_KWARGS:
    print(
        f"[muischeduler] Dash MCP server enabled at /{MCP_PATH.lstrip('/')} "
        f"(dash {dash.__version__})."
    )

# Expose backend info so layout components can render a badge without
# re-reading the env var (which could drift between processes/workers).
app._backend_info = BACKEND_INFO


# ----------------------------------------------------------------------------
# Per-request canonical URL.
# ----------------------------------------------------------------------------
# One HTML document serves all 17 routes, so a canonical baked into the template
# is right for exactly one of them. The inline script in templates/index.html
# keeps it right across CLIENT-side navigation; this hook makes the very first
# server response already correct, so a crawler that reads HTML without running
# JavaScript sees the real canonical instead of the home page's.
@dash.hooks.index()
def _resolve_page_url(index: str) -> str:
    path = "/"
    try:
        request = app.backend.request_adapter()
        if request is not None and getattr(request, "path", None):
            path = "/" + request.path.strip("/")
    except Exception:
        pass  # no request context (build check, tests) → fall back to the home URL
    return index.replace("__PAGE_URL__", BASE_URL + (path if path != "/" else "/"))


# ============================================================================
# AI/LLM & SEO Configuration
# ============================================================================

# Base URL for SEO (sitemap.xml + llms.txt emit absolute URLs from this).
# Env-driven so the Render service / custom domain sets it without a code change.

app._base_url = BASE_URL

# Bot management. See dash-improve-my-llms 2.0 SKILLS for the full menu.
#
# DELIBERATE DEVIATION from the network default (which is
# block_ai_training=True): these are MIT-licensed component docs, and being
# in the training corpus is precisely how a model comes to recommend the
# library. Under block_ai_training=False the package emits no training-bucket
# stanza at all — no ClaudeBot/GPTBot/CCBot lines. Both halves of that are
# asserted so the flag cannot flip silently:
# tests/test_llms_routes.test_robots_artifact_fingerprint locally, and
# scripts/smoke_live.py against the deployed host.
# (The comments below say what each flag DOES when true, not what is on.)
app._robots_config = RobotsConfig(
    block_ai_training=False,      # would Disallow GPTBot, ClaudeBot, CCBot, ...
    allow_ai_search=True,         # Allow Claude-User/-SearchBot, ChatGPT-User, ...
    allow_traditional=True,       # Allow Googlebot, Bingbot, etc.
    crawl_delay=10,
    disallowed_paths=[],
)

# ============================================================================
# Register supplemental metadata for the home page.
# Markdown-driven pages register their own LLMS_DOC inside pages/markdown.py
# (the expanded markdown body becomes the literal /llms.txt response).
# ============================================================================

register_page_metadata(
    path="/",
    # SITE_BRAND here is what dash-improve-my-llms ≥2.3.4 resolve_site_title
    # publishes as the /llms.txt H1 and the viewer's brand chip — the display
    # name "Home" is deliberately generic so this one is load-bearing.
    name=SITE_BRAND,
    description=SITE_DESCRIPTION,
    # Run through substitute_versions like every other served document.
    # This site has no home.md — the root's machine-lane prose is this
    # string — so pages/markdown.py's substitution never touches it, and a
    # `{{VERSION:...}}` written here would ship RAW on /llms.txt, the
    # most-read machine surface the site has. The docs lane and the home
    # lane must substitute the same things; tests/test_site_identity.py
    # pins both call sites by AST (a comment naming the call satisfies a
    # grep on a file that never runs it).
    llms_doc=substitute_versions(
        "# dash-mui-scheduler — MUI X scheduling for Dash\n\n"
        "A Plotly Dash component library wrapping the MUI X Scheduler.\n\n"
        "Install: `pip install dash-mui-scheduler`\n\n"
        "Components: EventCalendar (day/week/month/agenda views, drag & resize, "
        "inline editing, resources), EventCalendarPremium (adds the RRULE "
        "recurrence engine), EventTimeline (resource lane view), and the polar "
        "charts RadialLineChart and RadialBarChart. "
        "Premium MUI X features activate via the `licenseKey` prop.\n\n"
        "Docs pages (each has its own /<page>/llms.txt): /quickstart, "
        "/event-calendar, /playground, /events, /resources, /views, /navigation, "
        "/responsive, /drag-resize, /editing, /preferences, /recurrence, "
        "/event-timeline, /localization, /radial-lines, /radial-bars, "
        "/radial-axes.",
        source="run.py llms_doc",
    ),
    # This page IS the package's landing page, not an article about one.
    # SoftwareApplication is what puts the install line and the component
    # list in front of a search result instead of a generic WebPage.
    schema_type="SoftwareApplication",
    # No lastmod, deliberately: the home page is a standing index whose prose
    # tracks the whole site, so any single date here would be a guess. 2.6.0
    # omits the tag entirely when it is unset — silence beats a lie.
)

# ============================================================================
# Site identity for the CRAWLER document (dash-improve-my-llms 2.5.0).
# Until 2.5.0 the generated crawler HTML carried the page's content signals
# and none of its identity: browsers got the icon links, og:image and a
# twitter card from templates/index.html while Googlebot got zero of any of
# them, on every host in the network — so search showed the generic globe.
# One declaration covers every crawler surface, and it also claims
# /favicon.ico (Google's fallback), which Dash's page catch-all was
# answering with the app shell. Content may differ between the crawler
# document and the browser document; identity may not.
# ============================================================================
configure_seo(
    icons=[
        # Same pixels templates/index.html links, so the two heads agree.
        # The .ico href is the assets/favicon/ copy (byte-identical to the
        # root one Dash's {%favicon%} placeholder emits) so this list is
        # SET-equal to what 2.6.0's autodiscovery finds —
        # tests/test_seo_icons.py pins that agreement.
        "/assets/favicon/favicon.ico",
        {"href": "/assets/favicon/favicon-32x32.png", "sizes": "32x32"},
        {"href": "/assets/favicon/favicon-16x16.png", "sizes": "16x16"},
        {"href": "/assets/favicon/favicon-96x96.png", "sizes": "96x96"},
        {"href": "/assets/favicon/android-chrome-192x192.png", "sizes": "192x192"},
        {"href": "/assets/favicon/android-chrome-512x512.png", "sizes": "512x512"},
        {"href": "/assets/favicon/apple-touch-icon.png",
         "rel": "apple-touch-icon", "sizes": "180x180"},
    ],
    social_image=OG_IMAGE_URL,
    social_image_alt=OG_IMAGE_ALT,
    social_image_width=OG_IMAGE_WIDTH,
    social_image_height=OG_IMAGE_HEIGHT,
    publisher=PUBLISHER,
    same_as=SAME_AS,
)

# Internal pages — excluded from /sitemap.xml, blocked in /robots.txt,
# skipped by the MCP bridge, and return 404 to crawler requests on the
# page URL and on /<page>/llms.txt.
mark_hidden("/404")                 # the not-found page — never in sitemap/llms

# ============================================================================
# FastAPI showcase routes (only when running on FastAPI).
# These are NOT the AI/LLM endpoints — those are handled by add_llms_routes
# below. They are a small native API surface (`/healthz`, `/api/backend`,
# `/api/pages`) that demonstrates first-class OpenAPI/Swagger UI integration
# under Dash 4.1+'s FastAPI backend.
#
# Mounted BEFORE add_llms_routes so the package's catch-all
# `/<page>/llms.txt` matcher doesn't shadow these.
# ============================================================================

if BACKEND == "fastapi":
    from lib.asgi_routes import register_asgi_routes
    register_asgi_routes(app, BACKEND_INFO)
    print(
        "[muischeduler] FastAPI showcase routers mounted: /healthz, "
        "/api/backend, /api/pages. Swagger UI at /docs, ReDoc at /redoc."
    )
else:
    # Flask/Quart get the same /healthz the FastAPI build declares — the
    # 2plot.ai hourly health sweep, the CI battery and the CD deploy gate all
    # probe it and assert the exact field `ok: true`.
    from lib.health import register_health_route
    register_health_route(app, BACKEND)

# Cross-host directory for the 2plot network: <link rel="related"> tags, the
# "## Network" section in /llms.txt, and followed links in the prerendered
# body. Must run BEFORE add_llms_routes so the routes pick it up.
from lib import network_directory
network_directory.apply(BASE_URL)

# ----------------------------------------------------------------------------
# Crawler HTML: add the tags dash-improve-my-llms 2.0 does not emit.
# ----------------------------------------------------------------------------
# Search engines are served the package's prerendered per-page document, NOT the
# SPA shell — so the canonical link, og:site_name and og:image have to be added
# there too, or they are missing from exactly the response Google indexes.
# Patched at the module attribute because handlers.py imports the generator
# lazily inside the request path. Best-effort: any signature drift falls back to
# the untouched HTML rather than breaking the crawler response.


def _augment_crawler_html() -> None:
    from dash_improve_my_llms import html_generator as _gen

    _original = _gen.generate_static_page_html

    def _with_canonical(*args, **kwargs):
        html = _original(*args, **kwargs)
        try:
            path = kwargs.get("page_path") or "/"
            url = BASE_URL + (path if path != "/" else "/")
            extra = (
                f'    <meta property="og:site_name" content="{SITE_BRAND}">\n'
                f'    <meta property="og:image" content="{OG_IMAGE_URL}">\n'
                f'    <meta property="twitter:card" content="summary_large_image">\n'
                f'    <meta property="twitter:image" content="{OG_IMAGE_URL}">\n'
            )
            # dimll ≥2.3.4 emits its own canonical in the prerender; adding a
            # second identical tag fails the battery's exactly-one check (the
            # same double-canonical dash-email shipped and then removed). Only
            # inject ours if the artifact ever stops emitting it.
            if 'rel="canonical"' not in html:
                extra = f'    <link rel="canonical" href="{url}">\n' + extra
            return html.replace("</head>", extra + "</head>", 1)
        except Exception:
            return html

    _gen.generate_static_page_html = _with_canonical


try:
    _augment_crawler_html()
except Exception as e:  # pragma: no cover - never block startup on an SEO nicety
    print(f"[seo] crawler-HTML canonical injection skipped: {e!r}")

# ============================================================================
# Analytics tracking (flask) — registered BEFORE add_llms_routes, deliberately.
# Flask runs before_request hooks in registration order, and the package's bot
# middleware ANSWERS recognized crawlers itself: registered after it, this
# tracker never sees a Googlebot hit and the ledger undercounts every crawler.
# (FastAPI is unaffected — its tracking lives in ASGI middleware, outermost.)
# ============================================================================
if IS_FLASK:
    from flask import request as _flask_request

    @app.server.before_request
    def track_visitor():
        """Track visitor analytics before each request."""
        try:
            # Headers are passed so the tracker can read the REAL client IP
            # and country from the proxy/CDN (behind Render or Cloudflare,
            # remote_addr is the proxy — every visitor would look like one).
            tracker.track_visit(
                _flask_request.path,
                _flask_request.headers.get('User-Agent', ''),
                _flask_request.remote_addr,
                headers=dict(_flask_request.headers),
            )
        except Exception:
            pass

# ============================================================================
# Access control (dash-improve-my-llms 2.3). Reads the tiers the pages just
# declared, so it must run after they are registered and before the routes
# are attached. Stays OFF unless some page declares a non-public tier — the
# policy and the reasoning live in lib/access.py.
# ============================================================================

from lib import access as _access  # noqa: E402
from lib import page_tiers as _page_tiers  # noqa: E402
from lib import page_visibility as _page_visibility  # noqa: E402

# Tiered corpus documents (dash-improve-my-llms >= 2.4.0). Pseudo-paths: they
# never enter dash.page_registry, so they cannot leak into listings —
# registering them here lets this satellite tier its compact briefing and full
# corpus via env (LLMS_SMALL_TIER / LLMS_FULL_TIER), and the hub can tighten
# either network-wide through its page-tier ceilings with no redeploy here.
# The explicit `or "public"` matters: these registered under the
# PAGE_DEFAULT_TIER fallback before, which meant flipping that env to gate the
# *interactive* site would silently gate the corpus documents too. Their tier
# is now always a deliberate setting, never an ambient default.
_page_tiers.register("/llms-small.txt",
                     os.environ.get("LLMS_SMALL_TIER") or "public")
_page_tiers.register("/llms-full.txt",
                     os.environ.get("LLMS_FULL_TIER") or "public")

# The home page registers via pages/home.py, not pages/markdown.py, so no
# frontmatter ever declares its tier — under PAGE_DEFAULT_TIER=auth it would
# silently inherit the gate. The funnel's front door stays public, always.
_page_tiers.register("/", "public")

# force= when either gate env is present: with every tier still public the
# auto-detect would skip the wiring, but a host that flips by env needs the
# verdict plumbing (and the prerender's use of it) live during the dark
# launch, not on the flip.
ACCESS_ENABLED = _access.configure(
    force=bool(os.environ.get("PAGE_DEFAULT_TIER")
               or os.environ.get("LLMS_PUBLIC_DEFAULT"))
)

# Wire up the package: /llms.txt, /<page>/llms.txt, /robots.txt, /sitemap.xml,
# bot-detection middleware, and (on Dash 4.3+) MCP resource registration.
# Works under Flask, FastAPI, and Quart — no gating needed.
add_llms_routes(app, LLMSConfig(warn_missing_llms_doc=True))

# ============================================================================

app.layout = create_appshell(dash.page_registry.values())

server = app.server

# ============================================================================
# The person->agent handoff: /api/agent-key turns the browser's Clerk session
# into a portable ?key= for copied llms.txt URLs (lib/agent_key.py). Those
# URLs get pasted into an assistant, which fetches them with no cookie — so a
# gated document needs its authority in the URL or the agent gets the gate
# card instead of the docs. 204 for everyone until Clerk and the hub are
# configured, so it is safe to mount always.
# ============================================================================

from lib.agent_key import register_agent_key_route  # noqa: E402

register_agent_key_route(app, BACKEND)

_non_public = sum(1 for t in _page_tiers.registered().values() if t != "public")
print(
    f"[muischeduler] interactive gate: default tier "
    f"'{os.environ.get('PAGE_DEFAULT_TIER') or 'public'}', "
    f"{_non_public} non-public page(s), machine surfaces "
    f"{'GATED' if not _page_tiers.get_llms_public('/__probe__') else 'open'} "
    f"by default (LLMS_PUBLIC_DEFAULT), access wiring "
    f"{'ON' if ACCESS_ENABLED else 'off'}, control board at "
    f"/admin/control-board ({_page_visibility.override_count()} live "
    f"override(s))."
)

# THE SECOND HALF of dash-clerk-auth's wiring. `register()` above loaded the
# UI half; this registers the SERVER half — sessions, /api/auth/session,
# /api/auth/signout, and per-request identity. Both calls or neither: ship
# only the first and the site LIES. Components render, ClerkJS reports
# signed-in, and every server render reads signed-out — the control board
# serves the owner a sign-in card forever, the auth POSTs fall through to
# Dash's GET-only page catch-all and answer 405, and sign-out never revokes.
# flexlayout shipped exactly that on 2026-08-22 and locked its owner out.
# No local suite can see it (Clerk is off in test envs and configure_app
# no-ops without keys), so tests/test_auth_wiring.py pins both calls
# STRUCTURALLY via AST and smoke_live.py probes the routes on the live host.
#
# Must run AFTER Dash() and BEFORE the social-card wsgi wrap below, so on
# flask the social-card shim stays OUTERMOST (configure_app wraps wsgi_app
# in ProxyFix). Routed through lib/auth.py rather than the package directly:
# it owns the enabled check and swallows a wiring failure into a warning
# instead of a dead boot.
_auth.configure_app(app)

# Clerk webhook receiver (Svix-verified, observability log). Registered on
# both backends UNCONDITIONALLY — the handler fail-closes without
# CLERK_WEBHOOK_SECRET, so a stray POST just gets a 400. Subscribe exactly:
# user.created/updated/deleted + session.created/ended/revoked (six).
from lib.clerk_webhook import register_webhook as _register_clerk_webhook
_register_clerk_webhook(app, BACKEND)

# ============================================================================
# Social-card scrapers (Twitter / Facebook / Discord / Slack / …) are treated as
# bots by add_llms_routes and would get the SEO HTML (which has NO og:image). Serve
# them templates/index.html's <head> with a per-page og/twitter card rendered in
# place of {%metas%}, so unfurls show the image AND the right page's title/URL.
# Registered OUTERMOST so it pre-empts the package. See lib/social_cards.py.
# ============================================================================
from lib.social_cards import SOCIAL_UAS, SocialCardRenderer, is_social_card

_social_card = SocialCardRenderer(
    template=_INDEX_TEMPLATE.replace("__BASE_URL__", BASE_URL).replace("__VERSION__", APP_VERSION),
    base_url=BASE_URL,
    image_url=OG_IMAGE_URL,
    fallback_title=SITE_BRAND,
    fallback_description=SITE_DESCRIPTION,
)


# ============================================================================
# Social-card / canonical-host WSGI wrap — backend-specific.
# (Flask visitor tracking registers ABOVE add_llms_routes — see that block.)
# ============================================================================

if IS_FLASK:
    # Wrap OUTERMOST (after add_llms_routes wrapped server.wsgi_app) so social-card
    # scrapers get the full og:image HTML instead of the package's image-less SEO HTML.
    _orig_wsgi = server.wsgi_app

    def _social_card_wsgi(environ, start_response):
        path = environ.get('PATH_INFO', '/')
        method = environ.get('REQUEST_METHOD', 'GET')

        # Wrong host → 301 before anything renders. Outermost of all, so a
        # scraper or crawler on the onrender URL is sent to the real domain
        # rather than being served a duplicate of it.
        target = canonical_redirect(
            environ.get('HTTP_HOST'), path, method, environ.get('QUERY_STRING', ''),
            canonical_host=CANONICAL_HOST, enabled=CANONICAL_HOST_REDIRECT,
        )
        if target:
            start_response('301 Moved Permanently',
                           [('Location', target), ('Content-Length', '0')])
            return [b'']

        if is_social_card(environ.get('HTTP_USER_AGENT'), path, method):
            body = _social_card(path).encode('utf-8')
            start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8'),
                                      ('Content-Length', str(len(body)))])
            return [body]
        return _orig_wsgi(environ, start_response)

    server.wsgi_app = _social_card_wsgi

elif BACKEND == "fastapi":
    from lib.asgi_middleware import register_asgi_middleware

    register_asgi_middleware(
        app, _social_card, SOCIAL_UAS,
        canonical_host=CANONICAL_HOST,
        canonical_redirect_enabled=CANONICAL_HOST_REDIRECT,
    )

# ============================================================================
# Network analytics — hourly signed rollup POSTed to 2plot.ai so the hub's
# owner-only /traffic dashboard can chart this app alongside the network.
# Contract: 2plotai/docs/network/satellite-analytics.md.
# No-op unless CROSS_APP_WEBHOOK_SECRET is set.
# ============================================================================

from lib.satellite_reporter import start_reporter

start_reporter()

# ============================================================================
# Network bulletin — hub-published tips/announcements rendered in the llms.txt
# viewer header. The boot line states which of the two states the process is
# in; NETWORK_BULLETIN_URL must be set on the Render SERVICE (blueprint
# envVars only apply on Blueprint sync). See lib/bulletin.py.
# ============================================================================

from lib import bulletin as _bulletin

if _bulletin.configure():
    print(f"[dash-mui-scheduler] network bulletin: {_bulletin.url()} "
          f"(app='{_bulletin.app_id()}')")
else:
    print("[dash-mui-scheduler] network bulletin: off — set "
          f"NETWORK_BULLETIN_URL={_bulletin.HUB_BULLETIN_URL} to render the "
          "hub's announcements")

# MCP wiring used to live down here, calling `from dash import mcp_enabled`
# and `mcp_enabled(app)`. Both were wrong, and wrong in a way that reported
# success: the symbol lives in `dash.mcp`, not `dash`, so the import ALWAYS
# raised ImportError and this app printed "MCP not available in dash 4.4.1
# (needs >=4.3)" — while running 4.4.1. And `mcp_enabled` is the decorator
# that marks a *function* as an MCP tool, not a server switch. The server is
# started from Dash's constructor, so the real wiring is `enable_mcp=` at the
# top of this file.

# ============================================================================


if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get("PORT", "8598")))
