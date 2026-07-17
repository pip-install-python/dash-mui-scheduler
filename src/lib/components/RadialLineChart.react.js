/**
 * RadialLineChart — Dash wrapper for MUI X `Unstable_RadialLineChart`
 * (`@mui/x-charts-premium`, Premium / preview).
 *
 * import { Unstable_RadialLineChart } from '@mui/x-charts-premium/RadialLineChart'
 *
 * Renders line/area series in polar coordinates: `rotationAxis` replaces the
 * cartesian x-axis and `radiusAxis` replaces the y-axis. All data crosses the
 * Dash boundary as plain JSON (series, dataset, axes are dicts/lists), so
 * nothing here needs a serialization shim. Premium — requires a MUI X license
 * key (via `licenseKey`) to render without a watermark. Follows the surrounding
 * Mantine color scheme for dark mode, like the scheduler components.
 */
import React, {useCallback} from 'react';
import PropTypes from 'prop-types';
import {Unstable_RadialLineChart as MuiRadialLineChart} from '@mui/x-charts-premium/RadialLineChart';
import {ThemeProvider} from '@mui/material/styles';
import {LicenseInfo} from '@mui/x-license';
import {useMantineColorScheme, lightTheme, darkTheme} from '../utils/schedulerUtils';

const HIGHLIGHT = ['none', 'line', 'band'];

let _lastLicenseKey;
const ensureLicense = (key) => {
    if (key && key !== _lastLicenseKey) {
        LicenseInfo.setLicenseKey(key);
        _lastLicenseKey = key;
    }
};

/**
 * RadialLineChart shows trends along periodic values using a polar line (or
 * area) plot. Pass `series` plus `rotationAxis` / `radiusAxis` to map your data
 * into polar coordinates; clicking the chart reports the hit axis item via the
 * `clickData` output. Premium (preview) — set `licenseKey` to remove the
 * watermark.
 */
const RadialLineChart = (props) => {
    const {
        id,
        className,
        height,
        width,
        sx,
        licenseKey,
        series,
        dataset,
        rotationAxis,
        radiusAxis,
        grid,
        axisHighlight,
        margin,
        colors,
        hideLegend,
        disableLineItemHighlight,
        skipAnimation,
        showToolbar,
        slotProps,
        setProps,
    } = props;

    ensureLicense(licenseKey);

    const scheme = useMantineColorScheme();
    const theme = scheme === 'dark' ? darkTheme : lightTheme;

    const handleAxisClick = useCallback(
        (event, axisData) => {
            if (setProps) {
                setProps({clickData: {...axisData, event_timestamp: Date.now()}});
            }
        },
        [setProps]
    );

    const chartProps = {series: series || []};
    if (dataset !== undefined) chartProps.dataset = dataset;
    if (rotationAxis !== undefined) chartProps.rotationAxis = rotationAxis;
    if (radiusAxis !== undefined) chartProps.radiusAxis = radiusAxis;
    if (grid !== undefined) chartProps.grid = grid;
    if (axisHighlight !== undefined) chartProps.axisHighlight = axisHighlight;
    if (height !== undefined) chartProps.height = height;
    if (width !== undefined) chartProps.width = width;
    if (margin !== undefined) chartProps.margin = margin;
    if (colors !== undefined) chartProps.colors = colors;
    if (hideLegend !== undefined) chartProps.hideLegend = hideLegend;
    if (disableLineItemHighlight !== undefined) {
        chartProps.disableLineItemHighlight = disableLineItemHighlight;
    }
    if (skipAnimation !== undefined) chartProps.skipAnimation = skipAnimation;
    if (showToolbar !== undefined) chartProps.showToolbar = showToolbar;
    if (slotProps !== undefined) chartProps.slotProps = slotProps;
    if (sx !== undefined) chartProps.sx = sx;

    return (
        <div id={id} className={className}>
            <ThemeProvider theme={theme}>
                <MuiRadialLineChart {...chartProps} onAxisClick={handleAxisClick} />
            </ThemeProvider>
        </div>
    );
};

RadialLineChart.defaultProps = {
    height: 400,
};

RadialLineChart.propTypes = {
    /** The id used to identify this component in Dash callbacks. */
    id: PropTypes.string,

    /** CSS class applied to the wrapping div. */
    className: PropTypes.string,

    /** Chart height in px. Default 400. */
    height: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),

    /** Chart width in px (defaults to filling the container). */
    width: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),

    /** MUI `sx` styling object (object form only). */
    sx: PropTypes.object,

    /** MUI X Premium license key (removes the watermark). */
    licenseKey: PropTypes.string,

    /**
     * The line/area series to plot. Each item is a dict, e.g.
     * {dataKey, label, curve, showMark, shape, area, closePath, stack,
     *  highlightScope, color} or {data: [...], label, ...}.
     */
    series: PropTypes.arrayOf(PropTypes.object),

    /** Row-oriented data; series reference columns via `dataKey`. */
    dataset: PropTypes.arrayOf(PropTypes.object),

    /**
     * Rotation (angular) axis config — replaces the cartesian x-axis. A list of
     * axis dicts, e.g. [{scaleType:"point", dataKey:"month", disableLine:true}].
     */
    rotationAxis: PropTypes.arrayOf(PropTypes.object),

    /**
     * Radius axis config — replaces the cartesian y-axis. A list of axis dicts,
     * e.g. [{disableLine:true, minRadius:10, min:0, position:"none"}].
     */
    radiusAxis: PropTypes.arrayOf(PropTypes.object),

    /** Show background grid lines: {rotation: bool, radius: bool}. */
    grid: PropTypes.exact({
        rotation: PropTypes.bool,
        radius: PropTypes.bool,
    }),

    /**
     * Axis highlight behavior: {rotation, radius} where each is one of
     * "none" | "line" | "band". Default {rotation: "line"}.
     */
    axisHighlight: PropTypes.exact({
        rotation: PropTypes.oneOf(HIGHLIGHT),
        radius: PropTypes.oneOf(HIGHLIGHT),
    }),

    /** Margin around the plot — a number or {top,right,bottom,left}. */
    margin: PropTypes.oneOfType([PropTypes.number, PropTypes.object]),

    /** Color palette (list of CSS colors) used for the series. */
    colors: PropTypes.arrayOf(PropTypes.string),

    /** Hide the legend. */
    hideLegend: PropTypes.bool,

    /** Disable the per-item line highlight indicator. */
    disableLineItemHighlight: PropTypes.bool,

    /** Skip the entrance animation. */
    skipAnimation: PropTypes.bool,

    /** Show the default chart toolbar. */
    showToolbar: PropTypes.bool,

    /**
     * MUI X charts `slotProps` (plain-object form only). For example
     * {"tooltip": {"trigger": "item"}} makes the tooltip follow the hovered
     * mark/line instead of the whole rotation axis.
     */
    slotProps: PropTypes.object,

    // --- Outputs ------------------------------------------------------------
    /**
     * OUTPUT — set when the user clicks the chart. The clicked rotation-axis
     * item and its series values, e.g.
     * {dataIndex, axisValue, seriesValues, event_timestamp}.
     */
    clickData: PropTypes.object,

    /** Dash-assigned callback to report prop changes. */
    setProps: PropTypes.func,
};

export default RadialLineChart;
