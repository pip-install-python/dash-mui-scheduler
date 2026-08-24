"""Configuration that is silently wrong when it's wrong: base URL, template
metadata, and the version numbers that live in more than one file."""

from __future__ import annotations

import json
import re

import pytest

from conftest import REPO_ROOT
from lib import constants

INDEX_HTML = (REPO_ROOT / "templates" / "index.html").read_text()

# The template is heavily commented, and several comments quote the very tags
# they are explaining. Scanning for live markup has to ignore them.
INDEX_HTML_LIVE = re.sub(r"<!--.*?-->", "", INDEX_HTML, flags=re.S)


# ---------------------------------------------------------------------------
# BASE_URL guard
# ---------------------------------------------------------------------------


def test_default_base_url_is_the_public_domain():
    assert constants.DEFAULT_BASE_URL == "https://muischeduler.2plot.dev"
    assert not constants.DEFAULT_BASE_URL.endswith("/")


def test_guard_is_inert_outside_production(monkeypatch):
    monkeypatch.delenv("RENDER", raising=False)
    monkeypatch.delenv("APP_ENV", raising=False)
    monkeypatch.delenv("APP_BASE_URL", raising=False)
    constants.require_owned_base_url()  # must not raise locally or in CI


def test_guard_rejects_an_unset_base_url_in_production(monkeypatch):
    """A fork that deploys without setting APP_BASE_URL would serve the
    boilerplate's canonical on every page and ask to be deindexed."""
    monkeypatch.setenv("RENDER", "true")
    monkeypatch.delenv("APP_BASE_URL", raising=False)
    with pytest.raises(RuntimeError, match="APP_BASE_URL"):
        constants.require_owned_base_url()


def test_guard_rejects_platform_hostnames(monkeypatch):
    monkeypatch.setenv("RENDER", "true")
    monkeypatch.setenv("APP_BASE_URL", "https://my-docs.onrender.com")
    with pytest.raises(RuntimeError, match="platform-generated"):
        constants.require_owned_base_url("https://my-docs.onrender.com")


def test_guard_accepts_a_real_domain(monkeypatch):
    monkeypatch.setenv("RENDER", "true")
    monkeypatch.setenv("APP_BASE_URL", "https://leaflet.2plot.dev")
    constants.require_owned_base_url("https://leaflet.2plot.dev")


# ---------------------------------------------------------------------------
# index.html
# ---------------------------------------------------------------------------


def test_the_only_canonical_is_the_per_request_token():
    """This fork deviates from the template here, deliberately.

    The template ships no canonical at all and lets the package inject one.
    This app declares exactly ONE, as the literal token ``__PAGE_URL__``,
    which run.py's index hook replaces with the REQUESTED page's canonical
    URL on every response — so a crawler that reads HTML without running
    JavaScript already gets the right one, instead of the home page's.

    Both halves are load-bearing and both are pinned here: exactly one tag
    (a conflicting pair is no signal), and never a literal host (that is the
    "every page is a duplicate of a host that never existed" failure, and it
    is why lib/constants.BASE_URL is the only source of absolute URLs).
    """
    live = re.findall(r'<link[^>]+rel="canonical"[^>]*>', INDEX_HTML_LIVE)
    assert live == ['<link rel="canonical" href="__PAGE_URL__">'], (
        f"expected exactly the per-request canonical token, found: {live}"
    )


def test_template_has_no_placeholder_hosts():
    for placeholder in ("yourdomain.com", "onrender.com", "Your Organization Name",
                        "Your Name or Organization", "plotly.pro"):
        assert placeholder not in INDEX_HTML, f"{placeholder!r} left in templates/index.html"


def test_template_references_only_assets_that_exist():
    """A <link> or <meta> pointing at a missing asset is a 404 on every page
    load — invisible in a browser, noisy in the logs, and a broken preview
    card on every share."""
    referenced = set(
        re.findall(
            r'["\'(](?:https://boilerplate\.2plot\.dev)?/assets/([^"\')\s]+)',
            INDEX_HTML_LIVE,
        )
    )
    missing = {name for name in referenced if not (REPO_ROOT / "assets" / name).exists()}
    assert not missing, f"index.html references assets that do not exist: {sorted(missing)}"


def _ld_blocks() -> list[dict]:
    """Every JSON-LD block in the template, parsed. Raises on malformed markup."""
    raw = re.findall(
        r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', INDEX_HTML, re.S
    )
    return [json.loads(block) for block in raw]


