"""``/healthz`` — the probe contract, identical on every backend.

The 2plot.ai hub sweeps every satellite's ``/healthz`` once an hour and
records up/down + latency — the "Satellite health & reach" panel on
``/traffic``. The battery (scripts/network_smoke.py) and the CD deploy gate
both assert the exact field ``ok: true``; a 200 with different JSON reads as
"unhealthy" to them, deliberately.

The FastAPI build declares a *typed* ``/healthz`` in ``lib/asgi_routes`` so
it shows up in Swagger, but it renders from the SAME ``health_payload``
below — one payload builder on every backend, so the probe contract cannot
depend on which backend a deployment happens to run. It used to build its
own dict, which is how a FastAPI deployment silently lacked ``build``: the
exact field cd.yml's build-match wait polls for.

Keep it cheap: the hub measures the round trip, so any work done here is
reported back as this app being slow.
"""
from __future__ import annotations

import json
import os
import platform
from pathlib import Path

import dash


def _resolved_country(headers=None) -> str:
    """``geo.explain_resolution`` over THIS request's headers, or a reason.

    Reads the request headers directly rather than anything the package
    threads through, so it answers "did the country header reach this app at
    all?" independently of how the enforcement seam is wired.

    Each route passes its own framework's headers explicitly. The first
    version of this read Flask's request context, which made the FastAPI and
    Quart lanes answer "no request context" forever — and FastAPI is exactly
    what this app runs in production. ``normalize_headers`` accepts
    Flask/Starlette/Quart/dict and never raises; the Flask-context fallback
    stays for callers that pass nothing.
    """
    try:
        from dash_improve_my_llms import geo
        from dash_improve_my_llms._headers import normalize_headers
    except Exception:
        return "unavailable (pre-2.7.0 package)"

    try:
        if headers is not None:
            return geo.explain_resolution(normalize_headers(headers))

        from flask import has_request_context, request

        if not has_request_context():
            return "no request context"
        return geo.explain_resolution(normalize_headers(request.headers))
    except Exception:
        return "unavailable"


def _llms_version() -> dict:
    """``{"llms_version": "2.8.0"}``, or ``{}`` if the package cannot be read.

    1.6.44 item 1's rider, in excalidraw's name and shape — adopted verbatim
    so the fleet never carries two spellings of the same key.

    It exists because the CI-vs-production version gap was otherwise
    SELF-REPORTED: nothing on any host's wire said which wheel the running
    process actually resolved. This repo declares a ``>=`` FLOOR, not a pin
    (the fleet pin lands at 1.6.45), and a floor is exactly the declaration
    that cannot be read backwards — the Docker layer caches, so the image
    keeps whatever wheel it was first built with while requirements.txt goes
    on saying ">=2.8.0" and CI resolves something newer. This key is the only
    surface that can contradict either.

    Omitted rather than reported as "unknown": a health payload that invents
    a version is worse than one that is silent about it, and run.py's boot
    floor already refuses to start below ``LLMS_PKG_FLOOR`` — so an absent
    key here means the import broke AFTER boot, which is itself the finding.
    """
    try:
        import dash_improve_my_llms as _pkg

        version = getattr(_pkg, "__version__", None)
        return {"llms_version": version} if version else {}
    except Exception:
        return {}


def _ledger_block() -> dict:
    """``{"path", "persistent", "visits", "reads"}`` — the ledger, from outside.

    1.6.44 item 20. Three facts that were previously invisible on the wire.

    ``persistent`` is MEASURED, never declared. True iff the resolved path
    lies OUTSIDE the repository root — i.e. on a mounted disk such as
    ``/var/data/...``. A path under the app tree is the container filesystem
    and reads false EVEN WHERE A BLUEPRINT DECLARES A DISK: leaflet ran for
    weeks with a declared disk and no disk, and nothing on the wire could
    contradict the declaration. A boolean that reports the deployment's
    INTENTION is worth nothing; this one reports the filesystem.

    This host is exactly the case the item was written for: ``render.yaml``
    DECLARES a 1GB disk at ``/var/data`` and points
    ``TRAFFIC_ANALYTICS_FILE`` at it — and its own comment already says "A
    DECLARATION ATTACHES NOTHING", verifiable until now only in a dashboard
    tab nothing automated can read. If this key reads false in production,
    the disk is not attached and every deploy has been wiping the ledger.

    ``visits`` and ``reads`` are the two tables' current row counts, read
    from the same file the tracker writes. A missing file is ``0`` and ``0``
    — never an error, and /healthz stays 200: this block is a diagnostic,
    and a diagnostic that can take the health probe down with it is a
    liability.

    Row CONTENTS never appear here. Counts, a boolean and a path.
    """
    block = {"path": None, "persistent": False, "visits": 0, "reads": 0}
    try:
        from lib.analytics_tracker import analytics_path

        path = Path(analytics_path()).resolve()
        block["path"] = str(path)
        repo_root = Path(__file__).resolve().parent.parent
        try:
            path.relative_to(repo_root)
            block["persistent"] = False      # inside the tree: container fs
        except ValueError:
            block["persistent"] = True       # outside it: a mounted disk

        if path.exists():
            data = json.loads(path.read_text())
            if isinstance(data, dict):
                for table in ("visits", "reads"):
                    rows = data.get(table)
                    block[table] = len(rows) if isinstance(rows, list) else 0
    except Exception:
        # Never let a diagnostic break the health probe. An unreadable or
        # half-written ledger reports zeros, and the ``path`` already in the
        # block is what a reader needs in order to go and look.
        pass
    return block


