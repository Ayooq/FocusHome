import React from "react";
import { Link } from "react-router-dom";
import { connect } from "react-redux";

import InputSelect from "../tags/inputs/select";
import BGC from "../tags/bgc";

import utils from "../../utils";

class PageIndex extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      data: {},
      clientId: 4,
      timer: null
    };

    this.handleChange = this.handleChange.bind(this);
    this.updateList = this.updateList.bind(this);
  }

  // Хуки.
  componentDidMount() {
    this.updateList();
    let timer = setInterval(this.updateList, updateInterval);
    this.setState({ timer });
  }

  componentWillUnmount() {
    clearTimeout(this.state.timer);
    this.setState({ timer: null });
  }

  // Обработчики.
  handleChange(propertyName, value) {
    this.setState({ [propertyName]: value });
  }

  // Пользовательские функции.
  updateList() {
    utils.get({
      url: "/monitoring/api",
      data: {
        action: "devices",
        client_id: this.state.clientId
      },

      success: response => {
        this.setState({ data: response.data });
      }
    });
  }

  render() {
    let devices = [];

    if ("data" in this.state.data) {
      let list = this.state.data.data;

      for (let key in list) {
        let networkStatus = null,
          temp = { cpu: null, ext: null },
          ins = [],
          couts = [],
          misc = [];

        if ("self" in list[key].status) {
          let t = list[key].status.self.self;

          networkStatus = (
            <span className={"text-uppercase " + t.format.class}>
              <i className="ti-light-bulb" />
            </span>
          );
        }

        if ("temp" in list[key].status) {
          for (let unit in list[key].status.temp) {
            let t = list[key].status.temp[unit];
            temp[unit] = (
              <div
                key={unit}
                className={"device-ins-block-small " + t.format.class}
                title={t.format.title}
              >
                {t.format.title}
              </div>
            );
          }
        }

        if ("ins" in list[key].status) {
          for (let unit in list[key].status.ins) {
            let t = list[key].status.ins[unit];
            ins.push(
              <div
                key={unit}
                className={"device-ins-block-small " + t.format.class}
                title={t.format.title}
              >
                {t.format.caption}
              </div>
            );
          }
        }

        if ("couts" in list[key].status) {
          for (let unit in list[key].status.couts) {
            let t = list[key].status.couts[unit];
            couts.push(
              <div
                key={unit}
                className={"device-ins-block-small " + t.format.class}
                title={t.format.title}
              >
                {t.format.caption}
              </div>
            );
          }
        }

        if ("misc" in list[key].status) {
          for (let unit in list[key].status.misc) {
            let t = list[key].status.misc[unit];
            misc.push(
              <div
                key={unit}
                className={"device-ins-block-small " + t.format.class}
                title={t.format.title}
              >
                {t.format.caption}
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
            <td>{temp.ext}</td>
            <td>{temp.cpu}</td>
            <td>
              <Link to={"/monitoring/device/" + list[key].id}>Управление</Link>
            </td>
          </tr>
        );

        devices.push(
          <tr key={"info_" + list[key].id} className="tr-device-info">
            <td colSpan="7">
              {ins} {couts} {misc}
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
        onClick: this.updateList
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
              {this.state.data.client_choice && (
                <InputSelect
                  list={clients}
                  value={this.state.clientId}
                  style={{
                    width: "150px",
                    display: "inline-block",
                    marginLeft: "1em"
                  }}
                  onChange={this.handleChange("clientId")}
                  label="Клиент"
                />
              )}
            </div>
            <table className="table">
              <thead>
                <tr>
                  <th width="40px" />
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
