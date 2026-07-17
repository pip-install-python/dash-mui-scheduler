/**
 * RadialBarChart — Dash wrapper for MUI X `Unstable_RadialBarChart`
 * (`@mui/x-charts-premium`, Premium / preview).
 *
 * import { Unstable_RadialBarChart } from '@mui/x-charts-premium/RadialBarChart'
 *
 * Like the cartesian BarChart, but in polar coordinates: `rotationAxis` and
 * `radiusAxis` replace the x/y axes. Supports the usual bar options on each
 * series (`stack`, `layout`) and the band-axis gaps (`categoryGapRatio`,
 * `barGapRatio`). Data crosses the Dash boundary as plain JSON. Premium —
 * requires a MUI X license key (`licenseKey`). Follows the surrounding Mantine
 * color scheme for dark mode.
 */
import React, {useCallback} from 'react';
import PropTypes from 'prop-types';
import {Unstable_RadialBarChart as MuiRadialBarChart} from '@mui/x-charts-premium/RadialBarChart';
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
 * RadialBarChart compares values along periodic categories using polar bars.
 * Series accept `stack` and `layout` ("vertical" = radius encodes the value,
 * "horizontal" = rotation encodes it); the band rotation axis accepts
 * `categoryGapRatio` / `barGapRatio`. Clicking reports the hit item via the
 * `clickData` output. Premium (preview) — set `licenseKey`.
 */
const RadialBarChart = (props) => {
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
    if (skipAnimation !== undefined) chartProps.skipAnimation = skipAnimation;
    if (showToolbar !== undefined) chartProps.showToolbar = showToolbar;
    if (slotProps !== undefined) chartProps.slotProps = slotProps;
    if (sx !== undefined) chartProps.sx = sx;

    return (
        <div id={id} className={className}>
            <ThemeProvider theme={theme}>
                <MuiRadialBarChart {...chartProps} onAxisClick={handleAxisClick} />
            </ThemeProvider>
        </div>
    );
};

RadialBarChart.defaultProps = {
    height: 400,
};

RadialBarChart.propTypes = {
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
     * The bar series to plot. Each item is a dict, e.g.
     * {dataKey, label, stack, layout:"vertical"|"horizontal", color} or
     * {data: [...], label, ...}.
     */
    series: PropTypes.arrayOf(PropTypes.object),

    /** Row-oriented data; series reference columns via `dataKey`. */
    dataset: PropTypes.arrayOf(PropTypes.object),

    /**
     * Rotation (angular) axis config — replaces the cartesian x-axis. A list of
     * axis dicts. A band axis accepts `categoryGapRatio` / `barGapRatio`, e.g.
     * [{scaleType:"band", data:["2020","2021"], categoryGapRatio:0.3, barGapRatio:0.1}].
     */
    rotationAxis: PropTypes.arrayOf(PropTypes.object),

    /** Radius axis config — replaces the cartesian y-axis. A list of axis dicts. */
    radiusAxis: PropTypes.arrayOf(PropTypes.object),

    /** Show background grid lines: {rotation: bool, radius: bool}. */
    grid: PropTypes.exact({
        rotation: PropTypes.bool,
        radius: PropTypes.bool,
    }),

    /**
     * Axis highlight behavior: {rotation, radius} where each is one of
     * "none" | "line" | "band". Default depends on the layout.
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

    /** Skip the entrance animation. */
    skipAnimation: PropTypes.bool,

    /** Show the default chart toolbar. */
    showToolbar: PropTypes.bool,

    /** MUI X charts `slotProps` (plain-object form only), e.g. {"tooltip": {"trigger": "item"}}. */
    slotProps: PropTypes.object,

    // --- Outputs ------------------------------------------------------------
    /**
     * OUTPUT — set when the user clicks the chart. The clicked axis item and
     * its series values, e.g. {dataIndex, axisValue, seriesValues, event_timestamp}.
     */
    clickData: PropTypes.object,

    /** Dash-assigned callback to report prop changes. */
    setProps: PropTypes.func,
};

export default RadialBarChart;
