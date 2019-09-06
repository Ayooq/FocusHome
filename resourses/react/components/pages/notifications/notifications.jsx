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
      date_from: m.clone().subtract(1, 'months').toDate(),
      date_to: m.clone().add(1, 'days').toDate(),
      limit: 100,
      input_is_read: 0,
      input_device_oid: '',
      input_device_id: 0,
      inputs: {
        is_read: [
          <option value="-1" key={ '-1' }>статус: все</option>,
          <option value="0" key={ '0' }>не прочитано</option>,
          <option value="1" key={ '1' }>прочитано</option>
        ],
        devices: []
      }
    }

  }

  componentDidMount() {
    this.update_list();
  }

  update_list(){
    this.setState({request_send: true});
    let from = moment(this.state.date_from).format('YYYY-MM-DD HH:mm');
    let to   = moment(this.state.date_to  ).format('YYYY-MM-DD HH:mm');

    util.get({
      'url': '/api/monitoring?action=get_alerts',
      'data': {
        'from': from,
        'to': to, 
        'is_read': this.state.input_is_read,
        'limit': this.state.limit,
        'device_id': this.state.input_device_id,
        'device_oid': this.state.input_device_oid,
        'full': 1
      },
      'success': response => {
        this.setState({request_send: false});

        this.setState({data: response.data});

        // devices list
        let devices_options = [<option value={ 0 } key={ 0 }>устройства: все</option>];
        for(let i=0;i<response.data.devices.length;i++){
          let d = response.data.devices[i];
          devices_options.push(<option value={ d[0] } key={ d[0] }>{ d[1] }</option>);
        }
        this.setState({
          inputs: {
            ...this.state.inputs,
            devices: devices_options
          }
        });

      }
    });
  }


  date_from_update(newValue){
    this.setState({date_from: newValue});
  }

  date_to_update(newValue){
    this.setState({date_to: newValue});
  }

  input_is_read_update(event){
    let value = event.target.value;
    this.setState({input_is_read: +value});
  }

  input_device_oid_update(event){
    let value = event.target.value;
    this.setState({input_device_oid: value});
  }

  input_device_id_update(event){
    let value = event.target.value;
    this.setState({input_device_id: value});
  }

  set_read(nid){
    util.get({
      'url': '/api/monitoring?action=set_notification_read',
      'data': {'nid': nid},
      'success': response => {
        this.setState({request_send: false});
        this.update_list();
      }
    });
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

    let rows = [];
    if ( this.state.data ){
      for(let i=0;i<this.state.data.data.length;i++){
        let row = this.state.data.data[i];
        let message = <div>{row.message} {row.addr}<div><small>{ row.condition }</small></div></div>;
        let href = '/monitoring/device/' + row.device_id;
        switch (row.link_type) {
          case 'snmp_addr':
            href = '/monitoring/device/' + row.device_id + '/snmp/' + row.addr + '/history';
            break;
        }
              
        rows.push(<tr key={ row.id } className={ (row.is_read == 0?'table-warning':'') }>
          <td>{ row.updated }</td>
          <td>{ row.device_name }</td>
          <td>{ message }</td>
          <td>
            <div><Link to={ href }>подробности</Link></div>
            { row.is_read == 0 &&
              <div><span onClick={ this.set_read.bind(this, row.id) }
                       className="text-primary cur-p">отметить прочитаным</span></div>
            }
          </td>
        </tr>)
      }
    }


    return <div>
      <BGC title="Все уведомления"  buttons={buttons}>
        <div>
          <div>
            <div className="form-group">
              <div className="">
                <label className="col-form-label text-dark">Фильтр:</label>
                <span>&nbsp;</span>
                <span>с </span>
                <DatePicker
                  selected={ this.state.date_from }
                  onChange={ this.date_from_update.bind(this) }
                  showTimeSelect
                  dateFormat="dd.MM.yyyy HH:mm"
                  timeFormat="HH:mm"
                  locale="ru-RU"
                  className="form-control form-control-sm mw-150"
                />
                <span> по </span>
                <DatePicker
                  selected={ this.state.date_to }
                  onChange={ this.date_to_update.bind(this) }
                  showTimeSelect
                  dateFormat="dd.MM.yyyy HH:mm"
                  timeFormat="HH:mm"
                  locale="ru-RU"
                  className="form-control form-control-sm mw-150"
                />
                <span>&nbsp;</span>
                <select className="form-control form-control-sm d-inline mw-150" value={ this.state.input_is_read } onChange={ this.input_is_read_update.bind(this) }>
                  { this.state.inputs.is_read }
                </select>
                <span>&nbsp;</span>
                <select className="form-control form-control-sm d-inline mw-150" value={ this.state.input_device_id } onChange={ this.input_device_id_update.bind(this) }>
                  { this.state.inputs.devices }
                </select>
                <span>&nbsp;</span>
                <input className="form-control form-control-sm d-inline mw-150" value={ this.state.input_device_oid } onChange={ this.input_device_oid_update.bind(this) } type="text" placeholder="OID" />
                <span>&nbsp;</span>
                <button onClick={ this.update_list.bind(this) } className="btn btn-primary btn-sm"><i className="ti-reload"></i> обновить</button>
                { rows.length > 0 &&
                  <span>
                    <span>&nbsp;</span>
                    < button                                         className="btn btn-outline-primary btn-sm"><i className="ti-download"></i> скачать</button>
                  </span>
                }
                { this.state.request_send &&
                <small>&nbsp;обновляется...</small>
                }
              </div>
            </div>
          </div>
          
          <div>
            <table className="table table-sm table-bordered">
              <thead>
              <tr className="text-dark">
                <td>Дата</td>
                <td>Устройство</td>
                <td>Сообщение</td>
                <td></td>
              </tr>
              </thead>
              <tbody>
                { rows }
              </tbody>
            </table>
          </div>
        </div>
      </BGC>

    </div>
  }
}


export default SensorInfo;