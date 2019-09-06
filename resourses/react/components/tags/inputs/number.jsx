import React from 'react';

class InputNumber extends React.Component{
  constructor(props) {
    super(props);
    this.handleInputChange = this.handleInputChange.bind(this);
  }

  handleInputChange(event){
    let value = event.target.value;
    this.props.onChange(value);
  }
  
  render(){
    return <input type="number" min={this.props.min} max={this.props.max} className={this.props.className} value={this.props.value} onChange={this.handleInputChange} />
  }
}

InputNumber.defaultProps = {
  className: "form-control",
  onChange: (value)=>{""},
  min: "",
  max: ""
};

export default InputNumber;