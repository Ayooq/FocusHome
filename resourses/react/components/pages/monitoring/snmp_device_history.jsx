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
      history: null,
      request_send: false,
      device: props.match.params.deviceID,
      addr: props.match.params.addr,
      history_from: m.clone().subtract(1, 'months').toDate(),
      history_to: m.clone().add(1, 'days').toDate()
    }

  }

  componentDidMount() {
    this.update_list();
  }

  update_list(){
    this.setState({request_send: true});
    let from = moment(this.state.history_from).format('YYYY-MM-DD HH:mm');
    let to   = moment(this.state.history_to  ).format('YYYY-MM-DD HH:mm');
    
    util.get({
      'url': '/api/monitoring?action=snmp_sensor_get_history',
      'data': {'device_id': this.state.device, 'addr': this.state.addr, 'from': from, 'to': to},
      'success': response => {
        this.setState({request_send: false});
        this.setState({history: response.data});
      }
    });
  }


  history_from_update(newValue){
    this.setState({history_from: newValue});
  }

  history_to_update(newValue){
    this.setState({history_to: newValue});
  }

  render(){
    if (this.state.history === null){
      return <div>загрузка...</div>
    }

    let buttons = [
      {
        'caption':'',
        'title':'обновить',
        'ico':'ti-reload',
        'onClick': this.update_list.bind(this)
      }
    ];

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
      <BGC title="История"  buttons={buttons}>
        <div>
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
                  className="form-control form-control-sm"
                />
                <span> по </span>
                <DatePicker
                  selected={ this.state.history_to }
                  onChange={ this.history_to_update.bind(this) }
                  showTimeSelect
                  dateFormat="dd.MM.yyyy HH:mm"
                  timeFormat="HH:mm"
                  locale="ru-RU"
                  className="form-control form-control-sm"
                />
                <span>&nbsp;</span>
                <button onClick={ this.update_list.bind(this) } className="btn btn-primary btn-sm"><i className="ti-reload"></i> обновить</button>
                { this.state.request_send &&
                <small>&nbsp;обновляется...</small>
                }
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
      </BGC>

    </div>
  }
}


export default SensorInfo;