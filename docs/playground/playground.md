---
name: Playground
description: Drive the major Event Calendar props live with Dash Mantine Components inputs.
endpoint: /playground
package: dash_mui_scheduler
icon: mdi:tune-variant
---

.. llms_copy::Playground

.. toc::

### Try the props live

Every control below is a plain **Dash Mantine Components** input wired to an
`EventCalendar` prop with a normal Dash callback — change one and the calendar
updates instantly. It doubles as a demonstration of how `dash-mui-scheduler`
**pairs with DMC**: the calendar follows the Mantine color scheme (toggle dark
mode in the header), and DMC `Select` / `Switch` / `SegmentedControl` inputs map
cleanly onto the scheduler's props.

.. exec::docs.playground.playground
    :code: false

.. admonition::How it is wired
    :color: blue

    Each input drives a prop through a callback — e.g. a `dmc.SegmentedControl`
    sets `view`, a `dmc.Select` sets `eventColor` / `displayTimezone`, and the
    six preference `dmc.Switch`es are collected into the `preferences` dict.
    `view` is two-way bound, so clicking the calendar's own view buttons keeps
    the control in sync. The `lastAction` output feeds the readout under the
    calendar.

### Source

.. source::docs/playground/playground.py
    :defaultExpanded: false
    :withExpandedButton: true

### All Event Calendar props

.. kwargs::dash_mui_scheduler.EventCalendar
