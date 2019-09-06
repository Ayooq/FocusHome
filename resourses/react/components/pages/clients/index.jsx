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


class PageClients extends React.Component{
  constructor(props) {
    super(props);
    
    this.state = {
      data: null,
      filtr: {
        name: ''
      }
    };
  }
  
  componentDidMount() {
    this.update_list();
  }

  componentWillUnmount() {
  }

  update_list(){
    util.get({
      'url': '/api/clients/',
      'data': {
        'name': this.state.filtr.name
      },
      'success': response => {
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
        'href': '/clients/create/'
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
      let client = this.state.data.data[i];

      rows.push(<tr key={ client.client_id }>
        <td>{ client.client_id }</td>
        <td><Link to={ '/clients/'+client.client_id }>{ client.client_name }</Link></td>
      </tr>)
    }


    return <div className="page-content container-fluid">
      <div className="row">
        <BGC title={ this.state.data.title } buttons={buttons} col="col-md-12">
          <div className="form-group">
              <label className="col-form-label text-dark">Фильтр:</label>
              <span>&nbsp;</span>
              <input className="form-control form-control-sm d-inline mw-150" value={ this.state.filtr.name } onChange={ this.input_filtr_update.bind(this, 'name') } type="text" placeholder="название" />
              <span>&nbsp;</span>
              <button onClick={ this.update_list.bind(this) } className="btn btn-primary btn-sm"><i className="ti-reload"></i> найти</button>
              { this.state.request_send &&
              <small>&nbsp;обновляется...</small>
              }
          </div>
          
          <table className="table">
            <thead>
            <tr>
              <th>#</th>
              <th>Наименование</th>
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


export default connect(mapStateToProps)(PageClients);