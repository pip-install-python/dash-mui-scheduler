"""Network bulletin — hub-published tips and announcements.

The hub (2plot.dev) serves one JSON document at ``/api/network/bulletin`` and
every satellite renders it in the header of its llms.txt viewer — the network
says "here is what changed" once, in one place, instead of in a dozen
repositories that immediately drift.

The wiring is a function that returns whether it wired, ``run.py`` prints
that, and ``tests/test_bulletin.py`` exercises it directly — no commented-out
code, and a boot log line that says which of the two states you are in. (The
boilerplate learned this the hard way: four commented-out lines in run.py and
an env var set in production against code that never read it. Nothing failed;
the announcement just never appeared.)

NOTE: ``NETWORK_BULLETIN_URL`` must be set on the Render SERVICE, not only in
render.yaml — blueprint ``envVars`` apply on Blueprint sync, not on git-push
autodeploys. Detection: this satellite showing ONE generic tip where the hub
publishes more is an unwired bulletin, not a styling difference.

Env:
    NETWORK_BULLETIN_URL   the hub endpoint. Absent -> feature off, silently.
    NETWORK_BULLETIN_TTL_S seconds a cached bulletin stays fresh (default 900)
"""

from __future__ import annotations

import os
from typing import Optional

DEFAULT_TTL_S = 900.0

# The hub endpoint. Not a default — `configure()` requires the env var to be
# set, because a satellite that silently starts calling a hub it was never
# pointed at is a surprise. This constant is the one place render.yaml and
# .env docs copy from.
HUB_BULLETIN_URL = "https://2plot.dev/api/network/bulletin"


def url() -> Optional[str]:
    return os.environ.get("NETWORK_BULLETIN_URL") or None


def _ttl() -> float:
    try:
        return max(60.0, float(os.environ.get("NETWORK_BULLETIN_TTL_S",
                                              DEFAULT_TTL_S)))
    except (TypeError, ValueError):
        return DEFAULT_TTL_S


def app_id() -> str:
    """This app's key in the hub's network directory.

    Reused from ``lib.satellite_reporter`` rather than hard-coded, so a
    deployment that sets ``SATELLITE_APP_KEY`` for its traffic rollups is
    automatically identified the same way here. tests/test_internal_traffic.py
    pins this, ``ad_client.APP_ID`` and the reporter key to the one short id.
    """
    from lib.satellite_reporter import app_key

    return app_key()


def configure() -> bool:
    """Point the package at the hub's bulletin. Returns whether it did.

    Fail-open in both directions: with no URL the feature is off and the
    viewer header renders the package's defaults; with an unreachable URL the
    package's client degrades silently — a hub outage must not take the
    documentation down with it.
    """
    endpoint = url()
    if not endpoint:
        return False

    try:
        from dash_improve_my_llms import configure_bulletin
    except ImportError:  # pragma: no cover - older releases lack the feature
        return False

    configure_bulletin(url=endpoint, ttl=_ttl(), app_id=app_id())
    return True
