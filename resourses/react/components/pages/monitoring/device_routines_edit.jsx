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
import JsonView from 'tags/json-view';


class PageDeviceRoutines extends React.Component{
  constructor(props) {
    super(props);

    this.state = {
      data: null,
      units: [],
      compares: [],
      functions: [],
      modes: [],
      actions: [],
      request_send: false,
      input_name: '',
      device: props.match.params.deviceID,
      id: props.match.params.id || 0,

      inputs: {
        actions: [],
        units: [],
        functions: [],
        modes: []
      }
    };

    this.routine_save = this.routine_save.bind(this);
    this.routine_remove = this.routine_remove.bind(this);

  }

  componentDidMount() {
    this.update_list();
  }

  update_list(){
    this.setState({request_send: true});
    util.get({
      'url': '/api/monitoring?action=get_routines',
      'data': {'device_id':  this.state.device, 'id': this.state.id},
      'success' : response => {
        this.setState({request_send: false});
        

        this.setState({units: response.data.units});
        this.setState({compares: response.data.compares});
        this.setState({functions: response.data.functions});
        this.setState({modes: response.data.modes});
        this.setState({actions: response.data.actions});

        
        let actions = [];
        for(let i=0;i<response.data.actions.length;i++){
          let item = response.data.actions[i];
          actions.push(<option key={i} value={item.name}>{item.value}</option>)
        }
        this.setState({inputs: {...this.state.inputs, actions: actions}});

        let units = [];
        for(let i=0;i<response.data.units.length;i++){
          let item = response.data.units[i];
          units.push(<option key={i} value={item.name}>{item.title}</option>)
        }
        this.setState({inputs: {...this.state.inputs, units: units}});

        let functions = [];
        for(let key in response.data.functions){
          let item = response.data.functions[key];
          functions.push(<option key={key} value={item.name}>{item.name}</option>)
        }
        this.setState({inputs: {...this.state.inputs, functions: functions}});

        let modes = [];
        for(let i=0;i<response.data.modes.length;i++){
          let item = response.data.modes[i];
          modes.push(<option key={i} value={item.name}>{item.value}</option>)
        }
        this.setState({inputs: {...this.state.inputs, modes: modes}});

        let compares = [];
        for(let key in response.data.compares){
          let item = response.data.compares[key];
          compares.push(<option key={key} value={item.name}>{item.value}</option>)
        }
        this.setState({inputs: {...this.state.inputs, compares: compares}});

        this.setState({data: response.data.data});
      }
    });
  }

  data_name_update(event){
    let value = event.target.value;
    this.setState({
      data: {
        ...this.state.data,
        name: value.slice(0,255)
      }
    });
  }

  data_comment_update(event){
    let value = event.target.value;
    this.setState({
      data: {
        ...this.state.data,
        comment: value.slice(0,255)
      }
    });
  }

  routine_actions_add(){
    this.setState( (state) => {
      state.data.instruction.routine.actions = state.data.instruction.routine.actions.concat([{
        "action": (state.actions[0] || {"name": ""}).name,
        "unit": (state.units[0] || {"name": ""}).name,
        "value": ""
      }]);
      return state;
    });
  }

  routine_actions_remove(actionIndex, event){
    this.setState( (state) => {
      let actions = state.data.instruction.routine.actions;
      actions.splice(actionIndex, 1);
      state.data.instruction.routine.actions = actions;
      return state;
    });
  }

  routine_actions_action_update(actionIndex, event){
    let value = event.target.value;
    let firstFuncName = (this.state.functions[Object.keys(this.state.functions)[0]] || {"name": ""}).name;
    
    this.setState( (state) => {
      state.data.instruction.routine.actions[actionIndex].action = value;
      state.data.instruction.routine.actions[actionIndex].value = "";
      state.data.instruction.routine.actions[actionIndex].unit = "";
      state.data.instruction.routine.actions[actionIndex].function = firstFuncName;
      state.data.instruction.routine.actions[actionIndex].params = [];
      return state;
    });

    if (value === 'call' && firstFuncName != "") {
      this.routine_actions_function_update(actionIndex,{target:{value: firstFuncName}});
    }
  }

