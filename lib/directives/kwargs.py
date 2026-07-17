"""`.. kwargs::Component` directive.

Auto-builds a props table for a component by parsing its docstring. The
documentation-boilerplate original parsed numpy-style docstrings (for
dash-pydantic-form); Dash-generated components instead use a
"Keyword arguments:" section, so this version parses that format.

Usage in markdown:

    .. kwargs::dash_mui_scheduler.EventCalendar
    .. kwargs::dms.EventCalendar          (dms == dash_mui_scheduler)
    .. kwargs::dmc.Button                 (still works for DMC components)
"""
import importlib
import inspect
import re

import dash_mantine_components as dmc
from markdown2dash.src.directives.kwargs import Kwargs as KwargsBase

_PACKAGE_MAP = {
    "dms": "dash_mui_scheduler",
    "dash_mui_scheduler": "dash_mui_scheduler",
    "dmc": "dash_mantine_components",
    "html": "dash.html",
    "dcc": "dash.dcc",
    "dash": "dash",
}

# Matches a top-level prop header line: "- name (type; optional):  rest"
_HEADER_RE = re.compile(r"^-\s+(\w+)\s+\((.*?)\):\s*(.*)$")


def parse_dash_kwargs(docstring):
    """Parse a Dash component's "Keyword arguments:" docstring into a list of
    {name, type, description} dicts (top-level props only; nested dict-shape
    sub-bullets are folded into the parent prop's description)."""
    if not docstring:
        return []
    if "Keyword arguments:" in docstring:
        docstring = docstring.split("Keyword arguments:", 1)[1]

    params = []
    current = None
    for raw in docstring.split("\n"):
        line = raw.rstrip()
        m = _HEADER_RE.match(line)
        # Only column-0 "- name (type):" lines start a new top-level prop;
        # indented "- key (...)" lines belong to a nested dict and are text.
        if m and not raw.startswith((" ", "\t")):
            if current:
                params.append(current)
            current = {
                "name": m.group(1),
                "type": m.group(2),
                "description": m.group(3).strip(),
            }
        elif current is not None:
            text = line.strip()
            if text:
                current["description"] += (" " if current["description"] else "") + text
    if current:
        params.append(current)
    return params


class Kwargs(KwargsBase):
    def hook(self, md, state):
        sections = [tok for tok in state.tokens if tok["type"] == self.block_name]

        for section in sections:
            attrs = section["attrs"]
            component_spec = attrs["title"]

            if "." in component_spec:
                package_abbr, component_name = component_spec.rsplit(".", 1)
                package = _PACKAGE_MAP.get(package_abbr, package_abbr)
            else:
                package = attrs.pop("library", "dash_mui_scheduler")
                component_name = component_spec

            try:
                imported = importlib.import_module(package)
                component = getattr(imported, component_name)
                attrs["kwargs"] = parse_dash_kwargs(inspect.getdoc(component))
            except Exception:
                attrs["kwargs"] = []

    def render(self, renderer, title, content, **options):
        table = super().render(renderer, title, content, **options)
        if table is None:
            return table
        # Wrap the props table so its fixed-width columns scroll horizontally
        # inside this box instead of blowing out the page layout on phones.
        # (An inline style is used because the directive decorator overwrites
        # `className` with `m2d-block-kwargs`.)
        return dmc.Box(table, style={"overflowX": "auto", "maxWidth": "100%"})
