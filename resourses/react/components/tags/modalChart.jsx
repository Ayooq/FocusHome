import React from 'react';
import {MyFunc as util} from 'func.jsx';

class modalChart extends React.Component{
  constructor(props) {
    super(props);
    this.state = {
      'chart_style': {
        minWidth: '310px',
        height: '500px',
        margin: '0 auto'
      },
      data: this.props.data,
      id: this.props.id || "modal_" + util.random(0,10000)
    };
    
    this.chart = null;
    this.chartBox = React.createRef();
    //this.handleInputChange = this.handleInputChange.bind(this);
  }

  componentWillReceiveProps(nextProps) {
    if ( nextProps.data.date != this.state.data.date ) {
      this.setState({data: nextProps.data});
    }
  }

  shouldComponentUpdate(nextProps) {
    return nextProps.data.date != this.state.data.date;
  }
  
  componentWillUnmount()
  {
    if ( this.chart ){
      this.chart.destroy();
      this.chart = null;
    }
  }

  render(){
    let data = this.state.data.data || [];
    
    if ( this.chart ){
      this.chart.destroy();
      this.chart = null;
    }

    if (this.chartBox.current && data.length) {
      let chartSettings = {};
      switch(this.state.data.chartType) {
        // default: this.props.data.chartType === "line"
        case 'area':
          chartSettings = {
            type: "area",
            plotOptions: {
              area: {
                stacking: "normal",
                step: "left"
              }
            },
            data: data//data.map(e => e[1])
          };
          break;
        default:
          chartSettings = {
            type: "spline",
            plotOptions: {
              line: {
                dataLabels: {
                  enabled: false
                },
                enableMouseTracking: true
              }
            },
            data: data
          };
      }

      this.chart = Highcharts.chart(this.props.id + "__chart", {
        chart: {
          type: chartSettings.type,
          zoomType: 'x'
        },
        title: {
          text: this.state.data.unit_code || this.state.data.title
        },
        subtitle: {
          text: this.state.data.subtitle
        },
        legend: {
          enabled: false
        },
        xAxis: {
          type: 'datetime',
          labels: {
            //format: '{value:%Y-%m-%e %H:%M:%S}',
            format: '{value:%Y-%m-%e}',
            rotation: -90
          }
        },
        yAxis: {
          title: {
            text: 'Значение'
          }
        },
        plotOptions: chartSettings.plotOptions,
        series: [{
          name: '['+this.state.data.unit_code+']'+' '+this.state.data.title,
          data: chartSettings.data,
        }],
        time:{
          timezoneOffset: -60*3
          //useUTC: false
        }
      });
    }


    return <div className="modal fade" id={ this.props.id } tabIndex="-1" role="dialog" aria-labelledby="exampleModalLabel" aria-hidden="true">
      <div className="modal-dialog modal-lg" role="document">
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title">{ this.props.title }</h5>
            <button type="button" className="close" data-dismiss="modal" aria-label="Close">
              <span aria-hidden="true">&times;</span>
            </button>
          </div>
          <div className="modal-body">
            {this.props.children}
            { data.length == 0 &&
              <span>Нет данных для отображения</span>
            }
            <div id={ this.props.id + "__chart" } style={ this.state.chart_style } ref={this.chartBox}></div>
          </div>
          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" data-dismiss="modal">Закрыть</button>
            {/*<button type="button" className="btn btn-primary">Save changes</button>*/}
          </div>
        </div>
      </div>
    </div>
  }
}

modalChart.defaultProps = {
  title: "",
  data: {date: null},
  id: null
};

export default modalChart;