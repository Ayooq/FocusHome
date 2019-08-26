import React from "react";
import "moment";

class modalChart extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      chartStyle: {
        minWidth: "310px",
        height: "500px",
        margin: "0 auto"
      }
    };

    this.chart = null;
    this.chartBox = React.createRef();
  }

  componentWillUnmount() {
    if (this.chart) {
      this.chart.destroy();
      this.chart = null;
    }
  }

  render() {
    let data = this.props.data.data || [];

    if (this.chart) {
      this.chart.destroy();
      this.chart = null;
    }

    if (this.chartBox.current && data.length) {
      let chartSettings = {};
      switch (this.props.data.chartType) {
        case "area":
          chartSettings = {
            type: "area",
            plotOptions: {
              area: {
                stacking: "normal",
                step: "left"
              }
            },
            data
          };
          break;
        default:
          chartSettings = {
            type: "spline",
            plotOptions: {
              spline: {
                dataLabels: {
                  enabled: true
                }
              }
            },
            data
          };
      }

      this.chart = Highcharts.chart(this.props.id + "__chart", {
        chart: {
          type: chartSettings.type,
          zoomType: "x"
        },
        title: {
          text: this.props.data.title
        },
        subtitle: {
          text: this.props.data.subtitle
        },
        legend: {
          enabled: false
        },
        xAxis: {
          type: "datetime",
          labels: {
            format: "{value:%Y-%m-%e %H:%M:%S}"
          }
        },
        yAxis: {
          title: {
            text: "Значение"
          }
        },
        plotOptions: chartSettings.plotOptions,
        series: [
          {
            name:
              "[" + this.props.data.code + "]" + " " + this.props.data.title,
            data: chartSettings.data
          }
        ],
        time: {
          timezone: "Asia/Omsk"
        }
      });
      console.log("------------------------------");
      console.log(this.chart.series[0].data);
    }

    return (
      <div
        className="modal fade"
        id={this.props.id}
        tabIndex="-1"
        role="dialog"
        aria-labelledby="exampleModalLabel"
        aria-hidden="true"
      >
        <div className="modal-dialog modal-lg" role="document">
          <div className="modal-content">
            <div className="modal-header">
              <h5 className="modal-title">{this.props.title}</h5>
              <button
                type="button"
                className="close"
                data-dismiss="modal"
                aria-label="Close"
              >
                <span aria-hidden="true">&times;</span>
              </button>
            </div>
            <div className="modal-body">
              {/* {this.props.children} */}
              {/* {setTimeout(
                () =>
                  data.length === 0 && <span>Нет данных для отображения</span>,
                1000
              )} */}
              <div
                id={this.props.id + "__chart"}
                style={this.state.chartStyle}
                ref={this.chartBox}
              />
            </div>
            <div className="modal-footer">
              <button
                type="button"
                className="btn btn-secondary"
                data-dismiss="modal"
              >
                Закрыть
              </button>
              {/*<button type="button" className="btn btn-primary">Save changes</button>*/}
            </div>
          </div>
        </div>
      </div>
    );
  }
}

Number.defaultProps = {
  className: "form-control",
  id: "modal_1",
  title: "",
  data: []
};

export default modalChart;
