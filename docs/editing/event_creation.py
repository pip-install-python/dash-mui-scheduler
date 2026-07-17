from dash import Input, Output, callback
import dash_mantine_components as dmc
import dash_mui_scheduler as dms

# Dates are ISO strings (wall time, no "Z"). The component writes the
# full new array back to `events` on every create / move / resize / delete.
events = [
    {
        "id": "kickoff",
        "title": "Project kickoff",
        "start": "2024-01-15T10:00:00",
        "end": "2024-01-15T11:30:00",
        "color": "indigo",
    },
    {
        "id": "review",
        "title": "Design review",
        "start": "2024-01-17T14:00:00",
        "end": "2024-01-17T15:00:00",
        "color": "teal",
    },
]

component = dmc.Stack(
    [
        dmc.Text(
            "Double-click an empty slot to create a 45-minute event. "
            "Existing events stay draggable and resizable.",
            size="sm",
            c="dimmed",
        ),
        dms.EventCalendar(
            id="editing-creation-cal",
            events=events,
            # interaction: 'click' | 'double-click'; duration is in minutes.
            eventCreation={"interaction": "double-click", "duration": 45},
            defaultVisibleDate="2024-01-15",
            defaultView="week",
            height=600,
        ),
        dmc.Code(id="editing-creation-action", block=True),
    ],
    gap="sm",
)


@callback(
    Output("editing-creation-action", "children"),
    Input("editing-creation-cal", "lastAction"),
)
def show_action(last_action):
    if not last_action:
        return "No action yet — double-click an empty slot to create an event."
    event = last_action.get("event") or {}
    return f"{last_action.get('type')}: {event.get('title', '(none)')}"
