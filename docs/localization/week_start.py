from dash import html

import dash_mui_scheduler as dms

events = [
    {
        "id": "1",
        "title": "Sprint planning",
        "start": "2024-01-15T09:00:00",
        "end": "2024-01-15T10:30:00",
        "color": "indigo",
    },
    {
        "id": "2",
        "title": "Saturday demo",
        "start": "2024-01-20T11:00:00",
        "end": "2024-01-20T12:00:00",
        "color": "amber",
    },
    {
        "id": "3",
        "title": "Sunday on-call",
        "start": "2024-01-21T08:00:00",
        "end": "2024-01-21T09:00:00",
        "color": "red",
    },
]

# weekStartsOn (0 = Sunday … 6 = Saturday) and ampm live inside preferences.
# Here defaultPreferences seeds a Monday-first, 24-hour calendar on load.
component = html.Div(
    dms.EventCalendar(
        id="localization-week-start-cal",
        events=events,
        defaultView="week",
        defaultVisibleDate="2024-01-15",
        defaultPreferences={
            "weekStartsOn": 1,
            "ampm": False,
            "showWeekends": True,
            "showWeekNumber": True,
        },
        height=560,
    )
)
