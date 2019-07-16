// Webpack v4

var path = require('path');

module.exports = {
  //mode: 'development',
  entry: './components/app.jsx',
  output:  {
    path: path.resolve(__dirname, "../../static/"),
    //publicPath: '/public/',
    filename: 'monitoring.js'
  },
  /*resolve: {
    //extensions: ['', '.js', '.jsx', '.scss'],
    modulesDirectories: [
      'node_modules'
    ]
  },*/
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
    /*rules:[   //загрузчик для jsx
      {
        test: /\.jsx$/, // определяем тип файлов
        exclude: /(node_modules)/,  // исключаем из обработки папку node_modules
        loader: "babel-loader",   // определяем загрузчик
        options:{
          presets:["react"]    // используемые плагины
        }
      }
    ],*/
    /*loaders: [
      {
        test: /\.jsx?$/,
        loader: ['babel'],
        include: [
          path.resolve(__dirname, "./components")
        ],
        query: {
          presets: ['@babel/react', '@babel/es2015'],
          plugins: ['@babel/proposal-class-properties']
        }
      },
      {
        test: /\.s[a|c]ss$/,
        loader: 'style-loader!css-loader!sass-loader'
      }
    ]*/
  },
  resolve: {
    modules: ['node_modules', 'components'],
    extensions: ['.js', '.jsx'],
  }
  /*sassLoader: {
    includePaths: [
      path.resolve(__dirname, "./components"),
      path.resolve(__dirname, "./node_modules/bootstrap/scss")
    ]
  }*/
};

//module.exports = config;