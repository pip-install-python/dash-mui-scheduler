import os

from dash import html, Input, Output, callback
import dash_mantine_components as dmc
import dash_mui_scheduler as dms

dataset = [
    {"month": "Jan", "london": 49}, {"month": "Feb", "london": 38},
    {"month": "Mar", "london": 40}, {"month": "Apr", "london": 44},
    {"month": "May", "london": 49}, {"month": "Jun", "london": 45},
    {"month": "Jul", "london": 45}, {"month": "Aug", "london": 50},
    {"month": "Sep", "london": 49}, {"month": "Oct", "london": 69},
    {"month": "Nov", "london": 59}, {"month": "Dec", "london": 56},
]
SHAPES = ["circle", "square", "diamond", "cross", "star", "triangle", "wye"]


def _series(shape):
    return [{"dataKey": "london", "label": "London precipitation (mm)", "curve": "natural", "showMark": True, "shape": shape}]


# `showMark: True` draws marks; `shape` picks one of 7 mark shapes.
component = html.Div(
    [
        dmc.Select(id="radial-lines-shape", label="Mark shape", value="circle", data=SHAPES, maw=200, mb="md"),
        dms.RadialLineChart(
            id="radial-lines-marks",
            height=400,
            licenseKey=os.environ.get("MUI_X_LICENSE_KEY", ""),
            dataset=dataset,
            series=_series("circle"),
            rotationAxis=[{"scaleType": "point", "dataKey": "month", "disableLine": True}],
            radiusAxis=[{"disableLine": True}],
            grid={"rotation": True, "radius": True},
        ),
    ]
)


@callback(
    Output("radial-lines-marks", "series"),
    Input("radial-lines-shape", "value"),
    prevent_initial_call=True,
)
def set_shape(shape):
    return _series(shape)