  routine_actions_unit_update(actionIndex, event){
    let value = event.target.value;
    this.setState( (state) => {
      state.data.instruction.routine.actions[actionIndex].unit = value;
      return state;
    });
  }

  routine_actions_value_update(actionIndex, event){
    let value = event.target.value;
    this.setState( (state) => {
      state.data.instruction.routine.actions[actionIndex].value = value;
      return state;
    });
  }

  routine_actions_function_update(actionIndex, event){
    let value = event.target.value;
    
    this.setState( (state) => {
      let params = [];
      for (let i=0;i<this.state.functions[value].params.length;i++){
        let p = this.state.functions[value].params[i];
        params.push({
          "name": p.name,
          "value": p.value
        });
      }
            
      state.data.instruction.routine.actions[actionIndex].function = value;
      state.data.instruction.routine.actions[actionIndex].params = params;
      
      return state;
    });
  }
  
  routine_actions_function_param_update(actionIndex, paramIndex, paramName, event){
    let value = event.target.value;
    this.setState( (state) => {
      state.data.instruction.routine.actions[actionIndex].params[paramIndex][paramName] = value;
      return state;
    });
  }
  
  
  routine_save(){
    this.setState({request_send: true});
    
    util.post({
      'url': '/api/monitoring?action=routine_save',
      'data': {
        'device_id':  this.state.device,
        'id': this.state.id,
        'instruction': this.state.data.instruction,
        'name': this.state.data.name,
        'comment': this.state.data.comment
      },
      'success' : response => {
        this.setState({request_send: false});
        if (this.state.id == 0){
          this.setState({id: response.data.data.id});
          this.props.history.push('/monitoring/device/'+this.state.device+'/routines/'+response.data.data.id);
        }else {
          this.setState({data: response.data.data});
        }
      }
    });
  }

  routine_remove(){
    this.setState({request_send: true});
    util.post({
      'url': '/api/monitoring?action=routine_remove',
      'data': {'device_id':  this.state.device, 'id': this.state.id},
      'success' : response => {
        this.setState({request_send: false});
        this.props.history.push('/monitoring/device/'+this.state.device+'/routines');
      }
    });
  }

  get_condition_string(group, key){
    if(typeof key === 'undefined'){
      key = 0;
    }
    let result = [];
  
    for (let i=0;i<group.length;i++){
      let elem_type = util.gettype(group[i]);
  
      if (elem_type === 'String'){
        result.push(<span className="text-danger" key={i}> { group[i] } </span>);
      }
      if (elem_type === 'Array'){
        result.push(<span key={i}>({this.get_condition_string(group[i])})</span>);
      }
      if (elem_type === 'Object'){
        let comp = this.state.compares[group[i].compare] || {"desc":""};
        result.push(<span key={i}><span className="text-primary">{group[i].unit}</span> <span className="text-dark">{comp.desc}</span> <span className="text-success">"{group[i].value}"</span></span>);
      }
    }
  
    return result;
  }
  
  get_function_string(){
    let lines = [];

    lines.push(<div key={'b_'+0}><span className="text-danger">IF</span> { this.get_condition_string(this.state.data.instruction.routine.conditions) } <span className="text-danger">THEN</span></div>);
    
    for(let i=0;i<this.state.data.instruction.routine.actions.length;i++){
      let a = this.state.data.instruction.routine.actions[i];
      if (a.action === 'setValue'){
        lines.push(<div key={'a_'+i}><span>&nbsp;&nbsp;&nbsp;&nbsp;</span><span className="text-primary">{a.unit}</span> = <span className="text-success">"{a.value}"</span>;</div>);
      }
      if (a.action === 'call') {
        let params = [];
        for (let p = 0; p < a.params.length; p++) {
          params.push(<span key={'a_'+i+'_'+p}>{a.params[p].name}="{a.params[p].value}" { (p<a.params.length-1)?' ,':'' }</span>);
        }
        lines.push(<div key={'a_'+i}><span>&nbsp;&nbsp;&nbsp;&nbsp;</span><span className="text-danger">call</span> <span className="text-success">{a.function}</span>({ params });</div>);
      }
    }

    lines.push(<div key={'b_'+1}><span className="text-danger">END IF;</span></div>);
    
    return lines;
  }

