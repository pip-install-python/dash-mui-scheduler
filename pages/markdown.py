import logging
import re
from pathlib import Path
from typing import List, Optional

import dash
import dash_mantine_components as dmc
import frontmatter
from dash_improve_my_llms import register_page_metadata
from markdown2dash import Admonition, BlockExec, Divider, Image, create_parser
from pydantic import BaseModel, field_validator

from lib import gate_layouts, page_tiers, page_visibility
from lib.ad_client import inject_ad_into_aside
from lib.constants import PAGE_TITLE_PREFIX, NAME_CONTENT_MAP, OG_IMAGE_URL
from lib.directives.kwargs import Kwargs
from lib.directives.llms_copy import LlmsCopy
from lib.directives.source import SC
from lib.directives.toc import TOC
from lib.versions import substitute_versions

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

directory = "docs"

# read all markdown files
files = Path(directory).glob("**/*.md")


class Meta(BaseModel):
    name: str
    description: str
    endpoint: str
    package: str = "dash_mui_scheduler"
    category: Optional[str] = None
    icon: Optional[str] = None
    # Who may read this page: public | auth | admin | hidden. Absent means
    # the deployment default (PAGE_DEFAULT_TIER, else public) — see
    # lib/page_tiers.py for the tier model and why the default is open.
    tier: Optional[str] = None
    # The second axis: does the machine twin (/<page>/llms.txt, crawler HTML,
    # the prerender) stay open while the interactive page is gated? Absent
    # defers to LLMS_PUBLIC_DEFAULT (unset = open — the data-window posture).
    # Only meaningful on `auth` pages; see lib/page_tiers.get_llms_public.
    llms_public: Optional[bool] = None
    # schema.org @type for the crawler document's JSON-LD. Absent means
    # TechArticle — every page here documents a software component, and
    # "WebPage" (the package default) tells Google nothing it did not already
    # know. The home page declares SoftwareApplication in run.py.
    schema_type: Optional[str] = None
    # Sitemap <lastmod>, YYYY-MM-DD, emitted VERBATIM by dash-improve-my-llms
    # >= 2.6.0 — and omitted entirely when absent. Truth or silence: set it
    # when the page's content genuinely changes (the frontmatter edit rides
    # the same commit as the prose), never script it from file mtimes, which
    # reset on every Docker build and would re-invent the daily-lie sitemap
    # 2.6.0 exists to end. The validator exists because YAML parses a bare
    # `lastmod: 2026-08-22` into datetime.date before pydantic ever sees it.
    lastmod: Optional[str] = None

    @field_validator("lastmod", mode="before")
    @classmethod
    def _lastmod_to_iso(cls, value):
        return value.isoformat() if hasattr(value, "isoformat") else value


_SOURCE_DIRECTIVE = re.compile(r'^\.\. source::(.+?)$', re.MULTILINE)
_LANG_MAP = {
    'py': 'python', 'pyi': 'python',
    'js': 'javascript', 'jsx': 'jsx',
    'ts': 'typescript', 'tsx': 'tsx',
    'css': 'css', 'scss': 'scss', 'sass': 'sass', 'less': 'less',
    'html': 'html', 'htm': 'html', 'xml': 'xml',
    'json': 'json',
    'yaml': 'yaml', 'yml': 'yaml',
    'md': 'markdown', 'rst': 'rst', 'txt': 'text',
    'sh': 'bash', 'bash': 'bash',
    'sql': 'sql', 'r': 'r',
    'toml': 'toml', 'ini': 'ini', 'conf': 'conf',
}


def _expand_source_directives(markdown_content: str) -> str:
    """Inline `.. source::path` directives with the referenced file content.

    This produces the prose that dash-improve-my-llms 2.0 will serve at
    `/<page>/llms.txt`. Replacing the directive with the real file content
    is what makes the LLM output self-contained for the "paste into a chat
    window" audience.

    FENCE-AWARE, and it has to be: a directive INSIDE a fenced code block is
    documentation showing the syntax, not a directive to run. Expanding one
    injects a ```python fence inside the already-open fence, which CLOSES it
    early — from there the inlined file renders as markdown, every `#
    comment` line becomes an <h1>, and the machine lane of that page serves
    broken structure. The browser lane never showed it, because
    markdown2dash parses fences properly (upstream 1.6.11, found by the
    single-h1 pin in tests/test_pages.py).
    """
    def expansion(directive_line: str) -> str:
        file_path = _SOURCE_DIRECTIVE.match(directive_line).group(1).strip()
        try:
            full = Path(file_path)
            content = full.read_text()
            ext = full.suffix.lstrip('.').lower()
            lang = _LANG_MAP.get(ext, ext or 'text')
            tail = '' if content.endswith('\n') else '\n'
            return f'\n```{lang}\n# File: {file_path}\n\n{content}{tail}```\n'
        except FileNotFoundError:
            return f'\n<!-- Error: File not found: {file_path} -->\n'
        except Exception as exc:
            return f'\n<!-- Error reading {file_path}: {exc} -->\n'

    out: List[str] = []
    fence = None  # the marker that opened the block we are inside, if any
    for line in markdown_content.split('\n'):
        head = line.lstrip()[:3]
        if fence is None and head in ('```', '~~~'):
            fence = head
        elif fence is not None and head == fence:
            fence = None
        elif fence is None and _SOURCE_DIRECTIVE.match(line):
            out.append(expansion(line))
            continue
        out.append(line)
    return '\n'.join(out)


