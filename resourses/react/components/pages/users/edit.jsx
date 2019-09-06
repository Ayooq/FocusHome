import ReactDOM from 'react-dom';
import React from 'react';
import {BrowserRouter as Router, Route, Switch, Link} from 'react-router-dom';
import {connect} from 'react-redux';
import store from 'store.jsx';
import {MyFunc as util} from 'func.jsx';
import Paginate from 'tags/paginate.jsx';
import InputText from 'tags/inputs/text';
import InputNumber from 'tags/inputs/number';
import InputSelect from 'tags/inputs/select';
import JsonView from 'tags/json-view';
import BGC from 'tags/bgc';


class PageUsersEdit extends React.Component{
  constructor(props) {
    super(props);
    
    this.state = {
      request_send: false,
      data: null,
      user_id: props.match.params.userID,
      inputs: {}
    };

    this.save = this.save.bind(this);
  }

  componentWillReceiveProps(nextProps) {
    if ( nextProps.match.params.userID != this.state.user_id ) {
      this.setState({user_id: +nextProps.match.params.userID});
      this.update_list(+nextProps.match.params.userID);
    }
  }
  
  componentDidMount() {
    this.update_list();
  }

  componentWillUnmount() {
  }

  update_list(user_id, event){
    if (typeof user_id === 'undefined'){
      user_id = this.state.user_id;
    }

    
    
    this.setState({request_send: true});

    util.get({
      'url': '/api/users/' + (user_id > 0 ? 'edit/' : 'create/'),
      'data': {
        'user_id': user_id
      },
      'success': response => {
        this.setState({request_send: false});
        this.setState({data: response.data});
      }
    });    
  }

  user_property_update(propertyName, event) {
    let value = event.target.value;
    this.setState( (state) => {
      state.data.user[propertyName] = value;
      return state;
    });
  }
  
  save(){
    this.setState({request_send: true});

    util.post({
      'url': '/api/users/' + (this.state.user_id > 0 ? 'update/' : 'create/'),
      'data': {
        'user_id': this.state.user_id,
        'user': this.state.data.user
      },
      'success': response => {
        this.setState({request_send: false});
        if (!(this.state.user_id > 0)) {
          this.props.history.push('/users/' + response.data.user_id);
        }
      }
    });
  }


  render(){
    if (this.state.data === null){
      return <div>загрузка...</div>
    }

    let buttons = [
      {
        'caption':'',
        'title':'обновить',
        'ico':'ti-reload',
        'onClick': this.update_list.bind(this, this.state.user_id)
      }
    ];

    let clients_select_input_options = [<option value="0" key="-1">-- не выбрано --</option>];
    if ('clients' in this.props.appSettings) {
      for (let i = 0; i < this.props.appSettings.clients.length; i++) {
        let client = this.props.appSettings.clients[i];
        clients_select_input_options.push(<option value={client.id} key={client.id}>{client.name}</option>)
      }
    }

    return <div className="page-content container-fluid">
      <div className="row">
        <BGC title={ this.state.data.user.profile_lastname+' '+this.state.data.user.profile_firstname } buttons={buttons} col="col-md-6">
          <div className="form-group">
            <label>Фамилия</label>
            <input type="text" className="form-control" value={ this.state.data.user.profile_lastname } onChange={ this.user_property_update.bind(this, 'profile_lastname') } />
          </div>
          <div className="form-group">
            <label>Имя</label>
            <input type="text" className="form-control" value={ this.state.data.user.profile_firstname } onChange={ this.user_property_update.bind(this, 'profile_firstname') } />
          </div>
          <div className="form-group">
            <label>Телефон</label>
            <input type="text" className="form-control" value={ this.state.data.user.profile_phone } onChange={ this.user_property_update.bind(this, 'profile_phone') } />
          </div>
        </BGC>

        <div className="col-md-6">
          <BGC title="Данные для входа в личный кабинет">
            <div className="form-group">
              <label>Электронная почта</label>
              <input type="text" className="form-control" value={ this.state.data.user.auth_email } onChange={ this.user_property_update.bind(this, 'auth_email') } />
            </div>
            <div className="form-group">
              <label>Пароль</label>
              <input type="text" className="form-control" value={ this.state.data.user.auth_password } onChange={ this.user_property_update.bind(this, 'auth_password') } />
            </div>
          </BGC>

          { (this.state.data.is_perm_change === true && this.state.data.user.auth_id > 0) &&
          <BGC title="Права пользователя">
            <div>
              <Link to={ '/users/'+this.state.data.user.auth_id+'/perm' }
                    className="btn btn-outline-primary">изменить</Link>
            </div>
          </BGC>
          }

          { (this.state.data.is_client_change === true && this.state.data.user.auth_id == 0) &&
          <BGC title="Клиент пользователя">
            <div className="form-group">
              <label>Установить клиента</label>
              <select className="form-control" value={ this.state.data.user.client_id } onChange={ this.user_property_update.bind(this, 'client_id') } >
                { clients_select_input_options }
              </select>
            </div>
          </BGC>
          }
        </div>
      </div>

      <div className="col-md-12">
        <div className="form-group">
          <button className="btn btn-primary" onClick={ this.save }>Сохранить</button>
          <span>&nbsp;</span>
          { this.state.request_send &&
            <small>обновляется...</small>
          }
        </div>
      </div>
     </div>
  }
}

const mapStateToProps = function(store) {
  return {
    appSettings:  store.appSettings
  };
};
export default connect(mapStateToProps)(PageUsersEdit);