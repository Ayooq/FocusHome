import React from 'react';

class InputText extends React.Component{
  constructor(props) {
    super(props);
    this.handleInputChange = this.handleInputChange.bind(this);
  }

  handleInputChange(event){
    let value = event.target.value;
    this.props.onChange(value);
  }
  
  render(){
    return <input type="text" className={this.props.className} value={this.props.value} onChange={this.handleInputChange} />
  }
}

InputText.defaultProps = {
  className: "form-control",
  onChange: (value)=>{""}
};

export default InputText;