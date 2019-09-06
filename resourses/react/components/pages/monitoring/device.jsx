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
import ModalChart from 'tags/modalChart';


class PageDevice extends React.Component{
  constructor(props) {
    super(props);
    
    this.state = { 
      data: {},
      timer_id: null,
      modal: {}
    };

  }

  componentDidMount() {
    this.update_list();
    let timer_id = setInterval(this.update_list.bind(this),global_monitoring_update_period);
    this.setState({timer_id: timer_id});
  }

  componentWillUnmount() {
    clearTimeout(this.state.timer_id);
    // this.setState({timer_id: null});
  }

  update_list(){
    util.get({
      'url': '/api/monitoring?action=device_info',
      'data': {'device_id': this.props.match.params.deviceID},
      'success' : response => {
        this.setState({data: response.data});
      }
    });
  }

  handleChange(propertyName, value) {
    this.setState({ [propertyName] : value });
  }

  chartShow(deviceID, unitID, chartType) {
    this.setState({ modal : {} });
    util.get({
      'url': '/api/monitoring?action=chart',
      'data': {'device_id': deviceID, 'unitID': unitID, 'chartType': chartType},
      'success' : response => {
        let modal = {
          device: response.data.unit.device,
          title: response.data.unit.title,
          subtitle: '',
          unit_code: response.data.unit.name,
          chartType: chartType,
          data: response.data.data,
          date: (new Date()).toString()
        };
        
        this.setState({ modal : modal });
      }
    });
    $('#modal_chart').modal();
  }

  unitToggle(deviceID, unitID) {
    util.get({
      'url': '/api/monitoring?action=unit_toggle',
      'data': {'device_id': deviceID, 'unitID': unitID},
      'success' : response => {
        //console.log(response.data);
      }
    });
  }

  render(){
    if (!('data' in this.state.data)){
      return <div></div>
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

    let temps = [];
    let ins = [];
    let couts = [];
    let networkStatus = null;
    
    if ("data" in this.state.data) {
      if ("temp" in this.state.data.data.status) {
        for (let key in this.state.data.data.status.temp) {
          let t = this.state.data.data.status.temp[key];
          let chartBtn = null;
          if (t.unit_format.chart){
            chartBtn = <span className="float-right cur-p" onClick={ this.chartShow.bind(this, this.state.data.data.id, t.unit__id, t.unit_format.chart) }><i className="ti-bar-chart"></i></span>
          }
          
          temps.push(<div key={key} className={ "p-20 mb-4 " + t.unit_format.class }>
            <h6>{ t.unit_format.title } { chartBtn }</h6>
            <div>
              <h1 className="text-center">{ t.unit_format.caption }</h1>
              <div className="text-right">{ t.date }</div>
            </div>
          </div>)
        }
      }

      if ("ins" in this.state.data.data.status) {
        for (let key in this.state.data.data.status.ins) {
          let t = this.state.data.data.status.ins[key];

          let chartBtn = null;
          if (t.unit_format.chart){
            chartBtn = <span className="float-right cur-p" onClick={ this.chartShow.bind(this, this.state.data.data.id, t.unit__id, t.unit_format.chart) }><i className="ti-bar-chart"></i></span>
          }

          let ctrls = t.unit_format.controls || [];
          let ctrlBtn = [];
          for (let i=0;i<ctrls.length;i++){
            let ctrl = ctrls[i];
            if (ctrl === "toggle"){
              ctrlBtn.push(<span className="btn btn-danger btn-sm" onClick={ this.unitToggle.bind(this, this.state.data.data.id, t.unit__id) } key={i}><i className="ti-power-off"></i></span>);
            }       
          }

          ins.push(<div key={key} className="device-ins-block">
            <div className={ "p-10 " + t.unit_format.class }>
              <h6>{ t.unit_format.title } { chartBtn }</h6>
              <div>
                <h4 className="text-center">{ t.unit_format.caption }</h4>
                <div className="text-right">
                  <div className="float-left">{ ctrlBtn }</div>
                  <span>{ t.date }</span>
                </div>
              </div>
            </div>
          </div>)

        }          
      }

      if ("couts" in this.state.data.data.status) {
        for (let key in this.state.data.data.status.couts) {
          let t = this.state.data.data.status.couts[key];

          let chartBtn = null;
          if (t.unit_format.chart){
            chartBtn = <span className="float-right cur-p" onClick={ this.chartShow.bind(this, this.state.data.data.id, t.unit, t.unit_format.chart) }><i className="ti-bar-chart"></i></span>
          }

          let ctrls = t.unit_format.controls || [];
          let ctrlBtn = [];
          for (let i=0;i<ctrls.length;i++){
            let ctrl = ctrls[i];
            if (ctrl === "toggle"){
              ctrlBtn.push(<span className="btn btn-danger btn-sm" onClick={ this.unitToggle.bind(this, this.state.data.data.id, t.unit__id) } key={i}><i className="ti-power-off"></i></span>);
            }
          }

          couts.push(<div key={key} className="device-ins-block">
            <div className={ "p-10 " + t.unit_format.class }>
              <h6>{ t.unit_format.title } { chartBtn }</h6>
              <div>
                <h4 className="text-center">{ t.unit_format.caption }</h4>
                <div className="text-right">
                  <div className="float-left">{ ctrlBtn }</div>
                  <span>{ t.date }</span>
                </div>
              </div>
            </div>
          </div>)

        }
      }
      
      if ("self" in this.state.data.data.status) {
        if ("self" in this.state.data.data.status.self) {
          let t = this.state.data.data.status.self.self;
          let ico = null;
          if ( t.unit_format.value === 'online' ){
            ico = <i className="ti-light-bulb"></i>
          }else if ( t.unit_format.value === 'offline' ){
            ico = <i className="ti-light-bulb"></i>
          }else{
            ico = <i className="ti-light-bulb"></i>
          }
          networkStatus = <span className={ "text-uppercase " + t.unit_format.class }>{ ico } { t.date } { t.unit_format.caption }</span>
        }
      }

    }

    
    return <div className="page-content container-fluid">
      <div className="row">
        <div className="col-md-8">
          <BGC title={block_title} buttons={buttons}>
            <div>
              <i className="c-orange-500 ti-home"></i> { this.state.data.data.address }
            </div>
            <div>
              { networkStatus }
            </div>
          </BGC>
          <BGC title="Датчики">
            <div>{ ins }</div>
            <div>{ couts }</div>
          </BGC>
        </div>
        <div className="col-md-4">
          <BGC title="Температура">
            { temps }
          </BGC>
        </div>

      </div>

      <ModalChart id="modal_chart" title={this.state.modal.device} data={this.state.modal}>
        <div></div>
      </ModalChart>

     </div>
  }
}

const mapStateToProps = function(store) {
  return {
    appSettings:  store.appSettings
  };
};

export default connect(mapStateToProps)(PageDevice);