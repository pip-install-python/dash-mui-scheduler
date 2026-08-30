---
name: Responsive
description: Mobile-aware UX for the Event Calendar — a responsive event drawer, an auto-collapsing side panel, and panning the time grid to the current time.
endpoint: /responsive
category: Scheduler
order: 8
lastmod: 2026-07-16
package: dash_mui_scheduler
icon: mdi:cellphone-link
---

.. llms_copy::Responsive

.. toc::

### Overview

These props are Dash-wrapper additions on top of the MUI X Scheduler. They make
`EventCalendar` (and `EventCalendarPremium`) behave better on phones and small
screens, and let the day/week grid open already scrolled to "now".

| Prop | Default | What it does |
| --- | --- | --- |
| `eventDialogVariant` | `"drawer"` | Presents the event editor as a responsive drawer instead of a floating dialog. |
| `responsiveSidePanel` | `True` | Side panel starts open on wide screens, collapsed on phones. |
| `mobileBreakpoint` | `768` | Pixel width below which the mobile layout kicks in. |
| `scrollToCurrentTime` | `False` | Pan the day/week grid so the current-time line is centered on first render. |

### The event drawer

The Scheduler renders its event editor as a floating, draggable dialog that is
positioned next to the event you clicked — which tends not to "snap" anywhere
and reads poorly on a phone. With `eventDialogVariant="drawer"` (the default),
the wrapper restyles that editor into a drawer:

- **Desktop** (≥ `mobileBreakpoint`): a right-anchored, full-height panel.
- **Mobile** (< `mobileBreakpoint`): a bottom sheet taking 80% of the viewport
  height, with the form body scrolling and the title/Save/Delete pinned.

Click any event in the calendar below (try it at a narrow window width too) to
see the drawer:

.. exec::docs.responsive.now_indicator
    :code: false

Set `eventDialogVariant="dialog"` to restore the library's original floating
dialog. If your app has a fixed header, set `eventDialogTopOffset` to its height
(in px) so the desktop drawer starts below it and lines up with your sidebar
instead of covering the header — this documentation site uses `70`.

.. admonition::How this works
    :color: blue

    The MUI X Scheduler beta does not expose a slot to swap the editor, so this
    is a CSS restyle of the built-in dialog (which is portaled to `<body>` with
    stable `MuiEventCalendar-eventDialog*` classes) — not a separate
    `dmc.Drawer`. It keeps all of the Scheduler's own validation and recurrence
    UI while fixing the placement and mobile layout. A fully custom editor would
    require forking the component and is intentionally avoided while the
    Scheduler is in beta.

### The side panel

`responsiveSidePanel` decides the side panel's initial state from the viewport
width: open at `mobileBreakpoint` and above, collapsed below it. This only sets
the **initial** state — the user can still toggle it, and you can override it
entirely by pinning `isSidePanelOpen` in `preferences` / `defaultPreferences`.

```python
dms.EventCalendar(
    id="cal",
    events=events,
    responsiveSidePanel=True,   # default
    mobileBreakpoint=768,       # phones (< 768px) start collapsed
)
```

### Panning to the current time

In the `day` and `week` views the grid normally opens at midnight. Set
`scrollToCurrentTime=True` and the grid scrolls so the red current-time line is
centered on first render (and again when you switch into a time view). It works
together with `showCurrentTimeIndicator` (on by default):

.. source::docs/responsive/now_indicator.py

```python
dms.EventCalendar(
    id="cal",
    events=events,
    defaultView="week",
    scrollToCurrentTime=True,        # pan to now on load
    showCurrentTimeIndicator=True,   # the red "now" line (default)
)
```

In `month` and `agenda` views there is no time grid, so the prop is simply
ignored.

### Props

.. kwargs::dash_mui_scheduler.EventCalendar
