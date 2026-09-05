"""`/healthz`'s payload, and the lane that was quietly narrowing it.

1.6.44 items 1 and 20, built as one change because on THIS host they are one
defect. The template found item 20 while building it: a pydantic
`response_model` drops every field it does not declare, in silence, so item
1's `llms_version` was present on the Flask lane and absent from the FastAPI
one for two days. The template's production runs Flask, so nothing there said
so.

This service runs FastAPI. The narrowing lane is the only lane that answers
here, so the key would never have existed on this host at all — measured on
the wire before the build, against production:

    curl -sS -A 'curl/8 2plot-internal/probe' https://muischeduler.2plot.dev/healthz
    -> keys: app backend build dash_version geo ok python      (no llms_version)

The guard below is therefore written for the CLASS, not for two field names:
every key `health_payload` produces must reach the wire on whichever lane is
answering, and an undeclared key must survive the model.
"""

from __future__ import annotations

import json

import pytest

from conftest import REPO_ROOT


@pytest.fixture(scope="module")
def health(app_module):
    from lib import health as health_mod

    return health_mod


# ------------------------------------------- item 1: the resolved version --


def test_llms_version_reports_the_resolved_package(health):
    """The key exists and equals what the process actually imported.

    Not what requirements.txt asks for: this repo declares a `>=` FLOOR, and
    a floor cannot be read backwards through a cached Docker layer.
    """
    import dash_improve_my_llms as pkg

    assert health.health_payload("flask")["llms_version"] == pkg.__version__


def test_llms_version_is_omitted_rather_than_invented(health, monkeypatch):
    """A health payload that guesses a version is worse than a silent one."""
    monkeypatch.setattr(health, "_llms_version", lambda: {})
    assert "llms_version" not in health.health_payload("flask")


# ----------------------------------------------- item 20: the ledger block --


def test_the_ledger_block_has_its_four_keys_and_their_types(health):
    ledger = health.health_payload("flask")["ledger"]
    assert set(ledger) == {"path", "persistent", "visits", "reads"}
    assert isinstance(ledger["persistent"], bool)
    assert isinstance(ledger["visits"], int)
    assert isinstance(ledger["reads"], int)
    assert ledger["path"] is None or isinstance(ledger["path"], str)


def test_persistent_is_measured_from_the_path_not_declared(health, monkeypatch,
                                                           tmp_path):
    """BOTH directions, so the boolean cannot pass as a constant.

    This repo's `render.yaml` declares a 1GB disk at /var/data and points
    TRAFFIC_ANALYTICS_FILE at it — and its own comment says "A DECLARATION
    ATTACHES NOTHING". leaflet ran for weeks with a declared disk and no
    disk. An intention is not a filesystem.
    """
    import lib.analytics_tracker as tracker_mod

    outside = tmp_path / "ledger.json"
    monkeypatch.setattr(tracker_mod, "analytics_path", lambda: outside)
    assert health.health_payload("flask")["ledger"]["persistent"] is True

    inside = REPO_ROOT / "visitor_analytics.json"
    monkeypatch.setattr(tracker_mod, "analytics_path", lambda: inside)
    assert health.health_payload("flask")["ledger"]["persistent"] is False, (
        "a path under the app tree is the container filesystem, whatever the "
        "blueprint says"
    )


def test_a_missing_ledger_is_zeros_and_not_an_error(health, monkeypatch,
                                                    tmp_path):
    """/healthz must stay 200. A diagnostic that can take the health probe
    down with it is a liability."""
    import lib.analytics_tracker as tracker_mod

    monkeypatch.setattr(tracker_mod, "analytics_path",
                        lambda: tmp_path / "nothing-here.json")
    payload = health.health_payload("flask")
    assert payload["ok"] is True
    assert payload["ledger"]["visits"] == 0 and payload["ledger"]["reads"] == 0
    assert payload["ledger"]["path"].endswith("nothing-here.json")


def test_a_corrupt_ledger_is_zeros_and_not_an_error(health, monkeypatch,
                                                    tmp_path):
    import lib.analytics_tracker as tracker_mod

    broken = tmp_path / "half-written.json"
    broken.write_text('{"visits": [{"path": "/a"}')
    monkeypatch.setattr(tracker_mod, "analytics_path", lambda: broken)
    payload = health.health_payload("flask")
    assert payload["ok"] is True
    assert payload["ledger"]["visits"] == 0


def test_the_counts_are_the_rows_of_the_file_the_tracker_writes(health,
                                                                monkeypatch,
                                                                tmp_path):
    import lib.analytics_tracker as tracker_mod

    ledger = tmp_path / "a.json"
    ledger.write_text(json.dumps({
        "visits": [{"path": "/a"}, {"path": "/b"}, {"path": "/c"}],
        "reads": [{"path": "/llms.txt"}],
    }))
    monkeypatch.setattr(tracker_mod, "analytics_path", lambda: ledger)
    block = health.health_payload("flask")["ledger"]
    assert (block["visits"], block["reads"]) == (3, 1)


def test_the_block_never_carries_row_contents(health, monkeypatch, tmp_path):
    """Counts, a boolean and a path. Nothing about a visitor."""
    import lib.analytics_tracker as tracker_mod

    ledger = tmp_path / "a.json"
    ledger.write_text(json.dumps({
        "visits": [{"path": "/secret", "user_agent": "SECRET-UA",
                    "visitor_key": "deadbeefdeadbeef"}],
        "reads": [],
    }))
    monkeypatch.setattr(tracker_mod, "analytics_path", lambda: ledger)
    serialised = json.dumps(health.health_payload("flask")["ledger"])
    for leaked in ("SECRET-UA", "deadbeefdeadbeef", "/secret"):
        assert leaked not in serialised


# ------------------------------------- the guard, written for the class --


def test_the_fleet_keys_are_still_there(client):
    """Both blocks are ADDITIVE. A rename is still the failure."""
    body = json.loads(client.get("/healthz").text)
    for key in ("ok", "backend", "dash_version", "python", "app", "ledger"):
        assert key in body, f"/healthz lost {key}"


def test_the_lane_that_answers_serves_every_key_the_payload_builds(client):
    """The ASGI lane's response_model must not narrow the payload.

    THE point of item 20, and not a test of two field names: every key
    `health_payload` produces must reach the wire, whichever lane answers.
    On this host that lane is FastAPI, where a `response_model` discards
    undeclared fields without a word.
    """
    from conftest import backend
    from lib.health import health_payload

    served = json.loads(client.get("/healthz").text)
    expected = health_payload(backend())

    missing = sorted(set(expected) - set(served))
    assert missing == [], (
        f"the {backend()} lane's /healthz drops {missing} — a response_model "
        "that narrows the payload is the two-lanes trap with a type "
        "annotation on it"
    )


def test_the_asgi_model_keeps_keys_it_does_not_know_about():
    """Belt to the test above: the NEXT additive key must survive without
    anyone remembering to come back and declare it.

    Imported directly rather than through the client, so it runs on every
    leg of the matrix — this repo installs `dash[fastapi]` on all of them.
    """
    from lib.asgi_routes import HealthResponse

    widened = HealthResponse(backend="fastapi", dash_version="4.4.1",
                             python="3.14.7", a_future_key="kept")
    assert widened.model_dump().get("a_future_key") == "kept", (
        "an undeclared key is dropped — declare extra='allow'"
    )
