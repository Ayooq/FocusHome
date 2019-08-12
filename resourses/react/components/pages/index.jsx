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


class PageIndex extends React.Component{
  constructor(props) {
    super(props);
    
    this.state = { 
      data: {},
      client_id: 0,
      timer_id: null
    };
  }
  
  componentDidMount() {
    this.update_list();
    let timer_id = setInterval(this.update_list.bind(this),global_monitoring_update_period);
    this.setState({timer_id: timer_id});
  }

  componentWillUnmount() {
    clearTimeout(this.state.timer_id);
    this.setState({timer_id: null});
  }

  update_list(){
    util.get({
      'url': '/monitoring/api?action=devices_list',
      'data': {'client_id': this.state.client_id},
      'success' : response => {
        this.setState({data: response.data});
        //console.log(this.state.data.devices);
      }
    });    
  }

  handleChange(propertyName, value) {
    this.setState({ [propertyName] : value });
  }

  render(){

    let devices = [];
    if('data' in this.state.data){
      let list = this.state.data.data;
      for(let key in list){

        let networkStatus = null;
        let temps = {'cpu':null,'ext':null};
        let ins = [];
        let couts = [];
        if ("self" in list[key].status) {
          if ("self" in list[key].status.self) {
            let t = list[key].status.self.self;
            let ico = null;

            if ( t.unit_format.value === 'online' ){
              ico = <i className="ti-light-bulb"></i>
            }else if ( t.unit_format.value === 'offline' ){
              ico = <i className="ti-light-bulb"></i>
            }else{
              ico = <i className="ti-light-bulb"></i>
            }
            networkStatus = <span className={ "text-uppercase " + t.unit_format.class }>{ ico }</span>; //<span className={ "text-uppercase " + t.unit_format.class }>{ ico } { t.date } { t.unit_format.caption }</span>
          }
        }


        if ("temp" in list[key].status) {
          for (let temp_key in list[key].status.temp) {
            let t = list[key].status.temp[temp_key];
            temps[temp_key] = <div key={temp_key} className={ "device-ins-block-small " + t.unit_format.class } title={ t.unit_format.title }>{ t.unit_format.caption }</div>
          }
        }


        if ("ins" in list[key].status) {
          for (let ins_key in list[key].status.ins) {
            let t = list[key].status.ins[ins_key];

            ins.push(<div key={ins_key} className={ "device-ins-block-small " + t.unit_format.class } title={ t.unit_format.title }>{ t.unit_format.title }: { t.unit_format.caption }</div>)
          }
        }

        if ("couts" in list[key].status) {
          for (let couts_key in list[key].status.couts) {
            let t = list[key].status.couts[couts_key];

            couts.push(<div key={couts_key} className={ "device-ins-block-small " + t.unit_format.class } title={ t.unit_format.title }>{ t.unit_format.title }: { t.unit_format.caption }</div>)
          }
        }
        
        devices.push(<tr key={list[key].id} className="tr-device">
          <td>{networkStatus}</td>
          <td>{list[key].uid}</td>
          <td><div>{list[key].name}</div><small>{list[key].client__name}</small></td>
          <td>{list[key].address}</td>
          <td>{ temps.ext }</td>
          <td>{ temps.cpu }</td>
          <td><Link to={'/monitoring/device/'+list[key].id}>управление</Link></td>
        </tr>)

        devices.push(<tr key={ "info_" + list[key].id} className="tr-device-info">
          <td colSpan="7">{ ins } { couts }</td>
        </tr>)
      }
    }
    
    let block_title = "";
    if('title' in this.state.data){
      block_title = this.state.data.title;
    }
    
    let buttons = [
      {
        'caption':'',
        'title':'обновить',
        'ico':'ti-reload',
        'onClick': this.update_list.bind(this)
      }
    ];

    let clients = [];
    if ('clients' in this.props.appSettings) {
      clients = this.props.appSettings.clients;
    }
    


    
    return <div className="page-content container-fluid">
      <div className="row">
        <BGC title={block_title} buttons={buttons} col="col-md-12">
          <div className="mb-12">
            { this.state.data.client_change &&
              <InputSelect list={clients} value={this.state.client_id}
                           style={{'width': '150px','display':'inline-block'}}
                           onChange={this.handleChange.bind(this, 'client_id')} label="Клиент"/>
            }
          </div>
          <table className="table">
            <thead>
            <tr>
              <th width="40px"></th>
              <th width="125px">UID</th>
              <th>Наименование</th>
              <th>Адрес</th>
              <th width="95px">Темп.<br/>среды</th>
              <th width="95px">Темп.<br/>CPU</th>
              <th width="90px"></th>
            </tr>
            </thead>
            <tbody>
              {devices}
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

export default connect(mapStateToProps)(PageIndex);