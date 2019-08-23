module.exports = {
  type: "react-app",
  babel: {
    plugins: ["jsx-control-statements"]
  },
  webpack: {
    loaders: {
      babel: {
        test: /\.jsx?/
      }
    },
    extra: {
      resolve: {
        extensions: ["", ".js", ".jsx", ".json"]
      },
      node: {
        process: false
      }
    }
  }
};
