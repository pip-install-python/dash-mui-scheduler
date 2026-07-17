import datetime

import dash_mantine_components as dmc
from dash import Input, Output, callback
import dash_mui_scheduler as dms

# A live playground: every Dash Mantine Components input below is wired to a
# major EventCalendar prop, so you can see exactly how each one behaves. This is
# also a demonstration of how dash-mui-scheduler pairs with DMC — the calendar
# follows the Mantine color scheme, and DMC inputs drive its props.

# Anchor events to *today* (with UTC "Z" instants) so the Display controls have
# something to act on:
#   - the current-time line is visible (we are looking at this week),
#   - `displayTimezone` shifts the rendered times (Z instants are re-projected),
#   - and with NO per-event `color`, `eventColor` recolours every event live
#     (a per-event color would otherwise override the component default).
_TODAY = datetime.date.today()


def _ev(eid, title, day_offset, hour, minute, dur_min):
    start = datetime.datetime.combine(
        _TODAY + datetime.timedelta(days=day_offset), datetime.time(hour, minute)
    )
    end = start + datetime.timedelta(minutes=dur_min)
    fmt = "%Y-%m-%dT%H:%M:%SZ"  # trailing Z = UTC instant
    return {"id": eid, "title": title, "start": start.strftime(fmt), "end": end.strftime(fmt)}


EVENTS = [
    _ev("1", "Standup", 0, 13, 0, 30),
    _ev("2", "Design review", 0, 15, 30, 60),
    _ev("3", "Workshop", 1, 14, 0, 90),
    _ev("4", "1:1", 2, 16, 0, 30),
    _ev("5", "Retro", -1, 17, 0, 60),
]

COLORS = ["red", "pink", "purple", "indigo", "blue", "teal", "green", "lime", "amber", "orange", "grey"]
WEEKDAYS = [
    {"label": "Sunday", "value": "0"}, {"label": "Monday", "value": "1"}, {"label": "Tuesday", "value": "2"},
    {"label": "Wednesday", "value": "3"}, {"label": "Thursday", "value": "4"}, {"label": "Friday", "value": "5"},
    {"label": "Saturday", "value": "6"},
]
TIMEZONES = ["default", "UTC", "America/New_York", "Europe/Paris", "Asia/Tokyo"]


def _labeled(label, control):
    return dmc.Stack([dmc.Text(label, size="sm", fw=600), control], gap=4)


_controls = dmc.SimpleGrid(
    cols={"base": 1, "md": 2},
    spacing="lg",
    children=[
        dmc.Fieldset(
            legend="View & creation",
            children=dmc.Stack([
                _labeled("View", dmc.SegmentedControl(id="pg-view", value="week", fullWidth=True, data=[
                    {"label": "Day", "value": "day"}, {"label": "Week", "value": "week"},
                    {"label": "Month", "value": "month"}, {"label": "Agenda", "value": "agenda"}])),
                _labeled("Event editor", dmc.SegmentedControl(id="pg-dialog", value="drawer", data=[
                    {"label": "Drawer", "value": "drawer"}, {"label": "Dialog", "value": "dialog"}])),
                dmc.Switch(id="pg-creation", label="Allow event creation", checked=True),
            ], gap="sm"),
        ),
        dmc.Fieldset(
            legend="Interaction",
            children=dmc.Stack([
                dmc.Switch(id="pg-drag", label="Events draggable", checked=True),
                _labeled("Resizable", dmc.SegmentedControl(id="pg-resize", value="true", data=[
                    {"label": "Both", "value": "true"}, {"label": "Start", "value": "start"},
                    {"label": "End", "value": "end"}, {"label": "Off", "value": "false"}])),
                dmc.Switch(id="pg-readonly", label="Read-only", checked=False),
            ], gap="sm"),
        ),
        dmc.Fieldset(
            legend="Display",
            children=dmc.Stack([
                dmc.Select(id="pg-color", label="Default event color", value="teal", data=COLORS, allowDeselect=False),
                dmc.Select(id="pg-tz", label="Display timezone", value="default", data=TIMEZONES, allowDeselect=False),
                dmc.Switch(id="pg-nowline", label="Current-time line", checked=True),
                dmc.Switch(id="pg-scrollnow", label="Scroll to current time on load", checked=False),
            ], gap="sm"),
        ),
        dmc.Fieldset(
            legend="Preferences",
            children=dmc.Stack([
                dmc.Group([
                    dmc.Switch(id="pg-ampm", label="12-hour clock", checked=True),
                    dmc.Switch(id="pg-weekends", label="Weekends", checked=True),
                ], gap="lg"),
                dmc.Group([
                    dmc.Switch(id="pg-weeknum", label="Week numbers", checked=False),
                    dmc.Switch(id="pg-sidepanel", label="Side panel", checked=True),
                ], gap="lg"),
                dmc.Switch(id="pg-emptyagenda", label="Empty days in agenda", checked=True),
                dmc.Select(id="pg-weekstart", label="Week starts on", value="0", data=WEEKDAYS, allowDeselect=False),
            ], gap="sm"),
        ),
    ],
)

