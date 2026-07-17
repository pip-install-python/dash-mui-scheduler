"""
ASGI/Starlette middleware ports of Flask-only hooks used in this boilerplate.

When the Dash backend is FastAPI, these slot in where the Flask
``before_request`` decorator was used.
"""
from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from lib.analytics_tracker import tracker
from lib.auth import identify_request_user


class AnalyticsMiddleware(BaseHTTPMiddleware):
    """Track every request through the analytics tracker.

    Mirrors the Flask ``before_request`` shim in ``run.py``. Failures are
    silently swallowed — analytics should never block a real response.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        try:
            client = request.client
            ip = client.host if client else None
            tracker.track_visit(
                request.url.path,
                request.headers.get("user-agent", ""),
                ip,
                auth_name=identify_request_user(request.cookies),
            )
        except Exception:
            pass
        return await call_next(request)


class SocialCardMiddleware(BaseHTTPMiddleware):
    """Serve the full og:image HTML to social-card scrapers (Twitter/FB/Discord/…),
    which ``add_llms_routes`` would otherwise hand its image-less SEO HTML. Mirrors
    the Flask wsgi wrap in ``run.py``. Added LAST → outermost → pre-empts the package.
    """

    def __init__(self, app, social_html: str = "", social_uas=()) -> None:
        super().__init__(app)
        self._html = social_html or ""
        self._uas = tuple(social_uas)

    async def dispatch(self, request: Request, call_next) -> Response:
        ua = (request.headers.get("user-agent", "") or "").lower()
        path = request.url.path
        # method-aware: scrapers only GET/HEAD — spoofed-UA POSTs (e.g. to the
        # Svix-verified /webhooks/clerk) must reach the real handlers.
        if (self._html and self._uas and request.method in ("GET", "HEAD")
                and any(b in ua for b in self._uas)
                and not path.startswith("/assets") and not path.startswith("/_")
                and not path.startswith("/webhooks")):
            return Response(self._html, media_type="text/html; charset=utf-8")
        return await call_next(request)


def register_asgi_middleware(app, social_html: str = None, social_uas=()) -> None:
    """Attach all ASGI middleware to ``app.server`` (a FastAPI instance). Starlette runs
    middleware in REVERSE add-order, so the LAST added is OUTERMOST: analytics → social
    (the social-card shim sees the request first on the way in)."""
    app.server.add_middleware(AnalyticsMiddleware)
    if social_html:
        app.server.add_middleware(SocialCardMiddleware, social_html=social_html, social_uas=social_uas)
