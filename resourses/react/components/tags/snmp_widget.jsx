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


class SNMPWidget extends React.Component{
  constructor(props) {
    super(props);

    this.state = {

    }
  }


  render(){
    let w = null;
    if (this.props.data === null){
      w = {
        addr: null,
        comment: null,
        device_id: null,
        interval: null,
        mib_name: null,
        mib_node_desc: null,
        mib_node_name: null,
        mib_value: null,
        title: null,
        updated: null,
        value: null,
        value_type: null
      }
    }else{
      w = this.props.data;
    }

    let value = (w.mib_value)?w.mib_value+' ('+w.value+')':w.value;
    let updated = (w.interval)?w.updated+' (интервал: '+w.interval+' мин)':w.updated;

     return <div className="snmp-widget" key={ w.addr }>
      <div className="snmp-widget-body">
        <div className="snmp-widget-header">
          <p>
            <span><b>{ (w.title)?w.title:w.addr }</b></span>
            <span className="pull-right">
              <Link to={'/monitoring/device/'+w.device_id+'/snmp/'+w.addr+'/history'} className="" title="История"><i className="ti-book" /></Link>
              <Link to={'/monitoring/device/'+w.device_id+'/snmp/'+w.addr+'/widget'} className="" title="Настроить"><i className="ti-pencil-alt" /></Link>
            </span>
          </p>
        </div>
        <div className="snmp-widget-value ellipsis" title={value}>
          { value }
        </div>
        <div className="snmp-widget-desc">
          <div><span className="snmp-widget-desc-name">OID:</span>{ w.addr }</div>
          <div><span className="snmp-widget-desc-name">MIB:</span>{ w.mib_name }</div>
          <div className="ellipsis" title={w.mib_node_desc}><span className="snmp-widget-desc-name">Описание:</span>{ w.mib_node_desc }</div>
          <div className="ellipsis" title={w.comment}><span className="snmp-widget-desc-name">Коммент.:</span>{ w.comment }</div>
        </div>
        <div className="snmp-widget-footer">
          <span>{ updated }</span>
          <span className="pull-right">
            <Link to={'/monitoring/device/'+w.device_id+'/snmp/'+w.addr+'/details'} className="" title="Подробно"><small>подробно</small></Link>
          </span>
        </div>
      </div>
    </div>
  }
}

SNMPWidget.defaultProps = {
  data: null
};

export default SNMPWidget;