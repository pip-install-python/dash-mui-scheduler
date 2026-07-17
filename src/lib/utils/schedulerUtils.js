/**
 * Shared helpers for the MUI X Scheduler Dash wrappers.
 *
 * These are deliberately kept OUT of the `components/` directory so that
 * `dash-generate-components` does not try to turn them into Dash components.
 *
 * The Dash <-> Python boundary for the scheduler is almost entirely
 * JSON-serializable already:
 *   - `SchedulerEvent.start` / `.end` are ISO strings (per the MUI model), so
 *     `events` round-trips verbatim — no date library needed.
 *   - The only date that crosses as a real JS `Date` is `visibleDate`
 *     (the scheduler's default adapter is date-fns, whose supported object is
 *     `Date`). We convert `string -> Date` going in and `Date -> string`
 *     coming out, defensively handling Luxon/dayjs-shaped objects too.
 */
import {useEffect, useState} from 'react';
import {createTheme} from '@mui/material/styles';

// --- Dark mode: follow <html data-mantine-color-scheme="..."> ----------------
// Mirrors dash-mui-charts' TimeClock/TreeViewPro so the calendar re-skins when
// the surrounding Dash Mantine app toggles its color scheme. Falls back to
// "light" when there is no Mantine provider (standalone usage).
export const readMantineScheme = () => {
    if (typeof document === 'undefined') return 'light';
    const v = document.documentElement.getAttribute('data-mantine-color-scheme');
    return v === 'dark' ? 'dark' : 'light';
};

export const useMantineColorScheme = () => {
    const [scheme, setScheme] = useState(readMantineScheme);
    useEffect(() => {
        if (typeof document === 'undefined') return undefined;
        const html = document.documentElement;
        const sync = () => setScheme(readMantineScheme());
        const obs = new MutationObserver(sync);
        obs.observe(html, {
            attributes: true,
            attributeFilter: ['data-mantine-color-scheme'],
        });
        sync();
        return () => obs.disconnect();
    }, []);
    return scheme;
};

export const lightTheme = createTheme({palette: {mode: 'light'}});
export const darkTheme = createTheme({palette: {mode: 'dark'}});

// --- Date boundary (only used for visibleDate / defaultVisibleDate) -----------
const DATE_ONLY_RE = /^\d{4}-\d{2}-\d{2}$/;
const pad = (n) => String(n).padStart(2, '0');

/**
 * Parse a Dash string into a JS Date for `visibleDate` / `defaultVisibleDate`.
 * A bare "YYYY-MM-DD" is anchored to LOCAL midnight (not UTC) to avoid the
 * classic off-by-one-day shift in negative-UTC timezones.
 * Returns `undefined` for empty / invalid input so the prop can be omitted.
 */
export const parseDate = (val) => {
    if (val === null || val === undefined || val === '') return undefined;
    if (val instanceof Date) return Number.isNaN(val.getTime()) ? undefined : val;
    if (typeof val === 'string') {
        if (DATE_ONLY_RE.test(val)) {
            const [y, m, d] = val.split('-').map(Number);
            return new Date(y, m - 1, d);
        }
        const d = new Date(val);
        return Number.isNaN(d.getTime()) ? undefined : d;
    }
    return undefined;
};

/**
 * Format a date emitted by the scheduler back into a Dash string
 * ("YYYY-MM-DDTHH:mm:ss", local wall time). Defensive about the runtime
 * shape: native Date, Luxon DateTime (`.toISO`), or dayjs (`.toDate`).
 */
