/**
 * EventCalendarPremium — Dash wrapper for MUI X `EventCalendarPremium`.
 *
 * import { EventCalendarPremium } from '@mui/x-scheduler-premium/event-calendar-premium'
 *
 * Same surface as `EventCalendar`, plus the Premium recurrence engine: events
 * may carry an `rrule` (RFC-5545 string or object) and `exDates`, and the edit
 * dialog gains a Recurrence tab. Requires a valid MUI X Premium license key
 * (set via the `licenseKey` prop) to render without a watermark.
 */
import React, {useCallback, useEffect, useMemo, useRef} from 'react';
import PropTypes from 'prop-types';
import {EventCalendarPremium as MuiEventCalendarPremium} from '@mui/x-scheduler-premium/event-calendar-premium';
import {ThemeProvider} from '@mui/material/styles';
import {LicenseInfo} from '@mui/x-license';
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

// Set the MUI X license on the (v9) singleton once per distinct key.
let _lastLicenseKey;
const ensureLicense = (key) => {
    if (key && key !== _lastLicenseKey) {
        LicenseInfo.setLicenseKey(key);
        _lastLicenseKey = key;
    }
};

/**
 * EventCalendarPremium is the Event Calendar with the MUI X Premium recurrence
 * engine: events can carry an `rrule` (RFC-5545 string or object) and
 * `exDates`, and the edit dialog gains a Recurrence tab. Requires a MUI X
 * Premium license key (the `licenseKey` prop) to render without a watermark.
 */
const EventCalendarPremium = (props) => {
    const {
        id,
        className,
        height,
        sx,
        licenseKey,
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

    ensureLicense(licenseKey);

    const scheme = useMantineColorScheme();
    const theme = scheme === 'dark' ? darkTheme : lightTheme;

    const rootRef = useRef(null);

    const initialSidePanelOpen = useMemo(
        () => getInitialSidePanelOpen(mobileBreakpoint),
        // eslint-disable-next-line react-hooks/exhaustive-deps
        []
    );

    useEffect(() => {
        if (eventDialogVariant === 'drawer') injectSchedulerDialogCSS(mobileBreakpoint);
    }, [eventDialogVariant, mobileBreakpoint]);

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

    useScrollToCurrentTime(rootRef, scrollToCurrentTime, view);

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

    if (view !== undefined && view !== null) params.view = view;
    else if (defaultView !== undefined) params.defaultView = defaultView;

    if (visibleDate !== undefined && visibleDate !== null) {
        params.visibleDate = parseDate(visibleDate);
    } else if (defaultVisibleDate !== undefined) {
        params.defaultVisibleDate = parseDate(defaultVisibleDate);
    }

    if (visibleResources !== undefined && visibleResources !== null) {
        params.visibleResources = visibleResources;
    } else if (defaultVisibleResources !== undefined) {
        params.defaultVisibleResources = defaultVisibleResources;
    }

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
                {/* Remount on displayTimezone change so events re-project. */}
                <MuiEventCalendarPremium key={displayTimezone || 'default'} {...params} />
            </ThemeProvider>
        </div>
    );
};

EventCalendarPremium.defaultProps = {
    height: 600,
    eventDialogVariant: 'drawer',
    responsiveSidePanel: true,
    scrollToCurrentTime: false,
    mobileBreakpoint: 768,
};

EventCalendarPremium.propTypes = {
    /** The id used to identify this component in Dash callbacks. */
    id: PropTypes.string,

    /** CSS class applied to the wrapping div. */
    className: PropTypes.string,

    /** Height of the wrapping container (the calendar fills it). Default 600. */
    height: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),

    /** MUI `sx` styling object applied to the calendar (object form only). */
    sx: PropTypes.object,

    /**
     * MUI X Premium license key. Set once to remove the watermark and unlock
     * Premium features (recurrence). Read from an environment variable on the
     * server and pass it in.
     */
    licenseKey: PropTypes.string,

    // --- Events -------------------------------------------------------------
    /**
     * The events to render. Each event is a dict with at least `id`, `title`,
     * `start`, `end` (ISO strings). Premium events may also carry `rrule`
     * (recurrence) and `exDates`. INPUT + OUTPUT (round-trips on every change).
     */
    events: PropTypes.arrayOf(
        PropTypes.exact({
            id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
            title: PropTypes.string.isRequired,
            start: PropTypes.string.isRequired,
            end: PropTypes.string.isRequired,
            description: PropTypes.string,
            timezone: PropTypes.string,
            resource: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
            /**
             * Recurrence rule — RFC-5545 RRULE string
             * ("FREQ=WEEKLY;INTERVAL=2;BYDAY=TH") or an object
             * {freq:"DAILY|WEEKLY|MONTHLY|YEARLY", interval, byDay, byMonthDay,
             *  byMonth, count, until}.
             */
            rrule: PropTypes.oneOfType([PropTypes.string, PropTypes.object]),
            /** Exception dates (ISO strings) excluded from the recurrence. */
            exDates: PropTypes.arrayOf(PropTypes.string),
            allDay: PropTypes.bool,
            readOnly: PropTypes.bool,
            color: PropTypes.oneOf(COLORS),
            draggable: PropTypes.bool,
            resizable: PropTypes.oneOfType([
                PropTypes.bool,
                PropTypes.oneOf(['start', 'end']),
            ]),
            className: PropTypes.string,
            extractedFromId: PropTypes.oneOfType([
                PropTypes.string,
                PropTypes.number,
            ]),
        })
    ),

    /** Default color palette for all events (overridable). Default "teal". */
    eventColor: PropTypes.oneOf(COLORS),

    /**
     * Configures event creation. `false` disables it; `true` enables defaults;
     * an object sets {interaction, duration (minutes)}.
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

    /** Controlled active view. Also an OUTPUT. */
    view: PropTypes.oneOf(VIEWS),

    /** Uncontrolled initial view. Default "week". */
    defaultView: PropTypes.oneOf(VIEWS),

    // --- Navigation ---------------------------------------------------------
    /** Controlled visible date (ISO string). Also an OUTPUT. */
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

    /** Render timezone: IANA name, or "default"/"locale"/"UTC". Default "default". */
    displayTimezone: PropTypes.string,

    // --- Preferences --------------------------------------------------------
    /** Controlled user preferences. Also an OUTPUT. */
    preferences: PropTypes.exact({
        ampm: PropTypes.bool,
        weekStartsOn: PropTypes.oneOf([0, 1, 2, 3, 4, 5, 6]),
        showWeekends: PropTypes.bool,
        showWeekNumber: PropTypes.bool,
        isSidePanelOpen: PropTypes.bool,
        showEmptyDaysInAgenda: PropTypes.bool,
    }),

    /** Uncontrolled initial preferences. */
    defaultPreferences: PropTypes.exact({
        ampm: PropTypes.bool,
        weekStartsOn: PropTypes.oneOf([0, 1, 2, 3, 4, 5, 6]),
        showWeekends: PropTypes.bool,
        showWeekNumber: PropTypes.bool,
        isSidePanelOpen: PropTypes.bool,
        showEmptyDaysInAgenda: PropTypes.bool,
    }),

    /** Which items appear in the preferences menu, or `false` to hide it. */
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
     * {type, event, event_timestamp}.
     */
    lastAction: PropTypes.exact({
        type: PropTypes.string,
        event: PropTypes.object,
        event_timestamp: PropTypes.number,
    }),

    /** Dash-assigned callback to report prop changes. */
    setProps: PropTypes.func,
};

export default EventCalendarPremium;
