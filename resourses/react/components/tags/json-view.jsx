import React from 'react';

class JsonView extends React.Component{
  constructor(props) {
    super(props);
  }

  render(){
    return <div>
      <pre>{ JSON.stringify(this.props.data, null, 2) }</pre>
    </div>
  }
}

JsonView.defaultProps = {
  data: null
};

export default JsonView;