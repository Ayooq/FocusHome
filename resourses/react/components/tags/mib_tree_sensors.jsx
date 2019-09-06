import React from 'react';
import {BrowserRouter as Router, Route, Switch, Link} from 'react-router-dom';
import {MyFunc as util} from 'func.jsx';

let sensors = {};

class MIBtreeSensors extends React.Component{
  constructor(props) {
    super(props);

    this.state = {
      data: null,
      selected_sensor: null
    };
  }

  componentDidMount() {
    if (this.props.device in sensors){
      if (this.props.addr in sensors[this.props.device]){
        this.setState({data: sensors[this.props.device][this.props.addr]});
        sensors = {[this.props.device]: sensors[this.props.device]};
        return 0;
      }
    }
    this.update_list();
  }

  componentWillUnmount() {
    if (!(this.props.device in sensors)) {
      sensors[this.props.device] = {};
    }
    sensors[this.props.device][this.props.addr] = this.state.data;
  }

  update_list(){
    util.get({
      'url': '/api/monitoring?action=get_snmp',
      'data': {'device_id': this.props.device, 'addr': this.props.addr},
      'success' : response => {
        this.setState({data: response.data});
      }
    });
  }



  render(){
    if (this.state.data === null){
      return <div>загрузка...</div>
    }

    let rows = [];
    for (let i=0; i<this.state.data.data.length;i++){
      let row = this.state.data.data[i];

      rows.push(
        <tr key={ row['addr'] }>
          <td>
            <div className="btn-group btn-group-sm" role="group">
              <Link to={'/monitoring/device/'+this.props.device+'/snmp/'+row['addr']+'/details'} title="детали"><i className="ti-clipboard"></i></Link>
            </div>
          </td>
          <td>{ row['addr'] }</td>
          <td>{ row['value_type'] }</td>
          <td>{ row['value'] }</td>
          <td>{ row['desc'] }</td>
        </tr>
      );
    }

    return <div>
      <table className="table table-sm table-bordered">
        <thead className="text-dark">
          <tr>
            <td></td>
            <td>Адрес</td>
            <td>Тип</td>
            <td>Значение</td>
            <td>Описание</td>
          </tr>
        </thead>
        <tbody>
          {rows }
        </tbody>
      </table>
    </div>
  }
}

MIBtreeSensors.defaultProps = {
  addr: "",
  device: 0
};

export default MIBtreeSensors;