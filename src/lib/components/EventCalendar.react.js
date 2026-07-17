/**
 * EventCalendar — Dash wrapper for MUI X `EventCalendar` (Community, MIT).
 *
 * import { EventCalendar } from '@mui/x-scheduler/event-calendar'
 *
 * Dash boundary contract
 * ----------------------
 * The MUI `SchedulerEvent` model already uses ISO strings for `start`/`end`,
 * so `events` is fully JSON-serializable and round-trips verbatim between
 * Python and the component. The only value that crosses as a real JS `Date`
 * is `visibleDate` (the scheduler's default date adapter is date-fns), which
 * this wrapper converts string<->Date at the edge.
 *
 * Controlled outputs: `events` (+ a convenience `lastAction`), `view`,
 * `visibleDate`, `visibleResources`, and `preferences` are written back via
 * `setProps` whenever the user interacts, so each can be used as a Dash
 * `Input`. The component re-skins for dark mode by following the surrounding
 * Mantine color scheme (same mechanism as dash-mui-charts).
 */
import React, {useCallback, useEffect, useMemo, useRef} from 'react';
import PropTypes from 'prop-types';
import {EventCalendar as MuiEventCalendar} from '@mui/x-scheduler/event-calendar';
import {ThemeProvider} from '@mui/material/styles';
import {
    useMantineColorScheme,
    lightTheme,
    darkTheme,
    parseDate,
    dateToISO,
    diffEvents,
    injectSchedulerDialogCSS,
    getInitialSidePanelOpen,
    useScrollToCurrentTime,
} from '../utils/schedulerUtils';

const COLORS = [
    'red', 'pink', 'purple', 'indigo', 'blue',
    'teal', 'green', 'lime', 'amber', 'orange', 'grey',
];
const VIEWS = ['day', 'week', 'month', 'agenda'];

/**
 * EventCalendar is a day / week / month / agenda calendar for displaying and
 * editing events, wrapping the MUI X `EventCalendar` (Community, MIT). Events
 * cross the Dash boundary as plain dicts with ISO-string dates; user edits
 * (create / move / resize / delete) round-trip back through the `events` prop.
 */
