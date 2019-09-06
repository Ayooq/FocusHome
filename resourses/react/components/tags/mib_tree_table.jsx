import React from 'react';
import {MyFunc as util} from 'func.jsx';
import {Link} from 'react-router-dom';

let table = {}

class MIBtreeTable extends React.Component{
  constructor(props) {
    super(props);

    this.state = {
      data: null,
      device: props.device,
      addr: props.addr
    };
  }


  componentDidMount() {
    if (this.props.device in table){
      if (this.props.addr in table[this.props.device]){
        this.setState({data: table[this.props.device][this.props.addr]});
        table = {[this.props.device]: table[this.props.device]};
        return 0;
      }
    }
    this.update_list();
  }

  componentWillUnmount() {
    if (!(this.props.device in table)) {
      table[this.props.device] = {};
    }
    table[this.props.device][this.props.addr] = this.state.data;
  }

  update_list(){
    util.get({
      'url': '/api/monitoring?action=get_snmp_table',
      'data': {'device_id': this.props.device, 'addr': this.props.addr},
      'success' : response => {
        this.setState({data: response.data});
        //console.log(this.state.data);
      }
    });
  }

  render(){
    if (this.state.data === null){
      return <div>загрузка...</div>
    }

    let rows = [];
    for (let i=0; i<this.state.data.data.data.length;i++){
      let data_row = this.state.data.data.data[i];
      let row = [];
      for (let c=0;c<data_row.length;c++) {
        row.push(
          <td key={c}><div><Link to={'/monitoring/device/'+this.state.device+'/snmp/'+data_row[c][0]+'/details'} title="детали"><i className="ti-clipboard"></i></Link> { data_row[c][1] }</div></td>
        );
      }
      rows.push(<tr key={i}>{ row }</tr>);
    }
    
    let columns = [];
    let colLength = this.state.data.data.columns.length;
    for (let i=0; i<colLength;i++){
      let data_row = this.state.data.data.columns[i];
      let divClass = "ellipsis " + ((colLength>5)?"mw-100":"mw-150") ;
      
      columns.push(
        <td key={i} title={ data_row }><div className={ divClass }>{ data_row }</div></td>
      );
    }

    return <div className="table-responsive">
      <table className="table table-sm table-bordered">
        <thead className="text-dark">
          <tr>
            { columns }
          </tr>
        </thead>
        <tbody>
          { rows }
        </tbody>
      </table>
    </div>
  }
}

MIBtreeTable.defaultProps = {
  addr: {},
  device: 0
};

export default MIBtreeTable;