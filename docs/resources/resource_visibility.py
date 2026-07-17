from dash import dcc, html, Input, Output, callback
import dash_mantine_components as dmc
import dash_mui_scheduler as dms

resources = [
    {"id": "room-a", "title": "Room A", "eventColor": "teal"},
    {"id": "room-b", "title": "Room B", "eventColor": "orange"},
    {"id": "room-c", "title": "Room C", "eventColor": "indigo"},
]

events = [
    {
        "id": "1",
        "title": "Standup",
        "start": "2024-01-15T09:00:00",
        "end": "2024-01-15T09:30:00",
        "resource": "room-a",
    },
    {
        "id": "2",
        "title": "Design crit",
        "start": "2024-01-15T13:00:00",
        "end": "2024-01-15T14:00:00",
        "resource": "room-b",
    },
    {
        "id": "3",
        "title": "Client call",
        "start": "2024-01-16T11:00:00",
        "end": "2024-01-16T12:00:00",
        "resource": "room-c",
    },
    {
        "id": "4",
        "title": "Retro",
        "start": "2024-01-17T15:00:00",
        "end": "2024-01-17T16:00:00",
        "resource": "room-a",
    },
]

# Start with every room visible. `visibleResources` is a {resource_id: bool} map.
all_ids = [r["id"] for r in resources]

component = html.Div(
    dmc.Stack(
        [
            dmc.Text("Toggle rooms — hidden rooms keep their events in `events`."),
            dmc.ChipGroup(
                id="resources-visibility-chips",
                multiple=True,
                value=all_ids,
                children=dmc.Group(
                    [dmc.Chip(r["title"], value=r["id"]) for r in resources]
                ),
            ),
            dms.EventCalendar(
                id="resources-visibility-cal",
                events=events,
                resources=resources,
                defaultView="week",
                defaultVisibleDate="2024-01-15",
                # Controlled in + out: the callback drives which rooms show.
                visibleResources={rid: True for rid in all_ids},
                height=600,
            ),
        ],
        gap="sm",
    )
)


@callback(
    Output("resources-visibility-cal", "visibleResources"),
    Input("resources-visibility-chips", "value"),
)
def toggle_resources(checked):
    checked = checked or []
    # Explicitly mark each room True/False so unchecked rooms hide.
    return {rid: (rid in checked) for rid in all_ids}