def _ld_nodes() -> list[dict]:
    """Flatten @graph containers so a node is findable however it is nested."""
    nodes: list[dict] = []
    for block in _ld_blocks():
        graph = block.get("@graph")
        nodes.extend(graph if isinstance(graph, list) else [block])
    return nodes


def test_structured_data_parses():
    """This app states its identity in ONE @graph block rather than the
    template's several top-level blocks — same nodes, one parse."""
    assert _ld_blocks(), "no JSON-LD in templates/index.html"
    types = {node.get("@type") for node in _ld_nodes()}
    # WebSite carries the site identity, Organization the publisher, and
    # SoftwareSourceCode the documented package — this app is a component
    # LIBRARY, so the source-code node is the honest type for it.
    for required in ("WebSite", "Organization", "SoftwareSourceCode"):
        assert required in types, (
            f"no {required} node in the JSON-LD — found {sorted(t for t in types if t)}"
        )


def test_the_declared_version_is_the_token_not_a_literal():
    """The version cannot drift, because it is never written twice.

    The template hard-codes softwareVersion and pins it against constants.
    This app declares the literal token ``__VERSION__`` instead and run.py
    substitutes APP_VERSION (read from package.json) at boot — so the two
    CANNOT disagree. What has to be pinned is that nobody helpfully replaces
    the token with a number, which would reintroduce the drift the token
    exists to prevent.
    """
    versions = [
        node["version"] for node in _ld_nodes() if "version" in node
    ] + [
        node["softwareVersion"] for node in _ld_nodes() if "softwareVersion" in node
    ]
    assert versions, "no version declared in the JSON-LD"
    assert set(versions) == {"__VERSION__"}, (
        f"index.html hard-codes a version {versions} instead of the "
        "__VERSION__ token run.py substitutes — it will drift from "
        f"package.json (currently {constants.APP_VERSION})"
    )


def test_run_py_substitutes_the_version_token(app_module):
    """The other half: a token nobody replaces ships to production raw."""
    assert "__VERSION__" not in app_module._index_string, (
        "run.py no longer substitutes __VERSION__ — the literal token is "
        "being served to crawlers as this software's version"
    )
    assert constants.APP_VERSION in app_module._index_string


# ---------------------------------------------------------------------------
# The title element
#
# dash-improve-my-llms locates it with `re.compile(r"<title>.*?</title>",
# DOTALL | IGNORECASE)` and rewrites the first match. Two ways that goes
# wrong, both silent:
#
#   - No element at all: nothing to anchor on, so no page gets a title.
#   - The tag name written in angle brackets inside a nearby comment: the
#     match starts THERE and runs to the next closing tag, so every line in
#     between is replaced by the rewritten title and disappears from the
#     served page. With rewriting on it still looks correct.
# ---------------------------------------------------------------------------

TITLE_RE = re.compile(r"<title>.*?</title>", re.S | re.I)


def test_the_template_title_is_the_site_brand():
    """This fork ships a real <title> rather than the `{%title%}` placeholder.

    Deliberate, and pinned in tests/test_site_identity.py too: the SPA shell
    is one document for every route, so its title is the SSR fallback and the
    network standard says that fallback must be the BRAND. Per-page titles
    still reach both audiences — the renderer sets document.title from
    `register_page(title=)` on navigation, and crawlers are served
    dash-improve-my-llms' prerendered document, which carries the per-page
    title from `register_page_metadata(title=)`.

    A generic or empty title here is the failure this pins: it is what
    `resolve_site_title` would fall back to, on every surface at once.
    """
    assert f"<title>{constants.SITE_BRAND}</title>" in INDEX_HTML


def test_only_one_title_match_and_it_is_the_element():
    """Guards the comment trap in both directions."""
    matches = TITLE_RE.findall(INDEX_HTML)
    assert matches == [f"<title>{constants.SITE_BRAND}</title>"], (
        "the title regex matched something other than the element itself — "
        "check for the tag name written in angle brackets inside a comment"
    )


def test_no_title_tag_spelled_out_in_comments():
    for comment in re.findall(r"<!--.*?-->", INDEX_HTML, re.S):
        assert "<title" not in comment.lower(), (
            "a comment spells the title tag in angle brackets; the package's "
            "regex would start matching there and swallow the lines that follow"
        )


