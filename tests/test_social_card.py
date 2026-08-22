"""The social card and the installable-app surfaces.

NETWORK FILE: adapted from dash-email (itself from dash-documentation-
boilerplate 1.2.4). It changes only where this site legitimately differs —
see the theme-colour and origin-token tests.

Both things tested here fail silently and fail OUTSIDE the app, which is why
they need tests rather than a look at the page — nobody sees their own unfurls,
and no browser explains why it declined to offer an install.

The two failures the network has actually shipped, measured live in 2026:

1. **TWO empty og:image tags on every page.** No `register_page` call passed
   `image_url=`, so Dash emitted `og:image=""` (dash/_pages.py) — and an EMPTY
   tag unfurls worse than a missing one, because scrapers treat the empty value
   as the declared image and render a blank card. It was doubled because the
   template spelled the metas placeholder out inside an HTML comment, and Dash
   substitutes placeholders by plain string replacement over the whole
   template, comments included.

2. **A manifest naming another site** — the string an installed icon would
   carry on somebody's home screen forever.

Note where each tag comes from, because it decides which file to open when one
of these fails: `og:image`, `twitter:image` and the `twitter:*` set are DASH's
(per page, from `register_page`); `og:site_name`, `og:url`, the `og:image:*`
auxiliaries and the icon links are `templates/index.html`'s.
dash-improve-my-llms adds a third set, but only on the prerender path — for
actual social scrapers `lib/social_cards.py` renders the template's head with
a per-page card, which is a separate surface `scripts/network_smoke.py`
covers. That is why deleting the template would silently kill every unfurl.
"""

from __future__ import annotations

import json
import re

from conftest import REPO_ROOT
from lib.constants import (
    OG_IMAGE_ALT,
    OG_IMAGE_HEIGHT,
    OG_IMAGE_TYPE,
    OG_IMAGE_URL,
    OG_IMAGE_WIDTH,
    SITE_BRAND,
)

MANIFEST = REPO_ROOT / "assets" / "favicon" / "site.webmanifest"


def _visible(html: str) -> str:
    """The document with HTML comments removed.

    The template documents itself extensively, and a regex cannot tell a
    commented-out example tag from a live one.
    """
    return re.sub(r"<!--.*?-->", "", html, flags=re.S)


def _meta(html: str, value: str) -> list[str]:
    """Every `content` for a property/name — a list, so duplicates show up.

    Tags carrying `data-dimll-prerender` are excluded. dash-improve-my-llms
    injects its own description and OpenGraph block on the prerender path, and
    marks each one precisely so it can be told apart. Counting those here would
    make this test fail on a package behaviour nothing in this repo controls,
    and it would hide what the test is actually for: duplication between
    `templates/index.html` and the tags Dash generates from `register_page`.
    """
    pattern = (
        rf'<meta[^>]*(?:property|name)="{re.escape(value)}"[^>]*content="([^"]*)"'
        rf'|<meta[^>]*content="([^"]*)"[^>]*(?:property|name)="{re.escape(value)}"'
    )
    body = re.sub(r'<meta[^>]*data-dimll-prerender[^>]*>', "", _visible(html))
    return ["".join(m) for m in re.findall(pattern, body)]


# ------------------------------------------------------------- the og image --


def test_the_og_image_is_never_empty(client, page_paths):
    for path in page_paths[:8]:
        images = _meta(client.get(path).text, "og:image")
        assert images, f"{path} declares no og:image at all"
        assert all(src.strip() for src in images), (
            f"{path} serves an EMPTY og:image {images} — the card renders blank"
        )


def test_the_image_is_declared_exactly_once(client, page_paths):
    """The duplicate-tag regression, in both of the ways it has happened."""
    for path in page_paths[:8]:
        html = client.get(path).text
        assert len(_meta(html, "og:image")) == 1, (
            f"{path} has {_meta(html, 'og:image')} — a scraper picks one, and "
            "it will not be the one you meant"
        )
        assert len(_meta(html, "twitter:image")) == 1


def test_no_dash_placeholder_is_named_inside_a_comment():
    """The bug behind the doubled tags, pinned at its source.

    Dash resolves `{%…%}` by plain string replacement over the whole template.
    A placeholder named in a comment is therefore not documentation — it is a
    second, hidden copy of whatever that placeholder emits. The template's
    comments deliberately say "the metas placeholder" in words rather than
    spelling it; this keeps it that way.
    """
    template = (REPO_ROOT / "templates" / "index.html").read_text()
    for comment in re.findall(r"<!--.*?-->", template, flags=re.S):
        found = re.findall(r"\{%\s*\w+\s*%\}", comment)
        assert not found, (
            f"a comment in templates/index.html names {found} — Dash will "
            "substitute it there and emit the block twice"
        )


