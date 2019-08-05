import ReactDOM from 'react-dom';
import React from 'react';
import axios from 'axios';
import { BrowserRouter as Router, Route, Switch, Link } from 'react-router-dom';
import { connect } from 'react-redux';
import store from '../store.jsx';
import {MyFunc as util} from '../func.jsx';


class IndexNavLeft extends React.Component{
  
  render(){
    return <div className="nav-left">
      <div className="nav-brand">
        <div>{this.props.appSettings.appName}</div>
      </div>

      {this.props.profile.accessList !== undefined &&
      <div className="nav-left-scroll">
        {this.props.profile.accessList['register.show'] === true &&
          <Link to="/registration"><i className="fa fa-registered fa-fw"></i> Заявки на регистрацию</Link>
        }
        {this.props.profile.accessList['clients.show'] === true &&
          <Link to="/clients"><i className="fa fa-users fa-fw"></i> Пользователи системы</Link>
        }
        {this.props.profile.accessList['handbooks.show'] === true &&
          <Link to="/handbooks"><i className="fa fa-book fa-fw"></i> Справочники</Link>
        }
        {this.props.profile.accessList['mycompany.show'] === true &&
          <Link to="/company-info"><i className="fa fa-info-circle fa-fw"></i> Моя организация</Link>
        }
        {util.in_array(this.props.profile.role, [39]) === true &&
          <Link to="/engineer-info"><i className="fa fa-info-circle fa-fw"></i> Личные данные</Link>
        }
        {util.in_array(this.props.profile.role, [39]) === true &&
          <Link to="/speciality"><i className="fa fa-gavel fa-fw"></i>Специализация</Link>
        }
        {this.props.profile.accessList['storages.show'] === true &&
          <Link to="/storages"><i className="fa fa-folder fa-fw"></i> Склад</Link>
        }
        {(this.props.profile.accessList['devices.show'] === true && util.in_array(this.props.profile.role, [48, 49]) === true && false) &&
          <Link to="/devices"><i className="fa fa-microchip fa-fw"></i> Оборудование</Link>
        }
        {this.props.profile.accessList['users.show'] === true &&
          <Link to="/users/"><i className="fa fa-user fa-fw"></i> Сотрудники</Link>
        }
        {this.props.profile.accessList['projects.show'] === true &&
          <Link to="/projects/"><i className="fa fa-cog fa-fw"></i> Проекты</Link>
        }
        {this.props.profile.accessList['orders.show'] === true &&
          <Link to="/orders/"><i className="fa fa-cogs fa-fw"></i> Заявки</Link>
        }
        {this.props.profile.accessList['work.show'] === true &&
          <Link to="/work-area/"><i className="fa fa-rocket fa-fw"></i> Рабочие области</Link>
        }
        {this.props.profile.accessList['folders.show'] === true &&
          <Link to="/documents"><i className="fa fa-file-text fa-fw"></i> Документы</Link>
        }
      </div>
      }



      

      </div>
  }
}

const mapStateToProps = function(store) {
  return {
    profile:      store.profile,
    appSettings:  store.appSettings
  };
}

export default connect(mapStateToProps)(IndexNavLeft);