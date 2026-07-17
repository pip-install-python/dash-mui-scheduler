import dash_mui_scheduler as dms
from dash import html

# allDay events render in the calendar's all-day row, spanning whole days.
# Mix them freely with ordinary timed events.
events = [
    # All-day events: allDay=True. The time portion of start/end is ignored,
    # but keep them as valid ISO strings. end is exclusive of its last instant,
    # so a single-day all-day event ends the same day.
    {
        "id": "allday-holiday",
        "title": "Company Holiday",
        "start": "2024-01-15T00:00:00",
        "end": "2024-01-15T23:59:59",
        "allDay": True,
        "color": "green",
    },
    {
        "id": "allday-conference",
        "title": "Conference (3 days)",
        "start": "2024-01-17T00:00:00",
        "end": "2024-01-19T23:59:59",
        "allDay": True,
        "color": "indigo",
    },
    # Ordinary timed events sit in the day grid below the all-day row.
    {
        "id": "allday-call",
        "title": "Client Call",
        "start": "2024-01-16T10:00:00",
        "end": "2024-01-16T10:30:00",
        "color": "blue",
    },
    {
        "id": "allday-lunch",
        "title": "Team Lunch",
        "start": "2024-01-18T12:00:00",
        "end": "2024-01-18T13:00:00",
        "color": "amber",
    },
]

component = html.Div(
    dms.EventCalendar(
        id="events-allday-cal",
        events=events,
        defaultVisibleDate="2024-01-15",
        height=600,
    )
)
