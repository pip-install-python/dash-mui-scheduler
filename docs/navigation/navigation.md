---
name: Navigation
description: Navigate the dash-mui-scheduler EventCalendar through time by setting visibleDate, with Prev / Today / Next buttons computed in Python.
endpoint: /navigation
package: dash_mui_scheduler
icon: mdi:calendar-arrow-right
---

.. llms_copy::Navigation

.. toc::

### Navigation

Every scheduler component shows a single window of time — a day, a week, a
month. Which window is on screen is governed by one prop: **`visibleDate`**, an
ISO date **string** such as `"2024-01-15"`. To move forwards or backwards in
time you simply hand the component a *new* `visibleDate`.

.. admonition::There is no apiRef in Dash
    :color: blue

    In the React MUI X Scheduler you would call methods on an `apiRef` to jump
    around. Dash has no imperative ref — you navigate **declaratively** by
    setting `visibleDate`. Compute the next date in Python (with `datetime` /
    `timedelta`), return it as an ISO string, and the calendar re-renders on
    that window. Dates crossing the boundary are always plain strings, never
    Python `datetime` objects.

### Default visible date — `defaultVisibleDate`

`defaultVisibleDate` is the **uncontrolled** way to pick the opening window. Set
it once and the component manages the visible date from then on — the built-in
navigation arrows move it and Dash never hears about the changes. Use this when
you only need to land the user on the right week at load time:

```python
dms.EventCalendar(
    id="my-cal",
    events=events,
    defaultVisibleDate="2024-01-15",
    defaultView="week",
)
```

Because the events in these docs cluster around the week of **15 Jan 2024**,
seeding the visible date there means they are on screen the moment the page
loads.

### Controlling the visible date — `visibleDate`

`visibleDate` is the **controlled** counterpart and it is wired **IN and OUT**:

- **IN** — whatever ISO string you pass becomes the window the component shows.
- **OUT** — when the user clicks the component's own ‹ › arrows (or the Today
  button in its toolbar), the component writes the new ISO date *back* to Dash.

Pick `visibleDate` (not `defaultVisibleDate`) whenever Python needs to drive or
observe the date — for example to build your own navigation chrome, sync two
calendars, or display the current window elsewhere on the page. Don't mix the
two on the same component: a controlled `visibleDate` wins.

### Prev / Today / Next in Python

The example below replaces the toolbar arrows with three `dmc.Button`s. Each
click reads the current `visibleDate`, computes a new one with Python's
`datetime` module, and returns it:

- **Prev** / **Next** parse the current ISO string with `date.fromisoformat`,
  shift it by `timedelta(weeks=1)`, and re-serialise with `.isoformat()`.
- **Today** returns `date.today().isoformat()`.

A `dmc.Text` below the buttons reads `visibleDate` back out, so you can watch the
value change whether you click your own buttons *or* the calendar's built-in
arrows — both feed the same controlled prop.

.. admonition::Why visibleDate is also an Input
    :color: green

    The navigate callback takes `visibleDate` as an `Input` as well as an
    `Output`. That lets the *same* prop carry the calendar's built-in arrow
    presses through to Python: when the trigger is the calendar itself we just
    echo the value back, otherwise we compute the shifted date. The callback is
    `prevent_initial_call=True` so the seeded `"2024-01-15"` is left untouched
    on load.

.. exec::docs.navigation.navigation_buttons

.. source::docs/navigation/navigation_buttons.py

### EventCalendar props

`visibleDate`, `defaultVisibleDate`, `view`, and `defaultView` follow the same
controlled / uncontrolled pattern. The full prop reference:

.. kwargs::dash_mui_scheduler.EventCalendar
