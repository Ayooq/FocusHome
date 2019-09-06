import React from 'react';
import {Link} from 'react-router-dom';

class BGC extends React.Component{
  constructor(props) {
    super(props);

    this.state = {
      collapsing: props.collapsing
    };

    this.bgc_collapse = this.bgc_collapse.bind(this);
  }

  bgc_collapse(){
    this.setState({collapsing: ! this.state.collapsing});
  }
  
  render(){
    let buttons = [];
    for(let i=0;i<this.props.buttons.length;i++){
      let ico = "";
      if (this.props.buttons[i].ico){
        ico = <span><i className={this.props.buttons[i].ico}></i>&nbsp;</span>;
      }
      if ('href' in this.props.buttons[i]){
        buttons.push(<Link key={i} to={this.props.buttons[i].href} title={this.props.buttons[i].title} className="btn btn-outline-primary btn-sm">{ico}{this.props.buttons[i].caption}</Link>)
      }else {
        buttons.push(<button key={i} title={this.props.buttons[i].title} onClick={this.props.buttons[i].onClick} className="btn btn-outline-primary btn-sm">{ico}{this.props.buttons[i].caption}</button>)
      }
    }
    
    if ( this.props.collapsing !== null){
      let ico = <i className={ this.state.collapsing?'ti-angle-down':'ti-angle-up' } />;
      buttons.push(<button key={buttons.length} title="свернуть/развернуть" onClick={ this.bgc_collapse } className="btn btn-outline-primary btn-sm">{ico}</button>)
    }
    
    
    return <div className={ this.props.col }>
      <div className="bgc-white bd bdrs-3 p-20 mB-20">
        <div>
          { this.props.title &&
            <h6 className="c-grey-900 float-left">{ this.props.title }</h6>
          }
          <div className="pull-right btn-group">{buttons}</div>
        </div>
        
        <div className="mT-30">
          <div className={ this.state.collapsing?'collapsing':'' }>
            {this.props.children}
          </div>
        </div>
      </div>
    </div>
  }
}

BGC.defaultProps = {
  title: "",
  buttons: [],
  col:"",
  collapsing: null
};

export default BGC;