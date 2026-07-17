# AUTO GENERATED FILE - DO NOT EDIT

import typing  # noqa: F401
from typing_extensions import TypedDict, NotRequired, Literal # noqa: F401
from dash.development.base_component import Component, _explicitize_args

ComponentSingleType = typing.Union[str, int, float, Component, None]
ComponentType = typing.Union[
    ComponentSingleType,
    typing.Sequence[ComponentSingleType],
]

NumberType = typing.Union[
    typing.SupportsFloat, typing.SupportsInt, typing.SupportsComplex
]


class RadialLineChart(Component):
    """A RadialLineChart component.
RadialLineChart shows trends along periodic values using a polar line (or
area) plot. Pass `series` plus `rotationAxis` / `radiusAxis` to map your data
into polar coordinates; clicking the chart reports the hit axis item via the
`clickData` output. Premium (preview) — set `licenseKey` to remove the
watermark.

Keyword arguments:

- id (string; optional):
    The id used to identify this component in Dash callbacks.

- axisHighlight (dict; optional):
    Axis highlight behavior: {rotation, radius} where each is one of
    \"none\" | \"line\" | \"band\". Default {rotation: \"line\"}.

    `axisHighlight` is a dict with keys:

    - rotation (a value equal to: 'none', 'line', 'band'; optional)

    - radius (a value equal to: 'none', 'line', 'band'; optional)

- className (string; optional):
    CSS class applied to the wrapping div.

- clickData (dict; optional):
    OUTPUT — set when the user clicks the chart. The clicked
    rotation-axis item and its series values, e.g. {dataIndex,
    axisValue, seriesValues, event_timestamp}.

- colors (list of strings; optional):
    Color palette (list of CSS colors) used for the series.

- dataset (list of dicts; optional):
    Row-oriented data; series reference columns via `dataKey`.

- disableLineItemHighlight (boolean; optional):
    Disable the per-item line highlight indicator.

- grid (dict; optional):
    Show background grid lines: {rotation: bool, radius: bool}.

    `grid` is a dict with keys:

    - rotation (boolean; optional)

    - radius (boolean; optional)

- height (number | string; default 400):
    Chart height in px. Default 400.

- hideLegend (boolean; optional):
    Hide the legend.

- licenseKey (string; optional):
    MUI X Premium license key (removes the watermark).

- margin (number | dict; optional):
    Margin around the plot — a number or {top,right,bottom,left}.

- radiusAxis (list of dicts; optional):
    Radius axis config — replaces the cartesian y-axis. A list of axis
    dicts, e.g. [{disableLine:True, minRadius:10, min:0,
    position:\"none\"}].

- rotationAxis (list of dicts; optional):
    Rotation (angular) axis config — replaces the cartesian x-axis. A
    list of axis dicts, e.g. [{scaleType:\"point\", dataKey:\"month\",
    disableLine:True}].

- series (list of dicts; optional):
    The line/area series to plot. Each item is a dict, e.g. {dataKey,
    label, curve, showMark, shape, area, closePath, stack,
    highlightScope, color} or {data: [...], label, ...}.

- showToolbar (boolean; optional):
    Show the default chart toolbar.

- skipAnimation (boolean; optional):
    Skip the entrance animation.

- slotProps (dict; optional):
    MUI X charts `slotProps` (plain-object form only). For example
    {\"tooltip\": {\"trigger\": \"item\"}} makes the tooltip follow
    the hovered mark/line instead of the whole rotation axis.

- sx (dict; optional):
    MUI `sx` styling object (object form only).

- width (number | string; optional):
    Chart width in px (defaults to filling the container)."""
    _children_props: typing.List[str] = []
    _base_nodes = ['children']
    _namespace = 'dash_mui_scheduler'
    _type = 'RadialLineChart'
    Grid = TypedDict(
        "Grid",
            {
            "rotation": NotRequired[bool],
            "radius": NotRequired[bool]
        }
    )

    AxisHighlight = TypedDict(
        "AxisHighlight",
            {
            "rotation": NotRequired[Literal["none", "line", "band"]],
            "radius": NotRequired[Literal["none", "line", "band"]]
        }
    )


    def __init__(
        self,
        id: typing.Optional[typing.Union[str, dict]] = None,
        className: typing.Optional[str] = None,
        height: typing.Optional[typing.Union[NumberType, str]] = None,
        width: typing.Optional[typing.Union[NumberType, str]] = None,
        sx: typing.Optional[dict] = None,
        licenseKey: typing.Optional[str] = None,
        series: typing.Optional[typing.Sequence[dict]] = None,
        dataset: typing.Optional[typing.Sequence[dict]] = None,
        rotationAxis: typing.Optional[typing.Sequence[dict]] = None,
        radiusAxis: typing.Optional[typing.Sequence[dict]] = None,
        grid: typing.Optional["Grid"] = None,
        axisHighlight: typing.Optional["AxisHighlight"] = None,
        margin: typing.Optional[typing.Union[NumberType, dict]] = None,
        colors: typing.Optional[typing.Sequence[str]] = None,
        hideLegend: typing.Optional[bool] = None,
        disableLineItemHighlight: typing.Optional[bool] = None,
        skipAnimation: typing.Optional[bool] = None,
        showToolbar: typing.Optional[bool] = None,
        slotProps: typing.Optional[dict] = None,
        clickData: typing.Optional[dict] = None,
        **kwargs
    ):
        self._prop_names = ['id', 'axisHighlight', 'className', 'clickData', 'colors', 'dataset', 'disableLineItemHighlight', 'grid', 'height', 'hideLegend', 'licenseKey', 'margin', 'radiusAxis', 'rotationAxis', 'series', 'showToolbar', 'skipAnimation', 'slotProps', 'sx', 'width']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'axisHighlight', 'className', 'clickData', 'colors', 'dataset', 'disableLineItemHighlight', 'grid', 'height', 'hideLegend', 'licenseKey', 'margin', 'radiusAxis', 'rotationAxis', 'series', 'showToolbar', 'skipAnimation', 'slotProps', 'sx', 'width']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(RadialLineChart, self).__init__(**args)

setattr(RadialLineChart, "__init__", _explicitize_args(RadialLineChart.__init__))