def test_the_image_is_not_an_svg(client):
    """SVG is rejected by Facebook, Twitter/X, LinkedIn and Slack alike.

    Dash's asset inference reaches `logo.<ext>`, so this is one missing
    `image_url=` and one added `assets/logo.svg` away from happening — and
    this repo DOES ship an `assets/dms_logo.svg`.
    """
    for prop in ("og:image", "twitter:image"):
        for src in _meta(client.get("/").text, prop):
            assert not src.lower().endswith(".svg"), f"{prop} is an SVG: {src}"


def test_the_image_is_absolute_and_matches_the_constant(client):
    for prop in ("og:image", "twitter:image"):
        values = _meta(client.get("/").text, prop)
        assert values, f"no {prop} on the home page"
        for src in values:
            assert src.startswith("http"), f"{prop}={src!r} is not absolute"
            assert src == OG_IMAGE_URL


def test_the_image_is_hosted_off_the_app():
    """The card must be on the CDN, not served by this app.

    Not a style rule. A card the app serves is fetched by the scraper at unfurl
    time; on a cold free-tier container that request lands mid-wake and times
    out, the preview renders blank ONCE, and the platform caches the miss — so
    the first person to share the link poisons it for everyone.

    That the URL RESOLVES is deliberately not checked here. It is off-host now,
    and reaching a third party would make this suite depend on Cloudflare being
    up (the same reason conftest disables the geo lookup).
    `scripts/network_smoke.py` and `scripts/smoke_live.py` fetch the real file
    after every deploy and read its IHDR chunk — which also catches the CDN
    object being replaced with something a different shape, something no
    offline test can see.
    """
    assert OG_IMAGE_URL.startswith("https://cdn.2plot.ai/github_assets/"), (
        f"{OG_IMAGE_URL} is not on the network CDN"
    )
    assert "/assets/" not in OG_IMAGE_URL, "the app is serving its own card again"


def test_the_card_url_names_this_domain():
    """One card per host. A satellite pointing at another's card is a real
    mistake and an easy one — the CDN path is a hand-typed filename."""
    assert OG_IMAGE_URL.endswith("/muischeduler.2plot.dev.png")


def test_the_auxiliary_image_tags_match_the_constants(client):
    """index.html hard-codes the dimensions; lib/constants.py is the source.

    A declared width/height that disagrees with the file is worse than
    declaring none — the platform reserves the wrong box and crops.
    """
    html = client.get("/").text
    assert _meta(html, "og:image:width") == [str(OG_IMAGE_WIDTH)]
    assert _meta(html, "og:image:height") == [str(OG_IMAGE_HEIGHT)]
    assert _meta(html, "og:image:alt") == [OG_IMAGE_ALT]
    assert _meta(html, "og:image:type") == [OG_IMAGE_TYPE]
    assert _meta(html, "og:image:secure_url") == [OG_IMAGE_URL], (
        "secure_url must be the same file as og:image, not a stale copy"
    )


def test_the_declared_ratio_suits_a_large_image_card():
    """`summary_large_image` wants roughly 1.91:1."""
    ratio = OG_IMAGE_WIDTH / OG_IMAGE_HEIGHT
    assert 1.7 <= ratio <= 2.05, f"{OG_IMAGE_WIDTH}x{OG_IMAGE_HEIGHT} is {ratio:.2f}:1"


def test_the_rendered_card_on_disk_is_the_declared_shape():
    """If `scripts/make_social_card.py` has been run, its output must agree.

    The build directory is gitignored, so this skips on a fresh checkout — it
    is here for the machine that generated the card and is about to upload it,
    which is the moment the dimensions can still be fixed cheaply.
    """
    import pytest

    card = REPO_ROOT / "build" / "social-cards" / "muischeduler.2plot.dev.png"
    if not card.exists():
        pytest.skip("no rendered card in build/social-cards (gitignored)")

    raw = card.read_bytes()
    assert raw[1:4] == b"PNG"
    assert int.from_bytes(raw[16:20], "big") == OG_IMAGE_WIDTH
    assert int.from_bytes(raw[20:24], "big") == OG_IMAGE_HEIGHT


