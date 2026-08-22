import os as _os

# ---------------------------------------------------------------------------
# Site identity — one string, every surface (2plot network standard)
# ---------------------------------------------------------------------------
# The brand reaches: Dash(title=SITE_BRAND), register_page_metadata(path="/",
# name=SITE_BRAND) (→ the /llms.txt H1 and the viewer brand chip via
# dash-improve-my-llms ≥2.3.4 resolve_site_title), templates/index.html's
# <title>, and the home page prose. tests/test_site_identity.py pins them all
# to this constant — the failure mode is silent (a viewer chip reading a bare
# "Dash") so only a test catches it.
#
# Library rule: the PACKAGE NAME comes first in the brand (people install it);
# "Pip Install Python" is the byline, never part of the brand.
SITE_BRAND = "dash-mui-scheduler — MUI X scheduling for Dash"

# ~155 characters, deliberately. This is the meta description, and Google
# truncates the snippet around 155-160 — the previous 284-character version
# lost its whole second half (every component name after the first two, and
# the byline) to an ellipsis in the one place it was meant to be read. The
# full component list still reaches search: it is in the JSON-LD, the /llms.txt
# body and the crawler document's prose. Keep the byline — test_site_identity
# pins "Pip Install Python" here.
SITE_DESCRIPTION = (
    "Event calendar, resource timeline and radial chart components for Plotly "
    "Dash, wrapping the MUI X Scheduler. By Pip Install Python."
)

# The brand without its tagline — for surfaces that prefix something else and
# would otherwise run past platform truncation points.
SITE_SHORT_NAME = "dash-mui-scheduler"

# Prefixed to every per-page title. Dash passes page titles straight into
# og:title / twitter:title, so this is the headline on every share card.
# Derived, not retyped, so the two can't drift (test_site_identity pins it).
PAGE_TITLE_PREFIX = f"{SITE_SHORT_NAME} | "
# App accent: a blue palette ("brand") anchored on rgb(51,153,255) = #3399ff,
# defined in components/appshell.py theme.colors. Set back to "teal" to revert.
PRIMARY_COLOR = "brand"

# Read from package.json — the same file setup.py takes the version from, so the
# site, the wheel, and the JSON-LD in templates/index.html cannot drift apart.
try:
    import json as _json
    from pathlib import Path as _Path

    APP_VERSION = _json.loads(
        (_Path(__file__).resolve().parent.parent / "package.json").read_text()
    ).get("version", "0.0.0")
except Exception:  # pragma: no cover - never break startup over a version string
    APP_VERSION = "0.0.0"

# ---------------------------------------------------------------------------
# Canonical origin. ONE source of truth for every absolute URL the site emits:
# canonical links, og:url, og:image, sitemap.xml, robots.txt, llms.txt and the
# JSON-LD @ids. Env-driven (APP_BASE_URL, see render.yaml) so the host can move
# without a code change; the default below is the live public address.
#
# The Render service's own dash-mui-scheduler-docs.onrender.com URL keeps
# serving the same site forever — lib/canonical_host.py 301s it here so the two
# don't compete as duplicates.
# ---------------------------------------------------------------------------
# Named rather than inlined into the getenv call so the guard below, and
# tests/test_config.py, can assert what a deploy that forgets APP_BASE_URL
# would actually publish. Never trailing-slashed.
DEFAULT_BASE_URL = "https://muischeduler.2plot.dev"

BASE_URL = _os.getenv("APP_BASE_URL", DEFAULT_BASE_URL).rstrip("/")

# Hostname only — what lib/canonical_host.py compares the Host header against.
CANONICAL_HOST = BASE_URL.split("//", 1)[-1].split("/", 1)[0]

# Send every other host here with a 301. OFF unless CANONICAL_HOST_REDIRECT is
# set: switching it on before the custom domain's DNS resolves would bounce
# every visitor to a host that isn't answering yet.
CANONICAL_HOST_REDIRECT = _os.getenv("CANONICAL_HOST_REDIRECT", "").strip().lower() in (
    "1", "true", "yes", "on",
)

# ---------------------------------------------------------------------------
# The social card (2plot network standard)
# ---------------------------------------------------------------------------
# The card lives on the CDN, NOT in assets/: a scraper fetching from a cold
# free-tier container times out once and the platform caches the miss forever.
# Rendered by scripts/make_social_card.py (1200x630 — the Open Graph ideal)
# and uploaded BY HAND to the Cloudflare bucket. HARD GATE: never deploy code
# whose og:image points at this URL until the object answers 200 with a
# 1200x630 IHDR — scripts/smoke_live.py checks the real pixels after every
# deploy, and fails while it 404s, deliberately.
#
# image_url=OG_IMAGE_URL and description= go at EVERY register_page: one
# missing and Dash emits content="" — and the empty tag, later in document
# order, is the one scrapers take.
OG_IMAGE_URL = "https://cdn.2plot.ai/github_assets/muischeduler.2plot.dev.png"
OG_IMAGE_WIDTH = 1200
OG_IMAGE_HEIGHT = 630
OG_IMAGE_TYPE = "image/png"
OG_IMAGE_ALT = SITE_BRAND

