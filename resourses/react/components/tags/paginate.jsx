import React from 'react';

class Paginate extends React.Component{
  constructor(props) {
    super(props);
    console.log(this.props.data, props.data);
    this.state = {
      current_page: 1
    }
  }

  paginate(page) {
    console.log(this.state.current_page, '->', page);
    if (page < 1 || page > this.props.data.last_page) return false;
    this.setState(state => (state.current_page = page, state));
    //this.$emit('paginate');
    
    this.props.paginate(page);
  }

  prev(e) {
    e.preventDefault();
    if (this.state.current_page < 2) return false;
    this.setState(state => (state.current_page = this.props.data.current_page, state));
    this.paginate(this.state.current_page - 1);
  }

  next(e) {
    e.preventDefault();
    if (this.state.current_page >= this.props.data.last_page) return false;
    this.setState(state => (state.current_page = this.props.data.current_page, state));
    this.paginate(this.state.current_page + 1);
  }
  
  pagesNumber() {
    if(this.props.data.last_page<2) return [];

    let offset = 2;
    let from = this.props.data.current_page - offset;
    if (from < 1) {
      from = 1;
    }
    let to = from + (offset * 2);
    if (to >= this.props.data.last_page) {
      to = this.props.data.last_page;
    }

    let pagesArray = [];
    if( to-from<8 )from = to-offset * 2;
    if (from < 1) {
      from = 1;
    }
    for (let page = from; page <= to; page++) {
      pagesArray.push(page);
    }
    return pagesArray;
  }


  render(){
    if(this.props.data.last_page<2){
      return null
    }

    let pagesNumber = this.pagesNumber();

    return <div className={this.props.className}>
      { this.props.data.total &&
        <div className="result-items">Показано: <b>{ this.props.data.from }-{ this.props.data.to }</b> из { this.props.data.total }</div>
      }
      
      <div className="paginate">
        <div className="paginate-top-box">
          <ul aria-labelledby="paging-label">
            <li>
              <a onClick={(e)=>{this.prev(e)}} 
                className={'list one_end item-prev ' + (this.state.current_page<2?'disabled':'')} href="#" rel="prev" title="Previous">
                <span></span>
                <span><i className="fa fa-caret-left" aria-hidden="true"></i></span>
              </a>
            </li>

            {
              pagesNumber.map((page, index) =>
                <li key={index}>
                  <a href="#" onClick={(e)=>{this.paginate(page,e)}}
                    className={'list ' + (page == this.state.current_page?'list_active':'')}>
                    <span className="label"></span>
                    <span>{ page }</span>
                  </a>
                </li>
              )
            }
  
            <li>
              <a onClick={(e)=>{this.next(e)}} 
                className={'list one_end next item-next ' + (this.state.current_page>=this.props.data.last_page?'disabled':'')} href="#" rel="next" title="Next">
                <span><i className="fa fa-caret-right" aria-hidden="true"></i></span>
                <span></span>
              </a>
            </li>
          </ul>
        </div>
        paginate
      </div>
    </div>
  }
}

Paginate.defaultProps = {
  data: {
    last_page: 0,
    to: 0,
    from: 0,
    current_page: 1,
    total: 0
  },
  paginate: ()=>{}
};

export default Paginate;