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

import BGC from 'tags/bgc';


class PageDevices extends React.Component{
  constructor(props) {
    super(props);
    
    this.state = {
      request_send: false,
      data: null,
      filtr: {
        client: '',
        name: '',
        address: ''
      }
    };
  }
  
  componentDidMount() {
    this.update_list();
  }

  componentWillUnmount() {
  }

  update_list(){
    this.setState({request_send: true});
    util.get({
      'url': '/api/devices/',
      'data': {
        'client': this.state.filtr.client,
        'name': this.state.filtr.name,
        'address': this.state.filtr.address
      },
      'success': response => {
        this.setState({request_send: false});
        this.setState({data: response.data});
      }
    });    
  }

  input_filtr_update(propertyName, event) {
    let value = event.target.value;
    this.setState({filtr: {...this.state.filtr, [propertyName]: value}});
  }

  render(){
    if (this.state.data === null){
      return <div>загрузка...</div>
    }

    let buttons = [
      {
        'caption':'создать',
        'title':'создать',
        'ico':'ti-ti-widget',
        'href': '/devices/create/'
      },
      {
        'caption':'',
        'title':'обновить',
        'ico':'ti-reload',
        'onClick': this.update_list.bind(this)
      }
    ];
    
    let rows = [];
    for(let i=0;i<this.state.data.data.length;i++){
      let device = this.state.data.data[i];

      rows.push(<tr key={ device.device_id }>
        <td>{ device.device_id }</td>
        <td>{ device.client_name }</td>
        <td><Link to={ '/devices/'+device.device_id }>{ device.device_name }</Link></td>
        <td>{ device.device_address }</td>
        <td><small>{ device.device_comment }</small></td>
      </tr>)
    }


    return <div className="page-content container-fluid">
      <div className="row">
        <BGC title={ this.state.data.title } buttons={buttons} col="col-md-12">
          <div className="form-group">
              <label className="col-form-label text-dark">Фильтр:</label>
              <span>&nbsp;</span>
              <input className="form-control form-control-sm d-inline mw-150" value={ this.state.filtr.client } onChange={ this.input_filtr_update.bind(this, 'client') } type="text" placeholder="клиент" />
              <span>&nbsp;</span>
              <input className="form-control form-control-sm d-inline mw-150" value={ this.state.filtr.name } onChange={ this.input_filtr_update.bind(this, 'name') } type="text" placeholder="название" />
              <span>&nbsp;</span>
              <input className="form-control form-control-sm d-inline mw-150" value={ this.state.filtr.address } onChange={ this.input_filtr_update.bind(this, 'address') } type="text" placeholder="адрес" />
              <span>&nbsp;</span>
              <button onClick={ this.update_list.bind(this) } className="btn btn-primary btn-sm"><i className="ti-reload"></i> найти</button>
          </div>
          
          <table className="table">
            <thead>
            <tr>
              <th>#</th>
              <th>Клиент</th>
              <th>Наименование</th>
              <th>Адрес</th>
              <th>Комментарий</th>
            </tr>
            </thead>
            <tbody>
              { rows }
            </tbody>
          </table>
        </BGC>
      </div>
     </div>
  }
}


const mapStateToProps = function(store) {
  return {
    appSettings:  store.appSettings
  };
};


export default connect(mapStateToProps)(PageDevices);