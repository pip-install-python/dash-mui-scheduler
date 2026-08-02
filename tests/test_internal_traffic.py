"""The network's internal-traffic contract — the analytics point of truth.

NETWORK FILE: adapted from dash-email (itself from
dash-documentation-boilerplate 1.2.4). This app has no `lib/hub_client.py`
(it holds no key material and asks the hub for nothing), so that repo's third
outbound test has no counterpart here.

The rule (https://2plot.ai/docs/satellite-analytics, "Internal traffic"): a
request whose User-Agent contains `2plot-internal` is 2plot machinery talking
to itself — the hub's hourly health sweep, CI smoke batteries, the 4x-daily
heartbeat, cross-app calls — and is counted NOWHERE. Dropped at write time,
before device detection and before bot classification. `/healthz` is never a
visit either.

Both halves are tested here, because a contract kept on only one side is not
kept at all:

*inbound*   token-carrying requests never reach the ledger, and therefore
            never reach `human_hits` / `bot_hits` in the hourly rollup this
            app POSTs to 2plot.ai;
*outbound*  every call this host makes to another network host sends
            `INTERNAL_UA`, so the far side can apply the same rule — the
            hourly rollup POST and the ad client's per-page-view fetch.
"""

from __future__ import annotations

import json

import pytest

from conftest import BROWSER_UA, CRAWLER_UA, SAMPLE_PAGE
from lib.analytics_tracker import tracker
from lib.constants import INTERNAL_UA, INTERNAL_UA_TOKEN, internal_ua

# A real page. `lib/traffic_report` drops infrastructure paths (`/llms.txt`,
# `/robots.txt`, `/healthz`, ...) at read time, so a rollup assertion made
# against one of those would pass no matter what the tracker did.
PAGE = SAMPLE_PAGE


def _ledger_visits():
    """Every hit on disk. The tracker writes synchronously (whole-file
    rewrite per hit), so there is no buffer to flush first."""
    try:
        with open(tracker.data_file) as f:
            return json.load(f).get("visits", [])
    except FileNotFoundError:
        return []


def _rollup():
    """Today's rollup as the hub would receive it."""
    from lib.traffic_report import build_rollup

    return build_rollup()


# --------------------------------------------------------------- the token --


def test_token_is_the_network_wide_string():
    """The contract only works if every host agrees on the byte sequence."""
    assert INTERNAL_UA_TOKEN == "2plot-internal"
    assert INTERNAL_UA_TOKEN in INTERNAL_UA
    assert INTERNAL_UA.startswith(INTERNAL_UA_TOKEN)


def test_caller_suffix_never_breaks_the_token():
    ua = internal_ua("traffic-report")
    assert INTERNAL_UA_TOKEN in ua
    assert ua.endswith("traffic-report")
    assert internal_ua() == INTERNAL_UA


# ------------------------------------------------------------------ inbound --


def test_the_tests_can_see_the_ledger_at_all(client, tmp_state_dir):
    """Guard for every delta assertion below.

    If the ledger path were wrong (or the suite were writing into the repo's
    own visitor_analytics.json), every "count did not change" test would pass
    vacuously. Prove a write lands first.
    """
    assert str(tracker.data_file).startswith(tmp_state_dir), tracker.data_file
    before = len(_ledger_visits())
    client.get(PAGE, user_agent=BROWSER_UA)
    assert len(_ledger_visits()) == before + 1


def test_internal_ua_is_counted_nowhere(client):
    before = len(_ledger_visits())
    client.get(PAGE, user_agent=internal_ua("network-smoke"))
    client.get("/", user_agent=INTERNAL_UA)
    assert len(_ledger_visits()) == before


def test_a_crawler_shaped_probe_carrying_the_token_stays_internal(client):
    """The battery's crawler probe exercises the bot path deliberately.

    It must still not be counted. This is precisely why the drop happens
    before `detect_device_type` — classification would file it under `bot`.
    """
    before = len(_ledger_visits())
    client.get(PAGE, user_agent=f"{CRAWLER_UA} {INTERNAL_UA}")
    assert len(_ledger_visits()) == before


def test_the_token_is_matched_case_insensitively(client):
    before = len(_ledger_visits())
    client.get(PAGE, user_agent="2PLOT-INTERNAL/1.0 Health-Sweep")
    assert len(_ledger_visits()) == before


def test_healthz_is_never_a_visit(client):
    before = len(_ledger_visits())
    client.get("/healthz", user_agent="Render/1.0 health-check")
    client.get("/healthz", user_agent=BROWSER_UA)
    assert len(_ledger_visits()) == before


# ----------------------------------------------- the reported numbers -------
#
# The exclusion that actually matters. Everything above is about the ledger;
# this is about what 2plot.ai charts.


