"""The analytics ledger must never be able to kill the boot.

lib/analytics_tracker is imported at the top of run.py and constructs its
module-level tracker at import time — so an exception there crashes every
worker before a port is bound, and the platform loops the deploy forever
while the old build keeps serving. That is exactly what happened in
production on 2026-08-02: TRAFFIC_ANALYTICS_FILE pointed at
/var/data/visitor_analytics.json before the persistent disk was attached,
and the Gen-0 tracker's `_ensure_file_exists()` raised FileNotFoundError
in `__init__`.

The 1.3.0 tracker (the boilerplate trio) closes that mode structurally:
`__init__` does no filesystem I/O at all, the ledger is seeded on first
flush with the parent chain created, and a flush that cannot write swallows
the error and re-buffers instead of raising. Analytics is an accessory;
these tests pin the two behaviours that keep it one.
"""

from __future__ import annotations

import json

from lib.analytics_tracker import AnalyticsTracker

UA = "Mozilla/5.0 test-browser"


def test_a_missing_parent_directory_is_created(tmp_path):
    """The /var/data case once the disk IS there but empty: the first flush
    must create the directory chain and seed the ledger rather than fail."""
    ledger = tmp_path / "var" / "data" / "visitor_analytics.json"
    tracker = AnalyticsTracker(data_file=str(ledger))  # no I/O yet — no raise

    tracker.track_visit("/quickstart", UA, "203.0.113.9")
    tracker.flush()

    assert ledger.exists(), "the ledger file was not seeded on first flush"
    visits = json.loads(ledger.read_text())["visits"]
    assert len(visits) == 1 and visits[0]["path"] == "/quickstart"


def test_an_unwritable_ledger_path_disables_tracking_not_the_boot(tmp_path):
    """The production crash, pinned: a path that cannot be created (here, a
    directory component that is actually a FILE) must construct fine and
    no-op on flush — never an exception at import time or at write time."""
    blocker = tmp_path / "not-a-directory"
    blocker.write_text("occupied")
    ledger = blocker / "visitor_analytics.json"

    tracker = AnalyticsTracker(data_file=str(ledger))  # must not raise

    tracker.track_visit("/quickstart", UA, "203.0.113.9")  # must not raise
    tracker.flush()  # must not raise — the failure is swallowed, hits rebuffered
    assert not ledger.exists()
