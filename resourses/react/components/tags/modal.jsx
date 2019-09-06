import React from 'react';
import {MyFunc as util} from 'func.jsx';

class Dialog extends React.Component{
  constructor(props) {
    super(props);
    
    this.state = {
      ico: null,
      id: "modal_" + util.random(0,10000),
      title: null,
      size: '',                     // 'modal-lg', 'modal-sm'
      message: null,
      body: null,
      buttons: {
        okBtn: {
          title: 'OK',
          className: 'btn-primary',
          onClick: ()=> {
            this.hide();
          }
        }
      }
    };

  }

  componentDidUpdate(prevProps) {

  }

  componentDidMount() {}

  componentWillUnmount() {}

  hide(){
    $('#'+this.state.id).modal('hide');
  }
  
  show(kwargs){
    if ("size" in kwargs) {
      this.setState({'size': kwargs["size"]});
    }
    if ("title" in kwargs) {
      this.setState({'title': kwargs["title"]});
    }
    if ("buttons" in kwargs) {
      this.setState({'buttons': kwargs["buttons"]});
    }
    if ("message" in kwargs) {
      this.setState({'message': kwargs["message"]});
    }
    if ("ico" in kwargs) {
      this.setState({'ico': kwargs["ico"]});
    }
    if ("body" in kwargs) {
      this.setState({'body': kwargs["body"]});
    }
    
    $('#'+this.state.id).modal('show');
  }

  refresh(){
    
  }
  
  render(){

    let buttons = [];
    for (let i in this.state.buttons) {
      buttons.push(<button key={ i } type="button" onClick={ this.state.buttons[i].onClick } className={ 'btn btn-sm ' + this.state.buttons[i].className }>{ this.state.buttons[i].title }</button>)
    }
   
    return <div className="modal fade" id={ this.state.id } tabIndex="-1" role="dialog" aria-hidden="true">
      <div className={"modal-dialog " + this.state.size } role="document">
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title">
              { this.state.ico &&
                <span>{ this.state.ico }&nbsp;</span>
              }
              { this.state.title }
            </h5>
            <button type="button" className="close" data-dismiss="modal" aria-label="Close">
              <span aria-hidden="true">&times;</span>
            </button>
          </div>
          <div className="modal-body">
            { this.state.message &&
              <div className="text-dark">{ this.state.message }</div>
            }
            { this.props.children }
            { this.state.body }
          </div>
          <div className="modal-footer">
            { buttons }
          </div>
        </div>
      </div>
    </div>
  }
}

Dialog.defaultProps = {
  
};

export default Dialog;