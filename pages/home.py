"""dash-mui-scheduler docs home — component-library landing page (plain DMC)."""
import dash_mantine_components as dmc
from dash import register_page, html
from dash_iconify import DashIconify

from lib.constants import OG_IMAGE_URL, PAGE_TITLE_PREFIX, SITE_DESCRIPTION

register_page(
    __name__,
    path="/",
    name="Home",
    title=PAGE_TITLE_PREFIX + "Home",
    description=SITE_DESCRIPTION,
    # Pins og:image/twitter:image to the CDN card (see lib/constants).
    image_url=OG_IMAGE_URL,
)

ACCENT = "#3399ff"
VIDEO_ID = "i-CZH7W5ZsA"

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


def _walkthrough():
    """The walkthrough video, embedded on the landing page.

    Same tour that the README links as a thumbnail and that Quickstart embeds —
    here so a reader hitting the docs can watch it without leaving for GitHub.
    Responsive 16:9: the outer box caps the width, the padding-bottom trick
    holds the ratio at any screen size. youtube-nocookie keeps the landing page
    from setting tracking cookies before anyone presses play.
    """
    return dmc.Stack(
        [
            dmc.Group(
                [
                    dmc.Title("Watch the walkthrough", order=3),
                    dmc.Anchor(
                        dmc.Group(
                            [DashIconify(icon="tabler:brand-youtube", width=18),
                             dmc.Text("Open on YouTube", size="sm")],
                            gap=6, align="center",
                        ),
                        href=f"https://youtu.be/{VIDEO_ID}",
                        target="_blank", underline="hover",
                    ),
                ],
                justify="space-between", align="center", wrap="nowrap",
            ),
            dmc.Text(
                "A tour of the event calendar, the resource timeline, and the "
                "radial charts.",
                size="sm", c="dimmed",
            ),
            html.Div(
                html.Iframe(
                    src=f"https://www.youtube-nocookie.com/embed/{VIDEO_ID}",
                    title="dash-mui-scheduler walkthrough",
                    style={
                        "position": "absolute",
                        "top": 0,
                        "left": 0,
                        "width": "100%",
                        "height": "100%",
                        "border": 0,
                        "borderRadius": "8px",
                    },
                    allow=(
                        "accelerometer; autoplay; clipboard-write; encrypted-media; "
                        "gyroscope; picture-in-picture; web-share; fullscreen"
                    ),
                ),
                style={
                    "position": "relative",
                    "paddingBottom": "56.25%",  # 16:9
                    "height": 0,
                    "overflow": "hidden",
                },
            ),
        ],
        gap="xs", mb="xl", style={"maxWidth": 820, "margin": "0 auto"},
    )


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
            _walkthrough(),
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
