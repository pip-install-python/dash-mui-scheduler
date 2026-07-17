from dash import html
import dash_mantine_components as dmc

import dash_mui_scheduler as dms

# One shared set of events. Each `start`/`end` is an ISO string.
# These carry no trailing "Z", so they are wall-clock times — the same
# instant the component then re-renders in whatever displayTimezone is set.
events = [
    {
        "id": "1",
        "title": "Morning sync",
        "start": "2024-01-15T09:00:00",
        "end": "2024-01-15T10:00:00",
        "color": "blue",
    },
    {
        "id": "2",
        "title": "Design review",
        "start": "2024-01-16T13:00:00",
        "end": "2024-01-16T14:30:00",
        "color": "purple",
    },
    {
        "id": "3",
        "title": "Release window (UTC)",
        "start": "2024-01-17T18:00:00Z",
        "end": "2024-01-17T19:00:00Z",
        "color": "green",
    },
]

# Two calendars, identical events, different `displayTimezone`.
# displayTimezone is render-only: it shifts where blocks appear on the grid,
# but the underlying event data (the ISO strings above) never changes.
component = dmc.Stack(
    [
        dmc.Text("New York (America/New_York)", fw=600, size="sm"),
        dms.EventCalendar(
            id="localization-tz-ny-cal",
            events=events,
            defaultView="week",
            defaultVisibleDate="2024-01-15",
            displayTimezone="America/New_York",
            height=560,
        ),
        dmc.Text("Tokyo (Asia/Tokyo)", fw=600, size="sm"),
        dms.EventCalendar(
            id="localization-tz-tokyo-cal",
            events=events,
            defaultView="week",
            defaultVisibleDate="2024-01-15",
            displayTimezone="Asia/Tokyo",
            height=560,
        ),
    ],
    gap="sm",
)
