import os

from dash import Input, Output, callback
import dash_mantine_components as dmc
import dash_mui_scheduler as dms

# Rows.
resources = [
    {"id": "mixer", "title": "Mixer", "eventColor": "purple"},
    {"id": "studio", "title": "Studio", "eventColor": "teal"},
]

# A few multi-day allocations so the effect of each zoom preset is visible.
events = [
    {
        "id": "preset-1",
        "title": "Album mixdown",
        "start": "2024-01-15T10:00:00",
        "end": "2024-01-19T18:00:00",
        "resource": "mixer",
    },
    {
        "id": "preset-2",
        "title": "Tracking sessions",
        "start": "2024-01-16T09:00:00",
        "end": "2024-01-22T20:00:00",
        "resource": "studio",
    },
    {
        "id": "preset-3",
        "title": "Mastering",
        "start": "2024-01-23T10:00:00",
        "end": "2024-01-25T16:00:00",
        "resource": "mixer",
    },
]

# `preset` is controlled in + out: the SegmentedControl drives the zoom level.
# The five presets are dayAndHour, dayAndMonth, dayAndWeek, monthAndYear, year.
presets = ["dayAndHour", "dayAndWeek", "dayAndMonth", "monthAndYear", "year"]

component = dmc.Stack(
    [
        dmc.SegmentedControl(
            id="event_timeline-presets-control",
            data=[
                {"label": "Day / Hour", "value": "dayAndHour"},
                {"label": "Day / Week", "value": "dayAndWeek"},
                {"label": "Day / Month", "value": "dayAndMonth"},
                {"label": "Month / Year", "value": "monthAndYear"},
                {"label": "Year", "value": "year"},
            ],
            value="dayAndWeek",
        ),
        dms.EventTimeline(
            id="event_timeline-presets",
            licenseKey=os.environ.get("MUI_X_LICENSE_KEY", ""),
            events=events,
            resources=resources,
            resourceColumnLabel="Resource",
            presets=presets,
            preset="dayAndWeek",
            defaultVisibleDate="2024-01-15",
            height=400,
        ),
    ],
    gap="sm",
)


@callback(
    Output("event_timeline-presets", "preset"),
    Input("event_timeline-presets-control", "value"),
)
def set_preset(value):
    return value
