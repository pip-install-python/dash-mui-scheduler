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

# The rotation axis spans startAngle -> endAngle; the radius axis spans
# minRadius -> maxRadius. `grid` toggles the background rings/spokes.
component = html.Div(
    [
        dmc.Group(
            [
                dmc.NumberInput(id="ax-start", label="startAngle", value=-90, min=-360, max=360, w=110),
                dmc.NumberInput(id="ax-end", label="endAngle", value=180, min=-360, max=360, w=110),
                dmc.NumberInput(id="ax-minr", label="minRadius", value=30, min=0, max=200, w=110),
                dmc.NumberInput(id="ax-maxr", label="maxRadius", value=130, min=0, max=200, w=110),
                dmc.Switch(id="ax-grot", label="rotation grid", checked=True, mt="lg"),
                dmc.Switch(id="ax-grad", label="radius grid", checked=True, mt="lg"),
            ],
            mb="md",
            align="flex-end",
        ),
        dms.RadialLineChart(
            id="radial-axes-chart",
            height=420,
            licenseKey=os.environ.get("MUI_X_LICENSE_KEY", ""),
            dataset=dataset,
            series=[{"dataKey": "london", "label": "London precipitation (mm)", "curve": "natural", "showMark": True}],
            rotationAxis=[{"scaleType": "point", "dataKey": "month", "startAngle": -90, "endAngle": 180}],
            radiusAxis=[{"minRadius": 30, "maxRadius": 130}],
            grid={"rotation": True, "radius": True},
        ),
    ]
)


@callback(
    Output("radial-axes-chart", "rotationAxis"),
    Output("radial-axes-chart", "radiusAxis"),
    Output("radial-axes-chart", "grid"),
    Input("ax-start", "value"),
    Input("ax-end", "value"),
    Input("ax-minr", "value"),
    Input("ax-maxr", "value"),
    Input("ax-grot", "checked"),
    Input("ax-grad", "checked"),
)
def update_axes(start, end, min_r, max_r, g_rot, g_rad):
    return (
        [{"scaleType": "point", "dataKey": "month", "startAngle": start, "endAngle": end}],
        [{"minRadius": min_r, "maxRadius": max_r}],
        {"rotation": g_rot, "radius": g_rad},
    )