def _build_llms_doc(name: str, description: str, expanded_markdown: str, path: str) -> str:
    """Wrap the expanded markdown with the heading/description preamble that
    /llms.txt readers expect."""
    parts: List[str] = [f"# {name}\n"]
    if description:
        parts.append(f"> {description}\n")
    parts.append("---\n")
    parts.append(expanded_markdown.rstrip() + "\n")
    parts.append("\n---\n")
    parts.append(f"*Source: {path}*\n")
    return "\n".join(parts)


directives = [Admonition(), BlockExec(), Divider(), Image(), Kwargs(), LlmsCopy(), SC(), TOC()]
parse = create_parser(directives)

for file in files:
    logger.info("Loading %s..", file)
    metadata, content = frontmatter.parse(file.read_text())
    metadata = Meta(**metadata)

    # Substitute derived facts BEFORE any consumer sees the text, so the
    # browser page, the copy button, and /<page>/llms.txt all publish the
    # same truth. A doc writes {{VERSION:<distribution>}} instead of a
    # version number — any installed package, so this site documents its
    # own component library the same way. See lib/versions.py for why.
    content = substitute_versions(content, source=str(file))

    # Store raw markdown content in NAME_CONTENT_MAP for the LLM copy button.
    NAME_CONTENT_MAP[metadata.name] = content

    layout = parse(content)

    # add heading and description to the layout
    section = [
        dmc.Title(metadata.name, order=2, className="m2d-heading"),
        dmc.Text(metadata.description, className="m2d-paragraph"),
    ]
    layout = section + layout

    # 2plot.dev ad network: append the ad slot below the TOC links inside
    # the page's aside (pages without `.. toc::` simply get no ad).
    inject_ad_into_aside(layout, metadata.endpoint)

    # register with dash — the layout goes in behind the interactive gate.
    # The tree is still built once, above; gated_layout only decides per
    # render whether the visitor gets it or the sign-in/forbidden/404 card
    # (lib/gate_layouts.py). With every tier public the verdict is a dict
    # lookup that always says allow, so an ungated deployment pays ~nothing.
    dash.register_page(
        metadata.name,
        metadata.endpoint,
        name=metadata.name,
        title=PAGE_TITLE_PREFIX + metadata.name,
        description=metadata.description,
        layout=gate_layouts.gated_layout(
            metadata.endpoint, metadata.name, layout
        ),
        category=metadata.category,
        icon=metadata.icon,
        # Pins og:image/twitter:image to the canonical origin. Without it Dash
        # infers assets/logo.svg — an SVG, which no social scraper renders.
        image_url=OG_IMAGE_URL,
    )

    # Feed the expanded markdown into dash-improve-my-llms so /<page>/llms.txt
    # serves the directive-expanded prose. This replaces the custom Flask
    # route that used to live in run.py and works across all three backends.
    # Record the declared tier before the prose is registered, so a gate can
    # never be applied later than the content it is meant to gate.
    #
    # ONE declared value, TWO ledgers. The control board's row first —
    # overrides written there win at resolution time (lib.access.local_tier),
    # which is what makes a board toggle apply live. Then the network ledger:
    # what the hub's tier ceiling compares against and what lib.access
    # enforces underneath any override.
    page_visibility.register_default(metadata.endpoint, metadata.name,
                                     visibility=metadata.tier,
                                     llms_public=metadata.llms_public)
    page_tiers.register(metadata.endpoint, metadata.tier,
                        llms_public=metadata.llms_public)

    expanded = _expand_source_directives(content)
    # The full record, matching the dash.register_page call above. These two
    # calls must never describe the same page differently: the thinner record
    # is exactly how the fleet shipped "<site> | Attribution" to browsers and
    # a bare "Attribution" to Google (the one bug behind every SEO defect
    # measured across the network, 2026-08). title and image_url are read by
    # dash-improve-my-llms 2.5.0+.
    register_page_metadata(
        path=metadata.endpoint,
        name=metadata.name,
        description=metadata.description,
        llms_doc=_build_llms_doc(metadata.name, metadata.description, expanded, metadata.endpoint),
        title=PAGE_TITLE_PREFIX + metadata.name,
        image_url=OG_IMAGE_URL,
        schema_type=metadata.schema_type or "TechArticle",
        # Pre-2.6 packages swallow this into **kwargs and ignore it (no
        # TypeError — measured on 2.5.1); the floor in run.py guarantees
        # >= 2.7.1, well above the 2.6.0 release where a real date is
        # emitted and None omits the tag.
        lastmod=metadata.lastmod,
    )
