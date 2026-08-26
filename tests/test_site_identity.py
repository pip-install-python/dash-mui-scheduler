"""Site identity: one brand, every surface, verbatim.

NETWORK FILE: adapted from dash-email. The network standard says a site states
what it is in the same words everywhere an agent or a reader can reach. The
failure this pins is silent, which is why it needs tests rather than a code
review: nothing errors when a surface falls back to a default.

The precedent, measured live on email.2plot.dev: the /llms.txt H1 read a bare
"# Dash Email" — not a framework default, and not anything a reader could act
on either, because no package by that name exists on PyPI. The brand an agent
publishes has to be the string that finds the thing, which for this repo is
`pip install dash-mui-scheduler`.

dash-improve-my-llms 2.3.4's `resolve_site_title` is what makes the identity
resolvable: it takes the home page's registered `name` first, `app.title`
second, and *skips* generic candidates ("Home", "Index", "Dash") rather than
publishing them. These tests assert both ends of that — the inputs this repo
controls, and the H1 it produces.
"""

from __future__ import annotations

import re

from conftest import REPO_ROOT
from lib.constants import (
    PAGE_TITLE_PREFIX,
    SITE_BRAND,
    SITE_DESCRIPTION,
    SITE_SHORT_NAME,
)

# Spelled out rather than imported, so that renaming the constant cannot
# silently rename the site. Changing the brand should require changing this
# line, deliberately.
EXPECTED_BRAND = "dash-mui-scheduler — MUI X scheduling for Dash"


def test_brand_constant_is_the_agreed_identity():
    assert SITE_BRAND == EXPECTED_BRAND


def test_app_title_is_the_brand(app):
    """`Dash(title=...)` — the <title>, and `resolve_site_title`'s fallback."""
    assert app.title == EXPECTED_BRAND


def test_home_llms_doc_opens_with_the_brand():
    """run.py's `register_page_metadata(path="/", llms_doc=...)` is the home
    body that /llms.txt serves.

    This repo has no home markdown file — the prose lives inline in run.py —
    so the H1 an agent reads for the home page is whatever that literal says.
    Reading the source rather than importing keeps this test free of Dash's
    page-registry side effects (conftest boots the app for the tests that
    need it).
    """
    source = (REPO_ROOT / "run.py").read_text()
    # `llms_doc=` may be a bare parenthesised literal or wrapped in the
    # versions pipeline (`llms_doc=substitute_versions(`) — either way the
    # first string chunk after the opening paren is the H1.
    match = re.search(r'llms_doc=\w*\(\s*"((?:[^"\\]|\\.)*)"', source)
    assert match, "run.py no longer registers an inline llms_doc for the home page"
    assert match.group(1).startswith(f"# {EXPECTED_BRAND}"), (
        f"the home llms_doc opens {match.group(1)[:60]!r}, not the brand H1"
    )


def test_llms_index_h1_is_the_brand(client):
    """The single most-read line of this site, and the one nobody looks at."""
    response = client.get("/llms.txt")
    assert response.ok
    assert response.text.splitlines()[0] == f"# {EXPECTED_BRAND}"


def test_llms_index_tagline_is_the_description(client):
    body = client.get("/llms.txt").text
    assert f"> {SITE_DESCRIPTION}" in body


def test_the_viewer_brand_chip_is_not_a_framework_default(client):
    """The chip that reads "Dash" on a pre-2.3.4 artifact.

    It is rendered from the same `resolve_site_title` call as the H1, so
    asserting the brand is present catches both a stale package and a
    regressed constant. The banner is templated markup, so the brand may
    arrive HTML-escaped — compare both spellings rather than failing for a
    reason that has nothing to do with identity.
    """
    import html as html_module

    from conftest import BROWSER_ACCEPT, SAMPLE_PAGE

    page = client.get(f"{SAMPLE_PAGE}/llms.txt", accept=BROWSER_ACCEPT).text
    assert html_module.escape(EXPECTED_BRAND) in page or EXPECTED_BRAND in page, (
        "the viewer banner does not name this site"
    )


def test_the_byline_is_in_the_description_not_the_brand():
    """Naming rules from the standard.

    The brand says what the site *is*; the byline says who made it. A brand of
    "Pip Install Python" would make every satellite in the network share one
    name.

    The PACKAGE name deliberately leads the brand: for a component library the
    package IS what a reader came to find — same rule as leaflet.2plot.dev's
    "dash-leaflet2 — Leaflet 2 maps for Dash". Nobody installs a template; a
    lot of people install this.
    """
    assert SITE_SHORT_NAME in SITE_BRAND
    assert "Pip Install Python" in SITE_DESCRIPTION
    assert "Pip Install Python" not in SITE_BRAND


def test_no_surface_falls_back_to_a_generic_title():
    """The values `resolve_site_title` is designed to skip.

    If the brand were ever set to one of these, the package would silently fall
    through to the next candidate and this repo would have no idea which string
    it was publishing.
    """
    from dash_improve_my_llms.handlers import _GENERIC_SITE_TITLES

    assert SITE_BRAND.strip().lower() not in _GENERIC_SITE_TITLES


