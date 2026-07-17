/**
 * EventTimeline — Dash wrapper for MUI X `EventTimelinePremium`.
 *
 * import { EventTimelinePremium } from '@mui/x-scheduler-premium/event-timeline-premium'
 *
 * A resource-row Gantt-style timeline: each event sits on the row of the
 * `resource` it is assigned to. Premium-only — requires a MUI X Premium
 * license key (via `licenseKey`) to render without a watermark.
 *
 * Like the calendar wrappers, `events` round-trip as ISO strings and the only
 * date crossing as a JS `Date` is `visibleDate`. Zoom level is controlled
 * through the `preset` prop instead of a calendar `view`.
 */
import React, {useCallback, useEffect, useRef} from 'react';
import PropTypes from 'prop-types';
import {EventTimelinePremium as MuiEventTimelinePremium} from '@mui/x-scheduler-premium/event-timeline-premium';
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
} from '../utils/schedulerUtils';

const COLORS = [
    'red', 'pink', 'purple', 'indigo', 'blue',
    'teal', 'green', 'lime', 'amber', 'orange', 'grey',
];
const PRESETS = ['dayAndHour', 'dayAndMonth', 'dayAndWeek', 'monthAndYear', 'year'];

let _lastLicenseKey;
const ensureLicense = (key) => {
    if (key && key !== _lastLicenseKey) {
        LicenseInfo.setLicenseKey(key);
        _lastLicenseKey = key;
    }
};

/**
 * EventTimeline is a resource-row, Gantt-style timeline that places events on
 * the row of the resource they are assigned to, across configurable zoom
 * presets, wrapping the MUI X `EventTimelinePremium`. Requires a MUI X Premium
 * license key (the `licenseKey` prop) to render without a watermark.
 */
const EventTimeline = (props) => {
    const {
        id,
        className,
        height,
        sx,
        licenseKey,
        events,
        resources,
        resourceColumnLabel,
        visibleResources,
        defaultVisibleResources,
        shouldEventRequireResource,
        preset,
        defaultPreset,
        presets,
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
        localeText,
        eventDialogVariant,
        mobileBreakpoint,
        eventDialogTopOffset,
        setProps,
    } = props;

    ensureLicense(licenseKey);

    const scheme = useMantineColorScheme();
    const theme = scheme === 'dark' ? darkTheme : lightTheme;

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

    const handlePresetChange = useCallback(
        (newPreset) => {
            if (setProps) setProps({preset: newPreset});
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
        onPresetChange: handlePresetChange,
        onVisibleDateChange: handleVisibleDateChange,
        onVisibleResourcesChange: handleVisibleResourcesChange,
        onPreferencesChange: handlePreferencesChange,
    };

    if (resources !== undefined) params.resources = resources;
    if (resourceColumnLabel !== undefined) params.resourceColumnLabel = resourceColumnLabel;
    if (shouldEventRequireResource !== undefined) {
        params.shouldEventRequireResource = shouldEventRequireResource;
    }
    if (presets !== undefined) params.presets = presets;
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
    if (localeText !== undefined) params.localeText = localeText;
    if (sx !== undefined) params.sx = sx;

    // preset (controlled) vs defaultPreset (uncontrolled)
    if (preset !== undefined && preset !== null) params.preset = preset;
    else if (defaultPreset !== undefined) params.defaultPreset = defaultPreset;

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
    } else if (defaultPreferences !== undefined) {
        params.defaultPreferences = defaultPreferences;
    }

    return (
        <div id={id} className={className} style={{height, width: '100%'}}>
            <ThemeProvider theme={theme}>
                {/* Remount on displayTimezone change so events re-project. */}
                <MuiEventTimelinePremium key={displayTimezone || 'default'} {...params} />
            </ThemeProvider>
        </div>
    );
};

EventTimeline.defaultProps = {
    height: 400,
    eventDialogVariant: 'drawer',
    mobileBreakpoint: 768,
};

