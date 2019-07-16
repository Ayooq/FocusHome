
import ReactDOM from 'react-dom';
import React from 'react';
import { BrowserRouter as Router, Route, Redirect, Switch, Link } from 'react-router-dom';

import { Provider, connect } from 'react-redux';
import store from 'store.jsx';
import {MyFunc as util} from 'func.jsx';

//import IndexNavTop from 'tags/index-nav-top.jsx';
//import IndexNavLeft from 'tags/index-nav-left.jsx';

import PageIndex from './pages/index.jsx';
import PageDevice from './pages/device.jsx';

util.get({
  'url': '/monitoring/api?action=get_settings',
  'data': {'all': 'все'},
  'success' : response => {
    store.dispatch({
      type: 'appSettings_upload',
      data: response.data
    });
  }
});

ReactDOM.render(
  <Provider store={store}>
    <Router>
      <div>
        {/*<IndexNavTop />
        <IndexNavLeft />*/}
        <div className="body">
          {/*<ol className="breadcrumb">
            
          </ol>
          <ol class="breadcrumb">
            <li v-for="item in store.pageData.path">
              <Link to="item.href" v-if="item.href">{item.title}</Link>
              <span v-else v-html="item.title"></span>
            </li>
          </ol>*/}
          <Switch>
            <Redirect exact from="/react" to="/react/orders" />
            <Route exact path='/monitoring/' component={PageIndex} />
            <Route exact path='/monitoring/device/:deviceID' component={PageDevice} />

            <Route path="*" render={() => <div>404</div>}/>
          </Switch>
          {/*<Link to="/react/orders" >orders</Link>*/}          
        </div>
      </div>
    </Router>
  </Provider>,
  document.getElementById("react_app")
);

// this.props.match.params.productID