def test_the_home_page_display_name_really_is_generic(app_module):
    """Why `register_page_metadata(path="/", name=SITE_BRAND)` is load-bearing.

    `pages/home.py` registers the page as "Home" — the nav label, which is
    correct there and is on `resolve_site_title`'s skip list. Without the
    separate metadata registration in run.py the identity would fall through to
    `app.title`, which happens to be right today and would silently stop being
    right the moment somebody set a marketing title on the Dash constructor.
    """
    import dash

    from dash_improve_my_llms.handlers import _GENERIC_SITE_TITLES

    home = next(e for e in dash.page_registry.values() if e["path"] == "/")
    assert home["name"].strip().lower() in _GENERIC_SITE_TITLES


def test_readme_agrees_with_the_brand():
    """A README that names the site differently is the next drift."""
    readme = (REPO_ROOT / "README.md").read_text()
    assert EXPECTED_BRAND in readme, "README.md does not state the site brand"


def test_llms_package_floor_is_the_network_standard():
    """Identity resolution lives in the package; the floor is what delivers it."""
    import dash_improve_my_llms as pkg

    parts = tuple(int(p) for p in pkg.__version__.split(".")[:3] if p.isdigit())
    assert parts >= (2, 3, 4), (
        f"dash-improve-my-llms {pkg.__version__} predates resolve_site_title; "
        "the viewer chip and the /llms.txt H1 would fall back to app.title"
    )


# ---------------------------------------------------------------------------
# The per-page title — a share-card surface, not just a browser tab
#
# Dash passes each page's `title` straight into `og:title` and `twitter:title`
# (dash/_pages.py `_page_meta_tags`). PAGE_TITLE_PREFIX therefore sets the
# headline of every unfurl this site produces. Nobody sees their own share
# cards, so only a test catches it.
# ---------------------------------------------------------------------------


def test_the_page_title_prefix_is_derived_from_the_short_name():
    assert PAGE_TITLE_PREFIX == f"{SITE_SHORT_NAME} | "


def test_the_short_name_cannot_drift_from_the_brand():
    """Two constants, one identity. Derived, so this should be automatic."""
    assert SITE_BRAND.startswith(SITE_SHORT_NAME)


def test_the_share_card_headline_names_this_site(client):
    """og:title and twitter:title, as a scraper reads them."""
    html = client.get("/").text
    for tag in ("og:title", "twitter:title"):
        found = re.findall(
            rf'<meta[^>]*property="{tag}"[^>]*content="([^"]*)"', html
        )
        assert found, f"no {tag} on the home page"
        for value in found:
            assert SITE_SHORT_NAME in value, f"{tag}={value!r} does not name this site"


def test_no_surface_still_carries_the_old_display_name():
    """A sweep, because a rename never lands everywhere at once.

    This repo's pre-standard title was "MUI X Scheduler for Plotly Dash".
    Comments and docstrings are stripped first: a file below is allowed to
    document the old value while explaining the fix, and that is the one
    legitimate mention.

    Scope is the files that PUBLISH an identity. `setup.py` and the package
    metadata are out, because the library's PyPI description is a different
    thing from the site's name. README and the docs pages are out too — they
    legitimately describe "the MUI X Scheduler" (the upstream library) in
    prose that a whole-repo sweep could not tell from a stale title.
    """
    offenders = []
    for path in ("lib/constants.py", "templates/index.html",
                 "assets/favicon/site.webmanifest", "scripts/network_smoke.py"):
        text = (REPO_ROOT / path).read_text()
        if path.endswith(".py"):
            text = re.sub(r'"""(?:.|\n)*?"""', "", text)
            text = re.sub(r"#.*", "", text)
        text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
        if "MUI X Scheduler for Plotly Dash" in text:
            offenders.append(path)
    assert offenders == [], f"the old display name survives in {offenders}"


def test_both_content_lanes_run_the_versions_pipeline():
    """The docs lane and the home lane agree on the content pipeline.

    Upstream this pin reads `pages/home.py`, because the template's home is
    markdown and /llms.txt serves home.md's text. This site's home is a
    hand-written DMC page with no markdown at all — its root machine-lane
    prose is the `llms_doc=` string in run.py — so run.py is where the home
    half of the contract lives here. A `{{VERSION:...}}` written into that
    string without the call would ship RAW on /llms.txt, the most-read
    machine surface the site has.

    AST, not grep — the marker-in-comment trap cuts both ways: a comment
    naming the call would satisfy a grep on a file that never runs it.
    """
    import ast

    for rel in ("run.py", "pages/markdown.py"):
        tree = ast.parse((REPO_ROOT / rel).read_text(encoding="utf-8"))
        called = any(
            isinstance(node, ast.Call)
            and "substitute_versions"
            in (getattr(node.func, "id", ""), getattr(node.func, "attr", ""))
            for node in ast.walk(tree)
        )
        assert called, (
            f"{rel} never calls substitute_versions — its lane serves "
            "version tokens raw"
        )


def test_no_version_token_reaches_the_machine_lane(client):
    """The wire half. Vacuous on the day no served prose happens to carry a
    token — which is exactly why the source pin above ships with it, not
    instead of it."""
    for path in ("/llms.txt", "/quickstart/llms.txt"):
        body = client.get(path).text
        for token in ("{{VERSION:", "{{DIMLL_VERSION}}"):
            assert token not in body, f"{path} serves a raw {token} token"
