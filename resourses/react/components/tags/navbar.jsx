import React from 'react';
import ReactDOM from 'react-dom';
import {Link} from 'react-router-dom';
import {MyFunc as util} from 'func.jsx';
import store from 'store.jsx';
import { Provider, connect } from 'react-redux';


class NotificationItem extends React.Component{
  
  componentDidMount () {
    ReactDOM.findDOMNode(this.refs.item).addEventListener('click', this.notification_set_read.bind(this, this.props.data.id));
  }

  componentWillUnmount () {
    ReactDOM.findDOMNode(this.refs.item).removeEventListener('click', this.notification_set_read.bind(this, this.props.data.id));
  }

  notification_set_read(nid, e) {
    e.preventDefault();
    e.stopPropagation();
    util.get({
      'url': '/api/monitoring?action=set_notification_read',
      'data':  {'nid': nid},
      'success' : response => {
        this.props.onRead(response.data);
      }
    });
  };
  
  render(){
    if (this.props.data === null){
      return null;
    }
    
    let n = this.props.data;

    let ico = null;
    switch (n.type) {
      // image size 48x48
      case 'snmp':
        ico = <img className="w-3r bdrs-50p" src="/static/images/warning_48x48.png" alt="" />;
        break;
    }

    let href = '/monitoring/device/' + n.device_id;
    switch (n.link_type) {
      case 'snmp_addr':
        href = '/monitoring/device/' + n.device_id + '/snmp/' + n.addr + '/history';
        break;
    }
    
    return <li>
      <Link to={ href } className="peers fxw-nw td-n p-20 bdB c-grey-800 cH-blue bgcH-grey-100">
        <div className="peer mR-15">
          { ico }
        </div>
        <div className="peer peer-greed">
            <span>
              <div className="fw-500">{ n.device_name }</div>
              <span className="text-dark">
                <div>{ n.message }</div>
                <small>{ n.condition }</small>
              </span>
              <span className="c-grey-600">{ n.addr }</span>
            </span>
          <p className="m-0">
            <small className="fsz-xs">{ n.updated }</small>
              <span className="pull-right text-primary send-read-el" ref="item">
                <small>прочитано</small>
              </span>
          </p>
        </div>
      </Link>
    </li>
  }
}
NotificationItem.defaultProps = {
  data: null,
  onRead: function(value){}
};


class Navbar extends React.Component{
  constructor(props) {
    super(props);

    this.state = {
      notifications: {},
      notifications_count: 0,
      timer_id: null
    };
    
    this.sidebar_toggle = this.sidebar_toggle.bind(this);
  }

  componentDidMount() {
    this.notifications_get();
    let timer_id = setInterval(this.notifications_get.bind(this), 60*1000);
    this.setState({timer_id: timer_id});
  }

  componentWillUnmount() {
    clearTimeout(this.state.timer_id);
  }

  notifications_get(){
    util.get({
      'url': '/api/monitoring?action=get_alerts',
      'data': {},
      'success' : response => {
        // this.setState({notifications: response.data.data});
        // this.setState({notifications_count: response.data.count});
        this.notification_set(response.data);
      }
    });
  }
  
  notification_set(data){
    this.setState({notifications: data.data});
    this.setState({notifications_count: data.count});
  }

  sidebar_toggle(){
    store.dispatch({
      type: 'sidebar.toogle'
    });
  }
  

