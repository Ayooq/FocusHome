import React from 'react';
import {MyFunc as util} from 'func.jsx';

class ModalSensor extends React.Component{
  constructor(props) {
    super(props);
    this.state = {
      data: null,
      selected_sensor: ''
    };
    
  }

  componentDidUpdate(prevProps) {
    if(this.props.addr!="") {
      if (prevProps.addr !== this.props.addr && this.props.device != 0) {
        this.update_list();
      }
    }
  }

  componentDidMount() {

  }

  componentWillUnmount() {
    /*clearTimeout(this.state.timer_id);
     this.setState({timer_id: null});*/
  }

  update_list(){
    util.get({
      'url': '/monitoring/api?action=get_snmp',
      'data': {'device_id': this.props.device, 'addr': this.props.addr, 'full': 1},
      'success' : response => {
        this.setState({data: response.data});
        // console.log(this.state.data);
      }
    });
  }

  render(){
   


    return <div className="modal fade" id={ this.props.id } tabIndex="-1" role="dialog" aria-labelledby="exampleModalLabel" aria-hidden="true">
      <div className="modal-dialog modal-lg" role="document">
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title">{ this.props.title }</h5>
            <button type="button" className="close" data-dismiss="modal" aria-label="Close">
              <span aria-hidden="true">&times;</span>
            </button>
          </div>
          <div className="modal-body">
            modal
            <p>{this.props.device}</p>
            <p>{this.props.addr}</p>
          </div>
          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" data-dismiss="modal">Закрыть</button>
            {/*<button type="button" className="btn btn-primary">Save changes</button>*/}
          </div>
        </div>
      </div>
    </div>
  }
}

ModalSensor.defaultProps = {
  device: 0,
  addr: '',
  title: "Подробно",
  id: "modal_1"
};

export default ModalSensor;