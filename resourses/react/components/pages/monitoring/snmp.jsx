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
import MIBtree from 'tags/mib_tree';
import SensorInfo from 'tags/snmp_sensor_info';
import Dialog from 'tags/modal';

let tree = {};

class PageDevice extends React.Component{
  constructor(props) {
    super(props);
    
    this.state = { 
      data: null,
      device: props.match.params.deviceID
    };

  }

  componentDidMount() {
    if (this.state.device in tree) {
      this.setState({data: tree[this.state.device]});
      tree = {};
      return 0;
    }
    this.update_list();
  }

  componentWillUnmount() {
    tree[this.state.device] = this.state.data;
  }

  update_list(){
    util.get({
      'url': '/api/monitoring?action=get_snmp',
      'data': {'device_id': this.props.match.params.deviceID},
      'success' : response => {
        this.setState({data: response.data});
        //console.log(this.state.data);
      }
    });
  }

  snmp_reload(){
    this.dialog_sr.show({
      ico: <i className="ti-info-alt"></i>,
      title: 'Обновление конфиграции',
      message: <p>Отправить запрос на удаленное устройство для обновления конфигруции?<br/>Это может занять несколько минут</p>,
      buttons: {
        cancelBtn: {
          title: 'Отмена',
          className: 'btn-default',
          onClick: (e)=> {
            this.dialog_sr.hide();
          }
        },
        okBtn: {
          title: 'Отправить',
          className: 'btn-primary',
          onClick: ()=> {
            this.dialog_sr.hide();
            util.get({
              'url': '/api/monitoring?action=snmp_get_image',
              'data': {'device_id': this.state.device, 'addr': this.state.addr},
              'success' : response => {
                this.dialog_sr.show({
                  ico: <i className="ti-info-alt"></i>,
                  title: 'Обновление конфиграции',
                  message: <p>{ response.data.status }</p>,
                  buttons: {
                    cancelBtn: {
                      title: 'Закрыть',
                      className: 'btn-default',
                      onClick: (e)=> {
                        this.dialog_sr.hide();
                      }
                    }
                  }
                });
              }
            });
          }
        }
      }
    });
  }

  navigation(path){
    browserHistory.push('/monitoring/device/'+this.state.device+'/snmp/'+path);
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
      },
      {
        'caption':'виджеты',
        'title':'виджеты',
        'ico':'ti-ti-widget',
        'href': '/monitoring/device/'+this.state.device+'/snmp/widgets'
      },
      {
        'caption':'обновить конфигурацию',
        'title':'обновить конфигурацию',
        'ico':'ti-download',
        'onClick': this.snmp_reload.bind(this)
      }
    ];
    
    return <div className="page-content container-fluid">
      <div className="row">
        <div className="col-md-12">
          <BGC title="Объекты" buttons={buttons}>
            <MIBtree tree={ this.state.data.data } device={ this.props.match.params.deviceID } />
          </BGC>
        </div>
      </div>

      <Dialog ref={(el) => { this.dialog_sr = el }}></Dialog>

     </div>
  }
}

const mapStateToProps = function(store) {
  return {
    appSettings:  store.appSettings
  };
};

export default connect(mapStateToProps)(PageDevice);