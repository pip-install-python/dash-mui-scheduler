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


class EventCalendar(Component):
    """An EventCalendar component.
EventCalendar is a day / week / month / agenda calendar for displaying and
editing events, wrapping the MUI X `EventCalendar` (Community, MIT). Events
cross the Dash boundary as plain dicts with ISO-string dates; user edits
(create / move / resize / delete) round-trip back through the `events` prop.

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
    Uncontrolled initial preferences (same shape as `preferences`).

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
    Timezone used to render events: an IANA name
    (\"America/New_York\"), or \"default\" / \"locale\" / \"UTC\".
    Render-only — events keep their own data timezone. Default
    \"default\".

- eventColor (a value equal to: 'red', 'pink', 'purple', 'indigo', 'blue', 'teal', 'green', 'lime', 'amber', 'orange', 'grey'; optional):
    The default color palette used for all events. Overridden per
    resource (`eventColor`) and per event (`color`). Default \"teal\".

- eventCreation (dict; optional):
    Configures event creation. `False` disables it; `True` enables it
    with defaults; an object sets the interaction and default duration
    (minutes).

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
    `title`, `start` and `end` (ISO strings). This is BOTH an input
    and an output: the calendar writes the full array back on every
    create / edit / move / resize / delete.

    `events` is a list of dicts with keys:

    - id (string | number; required):
        Unique id (string or number).

    - title (string; required):
        Event title.

    - start (string; required):
        Start date-time, ISO string. \"Z\" suffix = UTC instant.

    - end (string; required):
        End date-time, ISO string. \"Z\" suffix = UTC instant.

    - description (string; optional):
        Optional longer description (shown in the event dialog).

    - timezone (string; optional):
        IANA timezone the wall-time start/end are interpreted in.

    - resource (string | number; optional):
        Id of the resource this event belongs to.

    - rrule (string | dict; optional):
        Recurrence rule — an RFC-5545 RRULE string
        (\"FREQ=WEEKLY;INTERVAL=2;BYDAY=TH\") or an object {freq,
        interval, byDay, byMonthDay, byMonth, count, until}.
        Recurrence is a Premium feature (use EventCalendarPremium).

    - exDates (list of strings; optional):
        Exception dates (ISO strings) excluded from the recurrence.

    - allDay (boolean; optional):
        Whether the event spans the whole day.

    - readOnly (boolean; optional):
        Whether the event cannot be edited / dragged / resized.

    - color (a value equal to: 'red', 'pink', 'purple', 'indigo', 'blue', 'teal', 'green', 'lime', 'amber', 'orange', 'grey'; optional):
        Event color (overrides resource + component color).

    - draggable (boolean; optional):
        Per-event drag override.

    - resizable (boolean | a value equal to: 'start', 'end'; optional):
        Per-event resize override (bool or which edge).

    - className (string; optional):
        Custom CSS class for the event element.

    - extractedFromId (string | number; optional):
        Id of the event this one was split from.

- height (number | string; default 600):
    Height of the wrapping container (the calendar fills it). Default
    600.

- lastAction (dict; optional):
    Convenience OUTPUT describing the most recent change to `events`:
    {type:
    \"create\"|\"update\"|\"delete\"|\"move\"|\"resize\"|\"change\",
    event: the affected event (or None), event_timestamp}.

    `lastAction` is a dict with keys:

    - type (string; optional)

    - event (dict; optional)

    - event_timestamp (number; optional)

- localeText (dict; optional):
    Override UI label strings (a partial map of translation keys).

- mobileBreakpoint (number; default 768):
    Width (px) below which the UI switches to its mobile layout.
    Default 768.

- preferences (dict; optional):
    Controlled user preferences. Also an OUTPUT. {ampm, weekStartsOn
    (0=Sun..6=Sat), showWeekends, showWeekNumber,  isSidePanelOpen,
    showEmptyDaysInAgenda}.

    `preferences` is a dict with keys:

    - ampm (boolean; optional)

    - weekStartsOn (a value equal to: 0, 1, 2, 3, 4, 5, 6; optional)

    - showWeekends (boolean; optional)

    - showWeekNumber (boolean; optional)

    - isSidePanelOpen (boolean; optional)

    - showEmptyDaysInAgenda (boolean; optional)

- preferencesMenuConfig (dict; optional):
    Which items appear in the preferences menu, or `False` to hide the
    menu.

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
    Controlled active view. Also an OUTPUT (updated on view change).

- views (list of a value equal to: 'day', 'week', 'month', 'agenda's; optional):
    Which views are offered. Default
    [\"day\",\"week\",\"month\",\"agenda\"].

- visibleDate (string; optional):
    Controlled visible date (ISO string). Drives which date range is
    shown. Also an OUTPUT — written back (ISO string) when the user
    navigates.

- visibleResources (dict; optional):
    Controlled resource visibility map {resourceId: bool}. Also an
    OUTPUT."""
    _children_props: typing.List[str] = []
    _base_nodes = ['children']
    _namespace = 'dash_mui_scheduler'
    _type = 'EventCalendar'
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
        self._prop_names = ['id', 'areEventsDraggable', 'areEventsResizable', 'canDragEventsFromTheOutside', 'canDropEventsToTheOutside', 'className', 'defaultPreferences', 'defaultView', 'defaultVisibleDate', 'defaultVisibleResources', 'displayTimezone', 'eventColor', 'eventCreation', 'eventDialogTopOffset', 'eventDialogVariant', 'events', 'height', 'lastAction', 'localeText', 'mobileBreakpoint', 'preferences', 'preferencesMenuConfig', 'readOnly', 'resources', 'responsiveSidePanel', 'scrollToCurrentTime', 'shouldEventRequireResource', 'showCurrentTimeIndicator', 'sx', 'view', 'views', 'visibleDate', 'visibleResources']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'areEventsDraggable', 'areEventsResizable', 'canDragEventsFromTheOutside', 'canDropEventsToTheOutside', 'className', 'defaultPreferences', 'defaultView', 'defaultVisibleDate', 'defaultVisibleResources', 'displayTimezone', 'eventColor', 'eventCreation', 'eventDialogTopOffset', 'eventDialogVariant', 'events', 'height', 'lastAction', 'localeText', 'mobileBreakpoint', 'preferences', 'preferencesMenuConfig', 'readOnly', 'resources', 'responsiveSidePanel', 'scrollToCurrentTime', 'shouldEventRequireResource', 'showCurrentTimeIndicator', 'sx', 'view', 'views', 'visibleDate', 'visibleResources']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(EventCalendar, self).__init__(**args)

setattr(EventCalendar, "__init__", _explicitize_args(EventCalendar.__init__))
