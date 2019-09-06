import ReactDOM from 'react-dom';
import React from 'react';
import {Link} from 'react-router-dom';
import {connect} from 'react-redux';
import store from 'store.jsx';
import {MyFunc as util} from 'func.jsx';
import Paginate from 'tags/paginate.jsx';
import InputText from 'tags/inputs/text';
import InputSelect from 'tags/inputs/select';
import BGC from 'tags/bgc';
import Dialog from 'tags/modal';
import InputNumber from 'tags/inputs/number';


class SensorInfo extends React.Component{
  constructor(props) {
    super(props);

    this.state = {
      data: null,
      request_send: false,
      toogle_to_monitoring_interval: 0,
      device: props.match.params.deviceID,
      addr: props.match.params.addr,
      notification: {conditions: []},
      conditions: {
        'lt':'<',
        'eq':'=',
        'gt':'>',
        'like':'содержит',
        'not_like':'не содержит'
      }
    }

  }

  componentDidMount() {
    this.update_list();
  }

  update_list(){
    this.setState({request_send: true});
    util.get({
      'url': '/api/monitoring?action=get_snmp',
      'data': {'device_id':  this.state.device, 'addr':  this.state.addr, 'full': 1},
      'success' : response => {
        this.setState({request_send: false});
        this.setState({data: response.data});
        this.setState({notification: response.data.notifications});
      }
    });
  }

  toogle_to_monitoring(device, addr){
    if (this.state.data.data.interval == 0){
      this.setState({toogle_to_monitoring_interval: this.state.data.data.interval});

      this.dialog_tm.show({
        ico: <i className="ti-timer"></i>,
        title: 'Отслеживание изменений',
        message: <p>Введите интервал снятия показаний параметра, в минутах</p>,
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
                'data': {'device_id': this.state.device, 'addr': this.state.addr, 'interval': this.state.toogle_to_monitoring_interval},
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
        'data': {'device_id': this.state.device, 'addr': this.state.addr, 'interval': 0},
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

  reload_value(device, addr){
    this.setState({request_send: true});
    util.get({
      'url': '/api/monitoring?action=snmp_sensor_reload_value',
      'data': {'device_id':  device, 'addr':  addr},
      'success' : response => {
        this.setState({request_send: false});
        this.update_list();
      }
    });
  }

  notification_condition_remove(index){
    let notification = this.state.notification;
    notification.conditions.splice(index,1);
    this.setState({notification: notification});
  }

  notification_condition_add(){
    let notification = this.state.notification;
    notification.conditions.push(['eq','']);
    this.setState({notification: notification});
  }

  notification_value_change(param, index, event){
    let notification = this.state.notification;
    notification.conditions[index][param] = event.target.value;
    this.setState({notification: notification});
  }

  create_notification(device_id, addr){
    this.dialog_nf.show({
      ico: <i className="ti-alert"></i>,
      size: 'modal-lg',
      title: 'Создать оповещение',
      message: <p>Создайте условия для оповещения</p>,
      buttons: {
        cancelBtn: {
          title: 'Отмена',
          className: 'btn-default',
          onClick: (e)=> {
            this.dialog_nf.hide();
          }
        },
        okBtn: {
          title: 'Создать',
          className: 'btn-primary',
          onClick: ()=> {
            this.dialog_nf.hide();
            this.setState({request_send: true});
            util.get({
              'url': '/api/monitoring?action=snmp_sensor_set_notification',
              'data': {'device_id': this.state.device, 'addr': this.state.addr, 'notifications': this.state.notification},
              'success' : response => {
                this.setState({request_send: false});
                this.setState({notification: response.data.notification});
              }
            });
          }
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
        'onClick': this.update_list.bind(this)
      }
    ];

    // notifications
    let options = [];
    for (let key in this.state.conditions){
      options.push(<option key={key} value={key}>{this.state.conditions[key]}</option>)
    }

    let fields = [];
    for (let i=0;i<this.state.notification.conditions.length;i++){
      fields.push(<div className="form-group row" key={i}>
        <label className="col-sm-3 col-form-label">
          <span onClick={ this.notification_condition_remove.bind(this, i) }><i className="ti-close text-danger" /></span> <span>Условие №{ i+1 }</span>
        </label>
        <div className="col-sm-3">
          <select value={ this.state.notification.conditions[i][0] } onChange={ this.notification_value_change.bind(this, 0, i) } className="form-control">{options}</select>
        </div>
        <div className="col-sm-6">
          <input type="text" className="form-control" value={ this.state.notification.conditions[i][1] } onChange={ this.notification_value_change.bind(this, 1, i) } />
        </div>
      </div>)
    }

    let notification_body = <div>
      { fields }
      <span className="text-primary" onClick={ this.notification_condition_add.bind(this) }><i className="ti-plus" /> добавить условие</span>
    </div>
    
    
    
    return <div>
      <BGC title="Детали" buttons={buttons}>
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
              <button onClick={ this.toogle_to_monitoring.bind(this, this.state.device, this.state.addr) } className={ 'btn ' + ((this.state.data.data.interval>0)?'btn-success':'btn-secondary') }>
                <i className="ti-timer" />&nbsp;
                <span>{ (this.state.data.data.interval>0)?'Удалить из отслеживаемых ('+this.state.data.data.interval+' мин)':'Добавить в отслеживаемые' }</span>
              </button>
              <Link to={'/monitoring/device/'+this.state.device+'/snmp/'+this.state.addr+'/history'} className="btn btn-info"><i className="ti-book"></i> История изменений</Link>
              <button className="btn btn-info" onClick={ this.reload_value.bind(this, this.state.device, this.state.addr) } ><i className="ti-reload"></i> Обновить значение</button>
              <button className="btn btn-warning" onClick={ this.create_notification.bind(this, this.state.device, this.state.addr) }><i className="ti-alert"></i> Создать оповещение</button>
              <Link to={'/monitoring/device/'+this.state.device+'/snmp/'+this.state.addr+'/widget'} className="btn btn-primary"><i className="ti-widget"></i> Создать виджет</Link>
            </div>
            { this.state.request_send &&
              <div><small>обновляется...</small></div>
            }
          </div>

        </div>
  
        <Dialog ref={(el) => { this.dialog_tm = el }}>
          <InputNumber className="form-control" min="0" max="1440" value={ this.state.toogle_to_monitoring_interval } onChange={ (e)=>{this.toogle_to_monitoring_update(e)} } />
        </Dialog>

        <Dialog ref={(el) => { this.dialog_nf = el }}>
          { notification_body }
        </Dialog>

      </BGC>

    </div>
  }
}


export default SensorInfo;