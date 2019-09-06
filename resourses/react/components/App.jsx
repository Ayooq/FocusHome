import ReactDOM from 'react-dom';
import React from 'react';
import { BrowserRouter as Router, Route, Redirect, Switch, Link } from 'react-router-dom';
import { Provider, connect } from 'react-redux';
import store from 'store.jsx';
import {MyFunc as util} from 'func.jsx';


// notification
import PageNotifications from './pages/notifications/notifications.jsx';
// monitoring
import PageIndex from './pages/monitoring/index.jsx';
import PageDevice from './pages/monitoring/device.jsx';
import PageDeviceSNMP from './pages/monitoring/snmp.jsx';
import PageDeviceSNMPDetails from './pages/monitoring/snmp_device_details.jsx';
import PageDeviceSNMPHistory from './pages/monitoring/snmp_device_history.jsx';
import PageDeviceSNMPWidgets from './pages/monitoring/snmp_widgets.jsx';
import PageDeviceSNMPWidgetSetting from './pages/monitoring/snmp_widget_setting.jsx';
import PageDeviceRoutines from './pages/monitoring/device_routines.jsx';
import PageDeviceRoutinesEdit from './pages/monitoring/device_routines_edit.jsx';
//devices
import PageDevices from './pages/devices/index.jsx';
import PageDevicesEdit from './pages/devices/edit.jsx';
//clients
import PageClients from './pages/clients/index.jsx';
import PageClientsEdit from './pages/clients/edit.jsx';
//users
import PageUsers from './pages/users/index.jsx';
import PageUsersEdit from './pages/users/edit.jsx';
import PageUsersPerm from './pages/users/perm.jsx';
//template
import SidebarLeft from './tags/sidebar-left';
import Navbar from './tags/navbar';
import Footer from './tags/footer';
import PageTitle from './tags/template-page-title';


class App extends React.Component{
  componentDidMount() {
    util.get({
      'url': '/api/settings',
      'data': {},
      'success' : response => {
        store.dispatch({
          type: 'appSettings_upload',
          data: response.data
        });
      }
    });
  }
  
  render(){
    return <Router>
        <div className={this.props.template.sidebar_is_collapsed?'is-collapsed':''}>
          <SidebarLeft />
          <div className="page-container">
            <Navbar />
            <main className="main-content bgc-grey-100">
              <div id="mainContent">
                <PageTitle />

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
                    {/*<Redirect exact from="/react" to="/react/orders" />*/}

                    <Route exact path='/clients/' component={PageClients} />
                    <Route exact path='/clients/:clientID(create)' component={PageClientsEdit} />
                    <Route exact path='/clients/:clientID(\d+)' component={PageClientsEdit} />

                    <Route exact path='/users/' component={PageUsers} />
                    <Route exact path='/users/:userID(create)' component={PageUsersEdit} />
                    <Route exact path='/users/:userID(\d+)/perm' component={PageUsersPerm} />
                    <Route exact path='/users/:userID(\d+)' component={PageUsersEdit} />

                    <Route exact path='/devices/' component={PageDevices} />
                    <Route exact path='/devices/:deviceID(create)' component={PageDevicesEdit} />
                    <Route exact path='/devices/:deviceID(\d+)' component={PageDevicesEdit} />

                    <Route exact path='/notifications/' component={PageNotifications} />

                    <Route exact path='/monitoring/' component={PageIndex} />
                    <Route exact path='/monitoring/device/:deviceID' component={PageDevice} />
                    <Route exact path='/monitoring/device/:deviceID/snmp' component={PageDeviceSNMP} />
                    <Route exact path='/monitoring/device/:deviceID/snmp/widgets' component={PageDeviceSNMPWidgets} />
                    <Route exact path='/monitoring/device/:deviceID/snmp/:addr/details' component={PageDeviceSNMPDetails} />
                    <Route exact path='/monitoring/device/:deviceID/snmp/:addr/history' component={PageDeviceSNMPHistory} />
                    <Route exact path='/monitoring/device/:deviceID/snmp/:addr/widget' component={PageDeviceSNMPWidgetSetting} />
                    <Route exact path='/monitoring/device/:deviceID/routines' component={PageDeviceRoutines} />
                    <Route exact path='/monitoring/device/:deviceID/routines/add' component={PageDeviceRoutinesEdit} />
                    <Route exact path='/monitoring/device/:deviceID/routines/:id' component={PageDeviceRoutinesEdit} />

                    <Route path="*" render={() => <div>Ничего не найдено</div>}/>

                  </Switch>
                </div>

              </div>
            </main>
            <Footer />
          </div>
        </div>
      </Router>
  }
}

const mapStateToProps = function(store) {
  return {
    template:  store.template
  };
};
export default connect(mapStateToProps)(App);