def _geo_headers_seen() -> list:
    """Which visitor-location headers this process has actually received.

    1.6.44 item 16's rider. Cloudflare's "Add visitor location headers"
    managed transform is an owner CLICK per zone, so the only honest answer
    to "is it on for this host?" is the set that has turned up — not a
    setting this app can read, and not a claim it can make on its own.

    On the ERROR branch too, deliberately: an old or broken package is
    exactly when an operator needs to know whether the edge is sending
    anything at all.
    """
    try:
        from lib.analytics_tracker import geo_headers_seen

        return geo_headers_seen()
    except Exception:
        return []


def health_payload(backend: str, headers=None) -> dict:
    payload = {
        "ok": True,
        "backend": backend,
        "dash_version": dash.__version__,
        # The RESOLVED dash-improve-my-llms version (1.6.44 item 1's rider).
        # Additive: every key the fleet reads by name stays, and a RENAME is
        # still the failure. See _llms_version for why a floor makes this the
        # only surface that can contradict the declaration.
        **_llms_version(),
        # WHICH interpreter is actually serving. Before this field a repo
        # could declare three different Pythons (image, CI matrix, platform
        # runtime) and nothing on the wire could contradict any of them —
        # the drift was invisible to the battery by construction (ops-seat
        # finding, 2026-08-25). scripts/network_smoke.py asserts this minor
        # against the Dockerfile's FROM tag, so on THIS repo — a Render
        # DOCKER service, where the image IS the runtime declaration — the
        # image and its declaration can no longer part ways silently.
        "python": platform.python_version(),
        # Where this host's ledger actually lives, whether it survives a
        # deploy, and how much is in it (1.6.44 item 20). Additive.
        "ledger": _ledger_block(),
    }
    # Which commit the RUNNING instance was built from. This is what lets CD
    # verify the artifact it shipped rather than whichever build happens to
    # be serving: this service has a disk, so it RESTARTS with a blip
    # instead of overlapping instances, and a bare 200 therefore proves
    # nothing about WHICH build answered. muicharts found its battery had
    # been verifying the previous release on every run, invisibly, until a
    # run added a surface the old build didn't have (2026-08-21).
    #
    # OPTIONAL by design: the field is simply absent on a build predating it
    # (or anywhere but Render), and the CD wait falls back with a warning
    # rather than failing. The probe contract — `ok: true` — is unchanged,
    # so the hub sweep and the battery are unaffected either way.
    build = os.environ.get("RENDER_GIT_COMMIT")
    if build:
        payload["build"] = build

    # WHICH satellite answered. `build` says which commit, this says which
    # app — and on a fleet where every host shares one template and a
    # hostname can be repointed between services (llms.2plot.dev was,
    # 2026-08-23), "is this the site I think it is?" is a different question
    # from "is this the build I shipped?".
    #
    # Read straight from the environment rather than through
    # satellite_reporter.app_key(): that helper falls back to "boilerplate"
    # (it is byte-identical to the template's), and a probe answering
    # "boilerplate" on a host whose identity is unset would be a confident
    # lie in the one place an operator goes for the truth. The fork point at
    # the top of run.py sets the variable, so the fallback below is only
    # ever reached when something is genuinely wrong.
    payload["app"] = os.environ.get("SATELLITE_APP_KEY") or "unknown"

    # The geo guardrail's LIVE state (dash-improve-my-llms >= 2.7.0). It
    # exists because "is the denylist actually in force?" could not be
    # answered from outside: the surfaces that can settle it (the boot log,
    # the operator panel) need credentials a verification pass does not have.
    #
    # Counts and flags only — never the denylist's country codes: a health
    # endpoint is not where anyone should learn policy. `resolved` reveals
    # only the caller's own country back to them, which Cloudflare's
    # /cdn-cgi/trace already does — and it is THE per-host check that has to
    # pass before anyone trusts a denylist. It also localises a failure: geo
    # can be configured with a full denylist and still never match if the
    # country header is not reaching the app — "configured: true, denied: 7,
    # resolved: unknown" says that in one line.
    try:
        from dash_improve_my_llms import geo
    except ImportError:
        # Pre-2.7 package: the key is OMITTED, not error-flagged — a host on
        # an older floor is not broken, it just predates the diagnostic.
        pass
    else:
        try:
            payload["geo"] = {
                "configured": bool(geo.is_configured()),
                "denied": len(
                    geo.effective_policy().get("deny_countries") or []
                ),
                "resolved": _resolved_country(headers),
                "headers_seen": _geo_headers_seen(),
            }
        except Exception:  # never let a diagnostic break the health probe
            payload["geo"] = {"configured": False, "denied": 0, "error": True,
                              "headers_seen": _geo_headers_seen()}

    return payload


def register_health_route(app, backend: str) -> None:
    """Mount ``/healthz`` on flask. No-op on FastAPI (already typed there)."""
    if backend == "fastapi":
        return

    server = app.server

    # Built PER REQUEST, not once at registration. It used to be a snapshot
    # closed over by the route — harmless while every field was static
    # (ok/backend/dash_version/build never change for a running process),
    # and silently wrong the moment one is not: this route is registered
    # long before any geo configuration runs, so a snapshot would report the
    # guardrail unconfigured on a host where it is configured — the
    # diagnostic lying in exactly the situation it exists for.
    if backend == "quart":
        from quart import jsonify, request

        @server.get("/healthz")
        async def _healthz():  # pragma: no cover — quart runtime
            return jsonify(health_payload(backend, headers=request.headers))
    else:
        from flask import jsonify, request

        @server.get("/healthz")
        def _healthz():
            return jsonify(health_payload(backend, headers=request.headers))

    print(f"[dash-mui-scheduler] /healthz registered ({backend}) — "
          "the 2plot.ai hourly health sweep probes this path.")
