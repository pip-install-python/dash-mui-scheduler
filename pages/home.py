"""dash-mui-scheduler docs home — component-library landing page (plain DMC)."""
import dash_mantine_components as dmc
from dash import register_page, html
from dash_iconify import DashIconify

register_page(
    __name__,
    path="/",
    title="dash-mui-scheduler — MUI X Scheduler for Plotly Dash",
    description=(
        "A Plotly Dash wrapper for the MUI X Scheduler: EventCalendar, "
        "EventCalendarPremium and EventTimeline plus the RadialLineChart and "
        "RadialBarChart polar charts, "
        "with recurrence, drag & resize, resources, timezones and theming."
    ),
)

ACCENT = "#3399ff"

_FEATURES = [
    ("tabler:calendar-event", "Event Calendar",
     "Day, week, month and agenda views with drag & resize, inline editing, "
     "resources, and recurring events.", "/event-calendar"),
    ("tabler:timeline", "Event Timeline",
     "A horizontal scheduler lane view for resource planning, with the same "
     "event model as the calendar.", "/event-timeline"),
    ("tabler:chart-donut", "Radial charts",
     "RadialLineChart and RadialBarChart — MUI X polar charts wrapped as "
     "first-class Dash components.", "/radial-lines"),
    ("tabler:world", "Localization & timezones",
     "Locale packs, week-start control, and timezone-aware rendering out of "
     "the box.", "/localization"),
]


def _feature_card(icon, title, body, href):
    return dmc.Anchor(
        dmc.Card(
            [
                dmc.Group([DashIconify(icon=icon, width=26, color=ACCENT),
                           dmc.Title(title, order=4, style={"marginBottom": 0})], gap="sm"),
                dmc.Text(body, size="sm", c="dimmed", mt="xs"),
            ],
            withBorder=True, radius="md", padding="lg", style={"height": "100%"},
        ),
        href=href, underline="never",
    )


def layout(**kwargs):
    return dmc.Container(
        [
            dmc.Stack(
                [
                    dmc.Center(html.Img(src="/assets/dms_logo.svg", style={"height": 84})),
                    dmc.Title("dash-mui-scheduler", order=1, ta="center"),
                    dmc.Text(
                        "The MUI X Scheduler — event calendar, timeline, and radial "
                        "charts — as native Plotly Dash components.",
                        size="lg", c="dimmed", ta="center", style={"maxWidth": 640,
                                                                   "margin": "0 auto"},
                    ),
                    dmc.Center(dmc.Code("pip install dash-mui-scheduler", block=True,
                                        style={"fontSize": "1rem", "padding": "10px 18px"})),
                    dmc.Group(
                        [
                            dmc.Anchor(dmc.Button("Quickstart", size="md", color="brand"),
                                       href="/quickstart", underline="never"),
                            dmc.Anchor(dmc.Button("Playground", size="md", variant="light"),
                                       href="/playground", underline="never"),
                            dmc.Anchor(
                                dmc.Button("GitHub", size="md", variant="default",
                                           leftSection=DashIconify(icon="tabler:brand-github",
                                                                   width=18)),
                                href="https://github.com/pip-install-python/dash-mui-scheduler",
                                target="_blank", underline="never"),
                        ],
                        justify="center", gap="md",
                    ),
                ],
                gap="lg", py="xl",
            ),
            dmc.SimpleGrid(
                [_feature_card(*f) for f in _FEATURES],
                cols={"base": 1, "sm": 2}, spacing="lg", mb="xl",
            ),
            dmc.Text(
                "Part of the 2plot network — the wrapper also powers the chart labs on "
                "2plot.xyz.",
                size="xs", c="dimmed", ta="center", pb="lg",
            ),
        ],
        size="lg",
    )
