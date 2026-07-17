import os

from dash import html
import dash_mui_scheduler as dms

# On a timeline, resources are the ROWS. Each event sits on the row whose id
# matches its `resource` key. Resources carry their own eventColor.
resources = [
    {"id": "team-a", "title": "Team A", "eventColor": "blue"},
    {"id": "team-b", "title": "Team B", "eventColor": "green"},
    {"id": "team-c", "title": "Team C", "eventColor": "orange"},
]

# Allocation bars span days. Dates are ISO strings (never Python datetime),
# and `events` is both input and output — the component writes the full array
# back on every create, move, resize or delete.
events = [
    {
        "id": "alloc-1",
        "title": "Discovery",
        "start": "2024-01-15T09:00:00",
        "end": "2024-01-17T17:00:00",
        "resource": "team-a",
    },
    {
        "id": "alloc-2",
        "title": "Build phase",
        "start": "2024-01-18T09:00:00",
        "end": "2024-01-23T17:00:00",
        "resource": "team-a",
    },
    {
        "id": "alloc-3",
        "title": "API integration",
        "start": "2024-01-16T09:00:00",
        "end": "2024-01-20T17:00:00",
        "resource": "team-b",
    },
    {
        "id": "alloc-4",
        "title": "QA & hardening",
        "start": "2024-01-22T09:00:00",
        "end": "2024-01-25T17:00:00",
        "resource": "team-b",
    },
    {
        "id": "alloc-5",
        "title": "Launch prep",
        "start": "2024-01-19T09:00:00",
        "end": "2024-01-24T17:00:00",
        "resource": "team-c",
    },
]

component = html.Div(
    dms.EventTimeline(
        id="event_timeline-basic",
        licenseKey=os.environ.get("MUI_X_LICENSE_KEY", ""),
        events=events,
        resources=resources,
        resourceColumnLabel="Team",
        defaultPreset="dayAndWeek",
        defaultVisibleDate="2024-01-15",
        height=400,
    )
)
