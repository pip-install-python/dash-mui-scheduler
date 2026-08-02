"""The analytics ledger must never be able to kill the boot.

lib/analytics_tracker is imported at the top of run.py and constructs its
module-level tracker at import time — so an exception there crashes every
worker before a port is bound, and the platform loops the deploy forever
while the old build keeps serving. That is exactly what happened in
production on 2026-08-02: TRAFFIC_ANALYTICS_FILE pointed at
/var/data/visitor_analytics.json before the persistent disk was attached,
and `_ensure_file_exists()` raised FileNotFoundError in `__init__`.

Analytics is an accessory. These tests pin the two required behaviours:
a missing parent directory is created, and a genuinely unwritable path
disables tracking instead of raising.
"""

from __future__ import annotations

import json

from lib.analytics_tracker import AnalyticsTracker

UA = "Mozilla/5.0 test-browser"


def test_a_missing_parent_directory_is_created(tmp_path):
    """The /var/data case once the disk IS there but empty: first boot must
    create the directory chain rather than failing on it."""
    ledger = tmp_path / "var" / "data" / "visitor_analytics.json"
    tracker = AnalyticsTracker(data_file=str(ledger))

    assert not tracker._disabled
    assert ledger.exists(), "the ledger file was not seeded"

    tracker.track_visit("/quickstart", UA, "203.0.113.9")
    visits = json.loads(ledger.read_text())["visits"]
    assert len(visits) == 1 and visits[0]["path"] == "/quickstart"


def test_an_unwritable_ledger_path_disables_tracking_not_the_boot(tmp_path):
    """The production crash, pinned: a path that cannot be created (here, a
    directory component that is actually a FILE) must yield a tracker that
    constructs fine and no-ops — never an exception at import time."""
    blocker = tmp_path / "not-a-directory"
    blocker.write_text("occupied")
    ledger = blocker / "visitor_analytics.json"

    tracker = AnalyticsTracker(data_file=str(ledger))  # must not raise

    assert tracker._disabled
    tracker.track_visit("/quickstart", UA, "203.0.113.9")  # must not raise
    assert not ledger.exists()
