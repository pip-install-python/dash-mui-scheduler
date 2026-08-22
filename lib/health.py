"""``/healthz`` liveness probe for the Flask backend.

The 2plot.ai hub sweeps every satellite's ``/healthz`` once an hour and
records up/down + latency — the "Satellite health & reach" panel on
``/traffic``. The battery (scripts/network_smoke.py) and the CD deploy gate
both assert the exact field ``ok: true``; a 200 with different JSON reads as
"unhealthy" to them, deliberately.

The FastAPI build already declares a typed ``/healthz`` in
``lib/asgi_routes`` (it shows up in Swagger); this module gives the flask
backend the same endpoint so the probe result doesn't depend on which backend
a deployment happens to run. Keep it cheap: the hub measures the round trip.
"""
from __future__ import annotations

import os

import dash


def health_payload(backend: str) -> dict:
    from lib.satellite_reporter import app_key

    payload = {
        "ok": True,
        "app": app_key(),
        "backend": backend,
        "dash_version": dash.__version__,
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
    return payload


def register_health_route(app, backend: str) -> None:
    """Mount ``/healthz`` on flask. No-op on FastAPI (already typed there)."""
    if backend == "fastapi":
        return

    server = app.server
    payload = health_payload(backend)

    if backend == "quart":
        from quart import jsonify

        @server.get("/healthz")
        async def _healthz():  # pragma: no cover — quart runtime
            return jsonify(payload)
    else:
        from flask import jsonify

        @server.get("/healthz")
        def _healthz():
            return jsonify(payload)

    print(f"[dash-mui-scheduler] /healthz registered ({backend}) — "
          "the 2plot.ai hourly health sweep probes this path.")
