---
name: Event Timeline
description: Build a resource-row, Gantt-style timeline in dash-mui-scheduler with EventTimeline — resources as rows, multi-day allocation bars and zoom presets.
endpoint: /event-timeline
lastmod: 2026-07-16
package: dash_mui_scheduler
icon: mdi:chart-timeline
---

.. llms_copy::Event Timeline

.. toc::

### Event Timeline (Premium)

`dms.EventTimeline` is a resource-row, Gantt-style timeline. Where the calendar
lays events out on a day/week/month grid, the timeline turns each **resource
into a row** and draws every event as a horizontal allocation bar on its row,
across a configurable zoom `preset`. It wraps the MUI X `EventTimelinePremium`
and, like every component here, is currently **beta**.

.. admonition::Premium
    :color: yellow

    `EventTimeline` requires a MUI X Premium license key. Pass it via
    `licenseKey=os.environ.get("MUI_X_LICENSE_KEY", "")`. Without a valid key
    the timeline still renders and stays fully interactive, but a MUI watermark
    is drawn over it. That is expected — supply a real key to remove it.

The data boundary is the same as the calendar. `events` is a list of plain
dicts and is **both input and output**: the component writes the full array
back on every create, move, resize or delete. Dates are ISO **strings** (for
example `"2024-01-15T09:00:00"` for wall time, or a trailing `Z` for UTC),
never Python `datetime` objects. The read-only `lastAction` output is
`{type, event, event_timestamp}`, where `type` is one of `create`, `update`,
`delete`, `move`, `resize` or `change`.

### Resources as rows

A timeline needs `resources` — they are the rows. Each resource is a dict with
at least an `id` and `title`, plus an optional `eventColor`:

```python
resources = [
    {"id": "team-a", "title": "Team A", "eventColor": "blue"},
    {"id": "team-b", "title": "Team B", "eventColor": "green"},
]
```

Each event names its row through the `resource` key, which must match one of
the resource ids. On the timeline events should almost always have a
`resource` — `shouldEventRequireResource` defaults to `True` here. The column
that lists the row labels is titled with `resourceColumnLabel` (for example
`"Team"`). The example below places several multi-day allocation bars across
three rows and opens at the `dayAndWeek` zoom level.

.. exec::docs.event_timeline.timeline_basic

.. source::docs/event_timeline/timeline_basic.py

### Zoom presets

A preset controls how much time one screen of the timeline spans and how the
header is divided. There are five: `dayAndHour` (the default), `dayAndMonth`,
`dayAndWeek`, `monthAndYear` and `year`. Two props drive this:

- `defaultPreset` / `preset` — the active zoom level. `defaultPreset` is
  uncontrolled (set it once at load); `preset` is controlled **in + out**, so a
  callback can both set it and read the user's changes back.
- `presets` — the list of presets offered in the timeline's own zoom switcher.

To drive the zoom from your own UI, wire a `dmc.SegmentedControl` to the
`preset` prop. Because `preset` is controlled in + out, the callback below sets
the zoom whenever the segmented control changes:

```python
@callback(
    Output("event_timeline-presets", "preset"),
    Input("event_timeline-presets-control", "value"),
)
def set_preset(value):
    return value
```

.. exec::docs.event_timeline.timeline_presets

.. source::docs/event_timeline/timeline_presets.py

### EventTimeline props

`EventTimeline` shares most of its props with the calendar (events, resources,
visibility, drag/resize flags, preferences, timezone) and adds the timeline
specifics: `resourceColumnLabel`, `preset` / `defaultPreset` and `presets`. It
needs a `licenseKey`.

.. kwargs::dash_mui_scheduler.EventTimeline
