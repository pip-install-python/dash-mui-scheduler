import os
import dash
from dash import Dash, _dash_renderer
from components.appshell import create_appshell
import dash_mantine_components as dmc

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

app = Dash(
    __name__,
    backend=BACKEND,
    suppress_callback_exceptions=True,
    use_pages=True,
    external_scripts=scripts,
    update_title=None,
    prevent_initial_callbacks=True,
    index_string=open('templates/index.html').read(),
    # Belt-and-suspenders: keep the GLOBAL websocket flag off too (see the
    # capability disable above for the full rationale).
    websocket_callbacks=False,
)

# Expose backend info so layout components can render a badge without
# re-reading the env var (which could drift between processes/workers).
app._backend_info = BACKEND_INFO

# ============================================================================
# AI/LLM & SEO Configuration
# ============================================================================

# Base URL for SEO (sitemap.xml + llms.txt emit absolute URLs from this).
# Env-driven so the Render service / custom domain sets it without a code change.
app._base_url = os.getenv("APP_BASE_URL", "https://dash-mui-scheduler-docs.onrender.com")

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
    name="dash-mui-scheduler",
    description=(
        "A Plotly Dash wrapper for the MUI X Scheduler — EventCalendar, "
        "EventCalendarPremium and EventTimeline plus the RadialLineChart and "
        "RadialBarChart polar charts — "
        "with recurrence, drag & resize, resources, timezones and theming. "
        "This site is the component documentation with live examples."
    ),
    llms_doc=(
        "# dash-mui-scheduler\n\n"
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
# them the full meta HTML (favicon + og:image/twitter:image from templates/index.html)
# so link unfurls show the card image. Registered OUTERMOST so it pre-empts the package.
# Scrapers only read <head> meta, so we strip the Dash placeholders → a static string.
# ============================================================================
_SOCIAL_UAS = ('twitterbot', 'facebookexternalhit', 'facebookcatalog', 'discordbot',
               'slackbot', 'slack-imgproxy', 'linkedinbot', 'whatsapp', 'telegrambot',
               'pinterest', 'redditbot', 'skypeuripreview', 'embedly', 'iframely')
_SOCIAL_HTML = open('templates/index.html').read()
for _ph in ('{%metas%}', '{%favicon%}', '{%css%}', '{%app_entry%}', '{%config%}',
            '{%scripts%}', '{%renderer%}', '{%title%}'):
    _SOCIAL_HTML = _SOCIAL_HTML.replace(_ph, '')


def _is_social_card(ua, path, method='GET'):
    # method-aware: social scrapers only ever GET/HEAD — a spoofed-UA POST must
    # fall through to the real handlers (e.g. the Svix-verified /webhooks/clerk).
    ua = (ua or '').lower()
    return (method in ('GET', 'HEAD')
            and any(b in ua for b in _SOCIAL_UAS)
            and not path.startswith('/assets') and not path.startswith('/_')
            and not path.startswith('/webhooks'))


# ============================================================================
# Analytics Tracking — backend-specific.
# Flask uses before_request; FastAPI uses ASGI middleware.
# ============================================================================

if IS_FLASK:
    from flask import request as _flask_request

    @server.before_request
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

    # Wrap OUTERMOST (after add_llms_routes wrapped server.wsgi_app) so social-card
    # scrapers get the full og:image HTML instead of the package's image-less SEO HTML.
    _orig_wsgi = server.wsgi_app

    def _social_card_wsgi(environ, start_response):
        path = environ.get('PATH_INFO', '/')
        method = environ.get('REQUEST_METHOD', 'GET')
        if _is_social_card(environ.get('HTTP_USER_AGENT'), path, method):
            body = _SOCIAL_HTML.encode('utf-8')
            start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8'),
                                      ('Content-Length', str(len(body)))])
            return [body]
        return _orig_wsgi(environ, start_response)

    server.wsgi_app = _social_card_wsgi

elif BACKEND == "fastapi":
    from lib.asgi_middleware import register_asgi_middleware

    register_asgi_middleware(app, _SOCIAL_HTML, _SOCIAL_UAS)

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
