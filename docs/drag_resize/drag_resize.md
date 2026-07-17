---
name: Drag & Resize
description: Toggle and fine-tune drag-and-drop and resizing in the dash-mui-scheduler EventCalendar, including per-event overrides and external drag.
endpoint: /drag-resize
package: dash_mui_scheduler
icon: mdi:cursor-move
---

.. llms_copy::Drag & Resize

.. toc::

### Drag & Resize

The MUI X Scheduler lets users reschedule an event by dragging it to a new
time, and change its duration by dragging its edges. `dms.EventCalendar`
exposes both behaviours through props and they are **on by default** — a
calendar with no callbacks at all is already fully interactive. Every move or
resize is written back to the `events` array (input *and* output) and announced
through `lastAction`, so all you have to do is read those props.

.. admonition::The data boundary
    :color: blue

    `events` is both an input and an output. When the user drags or resizes an
    event, the component sends the *entire* new array back to Dash. Dates are
    plain ISO strings (e.g. `"2024-01-15T10:00:00"`), never Python `datetime`
    objects. `lastAction` is output-only and reports the most recent
    interaction — its `type` is one of `create`, `update`, `delete`, `move`,
    `resize`, or `change`.

### Dragging — `areEventsDraggable`

`areEventsDraggable` (bool, default `True`) controls whether events can be
picked up and dropped onto a new time or day. Set it to `False` to pin every
event in place while still allowing creation and deletion. Dragging an event
emits a `lastAction` of type `move`.

### Resizing — `areEventsResizable`

`areEventsResizable` (default `True`) controls whether an event's edges can be
dragged to change its duration. It accepts:

- `True` — both the start and end edges are resizable.
- `False` — the event keeps a fixed duration.
- `'start'` — only the leading (start) edge can be dragged.
- `'end'` — only the trailing (end) edge can be dragged.

Resizing emits a `lastAction` of type `resize`.

### Live toggles

The example below wires a `dmc.Switch` to `areEventsDraggable` and a
`dmc.SegmentedControl` to `areEventsResizable`, so you can feel the difference
between each mode. A read-out below the calendar shows the latest `lastAction`,
which makes it easy to tell a **move** apart from a **resize**.

.. exec::docs.drag_resize.drag_resize_toggles

.. source::docs/drag_resize/drag_resize_toggles.py

### Per-event and per-resource overrides

The calendar-wide props set the default, but individual events and resources
can opt in or out:

- **Per event:** add `draggable` (bool) and/or `resizable` (`bool | 'start' | 'end'`)
  to an event dict. A locked event might use `{"draggable": False, "resizable": False}`
  even while the rest of the calendar stays movable. (`readOnly: True` locks an
  event completely.)
- **Per resource:** a resource dict accepts `areEventsDraggable`,
  `areEventsResizable`, and `areEventsReadOnly`, applying that policy to every
  event assigned to the resource.

These overrides are read straight off the `events` / `resources` data — there
is no extra prop to enable them.

### External drag — drag in and out of the calendar

Two props control whether events can cross the calendar's boundary:

- `canDragEventsFromTheOutside` (bool, default `False`) — allow an item from
  outside the calendar to be dropped onto it as a new event.
- `canDropEventsToTheOutside` (bool, default `False`) — allow an event to be
  dragged out of the calendar (for example, to remove it or hand it to another
  surface).

These enable the cross-boundary drag *targets*; wiring an actual external
drag source (a palette of draggable items elsewhere on the page) is left to
your own layout. Both default to `False`, so the calendar is self-contained
until you opt in.

.. admonition::Beta
    :color: yellow

    The MUI X Scheduler is in beta. Drag-and-drop and resizing work, but
    finer external-drag integration may change in future releases.

### EventCalendar props

.. kwargs::dash_mui_scheduler.EventCalendar
