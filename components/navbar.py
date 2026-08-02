import dash_mantine_components as dmc
from dash_iconify import DashIconify

excluded_links = [
    "/404",
    "/styles-api",
    "/style-props",
    "/dash-iconify",
    "/migration",
    "/learning-resources",
]


def create_nav_link(icon, text, href, external=False):
    """Create a styled navigation link with icon"""
    return dmc.Anchor(
        dmc.Group(
            [
                DashIconify(icon=icon, width=18),
                dmc.Text(text, size="sm", fw=500),
            ],
            gap="sm",
        ),
        href=href,
        target="_blank" if external else None,
        className="navbar-link",
        underline=False,
    )


def create_nav_section(title, links):
    """Create a navigation section with a title and links"""
    return dmc.Stack(
        [
            dmc.Text(
                title,
                size="xs",
                fw=700,
                tt="uppercase",
                c="dimmed",
                mb="xs",
            ),
            dmc.Stack(links, gap="xs"),
        ],
        gap="sm",
    )


def create_content(data):
    """Create navbar content with organized sections"""

    # Scheduler documentation pages (ordered).
    page_order = [
        "Quickstart",
        "Event Calendar",
        "Playground",
        "Events",
        "Resources",
        "Views",
        "Navigation",
        "Responsive",
        "Drag & Resize",
        "Editing",
        "Preferences",
        "Recurrence",
        "Event Timeline",
        "Localization & Timezones",
    ]

    # Radial chart pages live in their own navigation section, separate from
    # the scheduler docs.
    chart_page_order = [
        "Radial Lines",
        "Radial Bars",
        "Radial Axes",
    ]

    # Create a mapping of page names to their links
    page_dict = {}
    for entry in data:
        if entry["path"] not in excluded_links and entry["path"] != "/":
            link = create_nav_link(
                entry.get("icon", "fluent:document-24-regular"),
                entry["name"],
                entry["path"]
            )
            page_dict[entry["name"]] = link

    # Scheduler docs section (ordered), excluding the chart pages.
    page_links = []
    for page_name in page_order:
        if page_name in page_dict:
            page_links.append(page_dict[page_name])

    # Any remaining pages that aren't in any ordered list.
    for name, link in page_dict.items():
        if name not in page_order and name not in chart_page_order:
            page_links.append(link)

    # Radial charts section (ordered).
    chart_links = [page_dict[name] for name in chart_page_order if name in page_dict]

    return dmc.ScrollArea(
        offsetScrollbars=True,
        type="scroll",
        style={"height": "100%"},
        children=dmc.Stack(
            [
                # Home link
                create_nav_link(
                    "fluent:home-24-regular",
                    "Home",
                    "/"
                ),

                # Scheduler Documentation Section
                dmc.Divider(mt="xs", mb="xs"),
                create_nav_section(
                    "Scheduler",
                    page_links
                ),

                # Radial Charts Section (separate from the scheduler docs)
                dmc.Divider(mt="md", mb="sm"),
                create_nav_section(
                    "Radial Charts",
                    chart_links
                ),

                # External Resources Section
                dmc.Divider(mt="md", mb="sm"),
                create_nav_section(
                    "Resources",
                    [
                        create_nav_link(
                            "fluent-mdl2:forum",
                            "Dash Community",
                            "https://community.plotly.com/",
                            external=True
                        ),
                        create_nav_link(
                            "logos:material-ui",
                            "MUI X Scheduler",
                            "https://mui.com/x/react-scheduler/",
                            external=True
                        ),
                        create_nav_link(
                            "solar:box-bold-duotone",
                            "2plot.dev",
                            "https://2plot.dev/",
                            external=True
                        ),
                    ]
                ),
                dmc.Divider(mt="md", mb="sm"),
                create_nav_section(
                    "2plot network",
                    [
                        create_nav_link(
                            "game-icons:amoeba",
                            "2plot.xyz — the game",
                            "https://2plot.xyz",
                            external=True
                        ),
                        create_nav_link(
                            "fluent:home-24-regular",
                            "2plot.ai — the hub",
                            "https://2plot.ai",
                            external=True
                        ),
                        create_nav_link(
                            "solar:videocamera-record-bold-duotone",
                            "2plot.media — videography",
                            "https://2plot.media",
                            external=True
                        ),
                        create_nav_link(
                            "solar:cart-large-4-bold-duotone",
                            "PiratesBargain — commerce",
                            "https://piratesbargain.com",
                            external=True
                        ),
                        create_nav_link(
                            "solar:magic-stick-3-bold-duotone",
                            "ai-agent.buzz — AI canvas",
                            "https://ai-agent.buzz",
                            external=True
                        ),
                    ]
                )
            ],
            gap="xs",
            p="md",
        ),
    )


def create_navbar(data):
    """Create the main application navbar"""
    return dmc.AppShellNavbar(
        children=create_content(data),
        style={"borderRight": "1px solid var(--mantine-color-gray-3)"}
    )


def create_navbar_drawer(data):
    """Create mobile drawer navigation"""
    return dmc.Drawer(
        id="components-navbar-drawer",
        overlayProps={"opacity": 0.55, "blur": 3},
        zIndex=1500,
        offset=8,
        radius="md",
        withCloseButton=True,
        size="280px",
        children=create_content(data),
        trapFocus=False,
        position="left",
    )
