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


# ---------------- 1.6.44 item 22: the ledger says at boot whether it survives --


def _boot(env_overrides):
    """Import lib.analytics_tracker in a FRESH interpreter, return its output.

    A SUBPROCESS, not caplog, and not an in-process reimport. The drop said
    "via caplog"; a `print` at import time cannot be seen by caplog, and
    mirroring the existing `[visibility]` warning is the whole point — an
    operator greps ONE deploy log, and a warning in a different format is a
    warning they do not find. A subprocess also exercises the real boot path
    rather than a module already in sys.modules.
    """
    import os
    import subprocess
    import sys
    from pathlib import Path

    repo = Path(__file__).resolve().parent.parent
    env = {k: v for k, v in os.environ.items() if k != "TRAFFIC_ANALYTICS_FILE"}
    env.update({k: v for k, v in env_overrides.items() if v is not None})
    result = subprocess.run(
        [sys.executable, "-c",
         "import sys; sys.path.insert(0, '.'); import lib.analytics_tracker"],
        cwd=repo, env=env, capture_output=True, text=True, timeout=120,
    )
    assert result.returncode == 0, result.stderr[-800:]
    return result.stdout + result.stderr


def test_an_unset_ledger_path_warns_at_boot():
    out = _boot({})
    assert "[analytics] WARNING: TRAFFIC_ANALYTICS_FILE unset" in out, out[:400]
    assert "will not survive a deploy" in out


def test_a_configured_ledger_path_boots_in_silence(tmp_path):
    """The other direction, or the test above passes on a guard that warns
    unconditionally."""
    out = _boot({"TRAFFIC_ANALYTICS_FILE": str(tmp_path / "visitor.json")})
    assert "[analytics]" not in out, out[:400]


def test_the_warning_mirrors_the_visibility_one():
    """Same shape, so one grep finds both.

    The two stores fail for identical reasons and live on the same disk; an
    operator who has learnt to look for `[visibility] WARNING:` should find
    the ledger's beside it rather than in a format of its own.
    """
    from pathlib import Path

    repo = Path(__file__).resolve().parent.parent
    tracker = (repo / "lib" / "analytics_tracker.py").read_text()
    visibility = (repo / "lib" / "page_visibility.py").read_text()

    assert "[visibility] WARNING:" in visibility
    assert "[analytics] WARNING:" in tracker
    for phrase in ("is not a mounted disk on", "unset"):
        assert phrase in tracker and phrase in visibility, phrase


def test_the_boot_guard_and_the_healthz_block_agree(tmp_path, monkeypatch):
    """Item 22 pairs with item 20: the guard says it ONCE, the block says it
    continuously. If they ever disagreed, one of them would be lying.

    Checked in both directions against the same rule — a path inside the
    repository is the container filesystem, whatever the blueprint declares.
    """
    import lib.analytics_tracker as tracker_mod
    from conftest import REPO_ROOT
    from lib.health import health_payload

    outside = tmp_path / "ledger.json"
    monkeypatch.setattr(tracker_mod, "analytics_path", lambda: outside)
    assert health_payload("flask")["ledger"]["persistent"] is True
    assert "[analytics]" not in _boot({"TRAFFIC_ANALYTICS_FILE": str(outside)})

    inside = REPO_ROOT / "visitor_analytics.json"
    monkeypatch.setattr(tracker_mod, "analytics_path", lambda: inside)
    assert health_payload("flask")["ledger"]["persistent"] is False
    assert "[analytics] WARNING" in _boot({}), (
        "the wire says this ledger is not persistent and the boot said "
        "nothing — the two halves of the same fact disagree"
    )
