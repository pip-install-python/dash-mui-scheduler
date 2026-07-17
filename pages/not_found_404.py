"""Good-faith 404 for the dash-mui-scheduler docs.

Dash `use_pages` renders the module named ``not_found_404`` for any pathname that
matches no registered page: a typo or a stale link. Plain DMC — no game assets.
"""
import dash_mantine_components as dmc
from dash import register_page

register_page(__name__, path="/404", title="Page not found · dash-mui-scheduler")

ACCENT = "#3399ff"


def layout(**kwargs):
    return dmc.Center(
        dmc.Stack(
            [
                dmc.Text("404", fw=900, ta="center",
                         style={"fontSize": "clamp(46px,12vw,84px)", "lineHeight": 1,
                                "letterSpacing": "0.05em", "color": ACCENT,
                                "fontFamily": "monospace"}),
                dmc.Title("This page isn't on the calendar", order=3, ta="center"),
                dmc.Text("The page you were looking for may have been moved, renamed, or "
                         "never existed. Head back to the docs home or start at the "
                         "Quickstart.",
                         size="sm", c="dimmed", ta="center", style={"maxWidth": 420}),
                dmc.Group([
                    dmc.Anchor(dmc.Button("← Docs home", color="brand", size="md"),
                               href="/", underline="never"),
                    dmc.Anchor(dmc.Button("Quickstart", variant="light", size="md"),
                               href="/quickstart", underline="never"),
                ], gap="sm", justify="center"),
            ],
            gap="md", align="center",
        ),
        style={"minHeight": "calc(100vh - 140px)", "padding": "24px"},
    )