# ---------------------------------------------------------------------------
# Publisher identity for the crawler document's JSON-LD (configure_seo).
# ---------------------------------------------------------------------------
# `same_as` is the "these are all the same thing" signal on the crawler page:
# for a docs satellite it lists the documented package's GitHub repo and PyPI
# project — three properties pointing at each other is the strongest statement
# of which URL is this package's canonical docs home. The other half of the
# loop (PyPI project_urls and the GitHub README pointing back at this
# subdomain) is a per-package checklist item, not code.
PUBLISHER = "Pip Install Python LLC"
SAME_AS = [
    "https://github.com/pip-install-python/dash-mui-scheduler",
    "https://pypi.org/project/dash-mui-scheduler/",
]

# ---------------------------------------------------------------------------
# The network's internal-traffic contract
# ---------------------------------------------------------------------------
# Any request whose User-Agent contains INTERNAL_UA_TOKEN is 2plot machinery
# talking to itself (hub health sweeps, CI smoke batteries, this app's own
# calls to the hub) and is counted NOWHERE. Two halves, both required:
#   inbound  — lib/analytics_tracker drops token-carrying hits at WRITE time,
#              before device detection and bot classification;
#   outbound — every call this host makes to another network host sends
#              internal_ua(...), so the far side can apply the same rule.
# The token must stay byte-identical across the network (mirrors
# pip-docs+/lib/constants.py and the boilerplate).
INTERNAL_UA_TOKEN = "2plot-internal"
INTERNAL_UA = "2plot-internal/1.0 (+https://2plot.ai/docs/satellite-analytics)"


def internal_ua(caller: str = "") -> str:
    """``INTERNAL_UA`` with a caller suffix (e.g. ``"ad-client"``) for the far
    side's logs. Only the token matters to the contract."""
    caller = (caller or "").strip()
    return f"{INTERNAL_UA} {caller}" if caller else INTERNAL_UA


def require_owned_base_url(base_url: str = BASE_URL) -> None:
    """Fail fast in production when BASE_URL isn't this app's real origin.

    Only enforced when a hosting platform is detected (Render sets ``RENDER``;
    ``APP_ENV=production`` works anywhere else) so local runs and the test
    suite are unaffected. Catches APP_BASE_URL unset (the canonical would
    advertise whatever the default says) and platform-generated hostnames
    (``*.onrender.com`` still resolves after the custom domain attaches, and a
    canonical pointing there splits link equity across two hosts).
    """
    in_production = bool(
        _os.environ.get("RENDER") or _os.environ.get("APP_ENV") == "production"
    )
    if not in_production:
        return
    if not _os.environ.get("APP_BASE_URL"):
        raise RuntimeError(
            "APP_BASE_URL is not set. Canonical links, sitemap.xml and llms.txt "
            f"would all claim {base_url!r}. Set APP_BASE_URL to this "
            "deployment's real origin (e.g. https://muischeduler.2plot.dev)."
        )
    for platform_host in ("onrender.com", "herokuapp.com", "railway.app", "fly.dev"):
        if platform_host in base_url:
            raise RuntimeError(
                f"APP_BASE_URL={base_url!r} is a platform-generated hostname. "
                "Set APP_BASE_URL to the public domain so canonicals point at "
                "one host."
            )


# Height of the fixed AppShell header, in px. Consumed by AppShell(header=...)
# in components/appshell.py and by the mobile drawer, which docks itself
# directly below the header. Change it HERE only — the two must never drift
# apart, and a drawer that starts a few px off leaves the hamburger under an
# overlay it cannot be tapped through.
HEADER_HEIGHT = 70

# Populated by pages/markdown.py when loading documentation files (raw markdown
# keyed by page name) — used by the "copy for LLM" button directive.
NAME_CONTENT_MAP = {}

# Mantine style props that pollute auto-generated kwargs tables. Kept for
# parity with the documentation boilerplate; harmless for scheduler components.
PROPS_TO_EXCLUDE = [
    "unstyled", "m", "my", "mx", "mt", "mb", "ms", "me", "ml", "mr",
    "p", "py", "px", "pt", "pb", "ps", "pe", "pl", "pr",
    "bg", "c", "opacity", "ff", "fz", "fw", "lts", "ta", "lh", "fs", "tt",
    "td", "w", "miw", "maw", "h", "mih", "mah", "bgsz", "bgp", "bgr", "bga",
    "pos", "top", "left", "bottom", "right", "inset", "display", "flex",
]
