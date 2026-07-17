import os

import dash_mantine_components as dmc
import dash_mui_scheduler as dms

# Resources are the rows of the timeline. Each event points at a resource id.
resources = [
    {"id": "team-a", "title": "Team A"},
    {"id": "team-b", "title": "Team B"},
]

events = [
    {
        "id": "1",
        "title": "Migration",
        "start": "2024-01-15T09:00:00",
        "end": "2024-01-15T15:00:00",
        "resource": "team-a",
        "color": "indigo",
    },
    {
        "id": "2",
        "title": "QA Pass",
        "start": "2024-01-15T11:00:00",
        "end": "2024-01-15T18:00:00",
        "resource": "team-b",
        "color": "amber",
    },
]

component = dmc.Stack(
    [
        dms.EventTimeline(
            id="quickstart-timeline",
            licenseKey=os.environ.get("MUI_X_LICENSE_KEY", ""),
            resources=resources,
            events=events,
            resourceColumnLabel="Teams",
            defaultVisibleDate="2024-01-15",
            defaultPreset="dayAndHour",
            height=400,
        ),
    ],
    gap="sm",
)
