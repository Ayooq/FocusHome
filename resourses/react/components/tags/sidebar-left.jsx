import React from 'react';
import {Link} from 'react-router-dom';
import {connect} from 'react-redux';
import store from 'store.jsx';
import { Event } from 'react-socket-io';


class MenuItem extends React.Component{
  render(){
    if (this.props.data === null){
      return null;
    }

    return <li className="nav-item">
      <Link className="sidebar-link" to={this.props.data.href}>
        <span className="icon-holder"><i className={this.props.data.icon}></i></span>
        <span className="title">{this.props.data.title}</span>
      </Link>
    </li>
  }
}
MenuItem.defaultProps = {
  data: null
};


class SidebarLeft extends React.Component{
    constructor(props) {
        super(props);

        this.state = {
            menu_items: null
        };

        this.socket_server_state = this.socket_server_state.bind(this);
    }

    socket_server_state(message) {
        store.dispatch({
            type: 'socket_server_state.toogle'
        });
    }

    sidebar_toggle(){
        store.dispatch({
          type: 'sidebar.toogle'
        });
      }


    render() {
        let app_menu = this.props.appSettings.menu || [];
        let menu_items = [];
        for (let i = 0; i < app_menu.length; i++) {
            menu_items.push(<MenuItem data={app_menu[i]} key={app_menu[i].id}/>)
        }

        return <div className="sidebar">
            <Event event='connect' handler={this.socket_server_state}/>
            <Event event='disconnect' handler={this.socket_server_state}/>
            <div className="sidebar-inner">
                <div className="sidebar-logo">
                    <div className="peers ai-c fxw-nw">
                        <div className="peer peer-greed">
                            <span className="sidebar-link td-n" href="https://colorlib.com/polygon/adminator/index.html">
                                <div className="peers ai-c fxw-nw">
                                    <div className="peer">
                                        <div className="logo">
                                            <img
                                                src="https://media.glassdoor.com/sqls/29783/focus-electronics-group-squarelogo-1426857440912.png"
                                                alt="" style={{'maxHeight':'64px'}}/>
                                        </div>
                                    </div>
                                    <div className="peer peer-greed"><h5 className="lh-1 mB-0 logo-text">FOCUS</h5>
                                    </div>
                                </div>
                            </span>
                        </div>
                        <div className="peer">
                            <div className="mobile-toggle sidebar-toggle">
                                <span className="td-n" onClick={ this.sidebar_toggle }><i className="ti-arrow-circle-left"></i></span>
                            </div>
                        </div>
                    </div>
                </div>

                <ul className="sidebar-menu scrollable pos-r ps">
                    { menu_items }
                </ul>
            </div>
            <div style={{'margin':'-25px 0 0 10px'}}>
                <div><small><i className={'ti-light-bulb '+(this.props.template.socket_server_state?'text-success':'text-danger') } /> socket</small></div>
            </div>
        </div>
    }
}

const mapStateToProps = function(store) {
  return {
    appSettings:  store.appSettings,
    template:  store.template
  };
};
export default connect(mapStateToProps)(SidebarLeft);