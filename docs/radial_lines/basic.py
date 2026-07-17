import os

from dash import html
import dash_mui_scheduler as dms

# Row-oriented data; each series references a column via `dataKey`.
dataset = [
    {"month": "Jan", "london": 49}, {"month": "Feb", "london": 38},
    {"month": "Mar", "london": 40}, {"month": "Apr", "london": 44},
    {"month": "May", "london": 49}, {"month": "Jun", "london": 45},
    {"month": "Jul", "london": 45}, {"month": "Aug", "london": 50},
    {"month": "Sep", "london": 49}, {"month": "Oct", "london": 69},
    {"month": "Nov", "london": 59}, {"month": "Dec", "london": 56},
]

# rotationAxis is the angular (x-like) axis; radiusAxis is the radial (y-like) one.
component = html.Div(
    dms.RadialLineChart(
        id="radial-lines-basic",
        height=400,
        licenseKey=os.environ.get("MUI_X_LICENSE_KEY", ""),
        dataset=dataset,
        series=[{"dataKey": "london", "label": "London precipitation (mm)", "curve": "natural", "showMark": True}],
        rotationAxis=[{"scaleType": "point", "dataKey": "month", "disableLine": True}],
        radiusAxis=[{"disableLine": True}],
        grid={"rotation": True, "radius": True},
    )
)
