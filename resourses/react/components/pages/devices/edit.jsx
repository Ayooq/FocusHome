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
import Dialog from 'tags/modal';
import BGC from 'tags/bgc';


class PageDevicesEdit extends React.Component{
  constructor(props) {
    super(props);
    
    this.state = {
      request_send: false,
      data: null,
      device_id: props.match.params.deviceID,
      inputs: {
        pins: [],
        units: [],
        gpio_types: [],
        chart_types: [],
        gpio_controls: [],
        gpio_widget_formats: [],
      },
      device_unit_id: 0,
      gpio_values_default_key: 'иначе',
      selected_units: []
    };

    this.save = this.save.bind(this);
    this.device_client_change = this.device_client_change.bind(this);
  }

  componentWillReceiveProps(nextProps) {
    if ( nextProps.match.params.deviceID != this.state.device_id ) {
      this.setState({device_id: +nextProps.match.params.deviceID});
      this.update_list(+nextProps.match.params.deviceID);
    }
  }
  
  componentDidMount() {
    this.update_list();
  }

  componentWillUnmount() {
  }

  update_list(device_id){
    if (typeof device_id === 'undefined'){
      device_id = this.state.device_id;
    }
    
    this.setState({request_send: true});
    
    util.get({
      'url': '/api/devices/' + (device_id > 0 ? 'edit/' : 'create/'),
      'data': {
        'device_id': device_id
      },
      'success': response => {
        this.setState({request_send: false});

        let pins = [];
        for(let i=0;i<response.data.pins.length;i++){
          let item = response.data.pins[i];
          pins.push(<option key={i} value={item}>{item}</option>)
        }
        this.setState({inputs: {...this.state.inputs, pins: pins}});

        let family = null;
        let families = [];
        let units = [];
        for(let i=0;i<response.data.units.length;i++){
          let item = response.data.units[i];
          
          if (family != item.family__title){
            if (units.length) {
              families.push(<optgroup label={family} key={i}>{units}</optgroup>);
              units = [];
            }
            family = item.family__title;
          }
          units.push(<option key={i} value={ i }>{item.units__title}</option>)
        }
        if (units.length) {
          families.push(<optgroup label={family} key={family.length}>{units}</optgroup>);
        }
        this.setState({inputs: {...this.state.inputs, units: families}});

        let gpio_types = [];
        for(let i=0;i<response.data.gpio_types.length;i++){
          let item = response.data.gpio_types[i];
          gpio_types.push(<option key={i} value={ item.name }>{ item.desc }</option>)
        }
        this.setState({inputs: {...this.state.inputs, gpio_types: gpio_types}});

        let chart_types = [];
        chart_types.push(<option key={-1} value="">нет</option>);
        for(let i=0;i<response.data.chart_types.length;i++){
          let item = response.data.chart_types[i];
          chart_types.push(<option key={i} value={ item.name }>{ item.desc }</option>)
        }
        this.setState({inputs: {...this.state.inputs, chart_types: chart_types}});

        let gpio_controls = [];
        gpio_controls.push(<option key={-1} value="cntrl_remove">удалить</option>);
        for(let i=0;i<response.data.gpio_controls.length;i++){
          let item = response.data.gpio_controls[i];
          gpio_controls.push(<option key={i} value={ item.name }>{ item.desc }</option>)
        }
        this.setState({inputs: {...this.state.inputs, gpio_controls: gpio_controls}});

        let gpio_widget_formats = [];
        gpio_widget_formats.push(<option key={-1} value="">нет</option>);
        for(let i=0;i<response.data.gpio_widget_formats.length;i++){
          let item = response.data.gpio_widget_formats[i];
          gpio_widget_formats.push(<option key={i} value={ item.name }>{ item.desc }</option>)
        }
        this.setState({inputs: {...this.state.inputs, gpio_widget_formats: gpio_widget_formats}});

        this.setState({data: response.data});
      }
    });    
  }

  device_property_update(propertyName, event) {
    let value = event.target.value;
    this.setState( (state) => {
      state.data.device[propertyName] = value;
      return state;
    });
  }

  unit_property_update(unitIndex, propertyName, event) {
    let value = event.target.value;
    this.setState( (state) => {
      state.data.units[unitIndex][propertyName] = value;
      return state;
    });

    if ( propertyName === 'gpio__pin' ){
      let selected_units = [];
      for(let i=0;i<this.state.data.units.length;i++){
        if(unitIndex != i) {
          selected_units.push(+this.state.data.units[i].gpio__pin);
        }
      }
      this.setState({selected_units: selected_units});
    }
  }

  data_property_update(propertyName, event) {
    let value = event.target.value;
    this.setState( (state) => {
      state[propertyName] = value;
      return state;
    });


    if ( propertyName === 'device_unit_id' ){
      let selected_units = [];
      for(let i=0;i<this.state.data.units.length;i++){
        if(value != i) {
          selected_units.push(+this.state.data.units[i].gpio__pin);
        }
      }
      this.setState({selected_units: selected_units});
    }
  }