def _meta_attr(html: str, attr: str, value: str) -> list[str]:
    """`content`s for a meta tag matched on ONE attribute form specifically.

    `_meta` deliberately conflates `property=` and `name=`; twitter:card is
    the one tag where the difference decides whether anything renders, so it
    gets its own matcher.
    """
    pattern = (
        rf'<meta[^>]*{attr}="{re.escape(value)}"[^>]*content="([^"]*)"'
        rf'|<meta[^>]*content="([^"]*)"[^>]*{attr}="{re.escape(value)}"'
    )
    return [a or b for a, b in re.findall(pattern, html)]


def test_the_twitter_card_is_a_large_image(client):
    """Declared exactly once in the form Twitter/X actually parses.

    Dash emits `twitter:card` with `property=`, which is correct for Open
    Graph and INVISIBLE to Twitter's parser — measured across the network
    2026-08-14, when no page declared a card type any scraper could see.
    templates/index.html therefore adds the `name=` form, and the two
    coexisting is DELIBERATE: Twitter reads the name= one, everything else
    ignores it. What must never happen is a second copy of EITHER form, or
    the two disagreeing about the card type.
    """
    html = client.get("/").text
    by_name = _meta_attr(html, "name", "twitter:card")
    by_property = _meta_attr(html, "property", "twitter:card")
    assert by_name == ["summary_large_image"], (
        'expected exactly one name="twitter:card" — the only form Twitter/X '
        f"reads — found {by_name}"
    )
    assert by_property in ([], ["summary_large_image"]), (
        f"Dash's property= copy disagrees with the declared card type: {by_property}"
    )


def test_no_meta_tag_dash_emits_is_also_declared_statically(client):
    """The rule the OG and Twitter blocks in index.html are built on.

    Dash emits all of these per page. A static copy in the template makes two
    of each, and the static one describes the SITE where Dash's describes the
    PAGE — so the duplicate is both redundant and the less accurate of the two.
    """
    html = client.get("/").text
    # twitter:card is the deliberate exception, with its own test above:
    # Dash's property= form is invisible to Twitter/X's parser, so
    # templates/index.html declares the name= form alongside it ON PURPOSE.
    for tag in ("description", "og:type", "og:title", "og:description",
                "og:image", "twitter:url", "twitter:title",
                "twitter:description", "twitter:image"):
        found = _meta(html, tag)
        assert len(found) <= 1, f"{tag} is declared {len(found)} times: {found}"


def test_the_tags_dash_omits_are_declared_here(client):
    """The other half of the rule — do not delete these thinking Dash covers them."""
    html = client.get("/").text
    for tag in ("og:site_name", "og:url", "og:image:alt", "twitter:image:alt",
                "og:image:secure_url", "og:image:type",
                "og:image:width", "og:image:height"):
        assert _meta(html, tag), f"{tag} is missing and Dash does not emit it"


def test_og_site_name_is_the_brand(client):
    assert _meta(client.get("/").text, "og:site_name") == [SITE_BRAND]


# ------------------------------------------------------------- the manifest --


def test_the_manifest_is_linked_and_served(client):
    html = _visible(client.get("/").text)
    assert 'rel="manifest"' in html, "no manifest link — no install prompt"
    match = re.search(r'<link[^>]+rel="manifest"[^>]+href="([^"]+)"', html)
    assert match
    assert client.get(match.group(1)).ok, "the manifest link 404s"


def test_the_manifest_describes_THIS_site():
    """The string an installed icon carries on someone's home screen forever.

    On another satellite this file shipped still naming the hub it was copied
    from — an installed app takes its label from `short_name`, so a wrong
    string here becomes a permanent icon on someone's phone.
    """
    manifest = json.loads(MANIFEST.read_text())
    assert manifest["name"] == SITE_BRAND
    assert "2plot.dev" not in manifest["short_name"]
    assert "2plot.dev" not in manifest["description"]


def test_the_manifest_is_installable():
    manifest = json.loads(MANIFEST.read_text())
    assert manifest["name"].strip(), "empty name — no browser will offer install"
    assert manifest["short_name"].strip(), "empty short_name"
    assert manifest["start_url"] == "/"
    assert manifest["display"] == "standalone"


