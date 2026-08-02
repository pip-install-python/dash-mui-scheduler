"""Redirect every non-canonical host to the one canonical origin.

The docs are reachable at more than one address — the Render service's own
``*.onrender.com`` URL never stops working once a custom domain is attached. Two
hosts serving byte-identical pages is duplicate content: search engines pick a
winner per URL, links split between the two, and the ``rel=canonical`` we emit
is only a *hint*. A 301 is the instruction.

Off by default. ``CANONICAL_HOST_REDIRECT`` must be set to turn it on, because
enabling it before the custom domain's DNS actually resolves would bounce every
visitor to a dead host. Order of operations is in render.yaml.
"""
from __future__ import annotations

# Never redirected:
#   /healthz   — Render's health check; a 3xx there fails the deploy.
#   /assets, /_dash*  — static + the renderer's own XHR; an extra hop per asset
#                       buys nothing, and a redirected POST would lose its body.
#   /webhooks, /api   — signed/programmatic callers that address a fixed URL.
_EXEMPT_PREFIXES = ("/healthz", "/assets", "/_dash", "/_reload", "/_favicon",
                    "/webhooks", "/api/")

# Local development and in-process test clients are never "the wrong host".
_LOCAL_HOSTS = ("localhost", "127.0.0.1", "0.0.0.0", "[::1]", "testserver")


def canonical_redirect(
    host: str | None,
    path: str,
    method: str = "GET",
    query: str = "",
    *,
    canonical_host: str,
    enabled: bool,
) -> str | None:
    """Return the absolute URL to 301 to, or None to serve the request normally.

    ``host`` is the request's Host header (``example.com`` or ``example.com:443``).
    """
    if not enabled or not canonical_host or not host:
        return None
    if method not in ("GET", "HEAD"):
        return None

    hostname = host.split(":", 1)[0].strip().lower()
    if not hostname or hostname == canonical_host.lower():
        return None
    if hostname in _LOCAL_HOSTS or hostname.endswith(".local"):
        return None

    path = path or "/"
    if any(path.startswith(prefix) for prefix in _EXEMPT_PREFIXES):
        return None

    return f"https://{canonical_host}{path}" + (f"?{query}" if query else "")
