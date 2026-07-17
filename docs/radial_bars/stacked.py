import os

from dash import html, Input, Output, callback
import dash_mantine_components as dmc
import dash_mui_scheduler as dms

# Netflix balance sheet ($B). Series reference columns by dataKey.
dataset = [
    {"year": "2020", "totAss": 39.3, "totLia": 28.2, "totEq": 11.1},
    {"year": "2021", "totAss": 44.6, "totLia": 28.7, "totEq": 15.8},
    {"year": "2022", "totAss": 48.6, "totLia": 27.8, "totEq": 20.8},
    {"year": "2023", "totAss": 48.7, "totLia": 28.0, "totEq": 20.6},
]


def _series(layout, stack):
    # Total Assets stands alone; Liabilities + Equity stack into "passive".
    stk = "passive" if stack else None
    out = [{"dataKey": "totAss", "label": "Total Assets", "layout": layout}]
    for key, label in [("totLia", "Total Liabilities"), ("totEq", "Total Equity")]:
        s = {"dataKey": key, "label": label, "layout": layout}
        if stk:
            s["stack"] = stk
        out.append(s)
    return out


def _rotation(gap_cat, gap_bar):
    return [{
        "scaleType": "band",
        "dataKey": "year",
        "categoryGapRatio": gap_cat,
        "barGapRatio": gap_bar,
    }]


component = html.Div(
    [
        dmc.Group(
            [
                dmc.SegmentedControl(
                    id="radial-bars-layout",
                    value="vertical",
                    data=[{"label": "vertical", "value": "vertical"}, {"label": "horizontal", "value": "horizontal"}],
                ),
                dmc.Switch(id="radial-bars-stack", label="stack liabilities + equity", checked=True),
            ],
            mb="md",
        ),
        dms.RadialBarChart(
            id="radial-bars-stacked",
            height=400,
            licenseKey=os.environ.get("MUI_X_LICENSE_KEY", ""),
            dataset=dataset,
            series=_series("vertical", True),
            rotationAxis=_rotation(0.3, 0.1),
            grid={"radius": True},
        ),
    ]
)


@callback(
    Output("radial-bars-stacked", "series"),
    Input("radial-bars-layout", "value"),
    Input("radial-bars-stack", "checked"),
)
def update(layout, stack):
    return _series(layout, stack)