  render_condition_group_btn(group, conditionIndex, key /*, is_delete_btn, group, conditionIndex, key*/){
    return <small className="d-inline" key={key}>
      <span className="text-primary cur-p mr-3" onClick={ this.render_condition_group_add_group.bind(this, group, conditionIndex) }>+ группу</span>
      <span className="text-primary cur-p mr-3" onClick={ this.render_condition_group_add_condition.bind(this, group, conditionIndex) }><i className="ti-plus"></i> условие</span>
    </small>
  }

  render_condition_group_btn_delete(group, conditionIndex, key /*, is_delete_btn, group, conditionIndex, key*/){
    return <small className="d-inline" key={key}>
      <span className="text-danger cur-p mr-3" onClick={ this.render_condition_group_condition_remove.bind(this, group, conditionIndex) }><i className="ti-trash"></i></span>
    </small>
  }

  render_condition_group_add_condition(group, conditionIndex){
    let prevElem = group[conditionIndex-1] || '';
    let nextElem = group[conditionIndex] || '';

    group.splice(conditionIndex, 0, { 
      "unit": (this.state.units[0] || {"name": ""}).name, 
      "compare": (this.state.compares[Object.keys(this.state.compares)[0]] || {"name": ""}).name,
      "value": "0" }
    );

    if (util.gettype(prevElem) !== 'String'){
      group.splice(conditionIndex, 0, "and");
    }
    if (util.gettype(nextElem) !== 'String'){
      group.splice(conditionIndex+1, 0, "and");
    }
    this.forceUpdate();
  }

  render_condition_group_add_group(group, conditionIndex){
    let prevElem = group[conditionIndex-1] || '';
    let nextElem = group[conditionIndex] || '';

    group.splice(conditionIndex, 0, []);
    
    if (util.gettype(prevElem) !== 'String'){
      group.splice(conditionIndex, 0, "and");
    }
    if (util.gettype(nextElem) !== 'String'){
      group.splice(conditionIndex+1, 0, "and");
    }
    this.forceUpdate();
  }

  render_condition_group_condition_remove(group, conditionIndex){
    let prevElem = group[conditionIndex-1] || null;
    let nextElem = group[conditionIndex+1] || null;
    
    group.splice(conditionIndex, 1);

    if (util.gettype(prevElem) === 'String' && util.gettype(nextElem) === 'String'){
      group.splice(conditionIndex-1, 1);
    }

    if (util.gettype(prevElem) === 'String' && util.gettype(nextElem) === 'Null'){
      group.splice(conditionIndex-1, 1);
    }

    if (util.gettype(prevElem) === 'Null' && util.gettype(nextElem) === 'String'){
      group.splice(conditionIndex, 1);
    }
    
    
    this.forceUpdate();
  }

  render_select_modes(value, onChange){
    return <select className="form-control form-control-sm d-inline mw-100" value={ value } onChange={ onChange }>
      { this.state.inputs.modes }
    </select>
  }
  
  routine_actions_conditions_modes_update(group, index, event){
    group[index] = event.target.value;
    this.forceUpdate();
  }

  routine_actions_conditions_unit_update(group, index, event){
    group[index].unit = event.target.value;
    this.forceUpdate();
  }

