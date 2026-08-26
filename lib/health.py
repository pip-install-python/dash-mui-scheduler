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

import os
import platform

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


def health_payload(backend: str, headers=None) -> dict:
    payload = {
        "ok": True,
        "backend": backend,
        "dash_version": dash.__version__,
        # WHICH interpreter is actually serving. Before this field a repo
        # could declare three different Pythons (image, CI matrix, platform
        # runtime) and nothing on the wire could contradict any of them —
        # the drift was invisible to the battery by construction (ops-seat
        # finding, 2026-08-25). scripts/network_smoke.py asserts this minor
        # against the Dockerfile's FROM tag, so on THIS repo — a Render
        # DOCKER service, where the image IS the runtime declaration — the
        # image and its declaration can no longer part ways silently.
        "python": platform.python_version(),
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
            }
        except Exception:  # never let a diagnostic break the health probe
            payload["geo"] = {"configured": False, "denied": 0, "error": True}

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
