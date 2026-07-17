import os

from dash import Input, Output, callback
import dash_mantine_components as dmc
import dash_mui_scheduler as dms

# Premium events may carry an `rrule`. The RRULE string form follows RFC-5545:
# this event recurs every week on Monday, Wednesday and Friday at 10:00.
events = [
    {
        "id": "standup",
        "title": "Team Standup",
        "start": "2024-01-15T10:00:00",
        "end": "2024-01-15T10:30:00",
        "color": "blue",
        "rrule": "FREQ=WEEKLY;INTERVAL=1;BYDAY=MO,WE,FR",
    },
    {
        "id": "review",
        "title": "Sprint Review",
        "start": "2024-01-19T15:00:00",
        "end": "2024-01-19T16:00:00",
        "color": "purple",
    },
]

component = dmc.Stack(
    [
        dms.EventCalendarPremium(
            id="recurrence-string-cal",
            licenseKey=os.environ.get("MUI_X_LICENSE_KEY", ""),
            events=events,
            defaultView="week",
            defaultVisibleDate="2024-01-15",
            height=600,
        ),
        dmc.Text("Last action:", fw=600, size="sm"),
        dmc.Code(id="recurrence-string-action", block=True),
    ],
    gap="sm",
)


@callback(
    Output("recurrence-string-action", "children"),
    Input("recurrence-string-cal", "lastAction"),
)
def show_action(last_action):
    if not last_action:
        return "No action yet — drag, create, resize or delete an occurrence."
    return f"{last_action.get('type')} @ {last_action.get('event_timestamp')}"
