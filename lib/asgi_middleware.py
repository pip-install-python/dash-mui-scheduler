"""
ASGI/Starlette middleware ports of Flask-only hooks used in this boilerplate.

When the Dash backend is FastAPI, these slot in where the Flask
``before_request`` decorator was used.
"""
from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response

from lib.analytics_tracker import tracker
from lib.canonical_host import canonical_redirect
from lib.social_cards import is_social_card


class AnalyticsMiddleware(BaseHTTPMiddleware):
    """Track every request through the analytics tracker.

    Mirrors the Flask ``before_request`` shim in ``run.py``. Failures are
    silently swallowed — analytics should never block a real response.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        try:
            client = request.client
            ip = client.host if client else None
            # Headers carry the real client IP/country behind a proxy or CDN;
            # request.client is the last hop (the proxy) in production.
            tracker.track_visit(
                request.url.path,
                request.headers.get("user-agent", ""),
                ip,
                headers=dict(request.headers),
            )
        except Exception:
            pass
        return await call_next(request)


class StaticCacheMiddleware(BaseHTTPMiddleware):
    """Give ``/assets/`` a cache lifetime (1.6.44 item 6g).

    The ASGI half of the Flask ``after_request`` in ``run.py``; the policy
    itself lives in ``lib/static_cache`` so the two lanes cannot drift into
    serving different lifetimes for the same file. THIS is the lane that
    ships on this host.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        from lib.static_cache import cache_control_for

        value = cache_control_for(request.url.path)
        if value and response.status_code == 200:
            response.headers["Cache-Control"] = value
        return response


class SocialCardMiddleware(BaseHTTPMiddleware):
    """Serve the full og:image HTML to social-card scrapers (Twitter/FB/Discord/…),
    which ``add_llms_routes`` would otherwise hand its image-less SEO HTML. Mirrors
    the Flask wsgi wrap in ``run.py``. Added LAST → outermost → pre-empts the package.

    ``renderer`` is a ``lib.social_cards.SocialCardRenderer`` — a callable that
    builds the card for the requested path, so each URL unfurls as itself.
    """

    def __init__(self, app, renderer=None, social_uas=()) -> None:
        super().__init__(app)
        self._render = renderer
        self._uas = tuple(social_uas)

    async def dispatch(self, request: Request, call_next) -> Response:
        path = request.url.path
        if self._render and self._uas and is_social_card(
            request.headers.get("user-agent"), path, request.method
        ):
            return Response(self._render(path), media_type="text/html; charset=utf-8")
        return await call_next(request)


class CanonicalHostMiddleware(BaseHTTPMiddleware):
    """301 every non-canonical host to the canonical one. See lib/canonical_host."""

    def __init__(self, app, canonical_host: str = "", enabled: bool = False) -> None:
        super().__init__(app)
        self._host = canonical_host
        self._enabled = enabled

    async def dispatch(self, request: Request, call_next) -> Response:
        target = canonical_redirect(
            request.headers.get("host"),
            request.url.path,
            request.method,
            request.url.query,
            canonical_host=self._host,
            enabled=self._enabled,
        )
        if target:
            return RedirectResponse(target, status_code=301)
        return await call_next(request)


def register_asgi_middleware(app, social_renderer=None, social_uas=(),
                             canonical_host="", canonical_redirect_enabled=False) -> None:
    """Attach all ASGI middleware to ``app.server`` (a FastAPI instance). Starlette runs
    middleware in REVERSE add-order, so the LAST added is OUTERMOST: analytics → social
    → canonical host. The host redirect must be outermost of all — a request on the
    wrong host should be sent away before anything renders a page for it."""
    app.server.add_middleware(AnalyticsMiddleware)
    app.server.add_middleware(StaticCacheMiddleware)
    if social_renderer:
        app.server.add_middleware(
            SocialCardMiddleware, renderer=social_renderer, social_uas=social_uas
        )
    if canonical_redirect_enabled:
        app.server.add_middleware(
            CanonicalHostMiddleware, canonical_host=canonical_host, enabled=True
        )
