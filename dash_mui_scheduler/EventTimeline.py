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


class EventTimeline(Component):
    """An EventTimeline component.
EventTimeline is a resource-row, Gantt-style timeline that places events on
the row of the resource they are assigned to, across configurable zoom
presets, wrapping the MUI X `EventTimelinePremium`. Requires a MUI X Premium
license key (the `licenseKey` prop) to render without a watermark.

Keyword arguments:

- id (string; optional):
    The id used to identify this component in Dash callbacks.

- areEventsDraggable (boolean; optional):
    Allow drag-to-reschedule allocations. Default True.

- areEventsResizable (boolean | a value equal to: 'start', 'end'; optional):
    Allow resize (bool, or restrict to \"start\"/\"end\"). Default
    True.

- canDragEventsFromTheOutside (boolean; optional):
    Allow external events to be dragged in. Default False.

- canDropEventsToTheOutside (boolean; optional):
    Allow events to be dragged out of the timeline. Default False.

- className (string; optional):
    CSS class applied to the wrapping div.

- defaultPreferences (dict; optional):
    Uncontrolled initial preferences {ampm, weekStartsOn}. Default
    {ampm: True}.

    `defaultPreferences` is a dict with keys:

    - ampm (boolean; optional)

    - weekStartsOn (a value equal to: 0, 1, 2, 3, 4, 5, 6; optional)

- defaultPreset (a value equal to: 'dayAndHour', 'dayAndMonth', 'dayAndWeek', 'monthAndYear', 'year'; optional):
    Uncontrolled initial preset. Default \"dayAndHour\".

- defaultVisibleDate (string; optional):
    Uncontrolled initial visible date (ISO string). Default today.

- defaultVisibleResources (dict; optional):
    Uncontrolled initial resource visibility map. Default {} (all
    visible).

- displayTimezone (string; optional):
    Render timezone: IANA name, or \"default\"/\"locale\"/\"UTC\".
    Default \"default\".

- eventColor (a value equal to: 'red', 'pink', 'purple', 'indigo', 'blue', 'teal', 'green', 'lime', 'amber', 'orange', 'grey'; optional):
    Default color palette for all events (overridable). Default
    \"teal\".

- eventCreation (dict; optional):
    Configures event creation. `False` disables it; `True` enables
    defaults; an object sets {interaction, duration (minutes)}.

    `eventCreation` is a boolean | dict with keys:

    - interaction (a value equal to: 'click', 'double-click'; optional)

    - duration (number; optional)

- eventDialogTopOffset (number; optional):
    On desktop, inset the event drawer this many px from the top —
    e.g. set it to your fixed app header's height. Default 0.

- eventDialogVariant (a value equal to: 'drawer', 'dialog'; default 'drawer'):
    How the event editor is presented. \"drawer\" (default) restyles
    the built-in dialog into a responsive frosted-glass drawer —
    right-anchored on desktop, an 88%-height bottom sheet on mobile
    (below `mobileBreakpoint`). \"dialog\" keeps the library's
    floating dialog.

- events (list of dicts; optional):
    Allocation bars. Each event needs `id`, `title`, `start`, `end`
    (ISO strings) and usually a `resource` (the row it sits on). INPUT
    + OUTPUT.

    `events` is a list of dicts with keys:

    - id (string | number; required)

    - title (string; required)

    - start (string; required)

    - end (string; required)

    - description (string; optional)

    - timezone (string; optional)

    - resource (string | number; optional)

    - rrule (string | dict; optional)

    - exDates (list of strings; optional)

    - allDay (boolean; optional)

    - readOnly (boolean; optional)

    - color (a value equal to: 'red', 'pink', 'purple', 'indigo', 'blue', 'teal', 'green', 'lime', 'amber', 'orange', 'grey'; optional)

    - draggable (boolean; optional)

    - resizable (boolean | a value equal to: 'start', 'end'; optional)

    - className (string; optional)

    - extractedFromId (string | number; optional)

- height (number | string; default 400):
    Height of the wrapping container (the timeline fills it). Default
    400.

- lastAction (dict; optional):
    Convenience OUTPUT describing the most recent change to `events`.

    `lastAction` is a dict with keys:

    - type (string; optional)

    - event (dict; optional)

    - event_timestamp (number; optional)

- licenseKey (string; optional):
    MUI X Premium license key (removes the watermark).

- localeText (dict; optional):
    Override UI label strings (a partial map of translation keys).

- mobileBreakpoint (number; default 768):
    Width (px) below which the editor uses its mobile layout. Default
    768.

- preferences (dict; optional):
    Controlled preferences {ampm, weekStartsOn}. Also an OUTPUT.

    `preferences` is a dict with keys:

    - ampm (boolean; optional)

    - weekStartsOn (a value equal to: 0, 1, 2, 3, 4, 5, 6; optional)

- preset (a value equal to: 'dayAndHour', 'dayAndMonth', 'dayAndWeek', 'monthAndYear', 'year'; optional):
    Controlled zoom preset. Also an OUTPUT. One of \"dayAndHour\" |
    \"dayAndMonth\" | \"dayAndWeek\" | \"monthAndYear\" | \"year\".

- presets (list of a value equal to: 'dayAndHour', 'dayAndMonth', 'dayAndWeek', 'monthAndYear', 'year's; optional):
    The presets available (zoom levels offered). Default is all five,
    from most zoomed-in to most zoomed-out.

- readOnly (boolean; optional):
    Global read-only mode.

- resourceColumnLabel (string; optional):
    Label shown in the resource column header.

- resources (list of dicts; optional):
    The resource rows. Each event's `resource` points to one of these
    ids.

- shouldEventRequireResource (boolean; optional):
    Require every event to be assigned to a resource. Default True
    (timeline).

- showCurrentTimeIndicator (boolean; optional):
    Show the current-time indicator line. Default True.

- sx (dict; optional):
    MUI `sx` styling object applied to the timeline (object form
    only).

- visibleDate (string; optional):
    Controlled visible date (ISO string) — centers the window. Also
    OUTPUT.

- visibleResources (dict; optional):
    Controlled resource visibility map {resourceId: bool}. Also an
    OUTPUT."""
    _children_props: typing.List[str] = []
    _base_nodes = ['children']
    _namespace = 'dash_mui_scheduler'
    _type = 'EventTimeline'
    Events = TypedDict(
        "Events",
            {
            "id": typing.Union[str, NumberType],
            "title": str,
            "start": str,
            "end": str,
            "description": NotRequired[str],
            "timezone": NotRequired[str],
            "resource": NotRequired[typing.Union[str, NumberType]],
            "rrule": NotRequired[typing.Union[str, dict]],
            "exDates": NotRequired[typing.Sequence[str]],
            "allDay": NotRequired[bool],
            "readOnly": NotRequired[bool],
            "color": NotRequired[Literal["red", "pink", "purple", "indigo", "blue", "teal", "green", "lime", "amber", "orange", "grey"]],
            "draggable": NotRequired[bool],
            "resizable": NotRequired[typing.Union[bool, Literal["start", "end"]]],
            "className": NotRequired[str],
            "extractedFromId": NotRequired[typing.Union[str, NumberType]]
        }
    )

    EventCreation = TypedDict(
        "EventCreation",
            {
            "interaction": NotRequired[Literal["click", "double-click"]],
            "duration": NotRequired[NumberType]
        }
    )

    Preferences = TypedDict(
        "Preferences",
            {
            "ampm": NotRequired[bool],
            "weekStartsOn": NotRequired[Literal[0, 1, 2, 3, 4, 5, 6]]
        }
    )

    DefaultPreferences = TypedDict(
        "DefaultPreferences",
            {
            "ampm": NotRequired[bool],
            "weekStartsOn": NotRequired[Literal[0, 1, 2, 3, 4, 5, 6]]
        }
    )

    LastAction = TypedDict(
        "LastAction",
            {
            "type": NotRequired[str],
            "event": NotRequired[dict],
            "event_timestamp": NotRequired[NumberType]
        }
    )


    def __init__(
        self,
        id: typing.Optional[typing.Union[str, dict]] = None,
        className: typing.Optional[str] = None,
        height: typing.Optional[typing.Union[NumberType, str]] = None,
        sx: typing.Optional[dict] = None,
        licenseKey: typing.Optional[str] = None,
        events: typing.Optional[typing.Sequence["Events"]] = None,
        eventColor: typing.Optional[Literal["red", "pink", "purple", "indigo", "blue", "teal", "green", "lime", "amber", "orange", "grey"]] = None,
        eventCreation: typing.Optional[typing.Union[bool, "EventCreation"]] = None,
        resources: typing.Optional[typing.Sequence[dict]] = None,
        resourceColumnLabel: typing.Optional[str] = None,
        visibleResources: typing.Optional[dict] = None,
        defaultVisibleResources: typing.Optional[dict] = None,
        shouldEventRequireResource: typing.Optional[bool] = None,
        preset: typing.Optional[Literal["dayAndHour", "dayAndMonth", "dayAndWeek", "monthAndYear", "year"]] = None,
        defaultPreset: typing.Optional[Literal["dayAndHour", "dayAndMonth", "dayAndWeek", "monthAndYear", "year"]] = None,
        presets: typing.Optional[typing.Sequence[Literal["dayAndHour", "dayAndMonth", "dayAndWeek", "monthAndYear", "year"]]] = None,
        visibleDate: typing.Optional[str] = None,
        defaultVisibleDate: typing.Optional[str] = None,
        areEventsDraggable: typing.Optional[bool] = None,
        areEventsResizable: typing.Optional[typing.Union[bool, Literal["start", "end"]]] = None,
        canDragEventsFromTheOutside: typing.Optional[bool] = None,
        canDropEventsToTheOutside: typing.Optional[bool] = None,
        readOnly: typing.Optional[bool] = None,
        showCurrentTimeIndicator: typing.Optional[bool] = None,
        displayTimezone: typing.Optional[str] = None,
        preferences: typing.Optional["Preferences"] = None,
        defaultPreferences: typing.Optional["DefaultPreferences"] = None,
        localeText: typing.Optional[dict] = None,
        eventDialogVariant: typing.Optional[Literal["drawer", "dialog"]] = None,
        mobileBreakpoint: typing.Optional[NumberType] = None,
        eventDialogTopOffset: typing.Optional[NumberType] = None,
        lastAction: typing.Optional["LastAction"] = None,
        **kwargs
    ):
        self._prop_names = ['id', 'areEventsDraggable', 'areEventsResizable', 'canDragEventsFromTheOutside', 'canDropEventsToTheOutside', 'className', 'defaultPreferences', 'defaultPreset', 'defaultVisibleDate', 'defaultVisibleResources', 'displayTimezone', 'eventColor', 'eventCreation', 'eventDialogTopOffset', 'eventDialogVariant', 'events', 'height', 'lastAction', 'licenseKey', 'localeText', 'mobileBreakpoint', 'preferences', 'preset', 'presets', 'readOnly', 'resourceColumnLabel', 'resources', 'shouldEventRequireResource', 'showCurrentTimeIndicator', 'sx', 'visibleDate', 'visibleResources']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'areEventsDraggable', 'areEventsResizable', 'canDragEventsFromTheOutside', 'canDropEventsToTheOutside', 'className', 'defaultPreferences', 'defaultPreset', 'defaultVisibleDate', 'defaultVisibleResources', 'displayTimezone', 'eventColor', 'eventCreation', 'eventDialogTopOffset', 'eventDialogVariant', 'events', 'height', 'lastAction', 'licenseKey', 'localeText', 'mobileBreakpoint', 'preferences', 'preset', 'presets', 'readOnly', 'resourceColumnLabel', 'resources', 'shouldEventRequireResource', 'showCurrentTimeIndicator', 'sx', 'visibleDate', 'visibleResources']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(EventTimeline, self).__init__(**args)

setattr(EventTimeline, "__init__", _explicitize_args(EventTimeline.__init__))