component = dmc.Stack(
    [
        dmc.Paper(_controls, withBorder=True, p="md", radius="md"),
        dms.EventCalendar(
            id="playground-cal",
            events=EVENTS,
            defaultVisibleDate=_TODAY.isoformat(),
            height=620,
            view="week",
            eventColor="teal",
            displayTimezone="default",
            areEventsDraggable=True,
            areEventsResizable=True,
            readOnly=False,
            eventCreation=True,
            showCurrentTimeIndicator=True,
            scrollToCurrentTime=False,
            eventDialogVariant="drawer",
            preferences={"ampm": True, "weekStartsOn": 0, "showWeekends": True,
                         "showWeekNumber": False, "isSidePanelOpen": True, "showEmptyDaysInAgenda": True},
        ),
        dmc.Code(id="pg-readout", block=True),
    ],
    gap="md",
)


# --- View (two-way: control <-> the calendar's own view buttons) ------------
@callback(Output("playground-cal", "view"), Input("pg-view", "value"), prevent_initial_call=True)
def set_view(value):
    return value


@callback(Output("pg-view", "value"), Input("playground-cal", "view"), prevent_initial_call=True)
def read_view(value):
    return value


# --- Display / interaction / editor settings --------------------------------
@callback(
    Output("playground-cal", "eventColor"),
    Output("playground-cal", "displayTimezone"),
    Output("playground-cal", "showCurrentTimeIndicator"),
    Output("playground-cal", "scrollToCurrentTime"),
    Output("playground-cal", "areEventsDraggable"),
    Output("playground-cal", "areEventsResizable"),
    Output("playground-cal", "readOnly"),
    Output("playground-cal", "eventCreation"),
    Output("playground-cal", "eventDialogVariant"),
    Input("pg-color", "value"),
    Input("pg-tz", "value"),
    Input("pg-nowline", "checked"),
    Input("pg-scrollnow", "checked"),
    Input("pg-drag", "checked"),
    Input("pg-resize", "value"),
    Input("pg-readonly", "checked"),
    Input("pg-creation", "checked"),
    Input("pg-dialog", "value"),
)
def settings(color, tz, nowline, scroll_now, drag, resize, read_only, creation, dialog):
    resize_val = {"true": True, "false": False, "start": "start", "end": "end"}[resize]
    return color, tz, nowline, scroll_now, drag, resize_val, read_only, creation, dialog


# --- Preferences ------------------------------------------------------------
@callback(
    Output("playground-cal", "preferences"),
    Input("pg-ampm", "checked"),
    Input("pg-weekstart", "value"),
    Input("pg-weekends", "checked"),
    Input("pg-weeknum", "checked"),
    Input("pg-sidepanel", "checked"),
    Input("pg-emptyagenda", "checked"),
)
def preferences(ampm, week_start, weekends, week_number, side_panel, empty_agenda):
    return {
        "ampm": ampm,
        "weekStartsOn": int(week_start),
        "showWeekends": weekends,
        "showWeekNumber": week_number,
        "isSidePanelOpen": side_panel,
        "showEmptyDaysInAgenda": empty_agenda,
    }


# --- Live readout -----------------------------------------------------------
@callback(
    Output("pg-readout", "children"),
    Input("playground-cal", "events"),
    Input("playground-cal", "lastAction"),
)
def readout(events, last_action):
    count = len(events or [])
    if not last_action:
        return f"{count} events · interact with the calendar to see the last action"
    title = (last_action.get("event") or {}).get("title")
    suffix = f" — {title}" if title else ""
    return f"{count} events · last action: {last_action.get('type')}{suffix}"