def test_app_title_is_set(app_module):
    """`{%title%}` resolves to app.title in the served HTML. Unset, Dash's
    default is the bare string "Dash" on every page."""
    assert app_module.app.title == constants.SITE_BRAND
    assert constants.SITE_BRAND != "Dash"


def test_no_dead_llm_endpoints_advertised():
    """/page.json and /architecture.txt were removed in dash-improve-my-llms
    2.0. Advertising them points agents at two 404s."""
    for dead in ("/page.json", "/architecture.txt", "/llms.toon"):
        assert dead not in INDEX_HTML_LIVE, (
            f"{dead} is no longer served but is still advertised"
        )


# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------


def test_the_installed_package_meets_the_floor(app_module):
    """Fail with the reason, not with thirty downstream symptoms.

    An IDE run configuration pointing at another project's virtualenv starts
    this app quite happily against whatever versions that environment holds.
    On dash-improve-my-llms 2.0.0 there is no `llms_viewer.py` at all, so
    `/<page>/llms.txt` serves plain Markdown to everyone and the negotiation
    tests below fail in a way that reads like a bug in the app. It isn't; it's
    the interpreter.
    """
    import sys

    import dash_improve_my_llms as pkg

    installed = tuple(int(p) for p in pkg.__version__.split(".")[:3] if p.isdigit())
    assert installed >= app_module.LLMS_PKG_FLOOR, (
        f"dash-improve-my-llms {pkg.__version__} is below the "
        f"{app_module.LLMS_PKG_FLOOR} floor. Running from {sys.executable} — "
        "if that is not this project's .venv, that is the whole problem."
    )


# ---------------------------------------------------------------------------
# Constructor arguments
# ---------------------------------------------------------------------------


def test_mcp_kwargs_are_omitted_when_mcp_is_off(app_module):
    """Dash raises TypeError on unknown constructor keywords.

    `enable_mcp` landed in Dash 4.3, so naming it unconditionally made the app
    refuse to boot on 4.2 with `Dash() got an unexpected keyword argument
    'enable_mcp'` — an error that says nothing about MCP, over a feature that
    is off by default.
    """
    assert app_module.MCP_KWARGS == {}, (
        "MCP is off by default, so no MCP keyword should reach the Dash "
        "constructor at all"
    )


# ---------------------------------------------------------------------------
# Repo hygiene
# ---------------------------------------------------------------------------


# Live links to domains that have been retired. Matching the URL rather than
# the bare hostname on purpose: the changelog has to name plotly.pro in the
# entry that records its removal, and that mention is not a broken link.
RETIRED_LINKS = re.compile(r"https?://(?:www\.)?(plotly\.pro)")

SKIP_DIRS = {".venv", "node_modules", ".git", "__pycache__", ".claude", "vendor", ".idea"}


def test_no_links_to_retired_domains():
    """plotly.pro was retired in favour of 2plot.ai."""
    offenders = []
    for path in REPO_ROOT.glob("**/*"):
        if not path.is_file() or path.suffix not in {".py", ".md", ".html", ".css", ".yml"}:
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        for match in RETIRED_LINKS.finditer(path.read_text(errors="ignore")):
            offenders.append(f"{path.relative_to(REPO_ROOT)} -> {match.group(1)}")
    assert offenders == [], f"links to retired domains: {offenders}"


def test_noscript_block_carries_no_h1():
    """Crawlers run no JavaScript and PARSE noscript content — an h1 there
    becomes a second site-wide h1 on every page, competing with each page's
    own. This site served two h1s to every generic client until the
    every-page structure pin in tests/test_pages.py caught it (2026-08-23).
    HTML comments are stripped first so the explanatory comment naming the
    tag can't trip the check — the marker-in-comment lesson applied to our
    own guard."""
    import re
    from pathlib import Path

    html = (Path(__file__).resolve().parent.parent / "templates" / "index.html").read_text()
    html = re.sub(r"<!--.*?-->", "", html, flags=re.S)
    noscript = re.search(r"<noscript>(.*?)</noscript>", html, re.S)
    assert noscript, "index.html lost its noscript block?"
    assert "<h1" not in noscript.group(1), (
        "the noscript block carries an <h1> — every page now has a second "
        "site-wide h1 in the crawler's parse; use h2/h3 in this block"
    )
