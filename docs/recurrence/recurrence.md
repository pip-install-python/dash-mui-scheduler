---
name: Recurrence
description: Build recurring events in dash-mui-scheduler with EventCalendarPremium using RRULE strings, RRULE objects and exception dates.
endpoint: /recurrence
category: Scheduler
order: 12
lastmod: 2026-07-16
package: dash_mui_scheduler
icon: mdi:calendar-sync
---

.. llms_copy::Recurrence

.. toc::

### Recurrence (Premium)

Recurring events are a **Premium** feature. Use `dms.EventCalendarPremium`
instead of `dms.EventCalendar` — it is identical to the Community calendar but
adds a recurrence engine, a Recurrence tab in the edit dialog, and two new
per-event keys: `rrule` and `exDates`.

.. admonition::Premium
    :color: yellow

    `EventCalendarPremium` requires a MUI X Premium license key. Pass it via
    `licenseKey=os.environ.get("MUI_X_LICENSE_KEY", "")`. Without a valid key
    the calendar still renders and is fully interactive, but a MUI watermark is
    shown over it. That is expected — supply a real key to remove it.

The data boundary is unchanged from the Community calendar. `events` is a list
of plain dicts and is **both input and output**: the component writes the full
array back on every create, move, resize or delete. Dates are ISO **strings**
(for example `"2024-01-15T10:00:00"` for wall time, or a trailing `Z` for UTC),
never Python `datetime` objects. Recurring series are stored as a *single*
event dict carrying an `rrule`; the calendar expands it into occurrences for
display only.

### Recurrence as an RRULE string

The simplest form sets `event["rrule"]` to an RFC-5545 RRULE string. The event
below repeats every week on Monday, Wednesday and Friday:

```text
FREQ=WEEKLY;INTERVAL=1;BYDAY=MO,WE,FR
```

`FREQ` is one of `DAILY`, `WEEKLY`, `MONTHLY`, `YEARLY`. `BYDAY` codes are
`MO TU WE TH FR SA SU` (for monthly rules you may prefix an ordinal, e.g.
`2TU` = second Tuesday, `-1FR` = last Friday). You can also add `COUNT`,
`UNTIL` (an ISO string), `BYMONTHDAY` (1–31) and `BYMONTH` (1–12).

.. exec::docs.recurrence.recurrence_string

.. source::docs/recurrence/recurrence_string.py

### Recurrence as an object + exception dates

Instead of a string, `rrule` may be an object. This is convenient when you are
building the rule programmatically:

```python
{"freq": "WEEKLY", "interval": 1, "byDay": ["MO", "WE", "FR"], "count": 10}
```

The keys mirror the RRULE parts: `freq`, `interval`, `byDay`, `byMonthDay`,
`byMonth`, `count` and `until`. To remove individual occurrences from a series
without breaking the rule, add `exDates` — a list of ISO strings naming the
start times to skip:

```python
"exDates": ["2024-01-17T08:00:00", "2024-01-19T08:00:00"]
```

The example below recurs every weekday for ten occurrences, with two dates
excluded. Note that even though the calendar shows many occurrences, the
`events` output still contains a single definition dict.

.. exec::docs.recurrence.recurrence_object

.. source::docs/recurrence/recurrence_object.py

### Reading edits back

As with the Community calendar, you do not need a callback for the calendar to
be interactive — drags, creates and deletes round-trip through Dash on their
own. Add a callback only to *display* outputs. The `lastAction` output is
`{type, event, event_timestamp}`, where `type` is one of `create`, `update`,
`delete`, `move`, `resize` or `change`. The first example above wires
`lastAction` into a code block so you can watch edits as they happen.

### EventCalendarPremium props

`EventCalendarPremium` accepts every `EventCalendar` prop plus `licenseKey`,
and its `events` may include `rrule` and `exDates`.

.. kwargs::dash_mui_scheduler.EventCalendarPremium
