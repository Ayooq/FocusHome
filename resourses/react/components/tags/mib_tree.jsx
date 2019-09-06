import React from 'react';
import MIBtreeSensors from 'tags/mib_tree_sensors';
import MIBtreeTable from 'tags/mib_tree_table';

class MIBtree extends React.Component{
  constructor(props) {
    super(props);

    this.state = {
      data: 0
    };
  }

  componentDidMount() {
    // console.log(this.props);
  }

  componentWillUnmount() {
    /*clearTimeout(this.state.timer_id);
     this.setState({timer_id: null});*/
  }
  
  tree_toogle(key){
    if ( this.props.tree[key].is_open == 1){
      this.props.tree[key].is_open = 0;
    }else{
      this.props.tree[key].is_open = 1;
    }
    this.setState({data: 0});
  }

  render(){

    let rows = [];
    for(let key in this.props.tree){
      if (key != "mib" && key != "sensors" && key != "is_open") {
        let nextTree = null;
        let icoCollapseClass = "ti-plus";
        
        if (~key.indexOf('Table')){
          icoCollapseClass = "ti-layout-grid2";
        }else if (this.props.tree[key].sensors > 0){
          icoCollapseClass = "ti-layout-list-thumb-alt";
        }

        if(this.props.tree[key].is_open == 1){
          icoCollapseClass = "ti-minus"
          if( this.props.tree[key].sensors > 0){
            nextTree = <div><MIBtreeSensors addr={ this.props.tree[key]["mib"] } device={ this.props.device } /></div>
          }else if (~key.indexOf('Table')){
            nextTree = <div><MIBtreeTable addr={ this.props.tree[key]["mib"] } device={ this.props.device } /></div>
          }else{
            nextTree = <MIBtree tree={  this.props.tree[key] } device={ this.props.device } />
          }
        }

        rows.push(<div key={key}>
            <div onClick={ this.tree_toogle.bind(this, key) }><i className={ 'text-primary '+icoCollapseClass }></i> <span className="text-dark">{key}</span></div>
            <div>{ nextTree }</div>
        </div>)
      }
    }
    
    
    return <div style={{paddingLeft: '10px'}}>
      { rows }
    </div>
  }
}

MIBtree.defaultProps = {
  tree: {},
  device: 0
};

export default MIBtree;