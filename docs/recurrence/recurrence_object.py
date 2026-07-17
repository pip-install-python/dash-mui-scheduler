import os

from dash import Input, Output, callback
import dash_mantine_components as dmc
import dash_mui_scheduler as dms

# `rrule` may also be an object instead of a string. Here the event recurs
# every weekday morning for a total of 10 occurrences, but two specific
# dates are removed from the series via `exDates` (ISO strings).
events = [
    {
        "id": "yoga",
        "title": "Morning Yoga",
        "start": "2024-01-15T08:00:00",
        "end": "2024-01-15T08:45:00",
        "color": "green",
        "rrule": {
            "freq": "WEEKLY",
            "interval": 1,
            "byDay": ["MO", "TU", "WE", "TH", "FR"],
            "count": 10,
        },
        "exDates": [
            "2024-01-17T08:00:00",
            "2024-01-19T08:00:00",
        ],
    },
]

component = dmc.Stack(
    [
        dms.EventCalendarPremium(
            id="recurrence-object-cal",
            licenseKey=os.environ.get("MUI_X_LICENSE_KEY", ""),
            events=events,
            defaultView="week",
            defaultVisibleDate="2024-01-15",
            height=600,
        ),
        dmc.Text("Occurrence count in events output:", fw=600, size="sm"),
        dmc.Code(id="recurrence-object-count", block=True),
    ],
    gap="sm",
)


@callback(
    Output("recurrence-object-count", "children"),
    Input("recurrence-object-cal", "events"),
)
def show_count(events_out):
    # The component writes the full event array back on every edit. The
    # recurring definition stays a single dict with `rrule`/`exDates`;
    # the UI expands it into occurrences for display only.
    return f"{len(events_out or [])} stored event definition(s)"
