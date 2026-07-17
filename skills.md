---
name: dash-mui-scheduler
description: >
  How to use the dash-mui-scheduler package — Dash components wrapping the MUI X
  Scheduler (EventCalendar, EventCalendarPremium, EventTimeline) and the MUI X
  Premium radial charts (RadialLineChart, RadialBarChart). Read this before
  writing any Dash code that renders a calendar, resource timeline, or polar
  chart with this library.
---

# dash-mui-scheduler — agent skill

Dash (≥2.11, works on Dash 4) component library wrapping the
[MUI X Scheduler](https://mui.com/x/react-scheduler/) plus two polar chart
wrappers from `@mui/x-charts-premium`. Everything crosses the Dash ↔ Python
boundary as plain dicts and ISO-8601 strings — no Python `datetime` objects,
no JSON serialization work on your side.

```bash
pip install dash-mui-scheduler
```

```python
import dash_mui_scheduler as dms
```

> ⚠️ The upstream MUI X Scheduler is **beta** (`@mui/x-scheduler@9.0.0-beta.0`,
> pinned exactly). The wrapper API here is stable per release, but expect
> upstream churn before MUI's stable cut.

## Pick the right component

| Component | Plan | Use when |
|---|---|---|
| `dms.EventCalendar` | Community (MIT, **no license key**) | Day/week/month/agenda calendar with drag-and-drop, resize, resources, event dialog. |
| `dms.EventCalendarPremium` | Premium | Same calendar **plus recurrence** (`rrule` events + exception dates). |
| `dms.EventTimeline` | Premium | Resource-row, Gantt-style timeline with zoom presets (`time`/`days`/`weeks`/`months`/`years`). |
| `dms.RadialLineChart` | Premium (preview) | Polar line/area chart — trends over periodic categories (months, hours, compass directions). |
| `dms.RadialBarChart` | Premium (preview) | Polar bar chart — comparisons over periodic categories. |

Premium components take a `licenseKey` string prop and render a watermark
without a valid MUI X Premium key. **Never hard-code a license string** — pass
it from the environment: `licenseKey=os.environ.get("MUI_X_LICENSE_KEY", "")`.
One key covers all Premium components (shared `@mui/x-license@9` singleton).

## The data boundary (core mental model)

- **`events` is both input AND output.** Seed it with a list of dicts; when the
  user creates, moves, resizes, edits, or deletes an event in the UI, the
  component writes the **full new array** back to the `events` prop. A callback
  with `Input("cal", "events")` sees the complete post-change list.
- **Event dict shape:** required keys `id`, `title`, `start`, `end`. Optional:
  `color`, `resource` (a resource id), `allDay`, `description`, `readOnly`, and
  (Premium calendar only) `rrule` / `exDates`.
- **Dates are ISO strings.** `"2024-01-15T10:00:00"` is wall time; suffix `Z`
  for UTC. Never pass `datetime` objects.
- **`lastAction` (read-only output)** reports the most recent user interaction:
  `{"type": "create"|"update"|"delete"|"move"|"resize", "event": {...}, "event_timestamp": ...}`.
  Use it to know *what* changed without diffing `events`. The `event_timestamp`
  makes consecutive identical actions distinct.
- **Controlled/uncontrolled pairs.** Stateful concepts each ship as a
  controlled prop plus an uncontrolled `default*` twin, written back on change:
  `view`/`defaultView`, `visibleDate`/`defaultVisibleDate`,
  `preferences`/`defaultPreferences`, `visibleResources`/`defaultVisibleResources`,
  and (timeline) `preset`/`defaultPreset`. Use the `default*` form unless a
  callback needs to drive the value; if you both read and write the controlled
  prop, remember Dash's `allow_duplicate=True` requires `prevent_initial_call`.
- **Dark mode is automatic** — components follow the surrounding Dash Mantine
  Components color scheme; don't wire theme callbacks.

## Quickstart (Community calendar)

```python
import dash
from dash import Dash, html, Input, Output, callback
import dash_mui_scheduler as dms

app = Dash(__name__)

events = [
    {"id": "1", "title": "Standup",       "start": "2024-01-15T09:00:00", "end": "2024-01-15T09:30:00", "color": "blue"},
    {"id": "2", "title": "Design Review", "start": "2024-01-16T13:00:00", "end": "2024-01-16T14:30:00", "color": "purple"},
]

app.layout = html.Div(
    dms.EventCalendar(
        id="cal",
        events=events,
        defaultVisibleDate="2024-01-15",
        defaultView="week",          # "day" | "week" | "month" | "agenda"
        height=600,
    )
)

@callback(Output("cal", "events"), Input("cal", "lastAction"), prevent_initial_call=True)
def on_change(last_action):
    # last_action = {"type": "move", "event": {...}, "event_timestamp": ...}
    return dash.no_update   # or a corrected/persisted events list

if __name__ == "__main__":
    app.run(debug=True)
```

## Scheduler props that matter (calendar + timeline)

- `events`, `lastAction` — the boundary (above).
- `resources` — `[{"id": "r1", "name": "Room 1", "eventColor": "teal"}, ...]`;
  events point at one via `"resource": "r1"`. `visibleResources` is a dict of
  `{resource_id: bool}` (unlisted ⇒ visible). `shouldEventRequireResource`
  forces the dialog to demand one.
- `views` / `view` / `defaultView` (calendar) — subset of
  `["day", "week", "month", "agenda"]`.
- `preset` / `presets` (timeline) — zoom levels among
  `"time" | "days" | "weeks" | "months" | "years"`; `resourceColumnLabel`
  titles the left column.
- Interaction switches: `areEventsDraggable`, `areEventsResizable`
  (bool or `"start"`/`"end"`), `eventCreation` (bool or config dict),
  `readOnly` (kills all editing), `canDragEventsFromTheOutside` /
  `canDropEventsToTheOutside` (cross-component drag).
- Display: `height` (number or CSS string), `sx` (MUI system styles),
  `eventColor` (default palette name), `showCurrentTimeIndicator`,
  `scrollToCurrentTime`, `displayTimezone` (IANA name — shifts *display*, not
  data), `localeText` (translation overrides), `preferences` /
  `preferencesMenuConfig` (e.g. `{"ampm": False, "showWeekends": True}`),
  `eventDialogVariant`, `eventDialogTopOffset`, `responsiveSidePanel`,
  `mobileBreakpoint`.
- `EventCalendarPremium` = `EventCalendar` + `licenseKey` + recurrence:
  events may carry `"rrule": "FREQ=WEEKLY;BYDAY=MO,WE"` (RFC 5545 string) and
  `"exDates": ["2024-02-05T09:00:00"]`. Dragging one occurrence prompts
  this-event/all-events; `lastAction` reflects the outcome.

## Radial charts (RadialLineChart / RadialBarChart)

Row-oriented `dataset` + `series` referencing columns by `dataKey`.
`rotationAxis` is the angular (x-like) axis, `radiusAxis` the radial (y-like):

```python
import os
import dash_mui_scheduler as dms

dms.RadialLineChart(
    id="polar",
    height=400,
    licenseKey=os.environ.get("MUI_X_LICENSE_KEY", ""),
    dataset=[{"month": "Jan", "london": 49}, {"month": "Feb", "london": 38}],  # ...
    series=[{"dataKey": "london", "label": "London (mm)", "curve": "natural", "showMark": True}],
    rotationAxis=[{"scaleType": "point", "dataKey": "month", "disableLine": True}],
    radiusAxis=[{"disableLine": True}],
    grid={"rotation": True, "radius": True},
)
```

- Series options: `area`/`stack` (lines), `color`, `curve`; bars stack the same
  way. `colors` sets the palette; `hideLegend`, `skipAnimation`, `showToolbar`
  (Pro zoom toolbar), `slotProps` pass through.
- **`clickData` (read-only output)** fires on axis/item clicks —
  `Input("polar", "clickData")` for drill-downs.
- These wrap `Unstable_RadialChart` previews: functional, but upstream API may
  shift.

## Gotchas

- Event `id`s should be **strings** and unique; the component echoes whatever
  ids you seed, and generates ids for user-created events.
- Writing `events` from a callback **replaces** the whole array — merge, don't
  append blindly, or you'll drop concurrent UI edits.
- `lastAction` is `None` until the first interaction — guard your callback.
- Don't put `datetime`/`date` objects anywhere in `events`, `visibleDate`, or
  `dataset` — serialize to ISO strings first.
- The style props (`style`, `className`, `sx`, `height`) are the supported
  sizing path; the calendar fills its container width.
- All components load from one bundled JS file — no extra `external_scripts`,
  CSS, or React setup needed.

## Repo pointers (when working in this repository)

- React sources: `src/lib/components/*.react.js`; **built bundle + generated
  Python wrappers are committed** (`dash_mui_scheduler/`). After editing
  `src/`: `npm install && npm run build`, then commit the regenerated artifacts.
- Live docs site: `python run.py` (`DASH_BACKEND=flask PORT=8560` for dev);
  each page is `docs/<page>/<page>.md` + example `.py` modules setting
  `component = ...`.
- Version lives in `package.json` (read by `setup.py`) — keep them in sync.
- Full prop tables: the generated docstrings in
  `dash_mui_scheduler/<Component>.py`, or the `.. kwargs::` tables on the docs
  site.
