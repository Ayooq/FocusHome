import React from 'react';

class BGC extends React.Component{
  constructor(props) {
    super(props);
  }



  render(){
    let buttons = [];
    for(let key in this.props.buttons){
      let ico = "";
      if (this.props.buttons[key].ico){
        ico = <i className={'c-blue-500 '+this.props.buttons[key].ico}></i>;
      }
      buttons.push(<button key={key} title={this.props.buttons[key].title} onClick={this.props.buttons[key].onClick} className="btn btn-outline-primary btn-sm">{ico}{this.props.buttons[key].caption}</button>)
    }
    
    
    return <div className={ this.props.col }>
      <div className="bgc-white bd bdrs-3 p-20 mB-20">
        <div>
          { this.props.title &&
            <h6 className="c-grey-900 float-left">{ this.props.title }</h6>
          }
          <div className="float-right">{buttons}</div>
        </div>
        
        <div className="mT-30">
          {this.props.children}
        </div>
      </div>
    </div>
  }
}

BGC.defaultProps = {
  title: "",
  buttons: "",
  col:""
};

export default BGC;