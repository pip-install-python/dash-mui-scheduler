import os

from dash import html, Input, Output, callback
import dash_mantine_components as dmc
import dash_mui_scheduler as dms

_rows = [
    ("Jan", 49, 51, 78), ("Feb", 38, 41, 72), ("Mar", 40, 48, 95),
    ("Apr", 44, 47, 90), ("May", 49, 63, 92), ("Jun", 45, 56, 87),
    ("Jul", 45, 62, 100), ("Aug", 50, 54, 96), ("Sep", 49, 48, 90),
    ("Oct", 69, 60, 90), ("Nov", 59, 53, 85), ("Dec", 56, 56, 90),
]
DATASET_STR = [{"month": m, "london": lo, "paris": pa, "newYork": ny} for (m, lo, pa, ny) in _rows]
# A linear scale needs a numeric axis key, so swap the month label for its index.
DATASET_NUM = [{**d, "month": i + 1} for i, d in enumerate(DATASET_STR)]

SERIES = [
    {"dataKey": "london", "curve": "linear", "label": "London", "showMark": True},
    {"dataKey": "paris", "curve": "linear", "label": "Paris", "showMark": True},
    {"dataKey": "newYork", "curve": "linear", "label": "New York", "showMark": True},
]

# `axisHighlight` highlights data based on the pointer: each of `rotation` and
# `radius` can be "none", "line", or "band".
component = html.Div(
    [
        dmc.Group(
            [
                dmc.Stack([dmc.Text("scale type", size="sm", fw=600),
                           dmc.SegmentedControl(id="rax-scale", value="point",
                                                data=["band", "point", "linear"])], gap=2),
                dmc.Stack([dmc.Text("rotation highlight", size="sm", fw=600),
                           dmc.SegmentedControl(id="rax-rot", value="band",
                                                data=["none", "line", "band"])], gap=2),
                dmc.Stack([dmc.Text("radius highlight", size="sm", fw=600),
                           dmc.SegmentedControl(id="rax-rad", value="none",
                                                data=["none", "line"])], gap=2),
            ],
            mb="md",
        ),
        dms.RadialLineChart(
            id="radial-axes-highlight",
            height=400,
            licenseKey=os.environ.get("MUI_X_LICENSE_KEY", ""),
            dataset=DATASET_STR,
            series=SERIES,
            rotationAxis=[{"dataKey": "month", "scaleType": "point"}],
            radiusAxis=[{"minRadius": 10, "min": 0}],
            grid={"rotation": True, "radius": True},
            axisHighlight={"rotation": "band", "radius": "none"},
        ),
    ]
)


@callback(
    Output("radial-axes-highlight", "dataset"),
    Output("radial-axes-highlight", "rotationAxis"),
    Output("radial-axes-highlight", "axisHighlight"),
    Input("rax-scale", "value"),
    Input("rax-rot", "value"),
    Input("rax-rad", "value"),
)
def update_highlight(scale, rotation, radius):
    dataset = DATASET_NUM if scale == "linear" else DATASET_STR
    return dataset, [{"dataKey": "month", "scaleType": scale}], {"rotation": rotation, "radius": radius}