  routine_actions_conditions_compare_update(group, index, event){
    group[index].compare = event.target.value;
    this.forceUpdate();
  }

  routine_actions_conditions_value_update(group, index, event){
    group[index].value = event.target.value;
    this.forceUpdate();
  }
  
  render_conditions_group(group, level, key){
    if (typeof level === 'undefined'){
      level = 0;
    }
    if (typeof key === 'undefined'){
      key = 0;
    }
    let subkey = 0;
    
    
    let elements = [];
    let d_style = {'marginLeft': level*30+'px'};

    if (group.length === 0){
      let btns = this.render_condition_group_btn(group, 0, 'gb_'+key+'_'+(subkey++));
      elements.push(<div key={ key+'_'+(subkey++) } style={d_style}><div className="text-info d-inline">&#60;пустая группа&#62;</div>{ btns }</div>);
    };

    if (level === 0){
      elements.push(<div key={'gb_'+key+'_'+(subkey++)}>{this.render_condition_group_btn>this.render_condition_group_btn(group, 0, 'gb_'+key+'_'+(subkey++))}</div>);
    }

    for (let i=0;i<group.length;i++){
      let elem_type = util.gettype(group[i]);
      if (elem_type === 'String'){
        elements.push(<div key={ key+'_'+(subkey++) } style={d_style}>
          <select className="form-control form-control-sm d-inline mw-100" value={ group[i] } onChange={ this.routine_actions_conditions_modes_update.bind(this, group, i) }>
            { this.state.inputs.modes }
          </select>
        </div>);
      }
      if (elem_type === 'Array'){
        elements.push(this.render_condition_group_btn_delete(group, i, 'gb_'+key+'_'+(subkey++)));
        elements = elements.concat(this.render_conditions_group(group[i], level + 1, key+'_'+(subkey++)));
      }
      if (elem_type === 'Object'){
        let btn = this.render_condition_group_btn_delete(group, i, 'gb_'+key+'_'+(subkey++));
        elements.push(this.render_condition_group_btn(group, i, 'gb_'+key+'_'+(subkey++)));
        
        elements.push(<div key={ key+'_'+(subkey++) } style={d_style}>
          <div className="text-success d-inline">
            <select className="form-control form-control-sm d-inline mw-200" value={ group[i].unit } onChange={ this.routine_actions_conditions_unit_update.bind(this, group, i) }>
              { this.state.inputs.units }
            </select>
            <span>&nbsp;</span>
            <select className="form-control form-control-sm d-inline mw-200" value={ group[i].compare } onChange={ this.routine_actions_conditions_compare_update.bind(this, group, i) }>
              { this.state.inputs.compares }
            </select>
            <span>&nbsp;</span>
            <input className="form-control form-control-sm d-inline mw-100" value={ group[i].value } onChange={ this.routine_actions_conditions_value_update.bind(this, group, i) } type="text" placeholder="" />
            <span>&nbsp;</span>
            { this.render_condition_group_btn_delete(group, i, 'gb_'+key+'_'+(subkey++)) }
          </div>
        </div>);
        
        elements.push(this.render_condition_group_btn(group, i+1, 'gb_'+key+'_'+(subkey++)));
      }
    }

    if (level === 0){
      elements.push(<div key={'gb_'+key+'_'+(subkey++)}>{this.render_condition_group_btn>this.render_condition_group_btn(group, group.length, 'gb_'+key+'_'+(subkey++))}</div>);
    }

    return elements;
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

    let actions = [];
    for(let i=0;i<this.state.data.instruction.routine.actions.length;i++){
      let item = this.state.data.instruction.routine.actions[i];
      let panel = null;

      if (item.action === "setValue"){
        panel = <div className="ml-4">
          <div className="d-inline mr-5">
            <label className="col-form-label text-dark label-caption">разъем:</label>
            <select className="form-control form-control-sm d-inline mw-200" value={ item.unit } onChange={ this.routine_actions_unit_update.bind(this, i) }>
              { this.state.inputs.units }
            </select>
          </div>
          <div className="d-inline">
            <label className="col-form-label text-dark label-caption">значение:</label>
            <input className="form-control form-control-sm d-inline mw-200" value={ item.value } onChange={ this.routine_actions_value_update.bind(this, i) } type="text" placeholder="" />
          </div>          
        </div>
      }
      if (item.action === "call"){
        let function_params = [];
        for (let p=0;p<item.params.length;p++){
          let param = item.params[p];

          function_params.push(<div key={ p }>
            <label className="col-form-label label-caption">{ param.name }</label>
            <input className="form-control form-control-sm d-inline mw-200" value={ param.value } onChange={ this.routine_actions_function_param_update.bind(this, i, p, "value") } type="text" placeholder="" />
            <small className="d-block">{ this.state.functions[item.function].params[p].desc }</small>
          </div>);
        }

        panel = <div className="ml-4">
          <div className="d-inline">
            <label className="col-form-label text-dark label-caption">функция:</label>
            <select className="form-control form-control-sm d-inline mw-200" value={ item.function } onChange={ this.routine_actions_function_update.bind(this, i) }>
              { this.state.inputs.functions }
            </select>
            <div><small>{ this.state.functions[item.function].comment }</small></div>
          </div>

          { function_params.length > 0 &&
            <div className="text-secondary">
              <div className="col-form-label">параметры:</div>
              {function_params}
            </div>
          }
        </div>
      }

      actions.push(<div key={ i } className="mb-20">
        <div className="row">
          <div className="col-md-2">
            <span className="text-primary cur-p mr-2" onClick={ this.routine_actions_remove.bind(this, i) }><i className="ti-trash"></i></span>
            <label className="col-form-label text-dark">тип действия:</label>
          </div>
          <div className="col-md-10">
            <select className="form-control form-control-sm d-inline mw-200" value={ item.action } onChange={ this.routine_actions_action_update.bind(this, i) }>
              { this.state.inputs.actions }
            </select>
          </div>
        </div>
        { panel }
      </div>);
    }

    return <div>
      <BGC title="Программа" buttons={buttons}>
        <div>
          <div className="form-group row">
            <label className="col-sm-2 col-form-label">Название</label>
            <div className="col-sm-10">
              <input type="text" className="form-control" value={ this.state.data.name } onChange={ this.data_name_update.bind(this) } />
            </div>
          </div>

          {/**/}

          <hr/>

          <h6 className="text-success">События</h6>
          <div className="routine-instruction-edit mb-20">
            { this.render_conditions_group(this.state.data.instruction.routine.conditions) }
          </div>
          
          <h6 className="text-success">Действия</h6>
          <div className="routine-instruction-edit">
            { actions }
            <div>
              <span className="text-primary cur-p" onClick={ this.routine_actions_add.bind(this) }><i className="ti-plus"></i> добавить действие</span>
            </div>
          </div>

          <hr/>
          
          {/**/}
          
          <div className="form-group row">
            <label className="col-sm-2 col-form-label">Комментарий</label>
            <div className="col-sm-10">
              <textarea rows="2" className="form-control" value={ this.state.data.comment } onChange={ this.data_comment_update.bind(this) } />
            </div>
          </div>
          
          <hr/>

          <div className="form-group">
            <button className="btn btn-primary" onClick={ this.routine_save.bind(this) }>Сохранить</button>
            <span>&nbsp;</span>
            <button className="btn btn-default" onClick={ this.routine_remove.bind(this) }>Удалить</button>
            <span>&nbsp;</span>
            { this.state.request_send &&
              <small>обновляется...</small>
            }
          </div>
        </div>

        {/*<JsonView data={ this.state.data.instruction.routine.conditions } />*/}
        
        <div>{ this.get_function_string() }</div>
      </BGC>

    </div>
  }
}


export default PageDeviceRoutines;