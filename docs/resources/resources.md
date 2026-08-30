---
name: Resources
description: Organize EventCalendar events by resource — define resources with colors, assign events, control which resources are visible, and require a resource on creation.
endpoint: /resources
category: Scheduler
order: 5
lastmod: 2026-07-16
package: dash_mui_scheduler
icon: mdi:account-group
---

.. llms_copy::Resources

.. toc::

### Resources

A **resource** is a thing you schedule against — a person, a room, a machine, a team.
In `dms.EventCalendar` you declare resources once, then tag each event with a
`resource` id. The calendar colors events by their resource and lets you show or
hide a subset of resources without touching the underlying `events` array.

Resources are passed as a list of dicts through the `resources` prop. A resource dict
accepts:

| key | type | meaning |
| --- | --- | --- |
| `id` | str | unique resource id, referenced by `event["resource"]` (required) |
| `title` | str | label shown in the UI (required) |
| `eventColor` | palette name | color for this resource's events (default `teal`) |
| `children` | list | nested child resources |
| `areEventsDraggable` | bool | override drag for this resource's events |
| `areEventsResizable` | bool | override resize for this resource's events |
| `areEventsReadOnly` | bool | make this resource's events read-only |

The 11 palette names for `eventColor` are: `red`, `pink`, `purple`, `indigo`,
`blue`, `teal`, `green`, `lime`, `amber`, `orange`, `grey`.

.. admonition::The data boundary
    :color: blue

    `events` is both an input and an output. Dates are ISO strings
    (e.g. `"2024-01-15T10:00:00"`). Each event links to a resource through its
    `resource` key, which must match a resource `id`. When a user creates, moves,
    resizes, or deletes an event, the component writes the whole new array back to
    `events` — no callback required for that round-trip.

### Defining resources and assigning events

Give each resource an `id`, a `title`, and an `eventColor`. Then set
`event["resource"]` to the resource's `id`. The calendar paints each event with its
resource color automatically — you do not need to set a per-event `color`.

.. exec::docs.resources.resources_basic

.. source::docs/resources/resources_basic.py

### Resource colors

Color comes from the resource's `eventColor`. Any event whose `resource` points at
that resource inherits the color, which keeps a whole category visually consistent.
An individual event can still override with its own `color` key, but leaving it off
lets the resource drive the palette — change the resource color in one place and
every matching event follows.

### Showing and hiding resources

`visibleResources` is a mapping of resource id to a boolean. A resource is shown
unless it is explicitly set to `False`, so you only list the ones you want to hide
(or list all of them and flip values). It comes in two forms:

- `defaultVisibleResources` — **uncontrolled**: an initial value the component then
  manages on its own.
- `visibleResources` — **controlled** in and out: drive it from a callback and read
  user changes back.

The example below wires a `dmc.ChipGroup` to `visibleResources`. Each chip toggles
one resource on or off; the calendar updates immediately and the events for hidden
resources disappear without being removed from `events`.

.. exec::docs.resources.resource_visibility

.. source::docs/resources/resource_visibility.py

.. admonition::Controlled means in *and* out
    :color: green

    Because `visibleResources` is controlled, a user toggling resources through the
    calendar's own side panel would also flow back into your callback's input. Keep a
    single source of truth (here, the `ChipGroup` value) so the two stay in sync.

### Requiring a resource

Set `shouldEventRequireResource=True` to force every event to belong to a resource.
With it on, the create flow will not let a user save an event without picking a
resource — useful when "unassigned" is not a valid state (for example, a room-booking
calendar where every booking needs a room).

### Props reference

.. kwargs::dash_mui_scheduler.EventCalendar