  device_gpio_format_update(unitIndex, propertyName, event) {
    let value = event.target.type === 'checkbox' ? event.target.checked : event.target.value;
    this.setState( (state) => {
      state.data.units[unitIndex].gpio__format[propertyName] = value;
      return state;
    });
  }

  device_gpio_controls_update(unitIndex, cntrlIndex, event) {
    let value = event.target.value;
    
    this.setState((state) => {
      if ( value === 'cntrl_remove'){
        let values = state.data.units[unitIndex].gpio__format.controls;
        values.splice(cntrlIndex, 1);
        state.data.units[unitIndex].gpio__format.controls = values;
      }else {
        state.data.units[unitIndex].gpio__format.controls[cntrlIndex] = value;
      }
      return state;
    });
  }

  device_gpio_controls_add(unitIndex, event) {
    this.setState((state) => {
      let values = state.data.units[unitIndex].gpio__format.controls;
      values = values.concat([(this.state.data.gpio_controls[0] || {"name":''}).name]);
      state.data.units[unitIndex].gpio__format.controls = values;
      return state;
    });
  }

  device_gpio_values_update(unitIndex, valueKey, propertyName, event) {
    let value = event.target.value;
    this.setState( (state) => {
      state.data.units[unitIndex].gpio__format.values[valueKey][propertyName] = value;
      return state;
    });
  }

  device_gpio_values_remove(unitIndex, valueKey, event) {
    this.setState( (state) => {
      let values = state.data.units[unitIndex].gpio__format.values;
      values.splice(valueKey, 1);
      state.data.units[unitIndex].gpio__format.values = values;
      return state;
    });
  }

  device_gpio_values_add(unitIndex, valueKey, event) {
    this.setState( (state) => {
      let values = [];
      for(let key=0;key<state.data.units[unitIndex].gpio__format.values.length;key++){
        if ( key == valueKey){
          values.push({'value':'новое значение','title':'','class':''});
        }
        values.push(state.data.units[unitIndex].gpio__format.values[key]);
      }
      state.data.units[unitIndex].gpio__format.values = values;
      return state;
    });
  }
  
  save(){
    this.setState({request_send: true});

    util.post({
      'url': '/api/devices/' + (this.state.device_id > 0 ? 'update/' : 'create/'),
      'data': {
        'device_id': this.state.device_id,
        'device': this.state.data.device,
        'units': this.state.data.units
      },
      'success': response => {
        this.setState({request_send: false});
        if (!(this.state.device_id > 0)) {
          this.props.history.push('/devices/' + response.data.device_id);
        }
      }
    });
  }

  device_reboot(){
    this.dialog_dr.show({
      ico: <i className="ti-info-alt"></i>,
      title: 'Применение настроек',
      message: <p>Настройки вступят в силу после перезагрузки устройства. Это может занять несколько минут</p>,
      buttons: {
        cancelBtn: {
          title: 'Отмена',
          className: 'btn-default',
          onClick: (e)=> {
            this.dialog_dr.hide();
          }
        },
        okBtn: {
          title: 'Перезагрузить',
          className: 'btn-warning',
          onClick: ()=> {
            this.dialog_dr.hide();
            this.device_reboot_confirm();
          }
        }
      }
    });
  }

  device_reboot_confirm(){
    this.setState({request_send: true});

    util.post({
      'url': '/api/devices/' + this.state.device_id +  '/reboot/',
      'data': {
        'device_id': this.state.device_id
      },
      'success': response => {
        this.setState({request_send: false});
        
        this.dialog_dr.show({
          ico: <i className="ti-info-alt"></i>,
          title: 'Применение настроек',
          message: <p>{ response.data.message }</p>,
          buttons: {
            okBtn: {
              title: 'OK',
              className: 'btn-primary',
              onClick: ()=> {
                this.dialog_dr.hide();
              }
            }
          }
        });
      }
    });
  }
  
