const path = require('path');
const config = require('./webpack.config.js');

module.exports = (env, argv) => {
    const base = config(env, {...argv, mode: 'development'});
    return {
        ...base,
        mode: 'development',
        devtool: 'eval-source-map',
        entry: './src/demo/index.js',
        output: {
            ...base.output,
            path: path.resolve(__dirname, 'build'),
            filename: 'output.js',
        },
        externals: {},
        devServer: {
            static: {directory: path.join(__dirname, 'build')},
            hot: true,
            port: 8050,
        },
    };
};
