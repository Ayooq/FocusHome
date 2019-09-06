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


class PageDeviceRoutines extends React.Component{
  constructor(props) {
    super(props);

    this.state = {
      data: null,
      request_send: false,
      input_name: '',
      device: props.match.params.deviceID
    }
  }

  componentDidMount() {
    this.update_list();
  }

  update_list(){
    this.setState({request_send: true});
    util.get({
      'url': '/api/monitoring?action=get_routines',
      'data': {'device_id':  this.state.device, 'name': this.state.input_name},
      'success' : response => {
        this.setState({request_send: false});
        this.setState({data: response.data});
      }
    });
  }

  input_name_update(e){
    let value = event.target.value;
    this.setState({input_name: value});
  }

  render(){
    if (this.state.data === null){
      return <div>загрузка...</div>
    }

    let buttons = [
      {
        'caption':'создать',
        'title':'создать',
        'ico':'ti-ti-widget',
        'href': '/monitoring/device/'+this.state.device+'/routines/add'
      },
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

        rows.push(<tr key={ row.id }>
          <td><Link to={ '/monitoring/device/'+this.state.device+'/routines/'+row.id }>{ row.name }</Link></td>
          <td><small>{ row.comment }</small></td>
        </tr>)
      }
    }



    return <div>
      <BGC title="Программы" buttons={buttons}>
        <div>
          <div>
            <div className="form-group">
              <div className="">
                <label className="col-form-label text-dark">Фильтр:</label>
                <span>&nbsp;</span>
                <input className="form-control form-control-sm d-inline mw-150" value={ this.state.input_name } onChange={ this.input_name_update.bind(this) } type="text" placeholder="название" />
                <span>&nbsp;</span>
                <button onClick={ this.update_list.bind(this) } className="btn btn-primary btn-sm"><i className="ti-reload"></i> найти</button>
                { this.state.request_send &&
                <small>&nbsp;обновляется...</small>
                }
              </div>
            </div>
          </div>
          <hr/>
          <div>
            <table className="table table-sm table-bordered">
              <thead>
              <tr className="text-dark">
                <td>Название</td>
                <td>Комментарий</td>
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


export default PageDeviceRoutines;