const EventCalendar = (props) => {
    const {
        id,
        className,
        height,
        sx,
        events,
        resources,
        visibleResources,
        defaultVisibleResources,
        shouldEventRequireResource,
        views,
        view,
        defaultView,
        visibleDate,
        defaultVisibleDate,
        areEventsDraggable,
        areEventsResizable,
        canDragEventsFromTheOutside,
        canDropEventsToTheOutside,
        readOnly,
        eventColor,
        eventCreation,
        showCurrentTimeIndicator,
        displayTimezone,
        preferences,
        defaultPreferences,
        preferencesMenuConfig,
        localeText,
        eventDialogVariant,
        responsiveSidePanel,
        scrollToCurrentTime,
        mobileBreakpoint,
        eventDialogTopOffset,
        setProps,
    } = props;

    const scheme = useMantineColorScheme();
    const theme = scheme === 'dark' ? darkTheme : lightTheme;

    const rootRef = useRef(null);

    // The initial side-panel state is decided once, from the viewport width.
    const initialSidePanelOpen = useMemo(
        () => getInitialSidePanelOpen(mobileBreakpoint),
        // eslint-disable-next-line react-hooks/exhaustive-deps
        []
    );

    // Restyle the (body-portaled) event dialog into a responsive drawer.
    useEffect(() => {
        if (eventDialogVariant === 'drawer') injectSchedulerDialogCSS(mobileBreakpoint);
    }, [eventDialogVariant, mobileBreakpoint]);

    // Optionally inset the desktop drawer below a fixed app header.
    useEffect(() => {
        if (
            eventDialogTopOffset !== undefined &&
            eventDialogTopOffset !== null &&
            typeof document !== 'undefined'
        ) {
            document.documentElement.style.setProperty(
                '--dms-dialog-top-offset',
                `${eventDialogTopOffset}px`
            );
        }
    }, [eventDialogTopOffset]);

    // Pan the time grid so "now" is in view (day / week views).
    useScrollToCurrentTime(rootRef, scrollToCurrentTime, view);

    // Track the latest events so the change handler can diff prev -> next.
    const eventsRef = useRef(events);
    eventsRef.current = events;

    const handleEventsChange = useCallback(
        (newEvents) => {
            if (!setProps) return;
            setProps({
                events: newEvents,
                lastAction: diffEvents(eventsRef.current, newEvents),
            });
        },
        [setProps]
    );

    const handleViewChange = useCallback(
        (newView) => {
            if (setProps) setProps({view: newView});
        },
        [setProps]
    );

    const handleVisibleDateChange = useCallback(
        (newDate) => {
            if (setProps) setProps({visibleDate: dateToISO(newDate)});
        },
        [setProps]
    );

    const handleVisibleResourcesChange = useCallback(
        (map) => {
            if (setProps) setProps({visibleResources: map});
        },
        [setProps]
    );

    const handlePreferencesChange = useCallback(
        (prefs) => {
            if (setProps) setProps({preferences: prefs});
        },
        [setProps]
    );

    // Assemble the controlled / uncontrolled props, only including a controlled
    // prop when the user actually provided it (so we don't flip React between
    // controlled and uncontrolled and emit warnings).
    const params = {
        events: events || [],
        onEventsChange: handleEventsChange,
        onViewChange: handleViewChange,
        onVisibleDateChange: handleVisibleDateChange,
        onVisibleResourcesChange: handleVisibleResourcesChange,
        onPreferencesChange: handlePreferencesChange,
    };

    if (resources !== undefined) params.resources = resources;
    if (shouldEventRequireResource !== undefined) {
        params.shouldEventRequireResource = shouldEventRequireResource;
    }
    if (views !== undefined) params.views = views;
    if (areEventsDraggable !== undefined) params.areEventsDraggable = areEventsDraggable;
    if (areEventsResizable !== undefined) params.areEventsResizable = areEventsResizable;
    if (canDragEventsFromTheOutside !== undefined) {
        params.canDragEventsFromTheOutside = canDragEventsFromTheOutside;
    }
    if (canDropEventsToTheOutside !== undefined) {
        params.canDropEventsToTheOutside = canDropEventsToTheOutside;
    }
    if (readOnly !== undefined) params.readOnly = readOnly;
    if (eventColor !== undefined) params.eventColor = eventColor;
    if (eventCreation !== undefined) params.eventCreation = eventCreation;
    if (showCurrentTimeIndicator !== undefined) {
        params.showCurrentTimeIndicator = showCurrentTimeIndicator;
    }
    if (displayTimezone !== undefined) params.displayTimezone = displayTimezone;
    if (preferencesMenuConfig !== undefined) {
        params.preferencesMenuConfig = preferencesMenuConfig;
    }
    if (localeText !== undefined) params.localeText = localeText;
    if (sx !== undefined) params.sx = sx;

    // view (controlled) vs defaultView (uncontrolled)
    if (view !== undefined && view !== null) params.view = view;
    else if (defaultView !== undefined) params.defaultView = defaultView;

    // visibleDate (controlled) vs defaultVisibleDate (uncontrolled)
    if (visibleDate !== undefined && visibleDate !== null) {
        params.visibleDate = parseDate(visibleDate);
    } else if (defaultVisibleDate !== undefined) {
        params.defaultVisibleDate = parseDate(defaultVisibleDate);
    }

    // visibleResources (controlled) vs defaultVisibleResources (uncontrolled)
    if (visibleResources !== undefined && visibleResources !== null) {
        params.visibleResources = visibleResources;
    } else if (defaultVisibleResources !== undefined) {
        params.defaultVisibleResources = defaultVisibleResources;
    }

    // preferences (controlled) vs defaultPreferences (uncontrolled)
    if (preferences !== undefined && preferences !== null) {
        params.preferences = preferences;
    } else {
        let dp = defaultPreferences;
        if (responsiveSidePanel && (!dp || dp.isSidePanelOpen === undefined)) {
            dp = {...(dp || {}), isSidePanelOpen: initialSidePanelOpen};
        }
        if (dp !== undefined) params.defaultPreferences = dp;
    }

    return (
        <div id={id} ref={rootRef} className={className} style={{height, width: '100%'}}>
            <ThemeProvider theme={theme}>
                {/* Key on displayTimezone: the scheduler memoizes processed
                    event times and does not re-project them on a live
                    displayTimezone change, so remount to apply the new zone. */}
                <MuiEventCalendar key={displayTimezone || 'default'} {...params} />
            </ThemeProvider>
        </div>
    );
};

EventCalendar.defaultProps = {
    height: 600,
    eventDialogVariant: 'drawer',
    responsiveSidePanel: true,
    scrollToCurrentTime: false,
    mobileBreakpoint: 768,
};

