import ReactDOM from 'react-dom';
import React from 'react';
import {BrowserRouter as Router, Route, Switch, Link} from 'react-router-dom';
import {connect} from 'react-redux';
import store from 'store.jsx';
import {MyFunc as util} from 'func.jsx';
import Paginate from 'tags/paginate.jsx';
import InputText from 'tags/inputs/text';
import InputSelect from 'tags/inputs/select';
import BGC from 'tags/bgc';
import Dialog from 'tags/modal';
import InputNumber from 'tags/inputs/number';
import moment from 'moment';
import DatePicker, { registerLocale } from 'react-datepicker';
import ruRU from 'date-fns/locale/ru';
registerLocale('ru-RU', ruRU);
// https://reactdatepicker.com/#example-17

moment.locale('ru');

class SensorInfo extends React.Component{
  constructor(props) {
    super(props);

    let m = moment();
    m.set({hour:0,minute:0,second:0,millisecond:0});
    
    this.state = {
      data: null,
      request_send: false,
      toogle_to_monitoring_interval: 0,
      history: null,
      history_from: m.clone().subtract(1, 'months').toDate(),
      history_to: m.clone().add(1,'days').toDate(),
    }

  }

  componentDidMount() {
    this.update_list();
  }

  update_list(){
    this.setState({request_send: true});
    util.get({
      'url': '/api/monitoring?action=get_snmp',
      'data': {'device_id': this.props.device, 'addr': this.props.addr, 'full': 1},
      'success' : response => {
        this.setState({request_send: false});
        this.setState({data: response.data});
      }
    });
  }

  toogle_to_monitoring(device, addr){
    if (this.state.data.data.interval == 0){
      this.setState({toogle_to_monitoring_interval: this.state.data.data.interval});

      this.dialog_tm.show({
        ico: <i className="ti-timer"></i>,
        title: 'Отслеживание изменений',
        message: 'Введите интервал снятия показаний параметра, в минутах',
        buttons: {
          cancelBtn: {
            title: 'Отмена',
            className: 'btn-default',
            onClick: (e)=> {
              this.dialog_tm.hide();
            }
          },
          okBtn: {
            title: 'Применить',
            className: 'btn-primary',
            onClick: ()=> {
              this.dialog_tm.hide();
              this.setState({request_send: true});
              util.get({
                'url': '/api/monitoring?action=snmp_sensor_set_monitoring_interval',
                'data': {'device_id': this.props.device, 'addr': this.props.addr, 'interval': this.state.toogle_to_monitoring_interval},
                'success' : response => {
                  this.setState({request_send: false});
                  this.state.data.data.interval = response.data.data.interval;
                  this.forceUpdate();
                  console.log(response.data.data.interval);
                }
              });
            }
          }
        }
      });
    }else{
      this.setState({request_send: true});
      util.get({
        'url': '/api/monitoring?action=snmp_sensor_set_monitoring_interval',
        'data': {'device_id': this.props.device, 'addr': this.props.addr, 'interval': 0},
        'success' : response => {
          this.setState({request_send: false});
          this.state.data.data.interval = response.data.data.interval;
          this.forceUpdate();
        }
      });
    }
    
  }

  toogle_to_monitoring_update(newValue){
    this.setState({toogle_to_monitoring_interval: newValue});
  }

  history_from_update(newValue){
    this.setState({history_from: newValue});
  }

  history_to_update(newValue){
    this.setState({history_to: newValue});
  }

  show_history(isHide){
    if ( this.state.history && isHide!== false){
      this.setState({history: null});
    }else {
      this.setState({request_send: true});
      let from = moment(this.state.history_from).format('YYYY-MM-DD HH:mm');
      let to   = moment(this.state.history_to  ).format('YYYY-MM-DD HH:mm');

      util.get({
        'url': '/api/monitoring?action=snmp_sensor_get_history',
        'data': {'device_id': this.props.device, 'addr': this.props.addr, 'from': from, 'to': to},
        'success': response => {
          this.setState({request_send: false});
          this.setState({history: response.data});
        }
      });
    }
  }

