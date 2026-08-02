"""Link-unfurl (social card) HTML for scrapers.

Why this exists: ``add_llms_routes`` classifies Twitter/Facebook/Discord/Slack
crawlers as bots and hands them the package's prerendered SEO HTML, which has no
``og:image`` — so every shared link unfurled as a bare text row. These shims
serve those scrapers the site's own ``templates/index.html`` head instead.

Scrapers never run JavaScript, so the Dash placeholders are stripped and the
per-page ``og``/``twitter`` block that Dash would have emitted at ``{%metas%}``
is rendered here from ``dash.page_registry`` for the requested path. That keeps
the card per-page (right title, right description, right URL) rather than
describing the site on every link.
"""
from __future__ import annotations

# Scrapers only ever GET/HEAD. Matched case-insensitively against the UA.
SOCIAL_UAS = (
    "twitterbot", "facebookexternalhit", "facebookcatalog", "discordbot",
    "slackbot", "slack-imgproxy", "linkedinbot", "whatsapp", "telegrambot",
    "pinterest", "redditbot", "skypeuripreview", "embedly", "iframely",
)

# Placeholders Dash would fill. Scrapers read <head> meta only, so everything
# except {%metas%} (replaced with the card block) is simply dropped.
_DASH_PLACEHOLDERS = (
    "{%favicon%}", "{%css%}", "{%app_entry%}", "{%config%}", "{%scripts%}",
    "{%renderer%}", "{%title%}",
)

# Dimensions/type/alt come from lib.constants' OG block at render time so the
# scraper card can never disagree with what the SPA shell declares. 1200x630 →
# twitter:card=summary_large_image (the wide slot, no letterboxing).
_CARD = """
    <meta name="description" content="{description}">
    <meta property="og:type" content="website">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <meta property="og:image" content="{image}">
    <meta property="og:image:secure_url" content="{image}">
    <meta property="og:image:type" content="{image_type}">
    <meta property="og:image:width" content="{image_width}">
    <meta property="og:image:height" content="{image_height}">
    <meta property="og:image:alt" content="{image_alt}">
    <meta property="twitter:card" content="summary_large_image">
    <meta property="twitter:title" content="{title}">
    <meta property="twitter:description" content="{description}">
    <meta property="twitter:image" content="{image}">
    <meta property="twitter:image:alt" content="{image_alt}">
"""


def is_social_card(ua: str | None, path: str, method: str = "GET") -> bool:
    """True when this request is a social-card scraper fetching a page.

    Method-aware on purpose: a spoofed-UA POST must fall through to the real
    handlers (e.g. the Svix-verified ``/webhooks/clerk``).
    """
    ua = (ua or "").lower()
    return (
        method in ("GET", "HEAD")
        and any(bot in ua for bot in SOCIAL_UAS)
        and not path.startswith("/assets")
        and not path.startswith("/_")
        and not path.startswith("/webhooks")
    )


def _escape(text: str) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


class SocialCardRenderer:
    """Render the scraper-facing ``<head>`` for a given request path."""

    def __init__(self, template: str, base_url: str, image_url: str,
                 fallback_title: str, fallback_description: str) -> None:
        self._base_url = base_url.rstrip("/")
        self._image_url = image_url
        self._fallback = (fallback_title, fallback_description)

        html = template
        for placeholder in _DASH_PLACEHOLDERS:
            html = html.replace(placeholder, "")
        self._template = html  # still holds {%metas%} and __PAGE_URL__

    def _page_meta(self, path: str) -> tuple[str, str]:
        try:
            import dash

            for entry in (dash.page_registry or {}).values():
                if entry.get("path") == path:
                    title = entry.get("title") or self._fallback[0]
                    description = entry.get("description") or self._fallback[1]
                    return (
                        title() if callable(title) else title,
                        description() if callable(description) else description,
                    )
        except Exception:
            pass
        return self._fallback

    def __call__(self, path: str) -> str:
        from lib.constants import (
            OG_IMAGE_ALT, OG_IMAGE_HEIGHT, OG_IMAGE_TYPE, OG_IMAGE_WIDTH,
        )

        path = "/" + (path or "/").strip("/")
        title, description = self._page_meta(path)
        card = _CARD.format(
            title=_escape(title),
            description=_escape(description),
            image=self._image_url,
            image_type=OG_IMAGE_TYPE,
            image_width=OG_IMAGE_WIDTH,
            image_height=OG_IMAGE_HEIGHT,
            image_alt=_escape(OG_IMAGE_ALT),
        )
        page_url = self._base_url + (path if path != "/" else "/")
        return (
            self._template
            .replace("{%metas%}", card)
            .replace("__PAGE_URL__", page_url)
        )
