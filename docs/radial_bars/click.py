import json
import os

from dash import html, dcc, Input, Output, callback
import dash_mui_scheduler as dms

# Like the line chart, `onAxisClick` surfaces as the `clickData` output.
component = html.Div(
    [
        dms.RadialBarChart(
            id="radial-bars-click",
            height=380,
            licenseKey=os.environ.get("MUI_X_LICENSE_KEY", ""),
            series=[
                {"data": [3, 4, 1, 6, 5], "label": "A", "stack": "total"},
                {"data": [4, 3, 1, 5, 8], "label": "B", "stack": "total"},
                {"data": [4, 2, 5, 4, 1], "label": "C", "stack": "total"},
            ],
            rotationAxis=[{"scaleType": "band", "data": ["Mon", "Tue", "Wed", "Thu", "Fri"]}],
            grid={"radius": True},
        ),
        dcc.Markdown(id="radial-bars-click-out"),
    ]
)


@callback(
    Output("radial-bars-click-out", "children"),
    Input("radial-bars-click", "clickData"),
)
def show_click(data):
    if not data:
        return "_Click anywhere on the chart to see the clicked axis data._"
    return f"```json\n{json.dumps(data, indent=2)}\n```"
