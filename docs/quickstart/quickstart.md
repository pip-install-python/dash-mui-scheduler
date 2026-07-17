---
name: Quickstart
description: Install dash-mui-scheduler and render your first MUI X Scheduler calendar and timeline in Dash.
endpoint: /quickstart
package: dash_mui_scheduler
icon: mdi:rocket-launch-outline
---

.. llms_copy::Quickstart

.. toc::

### Installation

`dash-mui-scheduler` wraps the [MUI X Scheduler](https://mui.com/x/react-scheduler/) for Dash.
Install it from PyPI:

```bash
pip install dash-mui-scheduler
```

.. admonition::Beta
    :color: yellow

    The MUI X Scheduler is in beta, and so are these wrappers. Props and behaviour may
    change between releases. Pin your version if you need stability.

There are three components:

- `dms.EventCalendar` — Community (MIT). Day / week / month / agenda calendar. No license key.
- `dms.EventCalendarPremium` — adds recurrence (`rrule` / `exDates`). Needs a `licenseKey`.
- `dms.EventTimeline` — Premium resource-row timeline. Needs a `licenseKey`.

This page covers the two you will reach for first: `EventCalendar` and `EventTimeline`.

### Rendering an Event Calendar

Import the package as `dms`, hand it a list of events, and point it at a date. A standalone
calendar is **already fully interactive** — drag, resize, create, and delete all work and
persist through Dash's own `setProps` round-trip, with no callback required.

The `dcc.Markdown` readout below is wired to the calendar's `lastAction` output so you can
watch each edit as it happens (see [Reading changes](#reading-changes)).

.. exec::docs.quickstart.render_calendar

.. source::docs/quickstart/render_calendar.py

### The events model

`events` is a list of plain dicts. **Dates are ISO strings**, never Python `datetime`
objects. A string with no trailing `Z` (e.g. `"2024-01-15T10:00:00"`) is wall time; a
trailing `Z` (e.g. `"2024-01-15T10:00:00Z"`) is UTC.

Every event requires four keys:

| Key | Type | Example |
| --- | --- | --- |
| `id` | str or int | `"1"` |
| `title` | str | `"Team Standup"` |
| `start` | ISO str | `"2024-01-15T09:00:00"` |
| `end` | ISO str | `"2024-01-15T09:30:00"` |

Common optional keys include `color` (one of the 11 palette names: `red`, `pink`, `purple`,
`indigo`, `blue`, `teal`, `green`, `lime`, `amber`, `orange`, `grey`), `description`,
`allDay`, `resource`, `draggable`, `resizable`, and `readOnly`.

.. admonition::events is both input and output
    :color: blue

    The component writes the **entire new array** back to `events` on every create, move,
    resize, or delete. Read `events` in a callback to get the current state, or read
    `lastAction` to get just the change that triggered it.

### Reading changes

You never need a callback to make the calendar work — only to **display** what changed.
`lastAction` is an output-only prop shaped like
`{type, event, event_timestamp}`, where `type` is one of
`create`, `update`, `delete`, `move`, `resize`, or `change`, and `event` is the affected
event dict (or `None` for some actions).

The example above attaches this minimal callback to surface it:

```python
@callback(
    Output("quickstart-cal-readout", "children"),
    Input("quickstart-cal", "lastAction"),
)
def show_last_action(last_action):
    if not last_action:
        return "_Drag, create, or delete an event to see the last action._"
    action_type = last_action.get("type")
    event = last_action.get("event") or {}
    return f"**{action_type}** → `{event.get('title', '—')}`"
```

Create or drag an event in the calendar above and the readout updates in place.

### Rendering an Event Timeline

`EventTimeline` is the Premium resource-row view — a Gantt-style layout where each
**resource** is a row and each event sits on the row named by its `resource` id. Resources
are dicts like `{"id": "team-a", "title": "Team A"}`. The timeline shares the same events
model (ISO strings, `events` in/out, `lastAction`); it just adds zoom `preset`s such as
`dayAndHour` (default), `dayAndWeek`, and `monthAndYear`.

.. admonition::Premium
    :color: yellow

    `EventTimeline` (and `EventCalendarPremium`) are Premium components. Without a valid
    `licenseKey` they render with a watermark — that is expected. Set
    `MUI_X_LICENSE_KEY` in your environment to remove it. The component still functions
    either way.

.. exec::docs.quickstart.render_timeline

.. source::docs/quickstart/render_timeline.py

### EventCalendar props

The full, auto-generated prop reference for the Community `EventCalendar`:

.. kwargs::dash_mui_scheduler.EventCalendar
