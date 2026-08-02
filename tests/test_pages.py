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
