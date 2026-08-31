"""The `.. kwargs::` prop tables reach the MACHINE lane, not just React.

THE DEFECT (spec 1.6.42 highlight 7 as amended — the fourth mechanism that
produces an empty props surface at 200; measured on this host 2026-08-31):
a markdown2dash directive that renders Dash components puts its output in
the React tree ONLY. The machine lane, the dash-improve-my-llms prerender
and the crawler HTML are all built from the markdown SOURCE, where the
directive line is stripped — and the renderer returns None on empty, so a
broken spec renders as silence rather than as an error.

On a component-documentation site that is not cosmetic. Before the fix,
`/event-calendar/llms.txt` described the component and listed NOT ONE of its
33 props: an agent asking this site what `EventCalendar` accepts got prose
and nothing else.

WHAT THESE PINS ASSERT, and why it is not the obvious thing: ROWS and row
CONTENT, never a section heading. A heading pin passes on a table with zero
rows, which is exactly the shape the defect produces. Each pin below names
real prop names taken from the component at run time, so it cannot pass
against an empty table.

THE THREE ARTIFACTS, named rather than collapsed (the amendment's wire-byte
nuance): "the browser lane" is not one document. There is the app-shell
markup, the prerender block inside the SAME received HTML, and the
JS-rendered DOM. Only the first two are visible to curl, and they are what
these pins measure. The JS-rendered DOM is not asserted here — no test
client renders React — which is precisely why the defect survived: the one
artifact that always looked right was the only one anybody checked.
"""

from __future__ import annotations

import inspect
import re

import pytest

from conftest import BROWSER_UA, CRAWLER_UA

# A page whose markdown carries `.. kwargs::`, and the component it documents.
PAGE = "/event-calendar"
COMPONENT = "EventCalendar"


def _props() -> list[str]:
    """The prop names the directive's own parser finds — one shared parse, so
    these pins cannot drift from what the page renders."""
    import dash_mui_scheduler

    from lib.directives.kwargs import parse_dash_kwargs

    component = getattr(dash_mui_scheduler, COMPONENT)
    return [p["name"] for p in parse_dash_kwargs(inspect.getdoc(component))]


def _generated_rows(doc: str) -> list[str]:
    r"""Prop names from the GENERATED table only.

    Scoped deliberately: these pages carry hand-written markdown tables of
    their own (event-object fields — `title`, `start`, `create`…) in the very
    same `| \`name\` |` shape, so a document-wide regex reads those as prop
    rows and a "rows nobody declared" assertion fires on perfectly good prose.
    Found by this pin on its first run. Slice from the generated heading to
    the next heading.
    """
    start = doc.find(f"#### `{COMPONENT}` props")
    if start == -1:
        return []
    rest = doc[start + 1:]
    end = rest.find("\n#")
    section = rest if end == -1 else rest[:end]
    return re.findall(r"^\| `(\w+)` \|", section, re.MULTILINE)


def test_the_component_really_exposes_props():
    """Non-vacuity. If the parser returns nothing, every pin below would pass
    against silence — the defect's own signature."""
    props = _props()
    assert len(props) > 20, f"only {len(props)} props parsed from {COMPONENT}"


@pytest.mark.parametrize("lane_ua", [BROWSER_UA, CRAWLER_UA])
def test_the_page_html_carries_real_prop_rows(client, lane_ua):
    """The two curl-visible browser-lane artifacts: the app-shell markup and
    the prerender block. Both are built server-side, so both must carry the
    props — and before the fix neither did."""
    body = client.get(PAGE, user_agent=lane_ua).text
    for name in _props()[:6]:
        assert name in body, f"{name} missing from the page HTML for UA={lane_ua[:28]}"


def test_the_machine_lane_carries_real_prop_rows(client):
    """`/<page>/llms.txt` — what an agent reads. ROWS, and their CONTENT."""
    doc = client.get(f"{PAGE}/llms.txt", user_agent=CRAWLER_UA).text
    rows = _generated_rows(doc)
    assert len(rows) > 20, f"only {len(rows)} prop rows in the machine lane"
    declared = set(_props())
    assert set(rows) <= declared, f"rows nobody declared: {set(rows) - declared}"
    for name in _props()[:6]:
        assert name in rows, f"{name} is documented but absent from the machine lane"


def test_the_lanes_agree_on_the_prop_set(client):
    """Lane parity. Two lanes describing the same component differently is
    the failure one shared parse exists to prevent."""
    doc = client.get(f"{PAGE}/llms.txt", user_agent=CRAWLER_UA).text
    html = client.get(PAGE, user_agent=CRAWLER_UA).text
    rows = set(_generated_rows(doc))
    assert rows, "no rows in the machine lane"
    missing = {n for n in rows if n not in html}
    assert not missing, f"in the machine lane but not the crawler HTML: {sorted(missing)}"


def test_the_expansion_is_fence_aware():
    """A `.. kwargs::` INSIDE a fenced block is documentation of the syntax,
    not a directive to run — the same rule `.. source::` already follows,
    and the same trap: expanding one injects a table into an open fence."""
    from pages.markdown import _expand_source_directives

    fenced = "```markdown\n.. kwargs::dash_mui_scheduler.EventCalendar\n```\n"
    assert _expand_source_directives(fenced) == fenced.rstrip("\n") + "\n" or \
        ".. kwargs::" in _expand_source_directives(fenced), \
        "a fenced directive was expanded"


def test_an_unresolvable_spec_says_so_rather_than_going_quiet():
    """THE MUTATION CHECK, and the heart of it: the renderer returns None on
    empty, so a broken spec renders as SILENCE. Silence is what let this
    survive. An unresolvable component must leave a visible marker in the
    prose instead of nothing at all."""
    from pages.markdown import _kwargs_table

    out = _kwargs_table("dash_mui_scheduler.NoSuchComponent")
    assert out.strip(), "an unresolvable spec expanded to nothing"
    assert "NoSuchComponent" in out and "<!--" in out

    good = _kwargs_table(f"dash_mui_scheduler.{COMPONENT}")
    assert good.count("\n|") > 20, "the good path stopped producing rows"
