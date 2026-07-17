"""A controlled EventCalendar: the calendar is fully interactive on its own,
and a callback mirrors the live `events` array and the most recent
`lastAction` back to the page as JSON."""

import json

from dash import html, dcc, Input, Output, callback
import dash_mantine_components as dmc
import dash_mui_scheduler as dms

# Events cross the Dash boundary as plain dicts with ISO-string dates.
# "...:00" with no "Z" is wall time; a trailing "Z" would mean a UTC instant.
events = [
    {
        "id": "kickoff",
        "title": "Project kickoff",
        "start": "2024-01-15T09:00:00",
        "end": "2024-01-15T10:30:00",
        "color": "blue",
        "description": "Align on scope for the quarter.",
    },
    {
        "id": "design-review",
        "title": "Design review",
        "start": "2024-01-16T13:00:00",
        "end": "2024-01-16T14:00:00",
        "color": "purple",
    },
    {
        "id": "team-lunch",
        "title": "Team lunch",
        "start": "2024-01-17T12:00:00",
        "end": "2024-01-17T13:00:00",
        "color": "green",
    },
    {
        "id": "retro",
        "title": "Sprint retro",
        "start": "2024-01-18T16:00:00",
        "end": "2024-01-18T17:00:00",
        "color": "amber",
    },
]

component = dmc.Stack(
    [
        dms.EventCalendar(
            id="event_calendar-overview-cal",
            events=events,
            defaultView="week",
            defaultVisibleDate="2024-01-15",
            eventColor="teal",
            height=600,
        ),
        dmc.Group(
            [
                dmc.Stack(
                    [
                        dmc.Text("Live events array", fw=600, size="sm"),
                        dmc.Code(
                            id="event_calendar-overview-events",
                            block=True,
                            style={"maxHeight": 320, "overflow": "auto"},
                        ),
                    ],
                    gap=4,
                    style={"flex": 1, "minWidth": 280},
                ),
                dmc.Stack(
                    [
                        dmc.Text("Most recent lastAction", fw=600, size="sm"),
                        dmc.Code(
                            id="event_calendar-overview-action",
                            block=True,
                            style={"maxHeight": 320, "overflow": "auto"},
                        ),
                    ],
                    gap=4,
                    style={"flex": 1, "minWidth": 280},
                ),
            ],
            grow=True,
            align="flex-start",
        ),
    ],
    gap="md",
)


@callback(
    Output("event_calendar-overview-events", "children"),
    Output("event_calendar-overview-action", "children"),
    Input("event_calendar-overview-cal", "events"),
    Input("event_calendar-overview-cal", "lastAction"),
)
def show_boundary(current_events, last_action):
    """Render the two OUTPUT sides of the boundary as pretty JSON."""
    events_json = json.dumps(current_events or [], indent=2)
    action_json = json.dumps(last_action or {}, indent=2)
    return events_json, action_json
