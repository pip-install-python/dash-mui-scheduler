---
name: Event Calendar
description: The EventCalendar component — a day/week/month/agenda calendar whose events round-trip across the Dash boundary as plain dicts with ISO-string dates.
endpoint: /event-calendar
lastmod: 2026-07-16
package: dash_mui_scheduler
icon: mdi:calendar-month
---

.. llms_copy::Event Calendar

.. toc::

### Overview

`dms.EventCalendar` wraps the **MUI X Event Calendar** (Community, MIT — no
license key required). It renders a day / week / month / agenda calendar that
your users can read and edit: create, drag-to-reschedule, resize and delete
events directly in the UI.

```python
import dash_mui_scheduler as dms
```

The calendar is **interactive on its own**. A standalone `dms.EventCalendar`
with no callback already persists every create / move / resize / delete,
because each edit round-trips through Dash's own `setProps`. You only add a
callback when you want to *observe* the result — to render the current events,
react to the last action, or sync `view` / `visibleDate` elsewhere.

.. admonition::Beta component
    :color: blue

    The MUI X Scheduler is in beta. APIs may shift between releases. The props
    documented here are the ones the Dash wrapper exposes today.

### The data boundary

Everything the calendar shows and everything the user changes crosses the Dash
boundary as **plain, JSON-serializable values** — no Python `datetime` objects,
no functions. Dates are **ISO strings**.

#### Events in, events out

`events` is a list of dicts and is **both an input and an output**. You pass
events in; the calendar writes the *full new array* back to the same prop on
every create, move, resize and delete. Read it from a callback to keep your
own state in sync.

Each event dict has four **required** keys:

| Key     | Type        | Notes                                                        |
| ------- | ----------- | ------------------------------------------------------------ |
| `id`    | str \| int  | Unique within the array.                                     |
| `title` | str         | Shown on the event block.                                    |
| `start` | ISO str     | e.g. `"2024-01-15T09:00:00"`. A trailing `Z` means UTC.      |
| `end`   | ISO str     | Same format as `start`.                                      |

Common **optional** keys: `description`, `resource` (a resource id), `allDay`,
`color` (one of the 11 palette names), `timezone` (IANA name), `draggable`,
`resizable` (`bool | 'start' | 'end'`), `readOnly` and `className`. On
`EventCalendarPremium`, events may also carry `rrule` and `exDates` for
recurrence.

.. admonition::ISO strings, not datetimes
    :color: yellow

    Always pass dates as strings. `"2024-01-15T10:00:00"` (no `Z`) is *wall
    time*; `"2024-01-15T10:00:00Z"` is a UTC instant. `displayTimezone`
    controls only how events are *rendered* — it never rewrites their data.

#### lastAction (output only)

`lastAction` is a convenience **output** describing the most recent change to
`events`. It is a dict:

```python
{"type": "move", "event": { ... }, "event_timestamp": 1705312800000}
```

`type` tells you what just happened:

| `type`   | When it fires                                            | `event`            |
| -------- | ------------------------------------------------------- | ------------------ |
| `create` | A new event was added in the UI.                        | the new event      |
| `update` | An event's fields were edited (e.g. via the dialog).    | the updated event  |
| `delete` | An event was removed.                                   | the removed event  |
| `move`   | An event was dragged to a new time / day.               | the moved event    |
| `resize` | An event's start or end edge was dragged.               | the resized event  |
| `change` | A bulk / unclassified change to the array.              | `None`             |

`event_timestamp` is an epoch-milliseconds integer — use it as a callback
trigger that changes on every action, even when the same event is touched
twice in a row.

#### Visible date and other controlled props

`visibleDate` is an ISO **date** string (e.g. `"2024-01-15"`) and is
controlled both in and out — it is written back when the user navigates. Its
uncontrolled twin is `defaultVisibleDate`. Several props follow the same
controlled / uncontrolled pattern: `view` / `defaultView`,
`preferences` / `defaultPreferences`, and
`visibleResources` / `defaultVisibleResources`.

.. admonition::Dark mode is automatic
    :color: green

    The calendar follows the surrounding Mantine color scheme. Do not write a
    theme callback — toggle your app's color scheme and the calendar follows.

### A controlled calendar

The example below keeps the calendar uncontrolled (it manages its own edits)
and adds a single callback that mirrors the two output sides of the boundary:
the live `events` array and the latest `lastAction`, both rendered as JSON.

Create, drag, resize or delete an event in the calendar and watch both panels
update. The events pinned around **2024-01-15** are visible on load because the
calendar starts at `defaultVisibleDate="2024-01-15"`.

.. exec::docs.event_calendar.overview

.. source::docs/event_calendar/overview.py

### Props

Full prop reference for `dms.EventCalendar`. Use only these props — do not
invent new ones.

.. kwargs::dash_mui_scheduler.EventCalendar
