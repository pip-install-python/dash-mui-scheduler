"""ONE classifier — the tracker delegates to dash_improve_my_llms.classify().

Until 1.6.34 lib/analytics_tracker.py carried its own User-Agent lists: it
filed ClaudeBot (Anthropic's TRAINING crawler) under "search", still named
the retired `anthropic-ai` / `claude-web` tokens, and counted every UA-less
or library client (httpx, Go-http-client, node-fetch) as a human. Every
host in the fleet reported those numbers to the hub. These pins hold the
delegation in place — each UA string is one taken from the wire on
2026-08-29 — and the last test greps the module so a list cannot come
back quietly.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from lib.analytics_tracker import AnalyticsTracker
from lib.constants import INTERNAL_UA_TOKEN

CLAUDEBOT = ("Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; "
             "ClaudeBot/1.0; +claudebot@anthropic.com)")
GPTBOT = "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)"
GOOGLEBOT = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
HTTPX = "python-httpx/0.27.0"
CHROME = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
          "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")


@pytest.fixture
def tracker(tmp_path, monkeypatch):
    monkeypatch.setenv("ANALYTICS_GEO_LOOKUP", "0")
    return AnalyticsTracker(tmp_path / "ledger.json")


def _rows(tracker):
    tracker.flush()
    path = Path(tracker.data_file)
    if not path.exists():        # nothing written → the file is never created
        return []
    return json.loads(path.read_text())["visits"]


def _one(tracker, ua):
    tracker.track_visit("/", ua, "203.0.113.9")
    rows = _rows(tracker)
    assert len(rows) == 1, rows
    return rows[0]


@pytest.mark.parametrize("ua, bot_type, vendor_key", [
    (CLAUDEBOT, "training", "claudebot"),
    (GPTBOT, "training", "gptbot"),
    (GOOGLEBOT, "traditional", "googlebot"),
    (HTTPX, "unknown", None),
    ("", "unknown", None),
    (None, "unknown", None),
])
def test_crawler_lane_rows(tracker, ua, bot_type, vendor_key):
    assert tracker.is_bot(ua) is True
    assert tracker.detect_bot_type(ua) == bot_type
    row = _one(tracker, ua)
    assert row["device_type"] == "bot"
    assert row["bot_type"] == bot_type
    assert row["vendor_key"] == vendor_key
    assert row["lane"] == "crawler"
    assert row["verified"] in ("verified", "unverified", "n/a")


def test_claudebot_is_training_and_unverifiable(tracker):
    """The finding that produced this file: ClaudeBot was 'search' for a
    year. And Anthropic publishes no IP ranges, so `verified` is n/a — a
    property of the vendor, never a defect on this host."""
    row = _one(tracker, CLAUDEBOT)
    assert row["bot_type"] == "training"
    assert row["vendor_class"] == "training"
    assert row["verified"] == "n/a"


def test_a_browser_row_carries_no_vendor_keys(tracker):
    """Human rows are byte-for-byte what v3 wrote — the rollup's tests must
    not move on adoption."""
    assert tracker.is_bot(CHROME) is False
    row = _one(tracker, CHROME)
    assert row["device_type"] == "desktop"
    assert set(row) <= {"timestamp", "path", "device_type", "user_agent",
                        "ip_address", "location"}, row


def test_internal_traffic_is_still_dropped_before_classification(tracker):
    tracker.track_visit("/", f"Mozilla/5.0 {INTERNAL_UA_TOKEN}-sweep", "203.0.113.9")
    assert _rows(tracker) == []


def test_the_module_carries_no_user_agent_list():
    """The grep. A token the registry lacks is a pushback to the package,
    never a list here (.claude/CLAUDE.md trap)."""
    src = (Path(__file__).resolve().parent.parent / "lib" / "analytics_tracker.py").read_text()
    code = "\n".join(
        line for line in src.splitlines()
        if not line.lstrip().startswith("#")
    )
    # Strip the module docstring — it names the old tokens to explain why
    # they are gone; the assertion is about CODE.
    code = re.sub(r'^"""[\s\S]*?"""', "", code, count=1)
    survivors = [t for t in ("'anthropic-ai'", "'claude-web'", "'perplexitybot'",
                             "'gptbot'", "'claudebot'", "'googlebot'", "'bingbot'",
                             "'headlesschrome'", "'phantomjs'", "'pingdom'")
                 if t in code]
    assert survivors == [], f"a hand-written UA list is back: {survivors}"
    assert "from dash_improve_my_llms import classify" in src


# ------------------------- 1.6.44 item 8: prefer, then derive, never invent --


def test_a_package_supplied_class_passes_through_untouched():
    """PREFER, tested with a CONFLICTING fixture — or it cannot fail.

    A fixture whose package class already agrees with what a local
    derivation would produce passes whether the code prefers or derives.
    This one says `search` for a vendor the registry calls something else,
    so only a real pass-through survives it.
    """
    from dash_improve_my_llms import vendors

    from lib.analytics_tracker import _vendor_class_for

    registry_says = getattr(vendors.get_vendor("gptbot"), "cls", None)
    assert registry_says and registry_says != "search", (
        "pick a different vendor: this fixture is only conflicting while the "
        f"registry disagrees with 'search' (it says {registry_says!r})"
    )

    event = {"vendor_key": "gptbot", "vendor_class": "search"}
    assert _vendor_class_for(event) == "search", (
        "the package's own class was overruled by a local derivation — the "
        "host is now a second source of truth"
    )


def test_the_class_is_derived_only_where_the_event_lacks_it():
    """DERIVE, and from the package's registry rather than a local map."""
    from dash_improve_my_llms import vendors

    from lib.analytics_tracker import _vendor_class_for

    expected = getattr(vendors.get_vendor("gptbot"), "cls", None)
    assert expected, "the registry knows no class for gptbot; pick another"
    assert _vendor_class_for({"vendor_key": "gptbot"}) == expected
    assert _vendor_class_for({"vendor_key": "gptbot",
                              "vendor_class": None}) == expected


