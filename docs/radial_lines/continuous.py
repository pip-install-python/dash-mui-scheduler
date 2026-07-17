import math
import os

from dash import html
import dash_mui_scheduler as dms

# A continuous (numeric) rotation axis. cos(3θ) traces a three-petal rose.
SAMPLES = 200
angles = [i * 2 * math.pi / SAMPLES for i in range(SAMPLES + 1)]
cardioid = [100 * (1 + math.cos(a * 3)) for a in angles]

# `tickInterval` places ticks at the quarter angles; `min`/`max` bound the axis
# to a full turn. (The React demo's `valueFormatter`/`domainLimit` are JS
# functions, which cannot cross the Dash boundary — so ticks show radians and we
# bound the axis with `min`/`max` instead.)
component = html.Div(
    dms.RadialLineChart(
        id="radial-lines-continuous",
        height=400,
        licenseKey=os.environ.get("MUI_X_LICENSE_KEY", ""),
        series=[{"data": cardioid, "label": "Cardioid", "curve": "linear"}],
        rotationAxis=[{
            "data": angles,
            "min": 0,
            "max": 2 * math.pi,
            "tickInterval": [0, math.pi / 2, math.pi, 3 * math.pi / 2, 2 * math.pi],
        }],
        radiusAxis=[{"position": "none"}],
        grid={"rotation": True, "radius": True},
    )
)
