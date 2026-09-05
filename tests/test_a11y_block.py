"""The a11y / agentic block (1.6.44 item 6) — what this fork fixed and recorded.

Five sub-items, and this fork's answers differ from the template's in two
places, both measured rather than assumed:

  (a) FIXED   the Other Apps menu was `trigger="hover"` here too — pointer-only
  (b) FIXED   prose links carried no underline; the markdown renderer sets
              `underline=False` explicitly, so the fix has to overrule it
  (c) FIXED   ActionIcon size="lg" is 34px; the header and footer are made of
              them and the phone-width media query now floors them at 44px
  (d) RECORDED — see DIVERGENCES.md; not reproducible from this sandbox
  (e) RECORDED — assets are deliberately unminified
  (f) NOT APPLICABLE HERE, and the count is printed rather than implied: this
      repo's docs contain ZERO markdown images. A test that asserted anything
      about content images would sweep nothing and go green. What IS portable
      is the pin on WHY the attributes the item asked for cannot ship.
  (g) FIXED   /assets/ had no Cache-Control at all on the wire

SOURCE DETECTS IN THIS FILE STRIP COMMENTS FIRST (item 13's rule, which the
template hit one item early): a good comment explains the ABSENCE of the thing
a detect hunts, so a raw grep matches the explanation and reports the defect
it documents the absence of.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent


def code(path: Path) -> str:
    """`path`'s source with comments and docstrings removed."""
    text = path.read_text()
    tree = ast.parse(text)
    docstrings = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                             ast.AsyncFunctionDef)):
            doc = ast.get_docstring(node, clean=False)
            if doc:
                docstrings.add(doc)
    lines = [re.sub(r"#.*$", "", ln) for ln in text.splitlines()]
    stripped = "\n".join(lines)
    for doc in docstrings:
        stripped = stripped.replace(doc, "")
    return stripped


# ------------------------------------------------- (a) the keyboard path --


def test_the_other_apps_menu_is_not_pointer_only():
    """`trigger="hover"` makes the only listing of the sibling network in
    this app unreachable from a keyboard: focus the button, press Enter,
    nothing happens."""
    src = code(REPO / "components" / "header.py")
    assert 'trigger="click-hover"' in src, (
        "the Other Apps menu is not keyboard-openable"
    )
    assert 'trigger="hover"' not in src, (
        "a hover-only trigger came back"
    )


def test_the_menu_target_is_a_real_button(app_module):
    """The defect the item PREDICTED is not the one that was here.

    It expected a div with aria-haspopup. The target is a real dmc.Button,
    so the aria plumbing was never the problem — the trigger was. Pinned so
    nobody "fixes" a target that is already correct.
    """
    import dash_mantine_components as dmc

    from components.header import create_other_apps_menu

    menu = create_other_apps_menu()
    target = menu.children[0]
    inner = getattr(target, "children", target)
    assert isinstance(inner, dmc.Button), type(inner)


# --------------------------------------------------- (b) prose underlines --


def test_prose_links_are_underlined_not_colour_only():
    css = (REPO / "assets" / "main.css").read_text()
    block = re.search(r"#main-content a\.m2d-link\s*\{([^}]*)\}", css)
    assert block, "no prose-link rule scoped to #main-content a.m2d-link"
    assert "underline" in block.group(1)


def test_the_class_the_rule_targets_is_the_one_the_renderer_emits():
    """The selector is held against markdown2dash, not against a memory of it.

    If the renderer ever stops decorating links with @class_name, or
    create_class_name changes shape, this rule silently stops applying and
    the site goes back to colour-only links with nothing to say so.
    """
    from markdown2dash.src.utils import create_class_name

    assert create_class_name("link") == "m2d-link"

    css = (REPO / "assets" / "main.css").read_text()
    assert f"a.{create_class_name('link')}" in css


def test_the_rule_can_beat_the_renderers_own_underline_false():
    """The renderer hardcodes `underline=False` on every prose Anchor.

    Without `!important` this rule loses to the component's own styling and
    the fix is inert — green in the stylesheet, absent on the page.
    """
    import inspect

    from markdown2dash.src.renderer import DashRenderer

    assert "underline=False" in "".join(
        inspect.getsource(DashRenderer.link).split()
    ).replace(" ", ""), "the renderer no longer forces underline off — re-check the !important"

    css = (REPO / "assets" / "main.css").read_text()
    block = re.search(r"#main-content a\.m2d-link\s*\{([^}]*)\}", css)
    assert "!important" in block.group(1)


# ------------------------------------------------------ (c) touch targets --


