from dash import html, Input, Output, callback
import dash_mantine_components as dmc
import dash_mui_scheduler as dms

events = [
    {
        "id": "1",
        "title": "Standup",
        "start": "2024-01-15T09:00:00",
        "end": "2024-01-15T09:15:00",
        "color": "teal",
    },
    {
        "id": "2",
        "title": "Workshop",
        "start": "2024-01-16T14:00:00",
        "end": "2024-01-16T16:00:00",
        "color": "orange",
    },
    {
        "id": "3",
        "title": "Retro",
        "start": "2024-01-18T15:00:00",
        "end": "2024-01-18T16:00:00",
        "color": "pink",
    },
]

# `view` is controlled IN + OUT. The SegmentedControl writes it, and the
# calendar writes it back when the user clicks a built-in view button —
# the second callback keeps the SegmentedControl in sync.
component = dmc.Stack(
    [
        dmc.SegmentedControl(
            id="views-controlled-segmented",
            value="week",
            data=[
                {"label": "Day", "value": "day"},
                {"label": "Week", "value": "week"},
                {"label": "Month", "value": "month"},
                {"label": "Agenda", "value": "agenda"},
            ],
        ),
        dms.EventCalendar(
            id="views-controlled-cal",
            events=events,
            view="week",
            defaultVisibleDate="2024-01-15",
            height=600,
        ),
    ],
    gap="sm",
)


@callback(
    Output("views-controlled-cal", "view"),
    Input("views-controlled-segmented", "value"),
    prevent_initial_call=True,
)
def set_view(value):
    return value


@callback(
    Output("views-controlled-segmented", "value"),
    Input("views-controlled-cal", "view"),
    prevent_initial_call=True,
)
def read_view(view):
    return view