  render(){
    if (this.state.data === null){
      return <div>загрузка...</div>
    }

    let history_rows = [];
    if ( this.state.history ){
      for(let i=0;i<this.state.history.data.length;i++){
        let row = this.state.history.data[i];
        let value = (row.mib_value)?row.mib_value+' ('+row.value+')':row.value;
        history_rows.push(<tr key={ i }>
          <td>{ row.updated }</td>
          <td>{ value }</td>
        </tr>)
      }
    
    }

    
    return <div>

        <h3>
          { this.props.btnBack &&
            <span onClick={ this.props.btnBack }><i className="f text-primary ti-arrow-left"></i>&nbsp;</span>
          }
          <span>Подробно</span>
          <div className="pull-right" onClick={ this.update_list.bind(this) }>обновить</div>
        </h3>
        <div>

          <div className="form-group row">
            <label className="col-sm-2 col-form-label">OID</label>
            <div className="col-sm-10">
              <div className="form-control-plaintext">{ this.state.data.data.addr }</div>
            </div>
          </div>
          <div className="form-group row">
            <label className="col-sm-2 col-form-label">Значение</label>
            <div className="col-sm-10">
              <div className="form-control-plaintext">
                <div>
                  { this.state.data.data.mib_value ? (
                    this.state.data.data.mib_value + ' (' + this.state.data.data.value + ')'
                  ) : (
                    this.state.data.data.value
                  )}
                </div>
                <div>{ this.state.data.data.updated }</div>
              </div>
            </div>
          </div>
          <div className="form-group row">
            <label className="col-sm-2 col-form-label">Тип</label>
            <div className="col-sm-10">
              <div className="form-control-plaintext">{ this.state.data.data.value_type }</div>
            </div>
          </div>
          <div className="form-group row">
            <label className="col-sm-2 col-form-label">Диапазон значений</label>
            <div className="col-sm-10">
              <div className="form-control-plaintext">{ this.state.data.data.mib_syntax }</div>
            </div>
          </div>
          <hr/>
          <div className="form-group row">
            <label className="col-sm-2 col-form-label">MIB</label>
            <div className="col-sm-10">
              <div className="form-control-plaintext">{ this.state.data.data.mib_name }</div>
            </div>
          </div>
          <div className="form-group row">
            <label className="col-sm-2 col-form-label">MIB путь</label>
            <div className="col-sm-10">
              <div className="form-control-plaintext">{ this.state.data.data.mib_node_name }</div>
            </div>
          </div>
          <hr/>
          <div className="form-group row">
            <label className="col-sm-2 col-form-label">Описание</label>
            <div className="col-sm-10">
              <div className="form-control-plaintext">{ this.state.data.data.mib_node_desc }</div>
            </div>
          </div>
          <hr/>
          
          <div>
            <div className="btn-group" role="group">
              <button onClick={ this.toogle_to_monitoring.bind(this, this.props.device, this.state.data.data.addr) } className={ 'btn ' + ((this.state.data.data.interval>0)?'btn-success':'btn-secondary') }>
                <i className="ti-timer" />&nbsp;
                <span>{ (this.state.data.data.interval>0)?'Удалить из отслеживаемых ('+this.state.data.data.interval+' мин)':'Добавить в отслеживаемые' }</span>
              </button>
              <button onClick={ this.show_history.bind(this) } className="btn btn-info"><i className="ti-book"></i> История изменений</button>
              <button className="btn btn-info"><i className="ti-reload"></i> Обновить значение</button>
              <button className="btn btn-warning"><i className="ti-alert"></i> Создать оповещение</button>
              <button className="btn btn-primary"><i className="ti-widget"></i> Создать виджет</button>
            </div>
            { this.state.request_send &&
              <div><small>обновляется...</small></div>
            }
          </div>

      </div>

      { this.state.history &&
      <div>
        <h3>История</h3>
        <div>
          <div className="form-group row">
            <label className="col-sm-2 col-form-label">Период</label>
            <div className="col-sm-10">
              <span>с </span>
              <DatePicker
                selected={ this.state.history_from }
                onChange={ this.history_from_update.bind(this) }
                showTimeSelect
                dateFormat="dd.MM.yyyy HH:mm"
                timeFormat="HH:mm"
                locale="ru-RU"
                className="form-control"
              />
              <span> по </span>
              <DatePicker
                selected={ this.state.history_to }
                onChange={ this.history_to_update.bind(this) }
                showTimeSelect
                dateFormat="dd.MM.yyyy HH:mm"
                timeFormat="HH:mm"
                locale="ru-RU"
                className="form-control"
              />
              <span> </span>
              <button onClick={ this.show_history.bind(this, false) } className="btn btn-primary"><i className="ti-reload"></i> обновить</button>
            </div>
          </div>
        </div>
        <hr/>
        <div>
          <table className="table table-sm table-bordered">
            <thead>
              <tr className="text-dark">
                <td>Дата</td>
                <td>Значение</td>
              </tr>
            </thead>
            <tbody>
              { history_rows }
            </tbody>
          </table>
        </div>
      </div>
      }

      <Dialog ref={(el) => { this.dialog_tm = el }} >
        <InputNumber className="form-control" min="0" max="1440" value={ this.state.toogle_to_monitoring_interval } onChange={ (e)=>{this.toogle_to_monitoring_update(e)} } />
      </Dialog>

     </div>
  }
}

SensorInfo.defaultProps = {
  device: 0,
  addr: 0
};

export default SensorInfo;