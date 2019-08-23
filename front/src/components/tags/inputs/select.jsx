import React from "react";

class Select extends React.Component {
  constructor(props) {
    super(props);
    this.handleInputChange = this.handleInputChange.bind(this);
  }

  handleInputChange(event) {
    let value = event.target.value;
    this.props.onChange(value);
    event.preventDefault();
  }

  render() {
    let items = [];
    for (let key in this.props.list) {
      items.push(
        <option key={key} value={this.props.list[key].id}>
          {this.props.list[key].name}
        </option>
      );
    }

    return (
      <div>
        {this.props.label && <label>{this.props.label}</label>}
        <select
          className={this.props.className}
          onChange={this.handleInputChange}
          style={this.props.style}
        >
          {items}
        </select>
      </div>
    );
  }
}

Select.defaultProps = {
  className: "form-control",
  list: [],
  label: null,
  style: {},
  onChange: value => {
    return value;
  }
};

export default Select;
