import ReactDOM from "react-dom";
import React from "react";
import { BrowserRouter as Router, Route, Switch, Link } from "react-router-dom";
import { connect } from "react-redux";
import store from "store.jsx";
import myFunc from "func.jsx";
import Paginate from "tags/paginate.jsx";
import InputText from "tags/inputs/text";
import InputNumber from "tags/inputs/number";
import InputSelect from "tags/inputs/select";
import BGC from "tags/bgc";
import ModalChart from "tags/modalChart";

class PageDevice extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      data: {},
      timer: 0,
      modal: {}
    };
  }

  componentDidMount() {
    this.updateList();
    let timer = setInterval(
      this.updateList.bind(this),
      monitoring_update_interval
    );
    this.setState({ timer });
  }

  componentWillUnmount() {
    clearTimeout(this.state.timer);
    this.setState({ timer: null });
  }

  updateList() {
    myFunc.get({
      url: "/monitoring/api?action=device_info",
      data: { deviceId: this.props.match.params.device_id },
      success: response => {
        this.setState({ data: response.data });
        //console.log(this.state.data);
      }
    });
  }

  handleChange(propertyName, value) {
    this.setState({ [propertyName]: value });
  }

  chartShow(deviceId, unitId, chartType) {
    this.setState({ modal: {} });
    myFunc.get({
      url: "/monitoring/api?action=chart",
      data: { deviceId, unitId, chartType },
      success: response => {
        console.log(response);
        let modal = {
          device: response.data.unit.device,
          title: response.data.unit.title,
          subtitle: "",
          code: response.data.unit.name,
          chartType: chartType,
          data: response.data.data
        };

        this.setState({ modal });
      }
    });
    $("#modal_chart").modal();
  }

  unitToggle(deviceId, unitId) {
    myFunc.get({
      url: "/monitoring/api?action=unit_toggle",
      data: { deviceId, unitId },
      success: response => {
        console.log(response.data);
      }
    });
  }

  render() {
    if (!("data" in this.state.data)) {
      return <div></div>;
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
        for (let key in this.state.data.data.status.temp) {
          let t = this.state.data.data.status.temp[key];
          let chartBtn = null;
          if (t.format.chart) {
            chartBtn = (
              <span
                className="float-right cur-p"
                onClick={this.chartShow.bind(
                  this,
                  this.state.data.data.id,
                  t.id,
                  t.format.chart
                )}
              >
                <i className="ti-bar-chart" />
              </span>
            );
          }

          temp.push(
            <div key={key} className={"p-20 mb-4 " + t.format.class}>
              <h6>
                {t.format.title} {chartBtn}
              </h6>
              <div>
                <h1 className="text-center">{t.format.title}</h1>
                <div className="text-right">{t.timestamp}</div>
              </div>
            </div>
          );
        }
      }

      if ("ins" in this.state.data.data.status) {
        for (let key in this.state.data.data.status.ins) {
          let t = this.state.data.data.status.ins[key];

          let chartBtn = null;
          if (t.format.chart) {
            chartBtn = (
              <span
                className="float-right cur-p"
                onClick={this.chartShow.bind(
                  this,
                  this.state.data.data.id,
                  t.id,
                  t.format.chart
                )}
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
                onClick={this.unitToggle.bind(
                  this,
                  this.state.data.data.id,
                  t.id
                )}
              >
                <i className="ti-power-off" />
              </span>
            );
          }

          ins.push(
            <div key={key} className="device-ins-block">
              <div className={"p-10 " + t.format.class}>
                <h6>
                  {t.format.title} {chartBtn}
                </h6>
                <div>
                  <h4 className="text-center">{t.format.title}</h4>
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
        for (let key in this.state.data.data.status.couts) {
          let t = this.state.data.data.status.couts[key];

          let chartBtn = null;
          if (t.format.chart) {
            chartBtn = (
              <span
                className="float-right cur-p"
                onClick={this.chartShow.bind(
                  this,
                  this.state.data.data.id,
                  t.unit,
                  t.format.chart
                )}
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
                onClick={this.unitToggle.bind(
                  this,
                  this.state.data.data.id,
                  t.id
                )}
              >
                <i className="ti-power-off" />
              </span>
            );
          }

          couts.push(
            <div key={key} className="device-ins-block">
              <div className={"p-10 " + t.format.class}>
                <h6>
                  {t.format.title} {chartBtn}
                </h6>
                <div>
                  <h4 className="text-center">{t.format.title}</h4>
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
          let ico = null;
          if (t.format.value === "online") {
            ico = <i className="ti-light-bulb" />;
          } else if (t.format.value === "offline") {
            ico = <i className="ti-light-bulb" />;
          } else {
            ico = <i className="ti-light-bulb" />;
          }
          networkStatus = (
            <span className={"text-uppercase " + t.format.class}>
              {ico} {t.timestamp} {t.format.title}
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
                <i className="c-orange-500 ti-home" />{" "}
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
            <BGC title="Температура">{temps}</BGC>
          </div>
        </div>

        <ModalChart
          id="modal-chart"
          title={this.state.modal.device}
          data={this.state.modal}
        >
          <div />
        </ModalChart>
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
