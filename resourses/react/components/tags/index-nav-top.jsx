import ReactDOM from 'react-dom';
import React from 'react';
import {BrowserRouter as Router, Route, Switch, Link} from 'react-router-dom';
import {connect} from 'react-redux';
import store from 'store.jsx';
import {MyFunc as util} from 'func.jsx';


class IndexNavTop extends React.Component{

  componentDidMount() {
    util.get({
      'url': '/api/profile',
      'success' : response => {
        store.dispatch({
          type: 'RPOFILE_UPLOADED',
          data: response.data
        });
      }
    });
  }

  leftMenuToggle() {
    $('body').toggleClass('left-menu-open');
    util.setCookie('left-menu-open', $('body').hasClass('left-menu-open'));
  }
  
  render(){

    return <div className="nav-top clearfix">
      <div className="btn-open-box" onClick={this.leftMenuToggle}>
        <i className="fa fa-bars fa-fw" aria-hidden="true"></i>
      </div>

      <div className="nav-brand hidden">
        <div>{this.props.appSettings.appName}</div>
        <div className="nav-brand-line"></div>
      </div>

      <div className="user-box dropdown">
        <div data-toggle="dropdown">
          <div className="user-img" >
            {this.props.profile.image !== null &&
              <img src={this.props.profile.image} />
            }
           </div>
          <div className="user-info">
            <div className="user-info-name">{this.props.profile.name}</div>
            <div className="user-info-position">
              <small>{this.props.profile.position}</small>
            </div>
          </div>
          <div className="btn-open-box"><i className="fa fa-angle-down" aria-hidden="true"></i></div>
        </div>

        <ul className="dropdown-menu dropdown-menu-right" role="menu">
          <li role="presentation">
            <Link to="/profile"><i className="fa fa-user fa-fw"></i> Профиль</Link>
          </li>
          <li role="presentation"><a href="/logout"><i className="fa fa-sign-out fa-fw"></i> Выход</a></li>
        </ul>
      </div>



      

      </div>
  }
}

const mapStateToProps = function(store) {
  return {
    profile:      store.profile,
    appSettings:  store.appSettings
  };
}

export default connect(mapStateToProps)(IndexNavTop);