import os

from dash import html
import dash_mui_scheduler as dms

# Polar bars: a `band` rotation axis defines the categories around the circle,
# and the radius encodes each value.
component = html.Div(
    dms.RadialBarChart(
        id="radial-bars-basic",
        height=400,
        licenseKey=os.environ.get("MUI_X_LICENSE_KEY", ""),
        series=[{"data": [12, 19, 8, 15], "label": "Revenue ($M)"}],
        rotationAxis=[{"scaleType": "band", "data": ["Q1", "Q2", "Q3", "Q4"]}],
        grid={"rotation": True, "radius": True},
    )
)
