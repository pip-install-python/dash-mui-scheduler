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
    """Human rows carry no vendor identity — and, since 1.6.44 item 16, no
    raw address either.

    THE ROW-KEY SET IS A FORK-OWNED SEAM AND THIS TEST FLIPPED WHEN ITEM 16
    LANDED, which is the item landing rather than collateral: `ip_address` is
    gone from a default-config row and `visitor_key` has taken its place. A
    fork that has not applied item 16 sees this test fail against the new
    expectation, and that failure is the notification.
    """
    assert tracker.is_bot(CHROME) is False
    row = _one(tracker, CHROME)
    assert row["device_type"] == "desktop"
    assert set(row) <= {"timestamp", "path", "device_type", "user_agent",
                        "visitor_key", "location"}, row
    assert "ip_address" not in row, (
        "the client address is stored in a default-config visit row — item "
        "16 says it is resolved, used, and dropped"
    )
    assert row["visitor_key"], "no visitor_key: visitors cannot be told apart"


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


# ------------------------ 1.6.44 item 16: privacy by design in the tracker --


def test_the_module_makes_no_outbound_request_of_any_kind():
    """Item 16's detect — PARSED, not grepped, and the correction matters.

    The drop's original form was "no `ip-api` string in lib/". That cannot
    pass on any tree that DOCUMENTS the removal: this module explains it in
    a comment naming ip-api.com, and would fail its own detect. It is the
    class item 13 exists to stop.

    So the detect is on the CODE: the module imports no HTTP client, and none
    of the four removed callables is defined.
    """
    import ast

    src = (Path(__file__).resolve().parent.parent
           / "lib" / "analytics_tracker.py").read_text()
    tree = ast.parse(src)

    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert imported, "nothing parsed — an unreadable file must not pass"

    for client in ("requests", "urllib", "http", "socket", "httpx", "aiohttp"):
        assert client not in imported, (
            f"the tracker imports {client}: it can reach the network again"
        )

    defined = {n.name for n in ast.walk(tree)
               if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    assert defined, "no functions parsed out of the tracker"
    for gone in ("_geolocate", "geo_for", "get_geolocation", "_backfill_geo"):
        assert gone not in defined, f"{gone} is back"


def test_the_grep_form_of_that_detect_would_fail_on_this_tree():
    """Kept as evidence, not as a sentence about the past.

    The module names ip-api.com in the paragraph recording its removal, so a
    substring detect reports the defect that the documentation of its absence
    describes.
    """
    src = (Path(__file__).resolve().parent.parent
           / "lib" / "analytics_tracker.py").read_text()
    assert "ip-api" in src, (
        "the removal note is gone; if that is deliberate the correction "
        "above no longer has a subject"
    )


def test_a_default_config_visit_row_has_no_address(tracker):
    row = _one(tracker, CHROME)
    assert "ip_address" not in row
    assert "203.0.113" not in json.dumps(row), "an address leaked into the row"


def test_the_visitor_key_is_keyed_not_a_bare_digest():
    """HMAC, not sha256(ip): the IPv4 space is small enough to enumerate, so
    an UNKEYED hash of an address is a reversible encoding of the address."""
    import hashlib

    from lib.analytics_tracker import visitor_key

    ip, ua = "203.0.113.7", "Mozilla/5.0 Chrome"
    key = visitor_key(ip, ua)
    assert len(key) == 16 and all(c in "0123456789abcdef" for c in key)

    plain = hashlib.sha256(f"{ip}|{ua}".encode()).hexdigest()[:16]
    assert key != plain, (
        "visitor_key is an unsalted digest — it is a reversible encoding of "
        "the address it was supposed to replace"
    )


def test_the_visitor_key_separates_visitors_and_is_stable():
    from lib.analytics_tracker import visitor_key

    a = visitor_key("203.0.113.7", "Mozilla/5.0 Chrome")
    b = visitor_key("203.0.113.8", "Mozilla/5.0 Chrome")
    c = visitor_key("203.0.113.7", "Mozilla/5.0 Firefox")
    assert a != b and a != c
    assert a == visitor_key("203.0.113.7", "Mozilla/5.0 Chrome")


def test_the_salt_is_gitignored():
    """IN THE SAME COMMIT that introduced it, and proved from a CLONE.

    A committed salt makes every visitor_key in every clone computable by
    anyone with the repo, which undoes the item entirely. `git check-ignore`
    is the question actually being asked; the clone check in
    tests/test_claude_kit.py covers the other half of this class.
    """
    import subprocess

    repo = Path(__file__).resolve().parent.parent
    for candidate in (".visitor_salt", "some/dir/.visitor_salt"):
        result = subprocess.run(["git", "check-ignore", "-q", candidate],
                                cwd=repo, capture_output=True)
        assert result.returncode == 0, f"{candidate} is not gitignored"


@pytest.mark.parametrize("headers,expected", [
    ({"CF-IPCountry": "US", "CF-IPCity": "Austin", "CF-Region": "Texas"},
     {"country", "country_code", "city", "region"}),
    ({"CF-IPCountry": "GB"}, {"country", "country_code"}),
    ({}, set()),
])
def test_location_is_whatever_the_edge_sent(headers, expected):
    """All three directions, so the defensive read cannot pass as a constant.

    A zone WITH the visitor-location transform, a zone without it, and a
    request that arrived with nothing at all.
    """
    from lib.analytics_tracker import header_geo

    assert set(header_geo(headers)) == expected


def test_an_unknown_or_tor_country_is_not_a_country():
    from lib.analytics_tracker import header_geo

    assert header_geo({"CF-IPCountry": "XX"}) == {}
    assert header_geo({"CF-IPCountry": "T1"}) == {}


def test_the_rollup_prefers_the_stored_key_and_falls_back_to_the_old_shape():
    """Both directions, because a row from before this release is still
    inside the retention window.

    Without the fallback every historical row collapses to `?|<ua hash>` —
    one "visitor" per User-Agent — so the visitor and session counts crater
    across the deploy and the days either side are not comparable. That
    reads exactly like a traffic drop.
    """
    from lib.traffic_rollup import visitor_key as session_key

    new_row = {"visitor_key": "abc123def4567890", "user_agent": "Chrome"}
    assert session_key(new_row) == "abc123def4567890"

    old_row = {"ip_address": "203.0.113.7", "user_agent": "Chrome"}
    legacy = session_key(old_row)
    assert legacy.startswith("203.0.113.7|"), legacy
    assert session_key({"ip_address": "203.0.113.8",
                        "user_agent": "Chrome"}) != legacy, (
        "two historical visitors collapsed into one"
    )
