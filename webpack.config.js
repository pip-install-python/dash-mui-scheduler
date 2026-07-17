const path = require('path');
const webpack = require('webpack');
const WebpackDashDynamicImport = require('@plotly/webpack-dash-dynamic-import');
const packagejson = require('./package.json');

const dashLibraryName = packagejson.name.replace(/-/g, '_');

module.exports = (env, argv) => {
    const mode = (argv && argv.mode) || 'production';
    const entry = {index: './src/lib/index.js'};

    const output = {
        path: path.resolve(__dirname, dashLibraryName),
        filename: `${dashLibraryName}.min.js`,
        library: dashLibraryName,
        libraryTarget: 'window',
    };

    const externals = {
        react: 'React',
        'react-dom': 'ReactDOM',
        'plotly.js': 'Plotly',
        'prop-types': 'PropTypes',
    };

    return {
        mode,
        entry,
        output,
        externals,
        module: {
            rules: [
                {
                    test: /\.jsx?$/,
                    exclude: /node_modules/,
                    use: {
                        loader: 'babel-loader',
                    },
                },
                {
                    test: /\.css$/,
                    use: ['style-loader', 'css-loader'],
                },
                // MUI X / Base UI ship ESM with explicit extensions; relax fullySpecified.
                {
                    test: /\.m?js$/,
                    resolve: {
                        fullySpecified: false,
                    },
                },
            ],
        },
        resolve: {
            extensions: ['.js', '.jsx'],
        },
        optimization: {
            splitChunks: {
                name: `${dashLibraryName}-shared`,
                cacheGroups: {
                    async: {
                        chunks: 'async',
                        minSize: 0,
                        name(module, chunks, cacheGroupKey) {
                            return `${dashLibraryName}-${chunks[0].name}`;
                        },
                    },
                    shared: {
                        chunks: 'all',
                        minSize: 0,
                        minChunks: 2,
                        name: `${dashLibraryName}-shared`,
                        priority: -10,
                    },
                },
            },
        },
        plugins: [
            new WebpackDashDynamicImport(),
            new webpack.SourceMapDevToolPlugin({
                filename: '[file].map',
                exclude: /async-/,
            }),
        ],
    };
};
