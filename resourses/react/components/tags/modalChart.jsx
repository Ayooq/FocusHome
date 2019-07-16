import React from 'react';

class modalChart extends React.Component{
  constructor(props) {
    super(props);
    this.state = {
      'chart_style': {
        minWidth: '310px',
        height: '500px',
        margin: '0 auto'
      }
    };
    
    this.chart = null;
    this.chartBox = React.createRef();
    //this.handleInputChange = this.handleInputChange.bind(this);
  }

  componentWillUnmount()
  {
    if ( this.chart ){
      this.chart.destroy();
      this.chart = null;
    }
  }
  // handleInputChange(event){
  //   let value = event.target.value;
  //   this.props.onChange(value);
  // }

  render(){
    let data = this.props.data.data || [];
    
    if ( this.chart ){
      this.chart.destroy();
      this.chart = null;
    }

    if (this.chartBox.current && data.length) {
      let chartSettings = {};
      switch(this.props.data.chartType) {
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
          text: this.props.data.title
        },
        subtitle: {
          text: this.props.data.subtitle
        },
        legend: {
          enabled: false
        },
        xAxis: {
          type: 'datetime',
          labels: {
            format: '{value:%Y-%m-%e %H:%M:%S}',
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
          name: '['+this.props.data.unit_code+']'+' '+this.props.data.title,
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
            { data.length === 0 &&
            <span>Нет данных для отображения</span>
            }
            <div id={ this.props.id + "__chart" } style={ this.state.chart_style } ref={this.chartBox}>
            </div>
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

Number.defaultProps = {
  className: "form-control",
  id: "modal_1",
  title: "",
  data: []
  //onChange: (value)=>{""}
};

export default modalChart;