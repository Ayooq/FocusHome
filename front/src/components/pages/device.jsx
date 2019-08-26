import React from "react";
import { connect } from "react-redux";

import BGC from "../tags/bgc";
import ModalChart from "../tags/modalChart";

import utils from "../../utils";

class PageDevice extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      data: {},
      timer: 0,
      modal: {}
    };
  }

  // Хуки.
  componentDidMount() {
    this.updateList();
    let timer = setInterval(this.updateList.bind(this), updateInterval);
    this.setState({ timer });
  }

  componentWillUnmount() {
    clearTimeout(this.state.timer);
    // this.setState({ timer: null });
  }

  // Пользовательские функции.
  updateList() {
    utils.get({
      url: "/monitoring/api",
      data: {
        action: "device_info",
        device_id: this.props.match.params.id
      },

      success: response => {
        this.setState({ data: response.data });
      },
      error: error => {
        console.log(error);
      }
    });
  }

  chartShow(unitId, chartType) {
    this.setState({ modal: {} });
    utils.get({
      url: "/monitoring/api",
      data: {
        action: "chart",
        unit_id: unitId,
        chart_type: chartType
      },

      success: response => {
        let modal = {
          device: response.data.unit.device,
          title: response.data.unit.title,
          subtitle: "",
          code: response.data.unit.name,
          chartType,
          data: response.data.data
        };

        this.setState({ modal });
      },
      error: error => {
        console.log(error);
      }
    });
    $("#modal-chart").modal();
  }

  unitToggle(unitId) {
    utils.get({
      url: "/monitoring/api",
      data: {
        action: "unit_toggle",
        unit_id: unitId
      }
    });
  }

  render() {
    if (!("data" in this.state.data)) {
      return <div>Error!</div>;
    }

    let blockTitle = "";
    if ("title" in this.state.data) {
      blockTitle = this.state.data.title;
    }

    let buttons = [
      {
        title: "",
        title: "обновить",
        ico: "ti-reload",
        onClick: this.updateList.bind(this)
      }
    ];

    let temp = [];
    let ins = [];
    let couts = [];
    let networkStatus = null;

    if ("data" in this.state.data) {
      if ("temp" in this.state.data.data.status) {
        for (let unit in this.state.data.data.status.temp) {
          let t = this.state.data.data.status.temp[unit];
          let chartBtn = null;

          if (t.format.chart) {
            chartBtn = (
              <span
                className="float-right cur-p"
                onClick={this.chartShow.bind(this, t.id, t.format.chart)}
              >
                <i className="ti-bar-chart" />
              </span>
            );
          }

          temp.push(
            <div key={unit} className={"p-20 mb-4 " + t.format.class}>
              <h6>
                {t.format.title} {chartBtn}
              </h6>
              <div>
                <h1 className="text-center">{t.format.caption}</h1>
                <div className="text-right">{t.timestamp}</div>
              </div>
            </div>
          );
        }
      }

      if ("ins" in this.state.data.data.status) {
        for (let unit in this.state.data.data.status.ins) {
          let t = this.state.data.data.status.ins[unit];
          let chartBtn = null;

          if (t.format.chart) {
            chartBtn = (
              <span
                className="float-right cur-p"
                onClick={this.chartShow.bind(this, t.id, t.format.chart)}
              >
                <i className="ti-bar-chart" />
              </span>
            );
          }

          let ctrl = t.format.control || null;
          let ctrlBtn = null;

          if (ctrl === "toggle") {
            ctrlBtn = (
              <span
                className="float-left btn-toggle"
                onClick={this.unitToggle.bind(this, t.id)}
              >
                <i className="ti-power-off" />
              </span>
            );
          }

          ins.push(
            <div key={unit} className="device-ins-block">
              <div className={"p-10 " + t.format.class}>
                <h6>
                  {t.format.title} {chartBtn}
                </h6>
                <div>
                  <h4 className="text-center">{t.format.caption}</h4>
                  <div className="text-right">
                    {ctrlBtn} {t.timestamp}
                  </div>
                </div>
              </div>
            </div>
          );
        }
      }

      if ("couts" in this.state.data.data.status) {
        for (let unit in this.state.data.data.status.couts) {
          let t = this.state.data.data.status.couts[unit];
          let chartBtn = null;

          if (t.format.chart) {
            chartBtn = (
              <span
                className="float-right cur-p"
                onClick={this.chartShow.bind(this, t.id, t.format.chart)}
              >
                <i className="ti-bar-chart" />
              </span>
            );
          }

          let ctrl = t.format.control || null;
          let ctrlBtn = null;
          if (ctrl === "toggle") {
            ctrlBtn = (
              <span
                className="float-left btn-toggle"
                onClick={this.unitToggle.bind(this, t.id)}
              >
                <i className="ti-power-off" />
              </span>
            );
          }

          couts.push(
            <div key={unit} className="device-ins-block">
              <div className={"p-10 " + t.format.class}>
                <h6>
                  {t.format.title} {chartBtn}
                </h6>
                <div>
                  <h4 className="text-center">{t.format.caption}</h4>
                  <div className="text-right">
                    {ctrlBtn} {t.timestamp}
                  </div>
                </div>
              </div>
            </div>
          );
        }
      }

      if ("self" in this.state.data.data.status) {
        if ("self" in this.state.data.data.status.self) {
          let t = this.state.data.data.status.self.self;
          let ico = <i className="ti-light-bulb" />;

          networkStatus = (
            <span className={"text-uppercase " + t.format.class}>
              {ico} {t.timestamp} {t.format.caption}
            </span>
          );
        }
      }
    }

    return (
      <div className="page-content container-fluid">
        <div className="row">
          <div className="col-md-8">
            <BGC title={blockTitle} buttons={buttons}>
              <div>
                <i className="c-orange-500 ti-home" />
                {this.state.data.data.address}
              </div>
              <div>{networkStatus}</div>
            </BGC>
            <BGC title="Датчики">
              <div>{ins}</div>
              <div>{couts}</div>
            </BGC>
          </div>
          <div className="col-md-4">
            <BGC title="Температура">{temp}</BGC>
          </div>
        </div>

        <ModalChart
          id="modal-chart"
          title={this.state.modal.device}
          data={this.state.modal}
        ></ModalChart>
      </div>
    );
  }
}

const mapStateToProps = function(store) {
  return {
    appSettings: store.appSettings
  };
};

export default connect(mapStateToProps)(PageDevice);