def test_icon_controls_reach_44px_at_phone_width():
    """A Mantine ActionIcon size="lg" is 34px, and the header and footer are
    made of them."""
    css = (REPO / "assets" / "main.css").read_text()
    phone = css.split("@media only screen and (max-width: 750px) {", 1)[-1]
    phone = phone.split("\n}\n", 1)[0]
    assert "min-width: 44px" in phone and "min-height: 44px" in phone, (
        "no 44px floor inside the phone-width media query"
    )


def test_the_repo_really_uses_the_icons_this_rule_floors():
    """Non-vacuity: the rule is pointless if nothing renders an ActionIcon."""
    users = [p for p in (REPO / "components").glob("*.py")
             if "ActionIcon" in p.read_text()]
    assert len(users) >= 2, (
        f"only {len(users)} component files use ActionIcon — check the rule "
        "still has a subject"
    )


# --------------------------------------- (f) the attributes that cannot ship --


def test_this_repos_docs_contain_no_markdown_images():
    """The corpus assertion, made explicitly rather than left implied.

    Item 6f asks content images to reserve their box. This repo's docs render
    ZERO markdown images, so there is nothing to size and any test about them
    would sweep nothing and pass. If a doc ever adds one, this goes red and
    6f becomes real work — which is the only honest way to record a
    not-applicable.
    """
    docs = list((REPO / "docs").rglob("*.md"))
    assert docs, "no docs at all — this sweep would be vacuous"
    images = [(p, ln) for p in docs
              for ln in p.read_text().splitlines() if "![" in ln]
    assert images == [], (
        f"{len(images)} markdown image(s) appeared across {len(docs)} docs; "
        "item 6f (width/height on content images) now applies to this repo"
    )


@pytest.mark.parametrize("attribute", ["loading", "decoding"])
def test_dash_still_refuses_the_attributes_item_6f_asked_for(attribute):
    """`loading="lazy"` / `decoding="async"` CANNOT ship — measured, not read.

    Neither is a prop of this Dash's `html.Img`, and Dash RAISES rather than
    passing an unknown attribute through, so shipping them would not be a
    warning — it would be a collection error per import site. The day Dash
    learns them this test goes red and says so, which is the point of pinning
    a reason rather than an omission.
    """
    from dash import html

    with pytest.raises(TypeError):
        html.Img(src="/x.png", **{attribute: "lazy"})


def test_width_and_height_are_the_attributes_that_do_work():
    """The half of 6f that is shippable, so the pin above is not just a
    complaint."""
    from dash import html

    img = html.Img(src="/x.png", width=100, height=50)
    assert (img.width, img.height) == (100, 50)


# ---------------------------------------------- (g) the asset cache policy --


def test_assets_get_a_lifetime_and_documents_do_not():
    from lib.static_cache import ASSET_CACHE_CONTROL, cache_control_for

    assert cache_control_for("/assets/main.css") == ASSET_CACHE_CONTROL
    assert "max-age=" in ASSET_CACHE_CONTROL
    for document in ("/", "/quickstart", "/llms.txt", "/healthz",
                     "/admin/traffic", "/api", "/_dash-component-suites/x.js"):
        assert cache_control_for(document) is None, (
            f"{document} was given a cache lifetime — a stale document is a "
            "bug report nobody can reproduce"
        )


def test_both_lanes_apply_the_same_policy():
    """Flask and FastAPI cannot drift into different lifetimes for one file.

    Production here is FastAPI and CI's gunicorn boot is Flask, so a policy
    written on one lane only would be verified on the lane that does not
    ship.
    """
    flask_lane = code(REPO / "run.py")
    asgi_lane = code(REPO / "lib" / "asgi_middleware.py")
    assert "cache_control_for" in flask_lane, "the Flask lane sets no policy"
    assert "cache_control_for" in asgi_lane, "the ASGI lane sets no policy"
    assert "StaticCacheMiddleware" in code(REPO / "lib" / "asgi_middleware.py")


def test_the_header_reaches_the_wire_on_the_lane_under_test(client):
    """The assertion that matters: not that the policy exists, that it lands.

    Served through whichever backend this leg runs, because the two lanes
    apply it through completely different machinery — an `after_request` hook
    and an ASGI middleware.
    """
    from lib.static_cache import ASSET_CACHE_CONTROL

    response = client.get("/assets/main.css")
    assert response.status == 200, (
        f"/assets/main.css answered {response.status} — the assertion below "
        "would be vacuous"
    )
    assert response.header("cache-control") == ASSET_CACHE_CONTROL


def test_a_document_keeps_its_lack_of_a_lifetime(client):
    """The other direction, so the test above cannot pass by blanket-setting
    the header on everything."""
    response = client.get("/healthz")
    assert response.status == 200
    assert "max-age=3600" not in response.header("cache-control")
