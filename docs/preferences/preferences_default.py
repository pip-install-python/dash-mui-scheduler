import json

import dash_mantine_components as dmc
from dash import Input, Output, State, callback, html

import dash_mui_scheduler as dms

events = [
    {"id": "1", "title": "Design review", "start": "2024-01-15T09:00:00", "end": "2024-01-15T10:30:00", "color": "blue"},
    {"id": "2", "title": "Saturday standup", "start": "2024-01-20T11:00:00", "end": "2024-01-20T12:00:00", "color": "green"},
]

# `preferences` is controlled IN + OUT. We seed it, drive it from the switches
# below, and read it back in a callback. (The calendar also writes it back when
# the user toggles a setting in its own gear menu.)
INITIAL = {
    "ampm": False,
    "weekStartsOn": 1,
    "showWeekends": True,
    "showWeekNumber": True,
    "isSidePanelOpen": True,
    "showEmptyDaysInAgenda": True,
}

component = html.Div(
    [
        dmc.Group(
            [
                dmc.Switch(id="pref-ampm", label="12-hour clock", checked=INITIAL["ampm"]),
                dmc.Switch(id="pref-weekends", label="Show weekends", checked=INITIAL["showWeekends"]),
                dmc.Switch(id="pref-weeknum", label="Week numbers", checked=INITIAL["showWeekNumber"]),
            ],
            mb="md",
        ),
        dms.EventCalendar(
            id="preferences-default-cal",
            height=560,
            events=events,
            defaultView="week",
            defaultVisibleDate="2024-01-15",
            preferences=INITIAL,
        ),
        dmc.Code(id="preferences-default-readout", block=True, mt="sm"),
    ]
)


@callback(
    Output("preferences-default-cal", "preferences"),
    Input("pref-ampm", "checked"),
    Input("pref-weekends", "checked"),
    Input("pref-weeknum", "checked"),
    State("preferences-default-cal", "preferences"),
    prevent_initial_call=True,
)
def set_preferences(ampm, weekends, week_number, current):
    prefs = dict(current or INITIAL)
    prefs.update({"ampm": ampm, "showWeekends": weekends, "showWeekNumber": week_number})
    return prefs


@callback(
    Output("preferences-default-readout", "children"),
    Input("preferences-default-cal", "preferences"),
)
def show_preferences(preferences):
    # `preferences` flows back out whenever it changes — from the switches above
    # or from the calendar's own gear menu.
    return json.dumps(preferences or INITIAL, indent=2, sort_keys=True)