  device_client_change(){
    util.post({
      'url': '/api/devices/' + this.state.device_id + '/client_change/',
      'data': {
        'device_id': this.state.device_id,
        'client_id': this.state.data.device.device_client_id
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
        'onClick': this.update_list.bind(this, this.state.device_id)
      }
    ];

    let row = this.state.data.units[this.state.device_unit_id];

    let row_values = [];
    for (let key=0;key<row.gpio__format.values.length;key++){
      let v = row.gpio__format.values[key];

      let group_value = <input type="text" className="form-control form-control-sm" value={ v.value } onChange={ this.device_gpio_values_update.bind(this, this.state.device_unit_id, key, 'value') }/>
      if (v.value === this.state.gpio_values_default_key){
        group_value = <div className="form-control form-control-sm bg-lightgray" >{ v.value }</div>
      }
      
      row_values.push(<div key={ key } className="border border-info border-left-0 border-right-0 border-top-0 mb-12">
        <div>
          <small onClick={ this.device_gpio_values_add.bind(this, this.state.device_unit_id, key) } className="text-primary cur-p">
            <i className="ti-plus"/><span> добавить группу</span>
          </small>
        </div>
        <div className="form-group row">
          <label className="col-sm-4 col-form-label">
            { v.value !== this.state.gpio_values_default_key &&
            <span onClick={ this.device_gpio_values_remove.bind(this, this.state.device_unit_id, key) }><i
              className="ti-trash text-danger cur-p"/></span>
            }
            <span> значение</span>
          </label>
          <div className="col-sm-8">
            { group_value }
          </div>
        </div>
        <div className="form-group row">
          <label className="col-sm-4 col-form-label">название</label>
          <div className="col-sm-8">
            <input type="text" className="form-control form-control-sm" value={ v.title } onChange={ this.device_gpio_values_update.bind(this, this.state.device_unit_id, key, 'title') }/>
          </div>
        </div>
        <div className="form-group row">
          <label className="col-sm-4 col-form-label">оформление</label>
          <div className="col-sm-8">
            <select className="form-control form-control-sm" value={ v.class }
                    onChange={ this.device_gpio_values_update.bind(this, this.state.device_unit_id, key, 'class') }>
              { this.state.inputs.gpio_widget_formats }
            </select>
          </div>
        </div>
      </div>)
    }

    let gpio_controls = [];
    for (let key=0;key<row.gpio__format.controls.length;key++){
      let cntrl = row.gpio__format.controls[key];

      gpio_controls.push(<select className="form-control form-control-sm mw-100 d-inline mr-2" value={ cntrl } key={ key }
                                 onChange={ this.device_gpio_controls_update.bind(this, this.state.device_unit_id, key) }>
        { this.state.inputs.gpio_controls }
      </select>)
    }
    gpio_controls.push(<small key={row.gpio__format.controls.length} className="text-primary cur-p"
      onClick={ this.device_gpio_controls_add.bind(this, this.state.device_unit_id) } ><i className="ti-plus"/> добавить</small>)

    
    let pin = null;
    if (row.is_pin){
      pin = <select className="form-control" value={ row.gpio__pin } onChange={ this.unit_property_update.bind(this, this.state.device_unit_id, 'gpio__pin') } >
          { this.state.inputs.pins }
        </select>
    }else{
      pin = <div className="form-control">{ row.gpio__pin }</div>
    }

    let units = <div className="col-md-10 col-lg-8 col-xl-6">
      <div>
        <label>{ row.family__title } / { row.units__title }</label>
      </div>
      <div className="form-group row">
        <label className="col-sm-4 col-form-label">PIN</label>
        <div className="col-sm-8">
          { pin }
          { (util.in_array(+row.gpio__pin, this.state.selected_units)) &&
            <small className="text-danger">Этот PIN уже используется на другом датчике</small>
          }
        </div>
      </div>
      <div className="form-group">
        <label>Описание датчика</label>
        <div>
          <label>
            <input type="checkbox" checked={ row.gpio__format.is_default } onChange={this.device_gpio_format_update.bind(this, this.state.device_unit_id, 'is_default')} />
            <span> использовать значения по умолчанию</span>
          </label>
        </div>
        { row.gpio__format.is_default === false &&
        <div>
          <div className="form-group row">
            <label className="col-sm-4 col-form-label">название</label>
            <div className="col-sm-8">
              <input type="text" className="form-control form-control-sm" value={ row.gpio__format.title }
                     onChange={ this.device_gpio_format_update.bind(this, this.state.device_unit_id, 'title') }/>
            </div>
          </div>
          <div className="form-group row">
            <label className="col-sm-4 col-form-label">тип</label>
            <div className="col-sm-8">
              <select className="form-control form-control-sm" value={ row.gpio__format.type }
                      onChange={ this.device_gpio_format_update.bind(this, this.state.device_unit_id, 'type') }>
                { this.state.inputs.gpio_types }
              </select>
            </div>
          </div>
          <div className="form-group row">
            <label className="col-sm-4 col-form-label">тип диаграммы</label>
            <div className="col-sm-8">
              <select className="form-control form-control-sm" value={ row.gpio__format.chart }
                      onChange={ this.device_gpio_format_update.bind(this, this.state.device_unit_id, 'chart') }>
                { this.state.inputs.chart_types }
              </select>
            </div>
          </div>
          <div className="form-group row">
            <label className="col-sm-4 col-form-label">Кнопка управления</label>
            <div className="col-sm-8">
              { gpio_controls }
            </div>
          </div>
          <div className="form-group row">
            <label className="col-sm-4 col-form-label">Список возможных значений</label>
            <div className="col-sm-8">
              { row_values }
              <div>
                <small>Для указания диапозона значений, указывать в формате <code>-100..20</code> (от -100 до 20)</small>
              </div>
            </div>
          </div>
        </div>
        }
      </div>
    </div>;

    let clients_select_input_options = [];
    if ('clients' in this.props.appSettings) {
      for (let i = 0; i < this.props.appSettings.clients.length; i++) {
        let client = this.props.appSettings.clients[i];
        clients_select_input_options.push(<option value={client.id} key={client.id}>{client.name}</option>)
      }
    }


    return <div className="page-content container-fluid">
      <div className="row">
        <div className="col-md-6">
          <BGC title={ this.state.data.device.device_name } buttons={buttons}>
            <div className="form-group">
              <label>Название устройства</label>
              <div className="form-control bg-lightgray">{ this.state.data.device.device_name }</div>
            </div>
            <div className="form-group">
              <label>Адрес</label>
              <input type="text" className="form-control" value={ this.state.data.device.device_address } onChange={ this.device_property_update.bind(this, 'device_address') } />
            </div>
          </BGC>
          <BGC title="Настройка сетевого управления SNMP" collapsing={ true }>
            <div className="form-group">
              <label>IP snmp сервера (host)</label>
              <input type="text" 
                     className="form-control" 
                     value={ this.state.data.device.snmp_host } 
                     onChange={ this.device_property_update.bind(this, 'snmp_host') }
                     placeholder="192.168.1.1:161"
              />
            </div>
            <div className="row">
              <div className="col-md-6 form-group">
                <label>Сообщество (community)</label>
                <input type="text"
                       className="form-control"
                       value={ this.state.data.device.snmp_community }
                       onChange={ this.device_property_update.bind(this, 'snmp_community') }
                       placeholder="public"
                />
              </div>
              <div className="col-md-6 form-group">
                <label>Версия (version)</label>
                <select className="form-control" value={ this.state.data.device.snmp_version } onChange={ this.device_property_update.bind(this, 'snmp_version') }>
                  <option value="">-- не указано --</option>
                  <option value="2c">2c</option>
                </select>
              </div>
            </div>
            <div className="row">
              <div className="col-md-6 form-group">
                <label>Имя пользователя</label>
                <input type="text"
                       className="form-control"
                       value={ this.state.data.device.snmp_user }
                       onChange={ this.device_property_update.bind(this, 'snmp_user') }
                       placeholder="если требуется авторизация"
                />
              </div>
              <div className="col-md-6 form-group">
                <label>Пароль</label>
                <input type="text"
                       className="form-control"
                       value={ this.state.data.device.snmp_password }
                       onChange={ this.device_property_update.bind(this, 'snmp_password') }
                       placeholder="если требуется авторизация"
                />
              </div>
            </div>
          </BGC>
        </div>
        
        <BGC title="" col="col-md-6">
          <div className="form-group">
            <label>Комментарий</label>
            <textarea className="form-control" rows="3" value={ this.state.data.device.device_comment } onChange={ this.device_property_update.bind(this, 'device_comment') } />
          </div>
          { this.state.data.is_client_change &&
            <div className="form-group">
              <label>Сменить владельца устройства</label>
              <select className="form-control" value={ this.state.data.device.device_client_id } onChange={ this.device_property_update.bind(this, 'device_client_id') } >
                { clients_select_input_options }
              </select>
              <button className="btn btn-warning btn-sm mt-3" onClick={ this.device_client_change }>Сменить</button>
            </div>
          }
        </BGC>
        
        <BGC title="Датчики" col="col-md-12">
          <div className="form-group">
            <select className="form-control form-control-sm mw-200" value={ this.state.device_unit_id } onChange={ this.data_property_update.bind(this, 'device_unit_id') } >
              { this.state.inputs.units }
            </select>
          </div>
          
          <hr/>
          
          <div className="row">
            { units }
          </div>
        </BGC>
      </div>

      <div className="col-md-12">
        <div className="form-group">
          <button className="btn btn-primary" onClick={ this.save }>Сохранить</button>
          <span>&nbsp;</span>
          { this.state.device_id > 0 &&
            <div className="d-inline">
              <button className="btn btn-warning" onClick={ this.device_reboot.bind(this) }>Применить</button>
              <span>&nbsp;</span>
              <Dialog ref={(el) => { this.dialog_dr = el }} />
            </div>
          }
          <span>&nbsp;</span>
          { this.state.request_send &&
            <small>обновляется...</small>
          }
        </div>
      </div>
     </div>
  }
}

const mapStateToProps = function(store) {
  return {
    appSettings:  store.appSettings
  };
};
export default connect(mapStateToProps)(PageDevicesEdit);