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
import SNMPWidget from 'tags/snmp_widget';


class PageDeviceSNMPWidgetSetting extends React.Component{
  constructor(props) {
    super(props);

    this.state = {
      data: null,
      request_send: false,
      device: props.match.params.deviceID,
      addr: props.match.params.addr,
      widget: {
        addr: props.match.params.addr,
        comment: '',
        device_id: props.match.params.deviceID,
        interval: null,
        mib_name: null,
        mib_node_desc: null,
        mib_node_name: null,
        mib_value: null,
        title: '',
        updated: null,
        value: null,
        value_type: null
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

        let widget = this.state.widget;
        widget.mib_name = response.data.data.mib_name;
        widget.value_type = response.data.data.value_type;
        widget.value = response.data.data.value;
        widget.mib_value = response.data.data.mib_value;
        widget.updated = response.data.data.updated;
        widget.mib_node_desc = response.data.data.mib_node_desc;
        widget.interval = response.data.data.interval;
        widget.mib_node_name = response.data.data.mib_node_name;

        this.setState({widget: widget});
        
      }
    });
  }

  widget_title_change(event){
    this.setState({ widget: { ...this.state.widget, title: event.target.value.slice(0,40)} });
  }

  widget_comment_change(event){
    this.setState({ widget: { ...this.state.widget, comment: event.target.value.slice(0,255)} });
  }
  
  save(){
    this.setState({request_send: true});
    util.post({
      'url': '/api/monitoring?action=widget_add',
      'data': {'device_id':  this.state.device, 'addr': this.state.addr, 'widget': this.state.widget},
      'success' : response => {
        this.setState({request_send: false});
        this.setState({data: response.data});
      }
    });
  }

  remove(){
    this.setState({request_send: true});
    util.post({
      'url': '/api/monitoring?action=widget_remove',
      'data': {'device_id':  this.state.device, 'addr': this.state.addr},
      'success' : response => {
        this.setState({request_send: false});
        this.setState({data: response.data});
        // переадресация на /monitoring/device/1/snmp/.1.3.6.1.2.1.1.4.0/details
        this.props.history.push('/monitoring/device/'+this.state.device+'/snmp/'+this.state.addr+'/details');
      }
    });
  }

  render(){
    if (this.state.data === null){
      return <div>загрузка...</div>
    }

    let buttons = [
      {
        'caption':'виджеты',
        'title':'виджеты',
        'ico':'ti-ti-widget',
        'href': '/monitoring/device/'+this.state.device+'/snmp/widgets'
      },
      {
        'caption':'',
        'title':'обновить',
        'ico':'ti-reload',
        'onClick': this.update_list.bind(this)
      }
    ];

    
    return <div>
      <BGC title="Настройка виджета" buttons={buttons}>
        <div>
          <SNMPWidget data={ this.state.widget } />
        </div>

        <hr/>

        <div>
        
          <div className="form-group row">
            <label className="col-sm-2 col-form-label">Название</label>
            <div className="col-sm-10">
              <input type="text" className="form-control" value={ this.state.widget.title } onChange={ this.widget_title_change.bind(this) } />
            </div>
          </div>
          <div className="form-group row">
            <label className="col-sm-2 col-form-label">Комментарий</label>
            <div className="col-sm-10">
              <textarea rows="3" className="form-control" value={ this.state.widget.comment } onChange={ this.widget_comment_change.bind(this) } />
            </div>
          </div>
          
          <hr/>
         
          <div>
            <div className="">
              <button className="btn btn-primary" onClick={ this.save.bind(this) }>Сохранить</button>
              <button className="btn btn-default" onClick={ this.remove.bind(this) }>Удалить</button>
            </div>
            { this.state.request_send &&
              <div><small>обновляется...</small></div>
            }
          </div>
        
        </div>

      </BGC>

    </div>
  }
}


export default PageDeviceSNMPWidgetSetting;