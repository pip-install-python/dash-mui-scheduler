import dash_mantine_components as dmc
from dash import html

import dash_mui_scheduler as dms

events = [
    {"id": "1", "title": "Sprint planning", "start": "2024-01-15T13:00:00", "end": "2024-01-15T14:00:00", "color": "indigo"},
    {"id": "2", "title": "Retro", "start": "2024-01-18T15:00:00", "end": "2024-01-18T16:00:00", "color": "amber"},
]

# preferencesMenuConfig prunes the gear/preferences menu.
# Pass a dict to toggle individual items, or False to hide the whole menu.
component = dmc.Stack(
    [
        dmc.Text("Custom menu — only weekends, week number, and AM/PM toggles", fw=600, size="sm"),
        dms.EventCalendar(
            id="preferences-menu-cal",
            height=480,
            events=events,
            defaultView="week",
            defaultVisibleDate="2024-01-15",
            preferencesMenuConfig={
                "toggleWeekendVisibility": True,
                "toggleWeekNumberVisibility": True,
                "toggleAmpm": True,
                "toggleEmptyDaysInAgenda": False,
                "toggleWeekStartsOn": False,
            },
        ),
        dmc.Text("Menu hidden — preferencesMenuConfig=False (no gear button)", fw=600, size="sm", mt="md"),
        dms.EventCalendar(
            id="preferences-menu-hidden-cal",
            height=480,
            events=events,
            defaultView="week",
            defaultVisibleDate="2024-01-15",
            preferencesMenuConfig=False,
        ),
    ],
    gap="xs",
)
