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


class PageClientsEdit extends React.Component{
  constructor(props) {
    super(props);
    
    this.state = {
      request_send: false,
      data: null,
      client_id: props.match.params.clientID,
      inputs: {}
    };

    this.save = this.save.bind(this);
  }

  componentWillReceiveProps(nextProps) {
    if ( nextProps.match.params.clientID != this.state.client_id ) {
      this.setState({client_id: +nextProps.match.params.clientID});
      this.update_list(+nextProps.match.params.clientID);
    }
  }
  
  componentDidMount() {
    this.update_list();
  }

  componentWillUnmount() {
  }

  update_list(client_id, event){
    if (typeof client_id === 'undefined'){
      client_id = this.state.client_id;
    }

    
    
    this.setState({request_send: true});

    util.get({
      'url': '/api/clients/' + (client_id > 0 ? 'edit/' : 'create/'),
      'data': {
        'client_id': client_id
      },
      'success': response => {
        this.setState({request_send: false});
        this.setState({data: response.data});
      }
    });    
  }

  client_property_update(propertyName, event) {
    let value = event.target.value;
    this.setState( (state) => {
      state.data.client[propertyName] = value;
      return state;
    });
  }
  
  save(){
    this.setState({request_send: true});

    util.post({
      'url': '/api/clients/' + (this.state.client_id > 0 ? 'update/' : 'create/'),
      'data': {
        'client_id': this.state.client_id,
        'client': this.state.data.client
      },
      'success': response => {
        this.setState({request_send: false});
        if (!(this.state.client_id > 0)) {
          this.props.history.push('/clients/' + response.data.client_id);
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
        'onClick': this.update_list.bind(this, this.state.client_id)
      }
    ];

    return <div className="page-content container-fluid">
      <div className="row">
        <BGC title={ this.state.data.client.client_name } buttons={buttons} col="col-md-6">
          <div className="form-group">
            <label>Название</label>
            <input type="text" className="form-control" value={ this.state.data.client.client_name } onChange={ this.client_property_update.bind(this, 'client_name') } />
          </div>
        </BGC>
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


export default PageClientsEdit;