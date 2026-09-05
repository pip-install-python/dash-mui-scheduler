"""Cache lifetimes for the static files this app serves (1.6.44 item 6g).

MEASURED ON THIS HOST'S WIRE FIRST, before any policy was written, with
`curl -D -` against production (build 2cfc003):

    /assets/main.css       cf-cache-status: DYNAMIC   (no cache-control at all)
    /assets/llms_copy.js   cf-cache-status: DYNAMIC   (no cache-control at all)
    /assets/dms_logo.svg   cf-cache-status: DYNAMIC   (no cache-control at all)

which is a shade worse than the `no-cache` the template and pannellum found:
with no `Cache-Control` at all the edge stores nothing (DYNAMIC) and every
browser falls back to heuristic freshness — so the lifetime of this site's
stylesheet is currently whatever each visitor's browser decides it is, and
the origin answers most of those requests.

Only ``/assets/`` is given a lifetime here, and deliberately:

* Dash's own ``/_dash-component-suites/`` URLs are fingerprinted and the
  package already sets a long immutable lifetime on them — a second opinion
  from this app could only make that worse;
* documents must keep revalidating. A page, ``/llms.txt``, ``/healthz`` and
  anything under ``/admin`` or ``/api`` are answers about right now, and one
  hour of a stale one is a bug report nobody can reproduce.

The window is one hour with a day of ``stale-while-revalidate``: the assets
here are NOT fingerprinted (``main.css`` keeps its name across deploys), so
the lifetime is the longest a CSS fix may take to reach a returning reader.

Both lanes call this one function — the Flask ``after_request`` in run.py and
``StaticCacheMiddleware`` on the ASGI side — so Flask and FastAPI cannot drift
into serving different lifetimes for the same file. On this host that is not
hypothetical tidiness: production is FastAPI and CI's gunicorn boot is Flask,
so a policy written on one lane only would be verified on the lane that does
not ship.
"""
from __future__ import annotations

ASSET_PREFIX = "/assets/"
ASSET_CACHE_CONTROL = "public, max-age=3600, stale-while-revalidate=86400"


def cache_control_for(path: str) -> str | None:
    """The ``Cache-Control`` this app wants on ``path``, or None to leave it.

    None is the answer for everything that is not an unfingerprinted static
    asset — the caller must not invent a header for a document.
    """
    return ASSET_CACHE_CONTROL if (path or "").startswith(ASSET_PREFIX) else None
