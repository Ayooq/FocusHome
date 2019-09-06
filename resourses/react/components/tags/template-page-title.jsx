import React from 'react';
import store from 'store.jsx';
import { Provider, connect } from 'react-redux';


class PageTitle extends React.Component{
  constructor(props) {
    super(props);
    
    
  }

  render(){
    let page_title = this.props.pageInfo.title || "";
    
    return <div>
      <h5 className="c-grey-900 mT-10 mB-30">
        { this.props.pageInfo.request_send
          ? <i className="fa fa-refresh fa-spin fa-fw text-info" />
          : <i className="fa fa-spin fa-fw" />
        }
        <span>{ page_title }</span>
      </h5>
    </div>
  }
}

const mapStateToProps = function(store) {
  return {
    pageInfo:  store.pageInfo
  };
};

export default connect(mapStateToProps)(PageTitle);