export const dateToISO = (d) => {
    if (d === null || d === undefined) return null;
    if (d instanceof Date) {
        if (Number.isNaN(d.getTime())) return null;
        return (
            `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}` +
            `T${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
        );
    }
    if (typeof d === 'string') return d;
    if (typeof d.toISO === 'function') {
        const s = d.toISO();
        return typeof s === 'string' ? s.slice(0, 19) : null;
    }
    if (typeof d.toDate === 'function') return dateToISO(d.toDate());
    try {
        return dateToISO(new Date(d));
    } catch (e) {
        return null;
    }
};

// --- Event diffing: classify the change for the `lastAction` output ----------
const indexById = (arr) => {
    const m = new Map();
    (arr || []).forEach((e) => {
        if (e && e.id !== undefined && e.id !== null) m.set(String(e.id), e);
    });
    return m;
};

const durationMs = (e) => {
    const a = new Date(e.start).getTime();
    const b = new Date(e.end).getTime();
    return Number.isNaN(a) || Number.isNaN(b) ? null : b - a;
};

const action = (type, event) => ({
    type,
    event: event || null,
    event_timestamp: Date.now(),
});

/**
 * Classify the difference between the previous and next `events` arrays into a
 * single `lastAction` object so a Dash callback gets a precise signal
 * (create / delete / move / resize / update) without diffing server-side.
 * Handles the common case of a single UI interaction; bulk/ambiguous changes
 * collapse to type "change".
 */
export const diffEvents = (prev, next) => {
    const p = indexById(prev);
    const n = indexById(next);

    for (const [id, ev] of n) {
        if (!p.has(id)) return action('create', ev);
    }
    for (const [id, ev] of p) {
        if (!n.has(id)) return action('delete', ev);
    }
    for (const [id, ev] of n) {
        const old = p.get(id);
        if (!old) continue;
        if (old.start !== ev.start || old.end !== ev.end) {
            const dOld = durationMs(old);
            const dNew = durationMs(ev);
            const sameDuration = dOld !== null && dOld === dNew;
            return action(sameDuration ? 'move' : 'resize', ev);
        }
        if (JSON.stringify(old) !== JSON.stringify(ev)) return action('update', ev);
    }
    return action('change', null);
};

// --- Responsive event dialog -> drawer ----------------------------------------
// The MUI Scheduler renders its event editor as a draggable, absolutely-
// positioned MUI Dialog (portaled to <body>) — which "doesn't snap" and reads
// badly on phones. There is no public slot/disable hook in the beta, but every
// part carries a stable `MuiEventCalendar-eventDialog*` class, so we restyle it
// into a real drawer: right-anchored on desktop, an 80%-height bottom sheet on
// mobile, with a scrollable middle and pinned header/footer. Injected once.
const DIALOG_STYLE_ID = 'dms-scheduler-dialog-drawer';

export const injectSchedulerDialogCSS = (breakpoint = 768) => {
    if (typeof document === 'undefined') return;
    const css = `
/* dash-mui-scheduler: event dialog -> responsive drawer */
.MuiEventCalendar-eventDialogPaper {
    position: fixed !important;
    transform: none !important;
    margin: 0 !important;
    transition: none !important;
    display: flex !important;
    flex-direction: column !important;
    box-sizing: border-box !important;
    overflow-x: hidden !important;
}
/* Keep the form and its rows inside the drawer width (the editor keeps the
   library's intrinsic ~desktop width otherwise, spilling past a phone edge). */
.MuiEventCalendar-eventDialogContent,
.MuiEventCalendar-eventDialogForm,
.MuiEventCalendar-eventDialogTabPanel,
.MuiEventCalendar-eventDialogTabContent,
.MuiEventCalendar-eventDialogFormActions {
    box-sizing: border-box !important;
    max-width: 100% !important;
}
.MuiEventCalendar-eventDialogContent {
    display: flex !important;
    flex-direction: column !important;
    flex: 1 1 auto !important;
    min-height: 0 !important;
    padding: 0 !important;
    overflow: hidden !important;
}
.MuiEventCalendar-eventDialogForm {
    display: flex !important;
    flex-direction: column !important;
    flex: 1 1 auto !important;
    min-height: 0 !important;
}
.MuiEventCalendar-eventDialogTabPanel {
    flex: 1 1 auto !important;
    overflow-y: auto !important;
    overflow-x: hidden !important;
    min-height: 0 !important;
}
.MuiEventCalendar-eventDialogHeader,
.MuiEventCalendar-eventDialogFormActions {
    flex: 0 0 auto !important;
}
/* --- "Liquid glass": frosted translucent card + solid header/footer bars --- */
.MuiEventCalendar-eventDialogPaper {
    background-color: rgba(243, 243, 243, 0.62) !important;
    -webkit-backdrop-filter: blur(22px) saturate(180%) !important;
    backdrop-filter: blur(22px) saturate(180%) !important;
    border: 1px solid rgba(255, 255, 255, 0.5) !important;
}
/* Let the frosted card show through the form body. */
.MuiEventCalendar-eventDialogForm,
.MuiEventCalendar-eventDialogContent,
.MuiEventCalendar-eventDialogTabPanel,
.MuiEventCalendar-eventDialogTabContent,
.MuiEventCalendar-eventDialogTabsContainer,
.MuiEventCalendar-eventDialogRepeatSectionFieldset,
.MuiEventCalendar-eventDialogSectionFieldset {
    background-color: transparent !important;
}
/* Solid header + footer bars anchor the title and the actions. */
.MuiEventCalendar-eventDialogHeader,
.MuiEventCalendar-eventDialogFormActions {
    background-color: #f3f3f3 !important;
}
/* Soften + lightly blur the backdrop so the glass reads cleanly and the page
   behind shows a subtle sense of depth. */
.MuiDialog-root:has(.MuiEventCalendar-eventDialogPaper) .MuiBackdrop-root {
    background-color: rgba(0, 0, 0, 0.18) !important;
    -webkit-backdrop-filter: blur(2px) !important;
    backdrop-filter: blur(2px) !important;
}
/* Dark mode follows the surrounding Mantine color scheme. */
:root[data-mantine-color-scheme="dark"] .MuiEventCalendar-eventDialogPaper {
    background-color: rgba(36, 36, 36, 0.6) !important;
    border-color: rgba(255, 255, 255, 0.1) !important;
}
:root[data-mantine-color-scheme="dark"] .MuiEventCalendar-eventDialogHeader,
:root[data-mantine-color-scheme="dark"] .MuiEventCalendar-eventDialogFormActions {
    background-color: #242424 !important;
}
/* Desktop (>= breakpoint): right-anchored drawer. The top is inset by the
   --dms-dialog-top-offset CSS variable (0 by default) so it can sit below a
   fixed app header and line up with a sidebar instead of covering them. */
@media (min-width: ${breakpoint}px) {
    .MuiEventCalendar-eventDialogPaper {
        top: var(--dms-dialog-top-offset, 0px) !important;
        right: 0 !important;
        left: auto !important;
        bottom: 0 !important;
        height: calc(100vh - var(--dms-dialog-top-offset, 0px)) !important;
        max-height: calc(100vh - var(--dms-dialog-top-offset, 0px)) !important;
        width: 440px !important;
        max-width: 92vw !important;
        border-radius: 0 !important;
    }
    .MuiDialog-root:has(.MuiEventCalendar-eventDialogPaper) .MuiBackdrop-root {
        top: var(--dms-dialog-top-offset, 0px) !important;
    }
    /* Cap the scrollable form body on desktop. */
    .MuiEventCalendar-eventDialogTabContent {
        max-height: 675px !important;
    }
}
/* Mobile (< breakpoint): bottom sheet at 80% of the viewport height */
@media (max-width: ${breakpoint - 0.05}px) {
    .MuiEventCalendar-eventDialogPaper {
        top: auto !important;
        left: 0 !important;
        right: 0 !important;
        bottom: 0 !important;
        width: 100% !important;
        max-width: 100% !important;
        height: 88vh !important;
        max-height: 88vh !important;
        border-radius: 16px 16px 0 0 !important;
    }
    /* Stack the date+time field pairs so they don't overflow a phone width. */
    .MuiEventCalendar-eventDialogDateTimeFieldsRow {
        flex-direction: column !important;
    }
    /* Cap the scrollable form body on phones. */
    .MuiEventCalendar-eventDialogTabContent {
        max-height: 650px !important;
    }
}`;
    // The (Premium) Event Timeline renders the same editor under its own class
    // prefix, so mirror every rule for MuiEventTimeline to give it the same
    // responsive drawer + liquid-glass treatment.
    const cssBoth = css + '\n' + css.replace(/MuiEventCalendar-/g, 'MuiEventTimeline-');
    const existing = document.getElementById(DIALOG_STYLE_ID);
    if (existing) {
        if (existing.textContent !== cssBoth) existing.textContent = cssBoth;
        return;
    }
    const style = document.createElement('style');
    style.id = DIALOG_STYLE_ID;
    style.textContent = cssBoth;
    document.head.appendChild(style);
};

export const removeSchedulerDialogCSS = () => {
    if (typeof document === 'undefined') return;
    const el = document.getElementById(DIALOG_STYLE_ID);
    if (el) el.remove();
};

// --- Responsive side panel ----------------------------------------------------
/** True if the viewport is at least `breakpoint` px wide (open the side panel). */
export const getInitialSidePanelOpen = (breakpoint = 768) => {
    if (typeof window === 'undefined') return true;
    return window.innerWidth >= breakpoint;
};

// --- Scroll the now-indicator into view ---------------------------------------
const isScrollable = (n) => {
    const s = window.getComputedStyle(n);
    return /(auto|scroll)/.test(s.overflowY) && n.scrollHeight > n.clientHeight + 4;
};

const findScroller = (start, root) => {
    let n = start;
    while (n && n !== root && n !== document.body) {
        if (isScrollable(n)) return n;
        n = n.parentElement;
    }
    return null;
};

/**
 * In the day / week time views, scroll the time grid so the current-time
 * indicator (or, if it is hidden, the current time-of-day) is centered in view.
 * Re-runs on mount, when `enabled` flips, and when the `view` changes. The grid
 * renders asynchronously, so we retry briefly until the scroller appears
 * (and silently give up in month/agenda views, which have no time grid).
 */
export const useScrollToCurrentTime = (rootRef, enabled, view) => {
    useEffect(() => {
        if (!enabled || typeof document === 'undefined') return undefined;
        let cancelled = false;
        let tries = 0;
        let timer = null;

        const run = () => {
            if (cancelled) return;
            const root = rootRef.current;
            const content = root && root.querySelector(
                '.MuiEventCalendar-dayTimeGridScrollableContent'
            );
            const indicator = root && root.querySelector(
                '.MuiEventCalendar-dayTimeGridCurrentTimeIndicator'
            );
            const scroller = content && findScroller(indicator || content, root);

            if (!scroller) {
                // Not a time view yet, or not rendered — retry for ~1.5s.
                if (tries++ < 25) timer = setTimeout(run, 60);
                return;
            }

            let target;
            if (indicator) {
                const ir = indicator.getBoundingClientRect();
                const sr = scroller.getBoundingClientRect();
                target =
                    scroller.scrollTop + (ir.top - sr.top) -
                    scroller.clientHeight / 2 + ir.height / 2;
            } else {
                const now = new Date();
                const frac = (now.getHours() * 60 + now.getMinutes()) / (24 * 60);
                target = frac * scroller.scrollHeight - scroller.clientHeight / 2;
            }
            scroller.scrollTo({top: Math.max(0, target), behavior: 'auto'});
        };

        const raf = requestAnimationFrame(run);
        return () => {
            cancelled = true;
            cancelAnimationFrame(raf);
            if (timer) clearTimeout(timer);
        };
    }, [rootRef, enabled, view]);
};
