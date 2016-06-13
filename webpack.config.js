/*jshint esversion: 6 */
const path = require('path');
const webpack = require('webpack');
const autoprefixer = require('autoprefixer');
const ExtractTextPlugin = require('extract-text-webpack-plugin');

module.exports = {
    entry: "./recipes/static/js/dayMenu.js",
    output: {
        path: __dirname + '/recipes/static/js/',
        filename: "bundle.js"
    },
    module: {
        loaders: [
          {
            test: /(\.js|\.jsx)$/,
            exclude: /(node_modules)/,
            loader: 'babel',
            query: { presets: ['es2015', 'react'] }
          }, {
            test: /(\.scss|\.css)$/,
            loader: ExtractTextPlugin.extract('style', 'css?sourceMap&modules&importLoaders=1&localIdentName=[name]__[local]___[hash:base64:5]!postcss!sass')
          }, {
            test: /\.css$/,
            loader: "style-loader!css-loader"
          }
        ]
    },
    postcss: [autoprefixer],
    // sassLoader: {
    //   data: '@import "' + path.resolve(__dirname, '/recipes/static/css/dayMenu.scss') + '";'
    // },
    plugins: [
      new ExtractTextPlugin('react-toolbox.css', { allChunks: true }),
    ]
};
