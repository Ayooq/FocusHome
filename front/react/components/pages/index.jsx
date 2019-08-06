import ReactDOM from "react-dom";
import React from "react";
import { BrowserRouter as Router, Route, Switch, Link } from "react-router-dom";
import { connect } from "react-redux";
import store from "store.jsx";
import { myFunc as util } from "func.jsx";
import Paginate from "tags/paginate.jsx";
import InputText from "tags/inputs/text";
import InputNumber from "tags/inputs/number";
import InputSelect from "tags/inputs/select";

import BGC from "tags/bgc";

class PageIndex extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      data: {},
      clientId: 0,
      timer: null
    };
  }

  componentDidMount() {
    this.updateList();
    let timer = setInterval(this.updateList.bind(this), update_interval);
    this.setState({ timer });
  }

  componentWillUnmount() {
    clearTimeout(this.state.timer);
    this.setState({ timer: null });
  }

  updateList() {
    util.get({
      url: "/monitoring/api?action=devices",
      data: { client_id: this.state.clientId },
      success: response => {
        this.setState({ data: response.data });
        //console.log(this.state.data.devices);
      }
    });
  }

  handleChange(propertyName, value) {
    this.setState({ [propertyName]: value });
  }

  render() {
    let devices = [];

    if ("data" in this.state.data) {
      let list = this.state.data.data;

      for (let key in list) {
        let networkStatus = null;
        let temp = { cpu: null, ext: null };
        let ins = [];
        let couts = [];

        if ("self" in list[key].status) {
          let t = list[key].status.self.self;
          let ico = null;

          if (t.format.value === "online") {
            ico = <i className="ti-light-bulb" />;
          } else if (t.format.value === "offline") {
            ico = <i className="ti-light-bulb" />;
          } else {
            ico = <i className="ti-light-bulb" />;
          }
          networkStatus = (
            <span className={"text-uppercase " + t.format.class}>{ico}</span>
          ); //<span className={ "text-uppercase " + t.format.class }>{ ico } { t.date } { t.format.title }</span>
        }

        if ("temp" in list[key].status) {
          for (let k in list[key].status.temp) {
            let t = list[key].status.temp[k];
            temp[k] = (
              <div
                key={k}
                className={"device-ins-block-small " + t.format.class}
                title={t.format.title}
              >
                {t.format.title}
              </div>
            );
          }
        }

        if ("ins" in list[key].status) {
          for (let k in list[key].status.ins) {
            let t = list[key].status.ins[k];
            ins.push(
              <div
                key={k}
                className={"device-ins-block-small " + t.format.class}
                title={t.format.title}
              >
                {t.format.title}
              </div>
            );
          }
        }

        if ("couts" in list[key].status) {
          for (let k in list[key].status.couts) {
            let t = list[key].status.couts[k];
            couts.push(
              <div
                key={k}
                className={"device-ins-block-small " + t.format.class}
                title={t.format.title}
              >
                {t.format.title}
              </div>
            );
          }
        }

        devices.push(
          <tr key={list[key].id} className="tr-device">
            <td>{networkStatus}</td>
            <td>{list[key].name}</td>
            <td>
              <small>{list[key].client_name}</small>
            </td>
            <td>{list[key].address}</td>
            <td>{temps.ext}</td>
            <td>{temps.cpu}</td>
            <td>
              <Link to={"/monitoring/device/" + list[key].id}>Управление</Link>
            </td>
          </tr>
        );

        devices.push(
          <tr key={"info_" + list[key].id} className="tr-device-info">
            <td colSpan="7">
              {ins} {couts}
            </td>
          </tr>
        );
      }
    }

    let blockTitle = "";

    if ("title" in this.state.data) {
      blockTitle = this.state.data.title;
    }

    let buttons = [
      {
        title: "обновить",
        ico: "ti-reload",
        onClick: this.updateList.bind(this)
      }
    ];

    let clients = [];

    if ("clients" in this.props.appSettings) {
      clients = this.props.appSettings.clients;
    }

    return (
      <div className="page-content container-fluid">
        <div className="row">
          <BGC title={blockTitle} buttons={buttons} col="col-md-12">
            <div className="mb-12">
              {this.state.data.client_editable && (
                <InputSelect
                  list={clients}
                  value={this.state.clientId}
                  style={{ width: "150px", display: "inline-block" }}
                  onChange={this.handleChange.bind(this, "clientId")}
                  label="Клиент"
                />
              )}
            </div>
            <table className="table">
              <thead>
                <tr>
                  <th width="40px" />
                  <th width="125px">UID</th>
                  <th>Наименование</th>
                  <th>Адрес</th>
                  <th width="95px">
                    Темп.
                    <br />
                    среды
                  </th>
                  <th width="95px">
                    Темп.
                    <br />
                    CPU
                  </th>
                  <th width="90px" />
                </tr>
              </thead>
              <tbody>{devices}</tbody>
            </table>
          </BGC>
        </div>
      </div>
    );
  }
}

const mapStateToProps = function(store) {
  return {
    appSettings: store.appSettings
  };
};

export default connect(mapStateToProps)(PageIndex);
