from dash import html
import dash_mui_scheduler as dms

# Resources are the categories you schedule against. Each one carries its own
# eventColor; events inherit that color by pointing `resource` at the id.
resources = [
    {"id": "design", "title": "Design", "eventColor": "purple"},
    {"id": "engineering", "title": "Engineering", "eventColor": "blue"},
    {"id": "marketing", "title": "Marketing", "eventColor": "amber"},
]

# Dates are ISO strings. Each event names its resource via the `resource` key,
# which must match one of the resource ids above.
events = [
    {
        "id": "1",
        "title": "Wireframe review",
        "start": "2024-01-15T09:00:00",
        "end": "2024-01-15T10:30:00",
        "resource": "design",
    },
    {
        "id": "2",
        "title": "API sprint planning",
        "start": "2024-01-15T11:00:00",
        "end": "2024-01-15T12:00:00",
        "resource": "engineering",
    },
    {
        "id": "3",
        "title": "Launch campaign sync",
        "start": "2024-01-16T14:00:00",
        "end": "2024-01-16T15:00:00",
        "resource": "marketing",
    },
    {
        "id": "4",
        "title": "Component build",
        "start": "2024-01-17T10:00:00",
        "end": "2024-01-17T13:00:00",
        "resource": "engineering",
    },
]

component = html.Div(
    dms.EventCalendar(
        id="resources-basic-cal",
        events=events,
        resources=resources,
        defaultView="week",
        defaultVisibleDate="2024-01-15",
        height=600,
    )
)
