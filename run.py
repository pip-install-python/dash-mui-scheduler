import os
import dash
from dash import Dash
from components.appshell import create_appshell

# AI/LLM Integration & SEO — dash-improve-my-llms 2.0
# 2.0 supports Flask, FastAPI, and Quart via a single backend-detecting
# dispatcher. The custom Flask-only routes that used to live in this file
# (`/<page>/llms.txt`, `/<page>/page.json`, `/<page>/llms.toon`) are gone —
# the package owns `/llms.txt` and `/<page>/llms.txt`, and `/page.json` /
# `/llms.toon` were intentionally dropped in 2.0 (Dash 4.3 MCP covers the
# structured-introspection job they were doing).
from dash_improve_my_llms import (
    add_llms_routes,
    LLMSConfig,
    RobotsConfig,
    mark_hidden,
    register_page_metadata,
)

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

print(f"[boilerplate] Starting Dash {dash.__version__} on backend='{BACKEND}'")

# ----------------------------------------------------------------------------
# Optional Clerk authentication (dash-clerk-auth, vendored in vendor/). FULLY
# optional — and OFF at launch for the docs site: with no CLERK_* keys the
# package's dash hooks no-op and the app is identical to the unauthenticated
# build ($0, no network, no session files). If/when the docs get a 2plot.*
# domain, lib/clerk_satellite registers it as a SATELLITE of the 2plot.ai
# primary with one env flip (CLERK_* + CLERK_IS_SATELLITE/_SATELLITE_DOMAIN) —
# no code change. headless=True: the avatar chip lives in the app header
# (components/header._create_auth_chip → create_clerk_menu).
# ----------------------------------------------------------------------------
from lib.auth import clerk_enabled
from lib.clerk_satellite import register_clerk_satellite

CLERK_ENABLED = clerk_enabled()
if CLERK_ENABLED:
    from dash import hooks as _dash_hooks

    register_clerk_satellite(app_tag="dash-mui-scheduler")

    # Dash 4.2 WS-transported callbacks run in a THREAD POOL no HTTP middleware
    # ever touches — the package's WS hooks bind renderer→user at connect so
    # current_user() resolves in
    # WS callbacks too. Since dash-clerk-auth 0.9.0, configure_app registers
    # those hooks ITSELF (with the session_secret above, pulled from the active
    # config); the old explicit register_websocket_auth() call is gone. Assert
    # with dash_clerk_auth.ws_auth_registered() if in doubt.

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

    if not os.getenv("SESSION_SECRET"):
        print("[boilerplate] ⚠️  Clerk is ENABLED but SESSION_SECRET is unset — session/"
              "identity cookies would be signed with the package's PUBLIC dev default. "
              "Set SESSION_SECRET before deploying.")
    print("[boilerplate] Clerk auth ENABLED (headless; avatar chip in the header).")

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
    APP_VERSION, BASE_URL, CANONICAL_HOST, CANONICAL_HOST_REDIRECT, OG_IMAGE_URL,
    SITE_BRAND, SITE_DESCRIPTION, require_owned_base_url,
)

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

# Configure bot management policies. See dash-improve-my-llms 2.0 SKILLS for
# the full menu — balanced default = block training crawlers, allow AI search
# citations and traditional search.
app._robots_config = RobotsConfig(
    block_ai_training=False,      # Block GPTBot, CCBot, anthropic-ai, etc.
    allow_ai_search=True,         # Allow ChatGPT-User, ClaudeBot, PerplexityBot
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
    llms_doc=(
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
        "/radial-axes."
    ),
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
        "[boilerplate] FastAPI showcase routers mounted: /healthz, "
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
            from lib.auth import identify_request_user
            from lib.analytics_tracker import resolve_client_ip, resolve_country
            # Behind a proxy remote_addr is the PROXY — resolve the forwarded
            # client address so visitor counts and countries mean something.
            tracker.track_visit(
                _flask_request.path,
                _flask_request.headers.get('User-Agent', ''),
                resolve_client_ip(_flask_request.headers,
                                  _flask_request.remote_addr),
                auth_name=identify_request_user(_flask_request.cookies),
                country=resolve_country(_flask_request.headers),
            )
        except Exception:
            pass

# Wire up the package: /llms.txt, /<page>/llms.txt, /robots.txt, /sitemap.xml,
# bot-detection middleware, and (on Dash 4.3+) MCP resource registration.
# Works under Flask, FastAPI, and Quart — no gating needed.
add_llms_routes(app, LLMSConfig(warn_missing_llms_doc=True))

# ============================================================================

app.layout = create_appshell(dash.page_registry.values())

server = app.server

# Clerk server machinery (sessions + /api/auth/* + request identity). Must run
# AFTER Dash() and BEFORE the social-card wsgi wrap below, so on flask the
# social-card shim stays OUTERMOST (configure_app wraps wsgi_app in ProxyFix).
if CLERK_ENABLED:
    from dash_clerk_auth import configure_app as _clerk_configure
    _clerk_configure(app)

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
# Satellite traffic reporting — this app's hourly rollup POSTed to 2plot.ai,
# which is the analytics home for the whole 2plot network (its owner-only
# /traffic dashboard charts every satellite side by side). Contract:
# the hub repo's docs/network/satellite-analytics.md; sender: lib/traffic_report.
# No-ops entirely without CROSS_APP_WEBHOOK_SECRET (local runs, forks) — no
# thread, no network. Runs on both backends; keep WEB_WORKERS=1 so one
# process owns the ledger and one reporter speaks for the app.
# ============================================================================

from lib.traffic_report import start_reporter as _start_traffic_reporter

if not _start_traffic_reporter():
    print("[traffic-report] disabled (no CROSS_APP_WEBHOOK_SECRET) — "
          "the app will not appear on 2plot.ai/traffic.")

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

# ============================================================================
# Optional: Dash 4.3+ MCP server.
# When available, this exposes the app's layout, components, pages and
# (whitelisted) callbacks to MCP-compatible LLM clients over Streamable HTTP.
# Best-effort: silently no-op on Dash <4.3 or on non-FastAPI backends.
#
# Note: dash-improve-my-llms 2.0 *also* registers each page's LLMS_DOC as a
# `dash.mcp` resource via its MCP bridge — that gives MCP clients access to
# the prose docs alongside whatever native introspection Dash provides.
# ============================================================================

try:
    from dash import mcp_enabled  # type: ignore[attr-defined]
    HAS_MCP = True
except ImportError:
    HAS_MCP = False

if HAS_MCP and BACKEND == "fastapi" and os.environ.get("DASH_MCP_ENABLED", "0") == "1":
    try:
        mcp_enabled(app)  # noqa
        print("[boilerplate] MCP server enabled at /mcp (Dash 4.3+ feature).")
    except Exception as e:  # pragma: no cover - best-effort
        print(f"[boilerplate] MCP wire-up failed: {e!r}")
elif not HAS_MCP and BACKEND == "fastapi":
    print(
        f"[boilerplate] MCP not available in dash {dash.__version__} "
        "(needs >=4.3). Set DASH_MCP_ENABLED=1 once upgraded."
    )

# ============================================================================


if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get("PORT", "8598")))