def test_internal_traffic_is_absent_from_human_hits_and_bot_hits(client):
    before = _rollup()

    # Four calls that are all machinery, in the two shapes the network sends:
    # a plain internal UA, and a crawler-shaped probe carrying the token.
    for _ in range(2):
        client.get(PAGE, user_agent=internal_ua("network-smoke"))
        client.get(PAGE, user_agent=f"{CRAWLER_UA} {INTERNAL_UA}")

    after = _rollup()
    assert after["human_hits"] == before["human_hits"], (
        "internal traffic reached human_hits — the hub would chart the health "
        "sweep as readers of these docs"
    )
    assert after["bot_hits"] == before["bot_hits"], (
        "internal traffic reached bot_hits — the hub would chart CI as crawler "
        "interest"
    )


def test_real_traffic_is_still_counted(client):
    """The exclusions must not have lobotomised the tracker.

    A rule that drops everything also satisfies every assertion above, so the
    positive case is load-bearing: one browser hit is one human, one bot hit
    is one bot.

    The bot probe is an AI-agent UA rather than Googlebot: on the flask
    backend dash-improve-my-llms' bot middleware answers UAs on ITS bot list
    (googlebot, generic 'bot'/'crawler'/'curl', ...) before run.py's tracking
    hook runs — registered in the opposite order from dash-email — so a
    Googlebot hit never reaches the ledger there at all (see the ordering
    note in dash-email's run.py: tracking MUST precede add_llms_routes).
    `ChatGPT/1.0` is classified a bot by this app's tracker but is not on the
    package's list, so it exercises the full request path on both backends.
    """
    bot_ua = "ChatGPT/1.0 (AI assistant)"
    assert tracker.detect_device_type(bot_ua) == "bot"  # keep the probe honest

    before = _rollup()
    client.get(PAGE, user_agent=BROWSER_UA)
    client.get(PAGE, user_agent=bot_ua)
    after = _rollup()

    assert after["human_hits"] == before["human_hits"] + 1
    assert after["bot_hits"] == before["bot_hits"] + 1


# ----------------------------------------------------------------- outbound --


class _FakeResponse:
    status_code = 200
    text = ""


def test_the_traffic_rollup_post_sends_the_token(monkeypatch):
    """`post_rollup` is a clean no-op without the secret (the suite runs
    secretless), so give it a dummy secret and capture the POST it makes."""
    from lib import traffic_report

    monkeypatch.setenv("CROSS_APP_WEBHOOK_SECRET", "test-secret")

    seen = {}

    def fake_post(*args, **kwargs):
        seen.update(kwargs.get("headers") or {})
        return _FakeResponse()

    monkeypatch.setattr(traffic_report.requests, "post", fake_post)

    ok = traffic_report.post_rollup(
        {"app": "muischeduler", "date": "2026-08-01",
         "human_hits": 0, "bot_hits": 0}
    )
    assert ok is True
    ua = seen.get("User-Agent", "")
    assert INTERNAL_UA_TOKEN in ua
    assert ua.endswith("traffic-report")


def test_the_ad_fetch_sends_the_token(monkeypatch):
    """One call per docs page view — the loudest outbound path."""
    from lib import ad_client

    seen = {}

    class _Captured(Exception):
        """Abort the request once the headers have been seen."""

    def fake_get(*args, **kwargs):
        seen.update(kwargs.get("headers") or {})
        raise _Captured

    monkeypatch.setattr(ad_client._session, "get", fake_get)
    # The 60s circuit breaker survives from any earlier failure in this
    # process; reset it or fetch_ad returns None without calling anything.
    monkeypatch.setattr(ad_client, "_last_failure", 0.0)

    assert ad_client.fetch_ad(SAMPLE_PAGE) is None  # the fake raised
    assert INTERNAL_UA_TOKEN in seen.get("User-Agent", "")


def test_this_app_reports_under_its_short_directory_key():
    """One id on every hub surface: traffic, ads and the bulletin.

    The hub folds legacy spellings at ingest, so an old build keeps working —
    but a satellite that never converges shows up as two rows on
    /admin/ad-analytics and the network board, and nobody can tell they are
    the same host.
    """
    from lib import ad_client, bulletin, traffic_report

    assert traffic_report.app_key() == "muischeduler"
    assert bulletin.app_id() == "muischeduler"
    assert ad_client.APP_ID == "muischeduler"


@pytest.mark.parametrize("script", ["smoke_live", "network_smoke"])
def test_every_battery_script_sends_the_token(script):
    """A post-deploy battery sweeps every peer; it must not register anywhere."""
    import importlib.util

    from conftest import REPO_ROOT

    spec = importlib.util.spec_from_file_location(
        f"_ua_{script}", REPO_ROOT / "scripts" / f"{script}.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    agents = [
        value
        for name, value in vars(module).items()
        if (name == "UA" or name.endswith("_UA")) and isinstance(value, str)
    ]
    assert agents, f"scripts/{script}.py declares no User-Agent constant"
    missing = [ua for ua in agents if INTERNAL_UA_TOKEN not in ua]
    assert missing == [], f"scripts/{script}.py sends untokened UAs: {missing}"