EventTimeline.propTypes = {
    /** The id used to identify this component in Dash callbacks. */
    id: PropTypes.string,

    /** CSS class applied to the wrapping div. */
    className: PropTypes.string,

    /** Height of the wrapping container (the timeline fills it). Default 400. */
    height: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),

    /** MUI `sx` styling object applied to the timeline (object form only). */
    sx: PropTypes.object,

    /** MUI X Premium license key (removes the watermark). */
    licenseKey: PropTypes.string,

    // --- Events -------------------------------------------------------------
    /**
     * Allocation bars. Each event needs `id`, `title`, `start`, `end` (ISO
     * strings) and usually a `resource` (the row it sits on). INPUT + OUTPUT.
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
            rrule: PropTypes.oneOfType([PropTypes.string, PropTypes.object]),
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
    /** The resource rows. Each event's `resource` points to one of these ids. */
    resources: PropTypes.arrayOf(PropTypes.object),

    /** Label shown in the resource column header. */
    resourceColumnLabel: PropTypes.string,

    /** Controlled resource visibility map {resourceId: bool}. Also an OUTPUT. */
    visibleResources: PropTypes.object,

    /** Uncontrolled initial resource visibility map. Default {} (all visible). */
    defaultVisibleResources: PropTypes.object,

    /** Require every event to be assigned to a resource. Default true (timeline). */
    shouldEventRequireResource: PropTypes.bool,

    // --- Presets (zoom) -----------------------------------------------------
    /**
     * Controlled zoom preset. Also an OUTPUT. One of
     * "dayAndHour" | "dayAndMonth" | "dayAndWeek" | "monthAndYear" | "year".
     */
    preset: PropTypes.oneOf(PRESETS),

    /** Uncontrolled initial preset. Default "dayAndHour". */
    defaultPreset: PropTypes.oneOf(PRESETS),

    /**
     * The presets available (zoom levels offered). Default is all five, from
     * most zoomed-in to most zoomed-out.
     */
    presets: PropTypes.arrayOf(PropTypes.oneOf(PRESETS)),

    // --- Navigation ---------------------------------------------------------
    /** Controlled visible date (ISO string) — centers the window. Also OUTPUT. */
    visibleDate: PropTypes.string,

    /** Uncontrolled initial visible date (ISO string). Default today. */
    defaultVisibleDate: PropTypes.string,

    // --- Drag & resize ------------------------------------------------------
    /** Allow drag-to-reschedule allocations. Default true. */
    areEventsDraggable: PropTypes.bool,

    /** Allow resize (bool, or restrict to "start"/"end"). Default true. */
    areEventsResizable: PropTypes.oneOfType([
        PropTypes.bool,
        PropTypes.oneOf(['start', 'end']),
    ]),

    /** Allow external events to be dragged in. Default false. */
    canDragEventsFromTheOutside: PropTypes.bool,

    /** Allow events to be dragged out of the timeline. Default false. */
    canDropEventsToTheOutside: PropTypes.bool,

    // --- Editing ------------------------------------------------------------
    /** Global read-only mode. */
    readOnly: PropTypes.bool,

    // --- Display ------------------------------------------------------------
    /** Show the current-time indicator line. Default true. */
    showCurrentTimeIndicator: PropTypes.bool,

    /** Render timezone: IANA name, or "default"/"locale"/"UTC". Default "default". */
    displayTimezone: PropTypes.string,

    // --- Preferences --------------------------------------------------------
    /** Controlled preferences {ampm, weekStartsOn}. Also an OUTPUT. */
    preferences: PropTypes.exact({
        ampm: PropTypes.bool,
        weekStartsOn: PropTypes.oneOf([0, 1, 2, 3, 4, 5, 6]),
    }),

    /** Uncontrolled initial preferences {ampm, weekStartsOn}. Default {ampm: true}. */
    defaultPreferences: PropTypes.exact({
        ampm: PropTypes.bool,
        weekStartsOn: PropTypes.oneOf([0, 1, 2, 3, 4, 5, 6]),
    }),

    // --- Localization -------------------------------------------------------
    /** Override UI label strings (a partial map of translation keys). */
    localeText: PropTypes.object,

    // --- Responsive UX (Dash wrapper additions) -----------------------------
    /**
     * How the event editor is presented. "drawer" (default) restyles the
     * built-in dialog into a responsive frosted-glass drawer — right-anchored
     * on desktop, an 88%-height bottom sheet on mobile (below
     * `mobileBreakpoint`). "dialog" keeps the library's floating dialog.
     */
    eventDialogVariant: PropTypes.oneOf(['drawer', 'dialog']),

    /** Width (px) below which the editor uses its mobile layout. Default 768. */
    mobileBreakpoint: PropTypes.number,

    /**
     * On desktop, inset the event drawer this many px from the top — e.g. set
     * it to your fixed app header's height. Default 0.
     */
    eventDialogTopOffset: PropTypes.number,

    // --- Outputs ------------------------------------------------------------
    /** Convenience OUTPUT describing the most recent change to `events`. */
    lastAction: PropTypes.exact({
        type: PropTypes.string,
        event: PropTypes.object,
        event_timestamp: PropTypes.number,
    }),

    /** Dash-assigned callback to report prop changes. */
    setProps: PropTypes.func,
};

export default EventTimeline;