def test_an_unknown_or_absent_vendor_gets_no_invented_class():
    from lib.analytics_tracker import _vendor_class_for

    assert _vendor_class_for({"vendor_key": None}) is None
    assert _vendor_class_for({}) is None
    assert _vendor_class_for({"vendor_key": "not-a-real-vendor"}) is None
    assert _vendor_class_for(None) is None


def test_the_read_row_carries_a_class_on_this_repos_floor():
    """The defect this fixes, stated as a measurement.

    `vendor_class` reaches the read EVENT at dimll 2.9.2. This repo's floor
    is 2.8.0, where EVENT_FIELDS has no such key — so `record_read`'s
    `{k: event.get(k) for k in EVENT_FIELDS}` dropped it at the app boundary
    and every rollup's per-vendor class was null.
    """
    import dash_improve_my_llms as pkg
    from dash_improve_my_llms._ledger import EVENT_FIELDS

    from lib.analytics_tracker import tracker

    resolved = tuple(int(n) for n in pkg.__version__.split(".")[:3]
                     if n.isdigit())
    if resolved < (2, 9, 2):
        assert "vendor_class" not in EVENT_FIELDS, (
            f"dimll {pkg.__version__} unexpectedly carries vendor_class on "
            "the event; the derivation below is no longer the load-bearing "
            "half"
        )

    event = {k: None for k in EVENT_FIELDS}
    event.update(ts=0, path="/llms.txt", ua="GPTBot/1.0", vendor_key="gptbot",
                 kind="read")

    with tracker._buffer_lock:
        tracker._reads_buffer.clear()
    tracker.record_read(event)
    with tracker._buffer_lock:
        written = list(tracker._reads_buffer)
        tracker._reads_buffer.clear()

    assert len(written) == 1, written
    assert written[0]["vendor_class"], (
        "the read row reached the ledger with no class — this is the null "
        "the board has been showing for every vendor"
    )


def test_the_rollup_reads_the_key_this_writes():
    """The two ends are held together, not assumed to match.

    `lib/traffic_rollup` groups on `vendor_class`; a fix that wrote any
    other spelling would be green here and null on the board.
    """
    from pathlib import Path

    rollup = (Path(__file__).resolve().parent.parent
              / "lib" / "traffic_rollup.py").read_text()
    assert 'r.get("vendor_class")' in rollup, (
        "the rollup no longer reads `vendor_class` — the tracker is writing "
        "a key nothing consumes"
    )
