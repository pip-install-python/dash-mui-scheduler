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


class EventCalendarPremium(Component):
    """An EventCalendarPremium component.
EventCalendarPremium is the Event Calendar with the MUI X Premium recurrence
engine: events can carry an `rrule` (RFC-5545 string or object) and
`exDates`, and the edit dialog gains a Recurrence tab. Requires a MUI X
Premium license key (the `licenseKey` prop) to render without a watermark.

Keyword arguments:

- id (string; optional):
    The id used to identify this component in Dash callbacks.

- areEventsDraggable (boolean; optional):
    Allow drag-to-reschedule. Default True.

- areEventsResizable (boolean | a value equal to: 'start', 'end'; optional):
    Allow resize (bool, or restrict to \"start\"/\"end\"). Default
    True.

- canDragEventsFromTheOutside (boolean; optional):
    Allow external events to be dragged in. Default False.

- canDropEventsToTheOutside (boolean; optional):
    Allow events to be dragged out of the calendar. Default False.

- className (string; optional):
    CSS class applied to the wrapping div.

- defaultPreferences (dict; optional):
    Uncontrolled initial preferences.

    `defaultPreferences` is a dict with keys:

    - ampm (boolean; optional)

    - weekStartsOn (a value equal to: 0, 1, 2, 3, 4, 5, 6; optional)

    - showWeekends (boolean; optional)

    - showWeekNumber (boolean; optional)

    - isSidePanelOpen (boolean; optional)

    - showEmptyDaysInAgenda (boolean; optional)

- defaultView (a value equal to: 'day', 'week', 'month', 'agenda'; optional):
    Uncontrolled initial view. Default \"week\".

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
    e.g. set it to your fixed app header's height so the drawer lines
    up with a sidebar instead of covering the header. Default 0.

- eventDialogVariant (a value equal to: 'drawer', 'dialog'; default 'drawer'):
    How the event editor is presented. \"drawer\" (default) restyles
    the built-in dialog into a responsive drawer — right-anchored on
    desktop, an 80%-height bottom sheet on mobile (below
    `mobileBreakpoint`), with a scrollable body and pinned
    header/actions. \"dialog\" keeps the library's default floating,
    draggable dialog.

- events (list of dicts; optional):
    The events to render. Each event is a dict with at least `id`,
    `title`, `start`, `end` (ISO strings). Premium events may also
    carry `rrule` (recurrence) and `exDates`. INPUT + OUTPUT
    (round-trips on every change).

    `events` is a list of dicts with keys:

    - id (string | number; required)

    - title (string; required)

    - start (string; required)

    - end (string; required)

    - description (string; optional)

    - timezone (string; optional)

    - resource (string | number; optional)

    - rrule (string | dict; optional):
        Recurrence rule — RFC-5545 RRULE string
        (\"FREQ=WEEKLY;INTERVAL=2;BYDAY=TH\") or an object
        {freq:\"DAILY|WEEKLY|MONTHLY|YEARLY\", interval, byDay,
        byMonthDay,  byMonth, count, until}.

    - exDates (list of strings; optional):
        Exception dates (ISO strings) excluded from the recurrence.

    - allDay (boolean; optional)

    - readOnly (boolean; optional)

    - color (a value equal to: 'red', 'pink', 'purple', 'indigo', 'blue', 'teal', 'green', 'lime', 'amber', 'orange', 'grey'; optional)

    - draggable (boolean; optional)

    - resizable (boolean | a value equal to: 'start', 'end'; optional)

    - className (string; optional)

    - extractedFromId (string | number; optional)

- height (number | string; default 600):
    Height of the wrapping container (the calendar fills it). Default
    600.

- lastAction (dict; optional):
    Convenience OUTPUT describing the most recent change to `events`:
    {type, event, event_timestamp}.

    `lastAction` is a dict with keys:

    - type (string; optional)

    - event (dict; optional)

    - event_timestamp (number; optional)

- licenseKey (string; optional):
    MUI X Premium license key. Set once to remove the watermark and
    unlock Premium features (recurrence). Read from an environment
    variable on the server and pass it in.

- localeText (dict; optional):
    Override UI label strings (a partial map of translation keys).

- mobileBreakpoint (number; default 768):
    Width (px) below which the UI switches to its mobile layout.
    Default 768.

- preferences (dict; optional):
    Controlled user preferences. Also an OUTPUT.

    `preferences` is a dict with keys:

    - ampm (boolean; optional)

    - weekStartsOn (a value equal to: 0, 1, 2, 3, 4, 5, 6; optional)

    - showWeekends (boolean; optional)

    - showWeekNumber (boolean; optional)

    - isSidePanelOpen (boolean; optional)

    - showEmptyDaysInAgenda (boolean; optional)

- preferencesMenuConfig (dict; optional):
    Which items appear in the preferences menu, or `False` to hide it.

    `preferencesMenuConfig` is a a value equal to: false | dict with
    keys:

    - toggleWeekendVisibility (boolean; optional)

    - toggleWeekNumberVisibility (boolean; optional)

    - toggleAmpm (boolean; optional)

    - toggleEmptyDaysInAgenda (boolean; optional)

    - toggleWeekStartsOn (boolean; optional)

- readOnly (boolean; optional):
    Global read-only mode (disables create / drag / resize / dialog).

- resources (list of dicts; optional):
    Resources events can be assigned to (supports nested `children`).

- responsiveSidePanel (boolean; default True):
    When True (default), the side panel starts open on wide screens
    and collapsed below `mobileBreakpoint` on first render — unless
    you pin `isSidePanelOpen` via `preferences` /
    `defaultPreferences`.

- scrollToCurrentTime (boolean; default False):
    In the day / week views, scroll the time grid on first render (and
    on view change) so the current-time indicator is centered in view.
    Pairs with `showCurrentTimeIndicator`. Default False.

- shouldEventRequireResource (boolean; optional):
    Require every event to be assigned to a resource. Default False.

- showCurrentTimeIndicator (boolean; optional):
    Show the current-time indicator line in time views. Default True.

- sx (dict; optional):
    MUI `sx` styling object applied to the calendar (object form
    only).

- view (a value equal to: 'day', 'week', 'month', 'agenda'; optional):
    Controlled active view. Also an OUTPUT.

- views (list of a value equal to: 'day', 'week', 'month', 'agenda's; optional):
    Which views are offered. Default
    [\"day\",\"week\",\"month\",\"agenda\"].

- visibleDate (string; optional):
    Controlled visible date (ISO string). Also an OUTPUT.

- visibleResources (dict; optional):
    Controlled resource visibility map {resourceId: bool}. Also an
    OUTPUT."""
    _children_props: typing.List[str] = []
    _base_nodes = ['children']
    _namespace = 'dash_mui_scheduler'
    _type = 'EventCalendarPremium'
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
            "weekStartsOn": NotRequired[Literal[0, 1, 2, 3, 4, 5, 6]],
            "showWeekends": NotRequired[bool],
            "showWeekNumber": NotRequired[bool],
            "isSidePanelOpen": NotRequired[bool],
            "showEmptyDaysInAgenda": NotRequired[bool]
        }
    )

    DefaultPreferences = TypedDict(
        "DefaultPreferences",
            {
            "ampm": NotRequired[bool],
            "weekStartsOn": NotRequired[Literal[0, 1, 2, 3, 4, 5, 6]],
            "showWeekends": NotRequired[bool],
            "showWeekNumber": NotRequired[bool],
            "isSidePanelOpen": NotRequired[bool],
            "showEmptyDaysInAgenda": NotRequired[bool]
        }
    )

    PreferencesMenuConfig = TypedDict(
        "PreferencesMenuConfig",
            {
            "toggleWeekendVisibility": NotRequired[bool],
            "toggleWeekNumberVisibility": NotRequired[bool],
            "toggleAmpm": NotRequired[bool],
            "toggleEmptyDaysInAgenda": NotRequired[bool],
            "toggleWeekStartsOn": NotRequired[bool]
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
        visibleResources: typing.Optional[dict] = None,
        defaultVisibleResources: typing.Optional[dict] = None,
        shouldEventRequireResource: typing.Optional[bool] = None,
        views: typing.Optional[typing.Sequence[Literal["day", "week", "month", "agenda"]]] = None,
        view: typing.Optional[Literal["day", "week", "month", "agenda"]] = None,
        defaultView: typing.Optional[Literal["day", "week", "month", "agenda"]] = None,
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
        preferencesMenuConfig: typing.Optional[typing.Union[Literal[False], "PreferencesMenuConfig"]] = None,
        localeText: typing.Optional[dict] = None,
        eventDialogVariant: typing.Optional[Literal["drawer", "dialog"]] = None,
        responsiveSidePanel: typing.Optional[bool] = None,
        scrollToCurrentTime: typing.Optional[bool] = None,
        mobileBreakpoint: typing.Optional[NumberType] = None,
        eventDialogTopOffset: typing.Optional[NumberType] = None,
        lastAction: typing.Optional["LastAction"] = None,
        **kwargs
    ):
        self._prop_names = ['id', 'areEventsDraggable', 'areEventsResizable', 'canDragEventsFromTheOutside', 'canDropEventsToTheOutside', 'className', 'defaultPreferences', 'defaultView', 'defaultVisibleDate', 'defaultVisibleResources', 'displayTimezone', 'eventColor', 'eventCreation', 'eventDialogTopOffset', 'eventDialogVariant', 'events', 'height', 'lastAction', 'licenseKey', 'localeText', 'mobileBreakpoint', 'preferences', 'preferencesMenuConfig', 'readOnly', 'resources', 'responsiveSidePanel', 'scrollToCurrentTime', 'shouldEventRequireResource', 'showCurrentTimeIndicator', 'sx', 'view', 'views', 'visibleDate', 'visibleResources']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'areEventsDraggable', 'areEventsResizable', 'canDragEventsFromTheOutside', 'canDropEventsToTheOutside', 'className', 'defaultPreferences', 'defaultView', 'defaultVisibleDate', 'defaultVisibleResources', 'displayTimezone', 'eventColor', 'eventCreation', 'eventDialogTopOffset', 'eventDialogVariant', 'events', 'height', 'lastAction', 'licenseKey', 'localeText', 'mobileBreakpoint', 'preferences', 'preferencesMenuConfig', 'readOnly', 'resources', 'responsiveSidePanel', 'scrollToCurrentTime', 'shouldEventRequireResource', 'showCurrentTimeIndicator', 'sx', 'view', 'views', 'visibleDate', 'visibleResources']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(EventCalendarPremium, self).__init__(**args)

setattr(EventCalendarPremium, "__init__", _explicitize_args(EventCalendarPremium.__init__))
