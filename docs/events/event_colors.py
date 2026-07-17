import dash_mui_scheduler as dms
from dash import html

# The 11-color palette. Set a per-event "color" with any of these names.
PALETTE = [
    "red", "pink", "purple", "indigo", "blue",
    "teal", "green", "lime", "amber", "orange", "grey",
]

# One event per palette color, laid across the week so each is visible.
events = []
for i, name in enumerate(PALETTE):
    day = 15 + (i % 5)          # Mon–Fri of the week of 2024-01-15
    hour = 8 + (i // 5) * 3      # stagger rows so they don't overlap
    events.append(
        {
            "id": f"color-{name}",
            "title": name.capitalize(),
            "start": f"2024-01-{day:02d}T{hour:02d}:00:00",
            "end": f"2024-01-{day:02d}T{hour:02d}:45:00",
            "color": name,
        }
    )

# This event has no "color" of its own, so it falls back to eventColor below.
events.append(
    {
        "id": "color-default",
        "title": "Uses eventColor",
        "start": "2024-01-19T13:00:00",
        "end": "2024-01-19T14:00:00",
    }
)

component = html.Div(
    dms.EventCalendar(
        id="events-colors-cal",
        events=events,
        # eventColor is the calendar-wide default for any event without its
        # own "color" key. Per-event "color" always wins over this.
        eventColor="purple",
        defaultVisibleDate="2024-01-15",
        height=620,
    )
)
