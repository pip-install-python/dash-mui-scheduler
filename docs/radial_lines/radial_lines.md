---
name: Radial Lines
description: Polar line and area charts for showing trends along periodic values, wrapping MUI X RadialLineChart (Premium, preview).
endpoint: /radial-lines
lastmod: 2026-07-16
package: dash_mui_scheduler
category: Charts
icon: mdi:chart-bell-curve
---

.. llms_copy::Radial Lines

.. toc::

### Overview

`RadialLineChart` plots line (and area) series in **polar coordinates** — a
preview component from `@mui/x-charts-premium`, bundled here alongside the
scheduler. The cartesian x-axis is replaced by a **`rotationAxis`** (angular)
and the y-axis by a **`radiusAxis`** (radial). Data crosses the Dash boundary
as plain dicts and lists, so series, dataset, and axes are just Python objects.

.. admonition::Premium (preview)
    :color: yellow

    `RadialLineChart` and `RadialBarChart` come from MUI X **Premium** and are
    **preview** (`Unstable_`) — production-ready, but the API may shift in minor
    releases. Without a `licenseKey` they render a watermark; set
    `MUI_X_LICENSE_KEY` in your environment to remove it.

### Basic radial line

Pass `series` plus a `rotationAxis` / `radiusAxis`. Here a `point` rotation axis
maps each month around the circle, and `grid` draws the background rings/spokes.

.. exec::docs.radial_lines.basic
    :code: false

.. source::docs/radial_lines/basic.py

### Marks

Set `showMark: True` on a series to draw marks, and `shape` to pick one of seven
shapes: `circle`, `square`, `diamond`, `cross`, `star`, `triangle`, `wye`.

.. exec::docs.radial_lines.marks
    :code: false

.. source::docs/radial_lines/marks.py

### Continuous rotation axis

The rotation axis can use any scale type. Here a numeric axis spans a full turn
(0 → 2π) and `cos(3θ)` traces a three-petal rose:

.. exec::docs.radial_lines.continuous
    :code: false

.. source::docs/radial_lines/continuous.py

### Reading clicks

`onAxisClick` is surfaced as the **`clickData`** output — it reports the clicked
rotation-axis item and the series values at that index. Wire it to a callback:

.. exec::docs.radial_lines.axis_click
    :code: false

.. source::docs/radial_lines/axis_click.py

### Props

.. kwargs::dash_mui_scheduler.RadialLineChart
