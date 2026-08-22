---
name: Views
description: Switch, restrict, and control the day, week, month, and agenda views of the dash-mui-scheduler EventCalendar.
endpoint: /views
lastmod: 2026-07-16
package: dash_mui_scheduler
icon: mdi:calendar-multiselect
---

.. llms_copy::Views

.. toc::

### Calendar views

`dms.EventCalendar` ships four built-in views: **day**, **week**, **month**, and
**agenda**. By default all four are available and the calendar opens on
`"week"`. A standalone calendar already lets the user switch views with its
built-in view switcher — you only need a callback when you want to *restrict*,
*preset*, or *programmatically drive* the view from elsewhere in your layout.

The two props that govern this are `view` (the currently active view) and
`views` (the list of views the user is allowed to choose from).

.. admonition::ISO strings, not datetimes
    :color: blue

    `view` is a plain string — one of `"day"`, `"week"`, `"month"`,
    `"agenda"`. Keep `defaultVisibleDate` an ISO date string (here
    `"2024-01-15"`) so the seeded events land on screen at load.

### Available views

The four view names are fixed:

- `"day"` — a single day, hour by hour.
- `"week"` — seven day columns (the default).
- `"month"` — a month grid.
- `"agenda"` — a chronological list of upcoming events.

You set the starting view with `defaultView` (uncontrolled) or `view`
(controlled). `defaultView` defaults to `"week"`.

### Restricting views

Pass `views=[...]` to limit which view buttons the calendar renders. Anything
omitted from the list is hidden from the switcher. Combine it with
`defaultView` to choose which of the allowed views shows first — just make sure
`defaultView` is one of the values in `views`.

.. exec::docs.views.views_basic

.. source::docs/views/views_basic.py

### Controlling the active view

To drive the view from your own controls, treat `view` as a controlled
prop: it is both an input and an output. The example below wires a
`dmc.SegmentedControl` to the calendar's `view` prop. The first callback pushes
the segmented control's value into the calendar; the second reads `view` back
out — so when the user clicks the calendar's own view buttons, the segmented
control follows along. Both callbacks use `prevent_initial_call=True` to avoid a
fight on load.

.. exec::docs.views.controlled_view

.. source::docs/views/controlled_view.py

.. admonition::Controlled in + out
    :color: green

    `view` has an uncontrolled twin, `defaultView`. Use `defaultView` for a
    fixed starting view you never read back, and `view` when you need
    two-way binding like the example above. Don't set both.

### EventCalendar props

.. kwargs::dash_mui_scheduler.EventCalendar
