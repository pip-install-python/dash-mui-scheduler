---
name: Preferences
description: Control the EventCalendar's default display preferences and the user-facing preferences menu in dash-mui-scheduler.
endpoint: /preferences
package: dash_mui_scheduler
icon: mdi:tune
---

.. llms_copy::Preferences

.. toc::

### Preferences

Every calendar exposes a small set of **user preferences** — am/pm clock, which day the
week starts on, whether weekends and week numbers are shown, and so on. These are surfaced
through a built-in preferences menu (the gear button in the calendar header) so users can
tweak the view themselves.

In `dash_mui_scheduler` you control three related things:

- **`defaultPreferences`** — the initial, uncontrolled preference values applied on load.
- **`preferences`** — the controlled IN+OUT version. It seeds the UI *and* reports the
  current values back to Dash whenever the user changes a setting.
- **`preferencesMenuConfig`** — which entries appear in the preferences menu (or whether the
  menu shows at all).

All of these work the same way on `EventCalendar`, `EventCalendarPremium`, and
(a smaller subset) on `EventTimeline`.

### Default preferences

`defaultPreferences` is a dict. Set only the keys you care about — anything omitted falls
back to the component's own defaults.

| Key | Type | Meaning |
| --- | --- | --- |
| `ampm` | bool | 12-hour (`True`) vs 24-hour (`False`) clock |
| `weekStartsOn` | int 0–6 | First day of the week (0 = Sunday … 1 = Monday) |
| `showWeekends` | bool | Show Saturday/Sunday columns |
| `showWeekNumber` | bool | Show the ISO week number |
| `isSidePanelOpen` | bool | Whether the date/resource side panel starts open |
| `showEmptyDaysInAgenda` | bool | Keep empty days visible in the agenda view |

.. admonition::Uncontrolled vs controlled
    :color: blue

    Use `defaultPreferences` when you just want a starting configuration and don't need to
    read changes back. Use `preferences` when you want the current values in a callback —
    it is both an input and an output, so the component writes the full preferences dict
    back on every toggle.

### Reading preferences

Because `preferences` is IN+OUT, you can attach a callback whose **only** job is to read the
current values. The example below seeds the calendar with a Monday week start, 24-hour
clock, and visible week numbers via `defaultPreferences`, then echoes the live `preferences`
dict each time the user changes something in the menu.

.. exec::docs.preferences.preferences_default

.. source::docs/preferences/preferences_default.py

The readout updates as you toggle items in the calendar's preferences menu — no extra
plumbing required, since the component pushes the new dict back through Dash's normal
`setProps` round-trip.

### The preferences menu

`preferencesMenuConfig` controls the menu itself:

- Pass **`False`** to hide the entire preferences menu (useful for a locked-down, read-only
  display).
- Pass a **dict** to show or hide individual entries. Each key is a boolean:
  `toggleWeekendVisibility`, `toggleWeekNumberVisibility`, `toggleAmpm`,
  `toggleEmptyDaysInAgenda`, and `toggleWeekStartsOn`.

The first calendar below keeps the weekend, week-number, and am/pm toggles but removes the
"empty days in agenda" and "week starts on" entries. The second passes
`preferencesMenuConfig=False`, so its menu button disappears entirely.

.. exec::docs.preferences.preferences_menu

.. source::docs/preferences/preferences_menu.py

.. admonition::Menu config vs values
    :color: green

    `preferencesMenuConfig` only decides which controls are *available* to the user. It does
    not change the actual preference values — set those with `defaultPreferences` /
    `preferences`. Hiding a toggle simply means the user can't change that setting from the
    UI; you can still set it programmatically.

### Component reference

.. kwargs::dash_mui_scheduler.EventCalendar
