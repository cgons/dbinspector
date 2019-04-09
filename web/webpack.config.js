const path = require('path');
const CleanWebpackPlugin = require('clean-webpack-plugin');
const MiniCssExtractPlugin = require("mini-css-extract-plugin");


const cssconfig = {
  mode: 'development',
  entry: './src/css/sitestyles.scss',
  output: {
    path: path.resolve(__dirname, 'public', 'dist'),
  },
  module: {
    rules: [{
      test: /\.scss$/,
      use: [
        MiniCssExtractPlugin.loader,
        "css-loader",
        "sass-loader"
      ]
    }]
  },
  plugins: [
    new MiniCssExtractPlugin({
      filename: "[name].css",
      chunkFilename: "[id].css"
    })
  ]
};


const jsconfig = {
  mode: 'development',
  entry: './src/index.js',
  plugins: [
    new CleanWebpackPlugin(),
  ],
  output: {
    filename: '[name].bundle.js',
    path: path.resolve(__dirname, 'public', 'dist'),
  },
  module: {
    rules: [
      { test: /\.js$/, exclude: /node_modules/, loader: "babel-loader" }
    ],
  },
  devServer: {
    contentBase: path.join(__dirname, 'public'),
    publicPath: '/dist/',
    historyApiFallback: true,
    open: false,
  },
};


module.exports = [jsconfig, cssconfig];
