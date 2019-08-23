import React from "react";
import ReactDOM from "react-dom";
import { BrowserRouter as Router, Route, Switch } from "react-router-dom";

import { Provider } from "react-redux";

import store from "./store";
import utils from "./utils";

import PageIndex from "./components/pages/index";
import PageDevice from "./components/pages/device";

utils.get({
  url: "/monitoring/api",
  data: {
    action: "get_settings",
    all: "Все",
    group_id: 1
  },

  success: response => {
    console.log(response);
    store.dispatch({
      type: "settings",
      data: response.data
    });
  }
});

ReactDOM.render(
  <Provider store={store}>
    <Router>
      <div className="body">
        <Switch>
          <Route exact path="/monitoring/" component={PageIndex} />
          <Route exact path="/monitoring/device/:id" component={PageDevice} />
          <Route path="*" render={() => <div>404</div>} />
        </Switch>
      </div>
    </Router>
  </Provider>,
  document.getElementById("reactApp")
);
