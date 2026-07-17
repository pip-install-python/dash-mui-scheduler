import dash_mui_scheduler as dms
from dash import html, dcc, Input, Output, callback

# Each event is a plain dict. Dates are ISO strings (no "Z" = wall time).
# Required keys: id, title, start, end. Everything else is optional.
events = [
    {
        "id": "kickoff",
        "title": "Project Kickoff",
        "start": "2024-01-15T09:00:00",
        "end": "2024-01-15T10:00:00",
        "description": "Align on goals for the quarter.",
    },
    {
        "id": "standup",
        "title": "Daily Standup",
        "start": "2024-01-16T09:30:00",
        "end": "2024-01-16T09:45:00",
    },
    {
        "id": "review",
        "title": "Design Review",
        "start": "2024-01-17T14:00:00",
        "end": "2024-01-17T15:30:00",
        "description": "Walk through the new dashboard mockups.",
    },
    {
        "id": "1on1",
        "title": "1:1",
        "start": "2024-01-18T11:00:00",
        "end": "2024-01-18T11:30:00",
    },
]

component = html.Div(
    [
        dms.EventCalendar(
            id="events-basic-cal",
            events=events,
            defaultVisibleDate="2024-01-15",
            height=600,
        ),
        dcc.Markdown(id="events-basic-out", style={"marginTop": "0.75rem"}),
    ]
)


@callback(
    Output("events-basic-out", "children"),
    Input("events-basic-cal", "events"),
)
def show_count(current_events):
    return f"**{len(current_events or [])}** events currently on the calendar."
