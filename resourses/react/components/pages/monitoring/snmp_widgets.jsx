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


class PageDeviceSNMPWidgets extends React.Component{
  constructor(props) {
    super(props);

    this.state = {
      data: null,
      request_send: false,
      device: props.match.params.deviceID
    }

  }

  componentDidMount() {
    this.update_list();
  }

  update_list(){
    this.setState({request_send: true});
    util.get({
      'url': '/api/monitoring?action=get_widgets',
      'data': {'device_id':  this.state.device},
      'success' : response => {
        this.setState({request_send: false});
        this.setState({data: response.data});
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

    let widgets = [];
    for (let i=0;i<this.state.data.data.length;i++){
      widgets.push(<SNMPWidget data={ this.state.data.data[i] } key={ this.state.data.data[i].addr } />)
    }

    
    return <div>
      <BGC title="Виджеты" buttons={buttons}>
        { widgets }
      </BGC>

    </div>
  }
}


export default PageDeviceSNMPWidgets;