  render(){

    let notifications = [];
    for (let i=0;i<this.state.notifications.length;i++){
      notifications.push(<NotificationItem 
        data={this.state.notifications[i]} 
        key={this.state.notifications[i].id}
        onRead={value=>{this.notification_set(value)}}
      />);
    }

    return <div className="header navbar">
      <div className="header-container">
        <ul className="nav-left">
          <li>
            <span className="sidebar-toggle cur-p" onClick={ this.sidebar_toggle }><i className="ti-menu"></i></span>
          </li>
          <li className="search-box">
            <a className="search-toggle no-pdd-right" href="javascript:void(0);">
              <i className="search-icon ti-search pdd-right-10"></i> <i className="search-icon-close ti-close pdd-right-10"></i>
            </a>
          </li>
          <li className="search-input">
            <input className="form-control" type="text" placeholder="Search..."/>
          </li>
        </ul>
        <ul className="nav-right">
          <li className="notifications dropdown">
            { this.state.notifications_count > 0 &&
              <span className="counter bgc-red">{ this.state.notifications_count }</span>
            }
            <a href="" className="dropdown-toggle no-after" data-toggle="dropdown"><i className="ti-bell"></i></a>
            <ul className="dropdown-menu">
              <li className="pX-20 pY-15 bdB"><i className="ti-bell pR-10"></i> <span className="fsz-sm fw-600 c-grey-900">Уведомления</span></li>
              <li>
                <ul className="ovY-a pos-r scrollable lis-n p-0 m-0 fsz-sm ps">
                  { notifications }
                </ul>
              </li>
              <li className="pX-20 pY-15 ta-c bdT">
                  <span>
                    <Link to="/notifications" className="c-grey-600 cH-blue fsz-sm td-n">
                      <span>Все уведомления </span>
                      <i className="ti-angle-right fsz-xs mL-10"></i></Link>
                  </span>
              </li>
            </ul>
          </li>
          {/*
          <li className="notifications dropdown">
            <span className="counter bgc-blue" style={{'display': 'none'}}>0</span> <a href="" className="dropdown-toggle no-after" data-toggle="dropdown"><i
            className="ti-email"></i></a>
            <ul className="dropdown-menu">
              <li className="pX-20 pY-15 bdB"><i className="ti-email pR-10"></i> <span className="fsz-sm fw-600 c-grey-900">Emails</span></li>
              <li>
                <ul className="ovY-a pos-r scrollable lis-n p-0 m-0 fsz-sm ps">
                   <div className="ps__rail-x" style={{'left': '0px', 'bottom': '0px'}}>
                    <div className="ps__thumb-x" tabIndex="0" style={{'left': '0px','width': '0px'}}></div>
                  </div>
                  <div className="ps__rail-y" style={{'top': '0px', 'right': '0px'}}>
                    <div className="ps__thumb-y" tabIndex="0" style={{'top': '0px', 'height': '0px'}}></div>
                  </div>
                </ul>
              </li>
              <li className="pX-20 pY-15 ta-c bdT"><span><a href="" className="c-grey-600 cH-blue fsz-sm td-n">View All Email <i
                className="fs-xs ti-angle-right mL-10"></i></a></span></li>
            </ul>
          </li>
          */}
          <li className="dropdown">
            <a href="" className="dropdown-toggle no-after peers fxw-nw ai-c lh-1" data-toggle="dropdown">
              <div className="peer mR-10"><img className="w-2r bdrs-50p" src="https://findicons.com/files/icons/2354/dusseldorf/32/user.png" alt=""/></div>
              <div className="peer"><span className="fsz-sm c-grey-900">{this.props.appSettings.user.user_name}</span></div>
            </a>
            <ul className="dropdown-menu fsz-sm">
              {/*<li><a href="" className="d-b td-n pY-5 bgcH-grey-100 c-grey-700"><i className="ti-settings mR-10"></i> <span>Setting</span></a></li>
              <li><a href="" className="d-b td-n pY-5 bgcH-grey-100 c-grey-700"><i className="ti-user mR-10"></i> <span>Profile</span></a></li>
              <li><a href="" className="d-b td-n pY-5 bgcH-grey-100 c-grey-700"><i className="ti-email mR-10"></i> <span>Messages</span></a></li>
              <li role="separator" className="divider"></li>*/}
              <li><a href="/logout" className="d-b td-n pY-5 bgcH-grey-100 c-grey-700"><i className="ti-power-off mR-10"></i> <span>Выход</span></a></li>
            </ul>
          </li>
        </ul>
      </div>
    </div>
  }
}


const mapStateToProps = function (store) {
    return {
        appSettings: store.appSettings
    };
};
export default connect(mapStateToProps)(Navbar);