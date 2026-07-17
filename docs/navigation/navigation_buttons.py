from datetime import date, timedelta

from dash import Input, Output, callback
import dash_mantine_components as dmc
import dash_mui_scheduler as dms

# `visibleDate` is an ISO date STRING (e.g. "2024-01-15"). It is controlled
# IN *and* OUT: we hand the calendar a value, and the calendar also writes the
# date back when the user navigates with the built-in arrows. Because there is
# no apiRef in Dash, you move through time purely by *setting* visibleDate.
events = [
    {
        "id": "1",
        "title": "Sprint planning",
        "start": "2024-01-15T09:00:00",
        "end": "2024-01-15T10:30:00",
        "color": "blue",
    },
    {
        "id": "2",
        "title": "Design review",
        "start": "2024-01-16T13:00:00",
        "end": "2024-01-16T14:00:00",
        "color": "purple",
    },
    {
        "id": "3",
        "title": "Retro",
        "start": "2024-01-18T15:00:00",
        "end": "2024-01-18T16:00:00",
        "color": "green",
    },
]

# Seed the controlled value so the calendar opens on the week of the events.
INITIAL_DATE = "2024-01-15"

component = dmc.Stack(
    [
        dmc.Group(
            [
                dmc.Button("‹ Prev", id="navigation-prev", variant="default"),
                dmc.Button("Today", id="navigation-today", variant="light"),
                dmc.Button("Next ›", id="navigation-next", variant="default"),
            ],
            gap="xs",
        ),
        dmc.Text(id="navigation-readout", size="sm", c="dimmed"),
        dms.EventCalendar(
            id="navigation-cal",
            events=events,
            visibleDate=INITIAL_DATE,
            defaultView="week",
            height=600,
        ),
    ],
    gap="sm",
)


@callback(
    Output("navigation-cal", "visibleDate"),
    Input("navigation-prev", "n_clicks"),
    Input("navigation-next", "n_clicks"),
    Input("navigation-today", "n_clicks"),
    Input("navigation-cal", "visibleDate"),
    prevent_initial_call=True,
)
def navigate(prev_clicks, next_clicks, today_clicks, visible_date):
    from dash import ctx

    trigger = ctx.triggered_id

    # The calendar's own arrows already updated visibleDate -> nothing to do.
    if trigger == "navigation-cal":
        return visible_date

    if trigger == "navigation-today":
        return date.today().isoformat()

    # Parse the current ISO date string, shift by one week, re-serialize.
    current = date.fromisoformat((visible_date or INITIAL_DATE)[:10])
    if trigger == "navigation-prev":
        return (current - timedelta(weeks=1)).isoformat()
    if trigger == "navigation-next":
        return (current + timedelta(weeks=1)).isoformat()
    return visible_date


@callback(
    Output("navigation-readout", "children"),
    Input("navigation-cal", "visibleDate"),
)
def show_visible_date(visible_date):
    return f"Current visibleDate: {visible_date or INITIAL_DATE}"
