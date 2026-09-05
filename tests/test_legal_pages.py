"""/terms and /privacy — one document each, and the privacy text held to the code.

1.6.44 item 15. The shape is the point: ONE markdown string per page, rendered
for the browser and handed to the machine lane as `llms_doc`. A site whose
privacy page says one thing to a reader and another to a crawler has two
privacy policies, and only one of them was reviewed.

The binding test is `test_every_key_a_real_visit_row_carries_is_described`. It
does not read the prose for keywords — it drives the REAL tracker, takes the
row that lands in the ledger, and asserts every key in it is described on the
page. If the tracker starts storing something new, the page does not go
quietly false; the suite goes red.
"""

from __future__ import annotations

import json

import pytest

from conftest import CRAWLER_UA

LEGAL_PATHS = ("/terms", "/privacy")


# ------------------------------------------------------------ registration --


def test_both_pages_are_registered_under_legal(app_module):
    import dash

    entries = {e["path"]: e for e in dash.page_registry.values()}
    for path in LEGAL_PATHS:
        assert path in entries, f"{path} is not a registered page"
        assert entries[path]["category"] == "Legal", entries[path]


def test_legal_is_in_category_order_and_last():
    """Placement: the drop says "between Components and Admin". This tree has
    no Components category, and Admin is built separately by the navbar — so
    LAST is that position here, not a different decision."""
    from lib.constants import CATEGORY_ORDER

    assert "Legal" in CATEGORY_ORDER
    assert CATEGORY_ORDER[-1] == "Legal", CATEGORY_ORDER


def test_the_sidebar_renders_a_legal_section(app_module):
    from components.navbar import sections_for

    import dash

    sections = dict(sections_for(dash.page_registry.values()))
    assert "Legal" in sections, sorted(sections)
    paths = {e["path"] for e in sections["Legal"]}
    assert paths == set(LEGAL_PATHS), paths


def test_the_footer_links_both_and_they_resolve(app_module):
    """The pipdocs defect this item exists for, in its original shape: /terms
    and /privacy linked from every page in the fleet's footer, serving
    nothing. Dash answers 200 for an unregistered path, so only the registry
    can see it."""
    import dash

    from components.footer import create_footer

    text = str(create_footer())
    registered = {e["path"] for e in dash.page_registry.values()}
    for path in LEGAL_PATHS:
        assert path in text, f"the footer does not link {path}"
        assert path in registered


# ----------------------------------------------------- one document, two lanes --


@pytest.mark.parametrize("path", LEGAL_PATHS)
def test_the_browser_lane_renders_the_page(client, path):
    response = client.get(path)
    assert response.status == 200


@pytest.mark.parametrize("path", LEGAL_PATHS)
def test_the_machine_lane_serves_the_same_document(client, path):
    """ONE string, both lanes. Not "similar" — the same source.

    Compared on a distinctive sentence rather than byte-for-byte: the crawler
    document is wrapped by the package with its own header, so equality would
    fail for a reason that is not the one being tested.
    """
    from pages.legal import PRIVACY_DOC, TERMS_DOC

    source = TERMS_DOC if path == "/terms" else PRIVACY_DOC
    doc = client.get(f"{path}/llms.txt", user_agent=CRAWLER_UA)
    assert doc.status == 200, f"{path}/llms.txt answered {doc.status}"

    # A line from the middle of the document, so a stub or a title-only
    # response cannot pass.
    marker = [ln for ln in source.splitlines()
              if ln.startswith("## ")][2].lstrip("# ").strip()
    assert marker in doc.text, (
        f"{path}/llms.txt does not carry {marker!r} — the machine lane is "
        "being served something other than the page's own markdown"
    )


@pytest.mark.parametrize("path", LEGAL_PATHS)
def test_both_appear_in_the_root_index(client, path):
    """Item 15's acceptance: /terms/llms.txt and /privacy/llms.txt present in
    the root index, so an agent that finds the site finds them."""
    index = client.get("/llms.txt", user_agent=CRAWLER_UA)
    assert index.status == 200
    assert f"{path}/llms.txt" in index.text, (
        f"{path}/llms.txt is absent from the root index"
    )


# --------------------------- the privacy page is bound to the mechanism --


def test_every_key_a_real_visit_row_carries_is_described(tmp_path,
                                                         monkeypatch,
                                                         app_module):
    """The binding. A REAL row, not a fixture of one.

    The page claims a list of what is stored. This drives the actual tracker,
    reads the row it wrote, and requires the page to describe every key in
    it. A tracker that starts storing something new makes this red instead of
    making the page quietly false.
    """
    import lib.analytics_tracker as tracker_mod
    from pages.legal import PRIVACY_DOC

    ledger = tmp_path / "visitor_analytics.json"
    monkeypatch.setattr(tracker_mod, "analytics_path", lambda: ledger)
    tracker = tracker_mod.AnalyticsTracker(data_file=ledger)
    tracker.track_visit(
        "/quickstart",
        "Mozilla/5.0 (Macintosh) AppleWebKit/537.36 Chrome/120 Safari/537.36",
        "203.0.113.7",
        headers={"CF-IPCountry": "US", "CF-IPCity": "Austin"},
    )
    tracker.flush()

    rows = json.loads(ledger.read_text())["visits"]
    assert rows, "the tracker wrote no row — this test would assert nothing"
    row = rows[0]

    # What each stored key is called on the page, in the reader's words.
    described = {
        "timestamp": "the **time** of the request",
        "path": "the **path** requested",
        "device_type": "a **device type**",
        "user_agent": "the **User-Agent** string",
        "visitor_key": "a **visitor key**",
        "location": "a **location**",
    }
    undescribed = sorted(set(row) - set(described))
    assert undescribed == [], (
        f"the tracker stores {undescribed} and the privacy page does not "
        "mention it. Describe it there, or stop storing it."
    )
    for key, phrase in described.items():
        if key in row:
            assert phrase in PRIVACY_DOC, (
                f"the page's description of {key} ({phrase!r}) has been "
                "reworded; the binding above is no longer checking anything"
            )


def test_the_page_claims_no_address_is_stored_and_the_code_agrees():
    """Both halves, so the sentence cannot outlive the behaviour."""
    from pages.legal import PRIVACY_DOC

    assert "**Your IP address.**" in PRIVACY_DOC

    import lib.analytics_tracker as tracker_mod

    assert tracker_mod.KEEP_CLIENT_IP is False, (
        "ANALYTICS_KEEP_CLIENT_IP is on in this environment, so the page's "
        "claim would be false here"
    )


def test_the_page_claims_no_outbound_lookup_and_the_module_makes_none():
    import ast

    from conftest import REPO_ROOT
    from pages.legal import PRIVACY_DOC

    assert "REMOVED — not disabled" in PRIVACY_DOC

    tree = ast.parse((REPO_ROOT / "lib" / "analytics_tracker.py").read_text())
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert imported, "nothing parsed"
    assert not ({"requests", "urllib", "httpx", "aiohttp"} & imported)


def test_the_healthz_field_the_page_points_at_exists():
    """The page tells a reader to check `geo.headers_seen` on /healthz. If
    that field is renamed, the page sends them somewhere that answers
    nothing."""
    from lib.health import health_payload
    from pages.legal import PRIVACY_DOC

    assert "geo.headers_seen" in PRIVACY_DOC
    assert "headers_seen" in health_payload("flask")["geo"]
