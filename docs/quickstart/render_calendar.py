from dash import html, dcc, Input, Output, callback
import dash_mantine_components as dmc
import dash_mui_scheduler as dms

# events are plain dicts; dates are ISO strings (no Z = wall time).
# Required keys: id, title, start, end. Everything else is optional.
events = [
    {
        "id": "1",
        "title": "Team Standup",
        "start": "2024-01-15T09:00:00",
        "end": "2024-01-15T09:30:00",
        "color": "blue",
    },
    {
        "id": "2",
        "title": "Design Review",
        "start": "2024-01-16T13:00:00",
        "end": "2024-01-16T14:30:00",
        "color": "purple",
    },
    {
        "id": "3",
        "title": "Sprint Demo",
        "start": "2024-01-18T15:00:00",
        "end": "2024-01-18T16:00:00",
        "color": "green",
    },
]

component = dmc.Stack(
    [
        dms.EventCalendar(
            id="quickstart-cal",
            events=events,
            defaultVisibleDate="2024-01-15",
            defaultView="week",
            height=600,
        ),
        dmc.Text("Last action", fw=600, size="sm"),
        dcc.Markdown(id="quickstart-cal-readout"),
    ],
    gap="sm",
)


@callback(
    Output("quickstart-cal-readout", "children"),
    Input("quickstart-cal", "lastAction"),
)
def show_last_action(last_action):
    if not last_action:
        return "_Drag, create, or delete an event to see the last action._"
    action_type = last_action.get("type")
    event = last_action.get("event") or {}
    title = event.get("title", "—")
    return f"**{action_type}** → `{title}`"
