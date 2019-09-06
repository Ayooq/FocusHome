import React from 'react';
import {Link} from 'react-router-dom';
import {connect} from 'react-redux';
import store from 'store.jsx'


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
  }


  render(){
    let app_menu = this.props.appSettings.menu || [];
    let menu_items = [];
    for (let i=0;i<app_menu.length;i++){
      menu_items.push(<MenuItem data={app_menu[i]} key={app_menu[i].id} />)
    }
    
    return <div className="sidebar">
      <div className="sidebar-inner">
        <div className="sidebar-logo">
          <div className="peers ai-c fxw-nw">
            <div className="peer peer-greed">
              <a className="sidebar-link td-n" href="https://colorlib.com/polygon/adminator/index.html">
                <div className="peers ai-c fxw-nw">
                  <div className="peer">
                    <div className="logo">
                      <img src="https://media.glassdoor.com/sqls/29783/focus-electronics-group-squarelogo-1426857440912.png" alt="" style={{'maxHeight':'64px'}} />
                    </div>
                  </div>
                  <div className="peer peer-greed"><h5 className="lh-1 mB-0 logo-text">FOCUS</h5></div>
                </div>
              </a>
            </div>
            <div className="peer">
              <div className="mobile-toggle sidebar-toggle">
                <a href="" className="td-n"><i className="ti-arrow-circle-left"></i></a>
              </div>
            </div>
          </div>
        </div>

        <ul className="sidebar-menu scrollable pos-r ps">
          { menu_items }
        </ul>
      </div>
    </div>
  }
}

const mapStateToProps = function(store) {
  return {
    appSettings:  store.appSettings
  };
};
export default connect(mapStateToProps)(SidebarLeft);