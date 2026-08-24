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
            "'Loading...'; the floor first moved (to 2.6.1) for exactly "
            "this, and sits at >=2.7.1 now"
        )
        assert 'data-dimll-prerender="1">document.getElementById' in html, (
            f"{path}: the marked synchronous hide script is missing — "
            "JS browsers would flash the prose before React mounts"
        )
        assert "<main>" in html, f"{path}: prerender block carries no <main> prose"


def test_prerender_single_h1_and_deduped_footer_llms_links(client, page_paths):
    """What the >=2.7.1 floor buys, pinned from the app's side, EVERY page.

    Below dimll 2.7.0 every page served TWO h1s to a generic client — the
    injected prerender header plus the doc body's own markdown H1, a
    duplicate-H1 page in every crawler's eyes — and the home footer printed
    its /llms.txt link twice (on "/" the per-page link equals the root's;
    subpages legitimately carry both, DISTINCT).

    The sweep also catches app-side H1 pollution, which is why it runs on
    every page rather than a sample: upstream's first run of this test found
    a tutorial page's machine lane serving FIVE h1s because
    _expand_source_directives expanded a `.. source::` example inside a
    ```markdown teaching fence. This repo inlines example sources on 17 doc
    pages, so that class of defect is exactly the one it would hit.

    HTML comments are stripped before counting: templates/index.html
    legitimately SAYS "<h1>" inside the comment explaining its noscript
    block. Admin pages are skipped — they are hidden from machine surfaces
    and carry no prerender. So is "/404", for the same reason the 200-sweep
    above skips it: it is the layout Dash serves FOR unknown paths, it
    registers no prose, and it is correctly absent from the sitemap and
    llms.txt — there is no published document to have a structure.
    """
    for path in page_paths:
        if path.startswith("/admin") or path == "/404":
            continue
        html = client.get(path).text  # default UA — the universal lane
        stripped = re.sub(r"<!--.*?-->", "", html, flags=re.S)

        h1s = re.findall(r"<h1[\s>]", stripped)
        assert len(h1s) == 1, (
            f"{path}: {len(h1s)} h1 elements in the generic-lane document — "
            "either the pre-2.7.0 prerender-header duplicate or app-side "
            "markdown leaking headings (the fence-expansion class)"
        )

        footer = re.search(r"<footer.*?</footer>", stripped, re.S)
        assert footer, f"{path}: no prerender footer in the generic-lane document"
        llms_links = re.findall(r'href="([^"]*llms\.txt)"', footer.group(0))
        assert len(llms_links) == len(set(llms_links)), (
            f"{path}: duplicate llms.txt links in the prerender footer "
            f"({llms_links}) — 2.7.0 dedups the per-page link when it "
            "equals the root"
        )
        if path == "/":
            assert llms_links == ["/llms.txt"], (
                f"home footer llms links {llms_links} — expected exactly the "
                "root link once"
            )


def test_source_expansion_is_fence_aware(app):
    """A `.. source::` inside a fenced block is documentation, not a directive.

    Expanding one injects a ```python fence inside the already-open fence,
    which closes it early — from there the inlined file renders as markdown
    on the machine lane and every `# comment` line becomes an <h1>. The app
    fixture is requested only so pages/markdown.py is already imported with
    the repo root as CWD.
    """
    import sys

    expand = sys.modules["pages.markdown"]._expand_source_directives

    expanded = expand(".. source::requirements.txt")
    assert "# File: requirements.txt" in expanded, "real directive not expanded"
    assert "```" in expanded, "expansion lost its fence"

    taught = "```markdown\n.. source::requirements.txt\n```"
    assert expand(taught) == taught, "a fenced example was expanded"

    tilde = "~~~\n.. source::requirements.txt\n~~~"
    assert expand(tilde) == tilde, "a tilde-fenced example was expanded"
