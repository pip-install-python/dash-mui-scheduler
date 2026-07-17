import datetime

from dash import html
import dash_mui_scheduler as dms

_today = datetime.date.today()


def _iso(day, hour, minute=0):
    return datetime.datetime.combine(
        day, datetime.time(hour, minute)
    ).strftime("%Y-%m-%dT%H:%M:%S")


events = [
    {"id": "rni-1", "title": "Morning sync", "start": _iso(_today, 9), "end": _iso(_today, 9, 30), "color": "blue"},
    {"id": "rni-2", "title": "Focus block", "start": _iso(_today, 11), "end": _iso(_today, 12, 30), "color": "teal"},
    {"id": "rni-3", "title": "1:1", "start": _iso(_today, 15), "end": _iso(_today, 15, 45), "color": "purple"},
]

# `scrollToCurrentTime` pans the week grid so the red "now" line is centered on
# first render — no more scrolling up from midnight. It pairs with the default
# `showCurrentTimeIndicator`.
component = html.Div(
    dms.EventCalendar(
        id="responsive-now-cal",
        events=events,
        defaultView="week",
        defaultVisibleDate=_today.isoformat(),
        scrollToCurrentTime=True,
        showCurrentTimeIndicator=True,
        height=600,
    )
)
