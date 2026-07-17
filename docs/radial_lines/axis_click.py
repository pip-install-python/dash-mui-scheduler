import json
import os

from dash import html, dcc, Input, Output, callback
import dash_mui_scheduler as dms

# `onAxisClick` surfaces as the `clickData` output — the clicked rotation-axis
# item and the series values at that index.
component = html.Div(
    [
        dms.RadialLineChart(
            id="radial-lines-click",
            height=380,
            licenseKey=os.environ.get("MUI_X_LICENSE_KEY", ""),
            series=[
                {"id": "a", "data": [3, 4, 1, 6, 5], "label": "A", "stack": "total", "highlightScope": {"highlight": "item"}},
                {"id": "b", "data": [4, 3, 1, 5, 8], "label": "B", "stack": "total", "highlightScope": {"highlight": "item"}},
                {"id": "c", "data": [4, 2, 5, 4, 1], "label": "C", "highlightScope": {"highlight": "item"}},
            ],
            rotationAxis=[{"data": [0, 3, 6, 9, 12], "disableLine": True, "disableTicks": True}],
            radiusAxis=[{"position": "none"}],
            grid={"rotation": True, "radius": True},
        ),
        dcc.Markdown(id="radial-lines-click-out"),
    ]
)


@callback(
    Output("radial-lines-click-out", "children"),
    Input("radial-lines-click", "clickData"),
)
def show_click(data):
    if not data:
        return "_Click anywhere on the chart to see the clicked axis data._"
    return f"```json\n{json.dumps(data, indent=2)}\n```"
