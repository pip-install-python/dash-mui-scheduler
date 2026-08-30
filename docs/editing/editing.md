---
name: Editing
description: Create and edit events in dash-mui-scheduler — the edit dialog, event creation config, and read-only calendars or events.
endpoint: /editing
category: Scheduler
order: 10
lastmod: 2026-07-16
package: dash_mui_scheduler
icon: mdi:calendar-edit
---

.. llms_copy::Editing

.. toc::

### Editing events

`dms.EventCalendar` is interactive out of the box. With no callback at all, a
user can create, drag, resize, and delete events — Dash's own `setProps`
round-trip persists each change into the `events` prop. The component treats
`events` as **both input and output**: on every create, move, resize, or
delete it writes the *full new array* back. Dates inside `events` are always
**ISO strings** (e.g. `"2024-01-15T10:00:00"` for wall time, or a trailing
`Z` for UTC) — never Python `datetime` objects.

Add a callback only when you want to *observe* what changed: read `events` for
the new state, or read `lastAction` — an output-only dict shaped
`{type, event, event_timestamp}` where `type` is one of `create`, `update`,
`delete`, `move`, `resize`, or `change`.

### The edit dialog

Clicking an existing event opens the built-in edit dialog where the title,
time, color, and description can be changed; saving writes the updated event
back into `events`. Interacting with an empty slot starts event creation (see
below). You do not wire any of this up yourself — it is part of the component.

.. admonition::Beta
    :color: blue

    The MUI X Scheduler is in beta. The edit dialog's exact fields and styling
    may change in future releases. The Dash data boundary described here
    (`events` in/out, `lastAction`, ISO strings) is stable.

### Configuring event creation

The `eventCreation` prop controls how new events are drawn:

- `eventCreation=True` (default) — creation is enabled with the default gesture.
- `eventCreation=False` — creation is **disabled** entirely; users can still
  move or resize existing events (unless those are locked too).
- `eventCreation={"interaction": "double-click", "duration": 45}` — an object
  where `interaction` is `"click"` or `"double-click"`, and `duration` is the
  new event's length in **minutes**.

In the example below, double-clicking an empty slot creates a 45-minute event.
The `lastAction` output is echoed underneath so you can see each change.

.. exec::docs.editing.event_creation

.. source::docs/editing/event_creation.py

### Read-only: whole calendar vs. one event

Locking works at two levels:

- **Globally** — `readOnly=True` on the calendar disables all creating,
  moving, resizing, and deleting. The calendar becomes a pure display.
- **Per event** — add `"readOnly": True` to a single event dict to freeze
  just that event while the rest of the calendar stays editable.

The example shows both: a fully read-only calendar on the left, and an
editable calendar on the right where only the red all-hands event is locked.

.. exec::docs.editing.editing_readonly

.. source::docs/editing/editing_readonly.py

.. admonition::Disabling creation only
    :color: green

    To keep events editable but stop new ones from being drawn, set
    `eventCreation=False` rather than `readOnly=True`. `readOnly` locks
    everything; `eventCreation=False` locks creation alone.

### EventCalendar props

.. kwargs::dash_mui_scheduler.EventCalendar