def test_every_manifest_icon_resolves(client):
    manifest = json.loads(MANIFEST.read_text())
    icons = manifest.get("icons") or []
    assert icons, "the manifest declares no icons"
    for icon in icons:
        assert client.get(icon["src"]).ok, f"manifest icon {icon['src']} 404s"
    assert any(i.get("sizes") == "192x192" for i in icons)
    assert any(i.get("sizes") == "512x512" for i in icons)


def test_the_apple_touch_icon_is_declared_and_resolves(client):
    """iOS ignores the manifest and uses this for Add to Home Screen."""
    html = _visible(client.get("/").text)
    match = re.search(r'<link[^>]*rel="apple-touch-icon"[^>]*href="([^"]+)"', html)
    assert match, "no apple-touch-icon link"
    assert client.get(match.group(1)).ok, f"{match.group(1)} does not resolve"


def test_the_theme_colour_agrees_with_the_manifest(client):
    """A mismatch is one colour in the browser chrome, another on the splash.

    THIS SITE DIVERGES FROM dash-email, deliberately: it declares ONE
    theme-colour — the #3399ff brand accent — and the manifest carries the
    same value, while `background_color` stays white for the install splash.
    (dash-email declares two media-scoped colours and pins the manifest to the
    dark one; this appshell paints its own surfaces, so a single accent is the
    honest declaration here.) The assertion is membership so a future second,
    media-scoped declaration does not break it.
    """
    manifest = json.loads(MANIFEST.read_text())
    declared = [c.lower() for c in _meta(client.get("/").text, "theme-color")]
    assert declared, "no theme-color"
    assert manifest["theme_color"].lower() in declared, (
        f"manifest theme_color {manifest['theme_color']} matches none of the "
        f"declared theme-colours {declared}"
    )
    assert manifest.get("background_color", "").strip(), (
        "no background_color — the install splash paints black"
    )


def test_every_asset_the_template_references_resolves(client):
    """The half-landed-commit guard.

    The boilerplate once shipped a template pointing at `/assets/favicon/…`
    while the icon set sat UNTRACKED in git. The deploy builds from git, so
    production 404'd the manifest, the apple-touch-icon and every PNG icon —
    the whole installable-app surface — while every local boot looked perfect
    because the files were on disk. `git status` was the only place it showed.
    """
    html = _visible(client.get("/").text)
    referenced = sorted(set(re.findall(r'(?:href|content|src)="(/assets/[^"]+)"', html)))
    assert referenced, "no /assets/ references found — did the template change?"

    missing = [ref for ref in referenced if not client.get(ref).ok]
    assert missing == [], (
        f"templates/index.html references assets that do not resolve: {missing}. "
        "If they exist on disk, they are untracked — the deploy builds from git."
    )


def test_the_index_template_is_still_wired_in(app_module):
    """`templates/index.html` looks removable and is not.

    dash-improve-my-llms appears to cover OG, but its injection runs only on
    the prerender path, which social scrapers do not take. Deleting the
    template kills every unfurl, the icons and the manifest at once.
    """
    index = (REPO_ROOT / "templates" / "index.html").read_text()
    for placeholder in ("{%metas%}", "{%favicon%}", "{%css%}", "{%app_entry%}",
                        "{%config%}", "{%scripts%}", "{%renderer%}"):
        assert placeholder in index, f"{placeholder} missing from the template"
    assert app_module.app.index_string.startswith("<!DOCTYPE html>")


def test_the_template_takes_its_origin_from_the_constants(app_module, client):
    """No second copy of the canonical origin.

    The template is a static file and cannot import lib/constants, so run.py
    substitutes `__BASE_URL__` and `__VERSION__` at startup; `__PAGE_URL__` is
    deliberately left in `index_string` — the index hook fills it with the
    REQUESTED page's canonical URL on every response. If a hand-typed origin
    ever appears in the template, half the site can end up advertising one
    hostname and half another — and nothing looks broken.
    """
    from lib.constants import BASE_URL

    raw = (REPO_ROOT / "templates" / "index.html").read_text()
    for token in ("__BASE_URL__", "__PAGE_URL__", "__VERSION__"):
        assert token in raw, f"the template no longer uses the {token} token"

    index_string = app_module.app.index_string
    assert "__BASE_URL__" not in index_string, "run.py did not substitute the origin token"
    assert "__VERSION__" not in index_string, "run.py did not substitute the version token"
    assert BASE_URL in index_string

    # The per-request half: a served page must have no token left in it.
    assert "__PAGE_URL__" not in client.get("/").text, (
        "the index hook did not fill __PAGE_URL__ — canonical and og:url are broken"
    )
