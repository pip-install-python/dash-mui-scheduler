"""Every registered page serves, and every registry entry can unfurl.

Two cheap sweeps that catch the two ways a page breaks without anyone
noticing:

1. A route that 500s (an import-time error in a doc page's `.. exec::` module
   takes the whole page down, and `debug=False` hides the traceback).
2. A `register_page` call missing `description=` or `image_url=` — Dash then
   emits `content=""` for the meta tag, and an EMPTY og:image is worse than a
   missing one because scrapers treat it as the declared image and render a
   blank card. lib/constants.py states the rule; this is its enforcement at
   the registry level, so a new page cannot land without either.
"""

from __future__ import annotations

import re


def test_every_registered_page_serves_200(client, pages):
    """A browser GET on every registered path.

    "/404" is skipped: it is the layout Dash serves *for* unknown paths, not a
    destination anyone navigates to — its own contract is the test below.
    """
    failures = []
    for path, name, _entry in pages:
        if path == "/404":
            continue
        response = client.get(path)
        if not response.ok:
            failures.append(f"{path} ({name}) -> {response.status}")
    assert failures == [], f"pages did not serve: {failures}"


def test_unknown_paths_serve_the_spa_shell_not_an_error(client):
    """What Dash actually does with a bogus path, pinned.

    Dash's page routing is client-side: the server answers ANY path with the
    SPA shell (HTTP 200) and the renderer swaps in the "/404" layout after
    hydration. So the assertable server-side contract is: a 200, an HTML
    document, and the real app shell (title and renderer entry point) rather
    than a backend error page. If this test ever sees a 404/500 status, the
    routing changed underneath us and the "/404" page is likely unreachable.
    """
    response = client.get("/definitely-not-a-registered-page")
    assert response.status == 200, (
        f"bogus path returned {response.status}; Dash serves the shell + "
        "client-side 404 layout, so anything else is a routing regression"
    )
    assert "text/html" in response.content_type
    assert "_dash-renderer" in response.text or "react-entry-point" in response.text, (
        "the bogus-path response is not the Dash shell — the 404 layout can "
        "never render"
    )


def test_every_registry_entry_declares_description_and_image(pages):
    """The empty-og:image guard, at the source instead of the response.

    The response-side tests in test_social_card.py sample the first 8 pages;
    this covers all of them, including "/404" — a 404 unfurled into a chat
    still shows a card.
    """
    missing = []
    for path, name, entry in pages:
        if not (entry.get("description") or "").strip():
            missing.append(f"{path} ({name}): empty description")
        if not (entry.get("image_url") or "").strip():
            missing.append(f"{path} ({name}): empty image_url — og:image will "
                           "be content=\"\" and the share card renders blank")
    assert missing == [], f"register_page calls missing metadata: {missing}"


def test_prerender_rides_the_generic_lane_not_a_ua_gate(client):
    """The universal prerender must be in the initial HTML for a PLAIN
    client — no crawler user-agent. An outside SEO audit (2026-08-22) read
    five hosts as serving "Loading... and nothing else" to browsers; the
    prose was there all along, but every test that touched the prerender
    fetched with a CRAWLER UA (which exercises the separate bot-document
    path), so a regression that UA-gated the universal lane would have been
    invisible to the suite. This test is the generic-lane pin.

    Since the 2.6.1 floor the block must also be VISIBLE: dimll <= 2.6.0
    shipped the div with a literal `hidden` attribute, so every
    visibility-respecting text extractor (and arguably crawler
    content-weighting) saw only "Loading..." — present and invisible, the
    worst of both. 2.6.1 serves it visible and hides it via a synchronous
    inline script that only JS browsers execute (React's mount then wipes
    the pair, so nothing changes for humans). The div shape below is the
    regression pin for that fix, from the app's side.

    A second failure mode this catches for free: dimll's injector uses a
    SUBSTRING idempotency probe, so the marker string appearing anywhere in
    the served document — an index.html HTML comment is how two hosts in
    this fleet did it — makes every response read as already-injected and
    silently disables the entire prerender. Never spell the marker in any
    served template or asset text.
    """
    for path in ("/", "/quickstart"):
        html = client.get(path).text  # default UA — the point of the test
        div = re.search(r'<div id="dimll-prerender"[^>]*>', html)
        assert div, (
            f"{path}: no prerender block for a generic client — the "
            "universal lane is gated, off, or disabled by the marker string "
            "appearing somewhere else in the served document"
        )
        assert "hidden" not in div.group(0), (
            f"{path}: the prerender div carries `hidden` again — "
            "visibility-respecting consumers are back to reading "
            "'Loading...'; the dimll floor is >=2.6.1 for exactly this"
        )
        assert 'data-dimll-prerender="1">document.getElementById' in html, (
            f"{path}: the marked synchronous hide script is missing — "
            "JS browsers would flash the prose before React mounts"
        )
        assert "<main>" in html, f"{path}: prerender block carries no <main> prose"
