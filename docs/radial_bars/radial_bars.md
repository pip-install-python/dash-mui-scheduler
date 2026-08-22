---
name: Radial Bars
description: Polar bar charts for comparing values along periodic categories, wrapping MUI X RadialBarChart (Premium, preview).
endpoint: /radial-bars
lastmod: 2026-07-16
package: dash_mui_scheduler
category: Charts
icon: mdi:chart-arc
---

.. llms_copy::Radial Bars

.. toc::

### Overview

`RadialBarChart` is the polar counterpart of the bar chart: the x/y axes become
**`rotationAxis`** (a `band` axis of categories around the circle) and
**`radiusAxis`** (the radial value scale). It accepts the same display options
as a cartesian bar chart — `stack` and `layout` on each series, and
`categoryGapRatio` / `barGapRatio` on the band axis.

.. admonition::Premium (preview)
    :color: yellow

    Premium, preview (`Unstable_`) — set `MUI_X_LICENSE_KEY` to remove the
    watermark.

### Basic radial bars

.. exec::docs.radial_bars.basic
    :code: false

.. source::docs/radial_bars/basic.py

### Stacking and layout

Series with the same `stack` value are stacked together. `layout` swaps which
axis encodes the value: `"vertical"` (default) uses the radius, `"horizontal"`
uses the rotation. Toggle the controls below:

.. exec::docs.radial_bars.stacked
    :code: false

.. source::docs/radial_bars/stacked.py

### Reading clicks

.. exec::docs.radial_bars.click
    :code: false

.. source::docs/radial_bars/click.py

### Props

.. kwargs::dash_mui_scheduler.RadialBarChart
