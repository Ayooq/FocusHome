const webpack = require("webpack");
var path = require('path');

module.exports = {
  // mode: 'production',
  entry: './components/index.jsx',
  output:  {
    path: path.resolve(__dirname, "../../static/"),
    filename: 'cabinet.js'
  },
  module: {
    rules : [
      {
        test: /\.jsx?$/,
        loader: 'babel-loader',
        exclude: /(node_modules)/,
        options: {
          presets:["@babel/preset-env", "@babel/preset-react"]
        }
      }
    ]
  },
  resolve: {
    modules: ['node_modules', 'components'],
    extensions: ['.js', '.jsx']
  },
  // plugins: [
  //   new webpack.optimize.UglifyJsPlugin({
  //     include: /\.js$/,
  //     minimize: true
  //   })
  // ]
};

//module.exports = config;