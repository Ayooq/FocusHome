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
  
  componentDidMount() {
    this.update_list();
  }

  componentWillUnmount() {
  }

  update_list(event){
    util.get({
      'url': '/api/users/perm/',
      'data': {
        'user_id': this.state.user_id
      },
      'success': response => {
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

  user_perm_update(groupKey, permKey, event) {
    let value = event.target.type === 'checkbox' ? event.target.checked : event.target.value;
    this.setState( (state) => {
      state.data.perms[groupKey][permKey].check = value;
      return state;
    });
  }
  
  save(){
    let perms = [];
    for (let gkey in this.state.data.perms) {
      for (let pkey in this.state.data.perms[gkey]) {
        if (this.state.data.perms[gkey][pkey].check) {
          perms.push(this.state.data.perms[gkey][pkey].id)
        }
      }
    }

    util.post({
      'url': '/api/users/perm/',
      'data': {
        'user_id': this.state.user_id,
        'perms': perms
      },
      'success': response => {
    
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

    let groups_perms = [];
    for(let gkey in this.state.data.perms){
      let perms = [];
      for(let pkey in this.state.data.perms[gkey]){
        perms.push(<div key={pkey}>
          <label>
            <input type="checkbox" checked={ this.state.data.perms[gkey][pkey].check } onChange={this.user_perm_update.bind(this, gkey, pkey)} />
            <span className="ml-2">{ this.state.data.perms[gkey][pkey].name }</span>
          </label>
        </div>)
      }
      groups_perms.push(<div key={gkey}>
        <div>{ gkey }</div>
        <div className="pl-4">{ perms }</div>
      </div>)
    }

    return <div className="page-content container-fluid">
      <BGC title={ this.state.data.user.profile_lastname+' '+this.state.data.user.profile_firstname } buttons={buttons}>
        { groups_perms }
        {/*<div className="form-group">
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
        </div>*/}
      </BGC>


      <div className="col-md-12">
        <div className="form-group">
          <button className="btn btn-primary" onClick={ this.save }>Сохранить</button>
        </div>
      </div>
     </div>
  }
}

export default PageUsersEdit;