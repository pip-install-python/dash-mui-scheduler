---
name: Events
description: Define calendar events as plain dictionaries with ISO-string dates — including colors, all-day events, and creation controls.
endpoint: /events
lastmod: 2026-07-16
package: dash_mui_scheduler
icon: mdi:calendar-text
---

.. llms_copy::Events

.. toc::

### Events

An event is just a Python `dict`. You pass a list of them to the `events` prop, and
the calendar renders one block per event. Dates cross the boundary as **ISO strings**,
never Python `datetime` objects.

The `events` prop is both an **input and an output**: when a user creates, moves,
resizes, or deletes an event, the component writes the *entire* new array back to
`events`. You don't diff anything yourself — read `events` for the full picture, or
read `lastAction` for just-what-changed.

.. exec::docs.events.events_basic

.. source::docs/events/events_basic.py

The callback above only *reads* `events` to display a count. The calendar is fully
interactive **without any callback** — drag, create, and delete all persist on their
own through Dash's normal `setProps` round-trip. Add a callback only when you want to
*display* an output (`events`, `lastAction`, `view`, or `visibleDate`).

### Event fields

Every event needs four required keys; the rest are optional.

| Key | Type | Notes |
|---|---|---|
| `id` | str \| int | Unique per event. **Required.** |
| `title` | str | Shown on the event block. **Required.** |
| `start` | ISO str | e.g. `"2024-01-15T10:00:00"`. **Required.** |
| `end` | ISO str | e.g. `"2024-01-15T11:00:00"`. **Required.** |
| `description` | str | Free-text shown in the event dialog. |
| `resource` | str | Id of a resource this event belongs to. |
| `allDay` | bool | Render in the all-day row (see below). |
| `color` | str | One of the 11 palette names (see below). |
| `timezone` | str | IANA name, e.g. `"America/New_York"`. |
| `draggable` | bool | Override drag for this one event. |
| `resizable` | bool \| `'start'` \| `'end'` | Override resize for this one event. |
| `readOnly` | bool | Make this event non-editable. |
| `className` | str | CSS class on the event element. |

.. admonition::ISO strings, not datetimes
    :color: yellow

    Dates must be ISO **strings**. A string without a `Z` suffix
    (`"2024-01-15T10:00:00"`) is treated as wall-clock time; a string with `Z`
    (`"2024-01-15T10:00:00Z"`) is UTC. Never pass a Python `datetime` — it is not
    JSON-serializable across the Dash boundary.

### Colors

Set a per-event `color` to any of the **11 palette names**:

`red` · `pink` · `purple` · `indigo` · `blue` · `teal` *(default)* · `green` · `lime` · `amber` · `orange` · `grey`

The calendar-wide `eventColor` prop sets the default color for any event that does
**not** carry its own `color` key. A per-event `color` always overrides `eventColor`.

.. exec::docs.events.event_colors

.. source::docs/events/event_colors.py

### All-day events

Mark an event `allDay: True` to place it in the calendar's all-day row, spanning
whole days instead of a time slot. All-day and timed events mix freely in the same
`events` list.

.. exec::docs.events.all_day

.. source::docs/events/all_day.py

.. admonition::All-day spans
    :color: blue

    For an all-day event the time portion of `start`/`end` is ignored, but keep them
    as valid ISO strings. A multi-day span (`"2024-01-17"` → `"2024-01-19"`) shows as
    a single bar across those days.

### Controlling creation

The `eventCreation` prop decides whether — and how — users can create new events by
interacting with empty space.

- **`eventCreation=True`** *(default)* — creation is on with the component's default
  gesture.
- **`eventCreation=False`** — disable click/drag-to-create entirely (existing events
  can still be edited unless you also set `readOnly=True`).
- **`eventCreation={...}`** — fine-tune the gesture with two keys:
  - `interaction`: `'click'` or `'double-click'` — how a new event is started.
  - `duration`: minutes (int) — the length of an event created by a single click.

```python
# A double-click creates a 30-minute event in empty space.
dms.EventCalendar(
    id="events-creation-cal",
    events=events,
    eventCreation={"interaction": "double-click", "duration": 30},
    defaultVisibleDate="2024-01-15",
    height=600,
)
```

When a user creates an event, the new block is appended to `events` and
`lastAction` reports `{"type": "create", "event": {...}, "event_timestamp": ...}`.

### EventCalendar props

.. kwargs::dash_mui_scheduler.EventCalendar