EventCalendar.propTypes = {
    /** The id used to identify this component in Dash callbacks. */
    id: PropTypes.string,

    /** CSS class applied to the wrapping div. */
    className: PropTypes.string,

    /** Height of the wrapping container (the calendar fills it). Default 600. */
    height: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),

    /** MUI `sx` styling object applied to the calendar (object form only). */
    sx: PropTypes.object,

    // --- Events -------------------------------------------------------------
    /**
     * The events to render. Each event is a dict with at least `id`, `title`,
     * `start` and `end` (ISO strings). This is BOTH an input and an output:
     * the calendar writes the full array back on every create / edit / move /
     * resize / delete.
     */
    events: PropTypes.arrayOf(
        PropTypes.exact({
            /** Unique id (string or number). */
            id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
            /** Event title. */
            title: PropTypes.string.isRequired,
            /** Start date-time, ISO string. "Z" suffix = UTC instant. */
            start: PropTypes.string.isRequired,
            /** End date-time, ISO string. "Z" suffix = UTC instant. */
            end: PropTypes.string.isRequired,
            /** Optional longer description (shown in the event dialog). */
            description: PropTypes.string,
            /** IANA timezone the wall-time start/end are interpreted in. */
            timezone: PropTypes.string,
            /** Id of the resource this event belongs to. */
            resource: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
            /**
             * Recurrence rule — an RFC-5545 RRULE string
             * ("FREQ=WEEKLY;INTERVAL=2;BYDAY=TH") or an object
             * {freq, interval, byDay, byMonthDay, byMonth, count, until}.
             * Recurrence is a Premium feature (use EventCalendarPremium).
             */
            rrule: PropTypes.oneOfType([PropTypes.string, PropTypes.object]),
            /** Exception dates (ISO strings) excluded from the recurrence. */
            exDates: PropTypes.arrayOf(PropTypes.string),
            /** Whether the event spans the whole day. */
            allDay: PropTypes.bool,
            /** Whether the event cannot be edited / dragged / resized. */
            readOnly: PropTypes.bool,
            /** Event color (overrides resource + component color). */
            color: PropTypes.oneOf(COLORS),
            /** Per-event drag override. */
            draggable: PropTypes.bool,
            /** Per-event resize override (bool or which edge). */
            resizable: PropTypes.oneOfType([
                PropTypes.bool,
                PropTypes.oneOf(['start', 'end']),
            ]),
            /** Custom CSS class for the event element. */
            className: PropTypes.string,
            /** Id of the event this one was split from. */
            extractedFromId: PropTypes.oneOfType([
                PropTypes.string,
                PropTypes.number,
            ]),
        })
    ),

    /**
     * The default color palette used for all events. Overridden per resource
     * (`eventColor`) and per event (`color`). Default "teal".
     */
    eventColor: PropTypes.oneOf(COLORS),

    /**
     * Configures event creation. `false` disables it; `true` enables it with
     * defaults; an object sets the interaction and default duration (minutes).
     */
    eventCreation: PropTypes.oneOfType([
        PropTypes.bool,
        PropTypes.exact({
            interaction: PropTypes.oneOf(['click', 'double-click']),
            duration: PropTypes.number,
        }),
    ]),

    // --- Resources ----------------------------------------------------------
    /** Resources events can be assigned to (supports nested `children`). */
    resources: PropTypes.arrayOf(PropTypes.object),

    /** Controlled resource visibility map {resourceId: bool}. Also an OUTPUT. */
    visibleResources: PropTypes.object,

    /** Uncontrolled initial resource visibility map. Default {} (all visible). */
    defaultVisibleResources: PropTypes.object,

    /** Require every event to be assigned to a resource. Default false. */
    shouldEventRequireResource: PropTypes.bool,

    // --- Views --------------------------------------------------------------
    /** Which views are offered. Default ["day","week","month","agenda"]. */
    views: PropTypes.arrayOf(PropTypes.oneOf(VIEWS)),

    /** Controlled active view. Also an OUTPUT (updated on view change). */
    view: PropTypes.oneOf(VIEWS),

    /** Uncontrolled initial view. Default "week". */
    defaultView: PropTypes.oneOf(VIEWS),

    // --- Navigation ---------------------------------------------------------
    /**
     * Controlled visible date (ISO string). Drives which date range is shown.
     * Also an OUTPUT — written back (ISO string) when the user navigates.
     */
    visibleDate: PropTypes.string,

    /** Uncontrolled initial visible date (ISO string). Default today. */
    defaultVisibleDate: PropTypes.string,

    // --- Drag & resize ------------------------------------------------------
    /** Allow drag-to-reschedule. Default true. */
    areEventsDraggable: PropTypes.bool,

    /** Allow resize (bool, or restrict to "start"/"end"). Default true. */
    areEventsResizable: PropTypes.oneOfType([
        PropTypes.bool,
        PropTypes.oneOf(['start', 'end']),
    ]),

    /** Allow external events to be dragged in. Default false. */
    canDragEventsFromTheOutside: PropTypes.bool,

    /** Allow events to be dragged out of the calendar. Default false. */
    canDropEventsToTheOutside: PropTypes.bool,

    // --- Editing ------------------------------------------------------------
    /** Global read-only mode (disables create / drag / resize / dialog). */
    readOnly: PropTypes.bool,

    // --- Display ------------------------------------------------------------
    /** Show the current-time indicator line in time views. Default true. */
    showCurrentTimeIndicator: PropTypes.bool,

    /**
     * Timezone used to render events: an IANA name
     * ("America/New_York"), or "default" / "locale" / "UTC". Render-only —
     * events keep their own data timezone. Default "default".
     */
    displayTimezone: PropTypes.string,

    // --- Preferences --------------------------------------------------------
    /**
     * Controlled user preferences. Also an OUTPUT.
     * {ampm, weekStartsOn (0=Sun..6=Sat), showWeekends, showWeekNumber,
     *  isSidePanelOpen, showEmptyDaysInAgenda}.
     */
    preferences: PropTypes.exact({
        ampm: PropTypes.bool,
        weekStartsOn: PropTypes.oneOf([0, 1, 2, 3, 4, 5, 6]),
        showWeekends: PropTypes.bool,
        showWeekNumber: PropTypes.bool,
        isSidePanelOpen: PropTypes.bool,
        showEmptyDaysInAgenda: PropTypes.bool,
    }),

    /** Uncontrolled initial preferences (same shape as `preferences`). */
    defaultPreferences: PropTypes.exact({
        ampm: PropTypes.bool,
        weekStartsOn: PropTypes.oneOf([0, 1, 2, 3, 4, 5, 6]),
        showWeekends: PropTypes.bool,
        showWeekNumber: PropTypes.bool,
        isSidePanelOpen: PropTypes.bool,
        showEmptyDaysInAgenda: PropTypes.bool,
    }),

    /**
     * Which items appear in the preferences menu, or `false` to hide the menu.
     */
    preferencesMenuConfig: PropTypes.oneOfType([
        PropTypes.oneOf([false]),
        PropTypes.exact({
            toggleWeekendVisibility: PropTypes.bool,
            toggleWeekNumberVisibility: PropTypes.bool,
            toggleAmpm: PropTypes.bool,
            toggleEmptyDaysInAgenda: PropTypes.bool,
            toggleWeekStartsOn: PropTypes.bool,
        }),
    ]),

    // --- Localization -------------------------------------------------------
    /** Override UI label strings (a partial map of translation keys). */
    localeText: PropTypes.object,

    // --- Responsive UX (Dash wrapper additions) -----------------------------
    /**
     * How the event editor is presented. "drawer" (default) restyles the
     * built-in dialog into a responsive drawer — right-anchored on desktop, an
     * 80%-height bottom sheet on mobile (below `mobileBreakpoint`), with a
     * scrollable body and pinned header/actions. "dialog" keeps the library's
     * default floating, draggable dialog.
     */
    eventDialogVariant: PropTypes.oneOf(['drawer', 'dialog']),

    /**
     * When true (default), the side panel starts open on wide screens and
     * collapsed below `mobileBreakpoint` on first render — unless you pin
     * `isSidePanelOpen` via `preferences` / `defaultPreferences`.
     */
    responsiveSidePanel: PropTypes.bool,

    /**
     * In the day / week views, scroll the time grid on first render (and on
     * view change) so the current-time indicator is centered in view. Pairs
     * with `showCurrentTimeIndicator`. Default false.
     */
    scrollToCurrentTime: PropTypes.bool,

    /** Width (px) below which the UI switches to its mobile layout. Default 768. */
    mobileBreakpoint: PropTypes.number,

    /**
     * On desktop, inset the event drawer this many px from the top — e.g. set
     * it to your fixed app header's height so the drawer lines up with a
     * sidebar instead of covering the header. Default 0.
     */
    eventDialogTopOffset: PropTypes.number,

    // --- Outputs ------------------------------------------------------------
    /**
     * Convenience OUTPUT describing the most recent change to `events`:
     * {type: "create"|"update"|"delete"|"move"|"resize"|"change",
     *  event: the affected event (or null), event_timestamp}.
     */
    lastAction: PropTypes.exact({
        type: PropTypes.string,
        event: PropTypes.object,
        event_timestamp: PropTypes.number,
    }),

    /** Dash-assigned callback to report prop changes. */
    setProps: PropTypes.func,
};

export default EventCalendar;
