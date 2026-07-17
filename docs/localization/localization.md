---
name: Localization & Timezones
description: Set the display timezone, 12h/24h clock, week start day, and translate UI labels in the dash-mui-scheduler calendar.
endpoint: /localization
package: dash_mui_scheduler
icon: mdi:translate
---

.. llms_copy::Localization & Timezones

.. toc::

### Localization & Timezones

The scheduler can render the same events for users in different timezones and
locales without ever touching the event data itself. Four knobs cover almost
everything:

- **`displayTimezone`** — which timezone the grid is drawn in (render-only).
- **`preferences.ampm`** — 12-hour vs 24-hour clock.
- **`preferences.weekStartsOn`** — which weekday a week begins on.
- **`localeText`** — overrides for individual UI label strings.

The most important idea on this page is the **data boundary**: an event's
`start` / `end` are ISO strings that you own. Localization changes how those
times are *displayed*, not what they *are*.

### Display timezone

`displayTimezone` controls the timezone the calendar grid renders in. It accepts
an IANA timezone name like `"America/New_York"` or `"Asia/Tokyo"`, or one of the
special values:

| Value | Meaning |
| --- | --- |
| `"default"` | The component's default behavior (the initial value) |
| `"UTC"` | Render everything in UTC |
| `"locale"` | Use the browser's local timezone |
| IANA name | Render in that specific zone, e.g. `"Europe/Paris"` |

.. admonition::displayTimezone is render-only
    :color: yellow

    Changing `displayTimezone` only changes **where event blocks are drawn** on
    the grid. It does **not** rewrite your `events`. The ISO strings you pass in
    stay exactly as they are, and the array the component writes back keeps the
    same wall-clock / UTC strings. Think of it as a viewport over fixed instants.

How the strings are interpreted matters here:

- `"2024-01-17T18:00:00Z"` — the trailing `Z` means UTC. It refers to one fixed
  instant, so it lands at different wall-clock positions in New York vs Tokyo.
- `"2024-01-15T09:00:00"` — no `Z` is a wall-clock time with no zone attached.

The example below renders **one shared list of events** in two calendars — the
only difference is `displayTimezone`. Note how the "Release window (UTC)" event
(which uses a `Z` suffix) shifts between the two grids, while the rest stay put.

.. exec::docs.localization.timezones

.. source::docs/localization/timezones.py

### 12-hour vs 24-hour clock

The clock format lives in `preferences.ampm`:

- `ampm=True` → 12-hour clock (`2:00 PM`).
- `ampm=False` → 24-hour clock (`14:00`).

Set it via `defaultPreferences` (uncontrolled, initial value) or `preferences`
(controlled IN+OUT, also readable in a callback). Users can flip it themselves
from the preferences menu unless you disable that toggle. See the
[Preferences page](/preferences) for the full preferences dict and menu config.

### Week start

`preferences.weekStartsOn` is an integer from **0 to 6** that picks the first day
of the week:

| Value | Day |
| --- | --- |
| 0 | Sunday |
| 1 | Monday |
| 2 | Tuesday |
| 3 | Wednesday |
| 4 | Thursday |
| 5 | Friday |
| 6 | Saturday |

The example below seeds a Monday-first, 24-hour calendar with week numbers via
`defaultPreferences`. Because these are preferences, they apply to the week,
month, and agenda layouts consistently.

.. exec::docs.localization.week_start

.. source::docs/localization/week_start.py

.. admonition::Where ampm and weekStartsOn live
    :color: blue

    Both `ampm` and `weekStartsOn` are keys *inside* the preferences dict — there
    are no top-level `ampm` / `weekStartsOn` props. Pass them through
    `defaultPreferences={...}` or the controlled `preferences={...}`.

### Label overrides

`localeText` is a dict of overrides for the calendar's built-in UI label strings
— button captions, menu items, placeholders, and so on. Pass it as a dict where
each value replaces the default text for that key:

```python
dms.EventCalendar(
    id="my-cal",
    events=events,
    localeText={
        "today": "Aujourd'hui",
        "week": "Semaine",
        "month": "Mois",
    },
)
```

.. admonition::Only string-valued labels are settable from Python
    :color: yellow

    The MUI X Scheduler's locale text includes both plain strings and *functions*
    (for example, labels that format a date range). Because props cross the
    Dash boundary as JSON, **only the string-valued keys can be overridden from
    Python** — function-valued entries can't be passed and will fall back to their
    defaults. Use `localeText` for static caption text, not for dynamic formatters.

For full locale coverage (including the function-valued formatters), you would
provide a translation at the React/JS layer. From Dash, `localeText` is best
treated as a way to retitle the static buttons and menu items.

### Timezones and the data you store

Because `displayTimezone` never edits your events, your storage stays
predictable:

- Store events as ISO strings. Add a `Z` (or an explicit offset) when a value
  is a fixed UTC instant; omit it when it's a floating wall-clock time.
- An event may also carry its own `timezone` (IANA) key in its dict to anchor it
  to a specific zone independent of the display timezone.
- When the component writes `events` back after a drag/create/resize, it returns
  ISO strings in the same shape — so a round-trip through Dash doesn't silently
  re-localize your data.

.. admonition::Beta
    :color: blue

    The MUI X Scheduler is in beta. Timezone and locale behavior can change
    between releases; verify edge cases (DST boundaries, cross-zone all-day
    events) against your target version.

### Component reference

.. kwargs::dash_mui_scheduler.EventCalendar
