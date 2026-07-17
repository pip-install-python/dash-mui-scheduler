"""Toggle drag-and-drop and resizing on an EventCalendar at runtime.

A `dmc.Switch` drives `areEventsDraggable` and a `dmc.SegmentedControl` drives
`areEventsResizable` (True / False / 'start' / 'end'). The read-out shows the
latest `lastAction` so you can tell a move apart from a resize.
"""
from dash import html, Input, Output, callback
import dash_mantine_components as dmc
import dash_mui_scheduler as dms

EVENTS = [
    {"id": 1, "title": "Team Meeting", "start": "2024-01-15T10:00:00", "end": "2024-01-15T11:00:00", "color": "blue"},
    {"id": 2, "title": "Project Review", "start": "2024-01-16T14:00:00", "end": "2024-01-16T15:30:00", "color": "purple"},
    {"id": 3, "title": "Client Call", "start": "2024-01-17T09:00:00", "end": "2024-01-17T10:00:00", "color": "green"},
    {"id": 4, "title": "Locked: Sprint Demo", "start": "2024-01-18T13:00:00", "end": "2024-01-18T14:00:00",
     "color": "grey", "draggable": False, "resizable": False},
]

component = dmc.Stack(
    [
        dmc.Group(
            [
                dmc.Switch(
                    id="drag_resize-draggable-switch",
                    label="areEventsDraggable",
                    checked=True,
                ),
                dmc.SegmentedControl(
                    id="drag_resize-resizable-control",
                    data=[
                        {"label": "Both", "value": "true"},
                        {"label": "Off", "value": "false"},
                        {"label": "Start edge", "value": "start"},
                        {"label": "End edge", "value": "end"},
                    ],
                    value="true",
                ),
            ],
            align="center",
            gap="lg",
        ),
        dms.EventCalendar(
            id="drag_resize-cal",
            events=EVENTS,
            defaultVisibleDate="2024-01-15",
            areEventsDraggable=True,
            areEventsResizable=True,
            height=600,
        ),
        dmc.Code(id="drag_resize-readout", block=True),
    ],
    gap="md",
)


@callback(
    Output("drag_resize-cal", "areEventsDraggable"),
    Output("drag_resize-cal", "areEventsResizable"),
    Input("drag_resize-draggable-switch", "checked"),
    Input("drag_resize-resizable-control", "value"),
)
def set_interactions(draggable, resizable):
    # Map the SegmentedControl string back to the prop's bool/'start'/'end' shape.
    resizable_value = {"true": True, "false": False, "start": "start", "end": "end"}[resizable]
    return draggable, resizable_value


@callback(
    Output("drag_resize-readout", "children"),
    Input("drag_resize-cal", "lastAction"),
)
def show_last_action(last_action):
    if not last_action:
        return "Drag an event to move it, or drag its edge to resize it — lastAction shows up here."
    event = last_action.get("event") or {}
    return (
        f"lastAction.type: {last_action.get('type')}\n"
        f"event: {event.get('title', '-')}  "
        f"{event.get('start', '-')} -> {event.get('end', '-')}"
    )
