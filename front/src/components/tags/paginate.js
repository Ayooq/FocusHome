import React from "react";

class Paginate extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      currentPage: 1
    };
  }

  paginate(page) {
    console.log(this.state.currentPage, "->", page);
    if (page < 1 || page > this.props.data.lastPage) return false;
    this.setState(state => ((state.currentPage = page), state));
    //this.$emit('paginate');

    this.props.paginate(page);
  }

  prev(e) {
    e.preventDefault();
    if (this.state.currentPage < 2) return false;
    this.setState(
      state => ((state.currentPage = this.props.data.currentPage), state)
    );
    this.paginate(this.state.currentPage - 1);
  }

  next(e) {
    e.preventDefault();
    if (this.state.currentPage >= this.props.data.lastPage) return false;
    this.setState(
      state => ((state.currentPage = this.props.data.currentPage), state)
    );
    this.paginate(this.state.currentPage + 1);
  }

  pagesNumber() {
    if (this.props.data.lastPage < 2) return [];

    let offset = 2;
    let from = this.props.data.currentPage - offset;
    if (from < 1) {
      from = 1;
    }
    let to = from + offset * 2;
    if (to >= this.props.data.lastPage) {
      to = this.props.data.lastPage;
    }

    let pagesArray = [];
    if (to - from < 8) from = to - offset * 2;
    if (from < 1) {
      from = 1;
    }
    for (let page = from; page <= to; page++) {
      pagesArray.push(page);
    }
    return pagesArray;
  }

  render() {
    if (this.props.data.lastPage < 2) {
      return null;
    }

    let pagesNumber = this.pagesNumber();

    return (
      <div className={this.props.className}>
        {this.props.data.total && (
          <div className="result-items">
            Показано:{" "}
            <b>
              {this.props.data.from}-{this.props.data.to}
            </b>{" "}
            из {this.props.data.total}
          </div>
        )}

        <div className="paginate">
          <div className="paginate-top-box">
            <ul aria-labelledby="paging-label">
              <li>
                <a
                  onClick={e => {
                    this.prev(e);
                  }}
                  className={
                    "list one_end item-prev " +
                    (this.state.currentPage < 2 ? "disabled" : "")
                  }
                  href="#"
                  rel="prev"
                  title="Previous"
                >
                  <span />
                  <span>
                    <i className="fa fa-caret-left" aria-hidden="true" />
                  </span>
                </a>
              </li>

              {pagesNumber.map((page, index) => (
                <li key={index}>
                  <a
                    href="#"
                    onClick={e => {
                      this.paginate(page, e);
                    }}
                    className={
                      "list " +
                      (page == this.state.currentPage ? "list_active" : "")
                    }
                  >
                    <span className="label" />
                    <span>{page}</span>
                  </a>
                </li>
              ))}

              <li>
                <a
                  onClick={e => {
                    this.next(e);
                  }}
                  className={
                    "list one_end next item-next " +
                    (this.state.currentPage >= this.props.data.lastPage
                      ? "disabled"
                      : "")
                  }
                  href="#"
                  rel="next"
                  title="Next"
                >
                  <span>
                    <i className="fa fa-caret-right" aria-hidden="true" />
                  </span>
                  <span />
                </a>
              </li>
            </ul>
          </div>
          paginate
        </div>
      </div>
    );
  }
}

Paginate.defaultProps = {
  data: {
    lastPage: 0,
    to: 0,
    from: 0,
    currentPage: 1,
    total: 0
  },
  paginate: () => {}
};

export default Paginate;
