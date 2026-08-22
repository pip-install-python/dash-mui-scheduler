---
name: Radial Axes
description: Configure the grid, radius axis, rotation axis, and axis highlight for the radial charts.
endpoint: /radial-axes
lastmod: 2026-07-16
package: dash_mui_scheduler
category: Charts
icon: mdi:axis-arrow
---

.. llms_copy::Radial Axes

.. toc::

### Overview

Both radial charts share the same polar axes, configured through the
**`rotationAxis`** (angular), **`radiusAxis`** (radial), **`grid`**, and
**`axisHighlight`** props. Each is a plain dict (or list of dicts), so you set
them straight from Python.

.. admonition::Premium (preview)
    :color: yellow

    The radial charts are MUI X **Premium** (preview). Set `MUI_X_LICENSE_KEY`
    to remove the watermark.

### Grid and axis geometry

The rotation axis spans `startAngle` → `endAngle`; the radius axis spans
`minRadius` → `maxRadius`. `grid={"rotation": ..., "radius": ...}` toggles the
background spokes and rings. Try the controls:

.. exec::docs.radial_axes.axes
    :code: false

.. source::docs/radial_axes/axes.py

Common axis options include `scaleType` (`"point"`, `"band"`, `"linear"`),
`disableLine`, `disableTicks`, `tickNumber`, `position`, and `valueFormatter`
(the last is a function and so is not settable from Python — use the chart's
defaults or a `dataKey` instead).

### Axis highlight

`axisHighlight` highlights data based on the pointer position. Each of
`rotation` and `radius` can be `"none"`, `"line"`, or `"band"`:

.. exec::docs.radial_axes.highlight
    :code: false

.. source::docs/radial_axes/highlight.py
