'use strict';

$(document).ready(function() {

  /*
  // this function will generate output in this format
  // data = [ [timestamp, 23], ... ]
  */
  function generateData(baseval, count, yrange) {
    var i = 0;
    var series = [];
    while (i < count) {
      var x = Math.floor(Math.random() * (750 - 1 + 1)) + 1;;
      var y = Math.floor(Math.random() * (yrange.max - yrange.min + 1)) + yrange.min;
      var z = Math.floor(Math.random() * (75 - 15 + 1)) + 15;

      series.push([x, y, z]);
      baseval += 86400000;
      i++;
    }
    return series;
  }


  // Column chart
  var columnCtx = document.getElementById("dsh_chart_ex_column"),
  columnConfig = { 
  colors: ['#bc7ff7', '#4a4da0', '#fdaa88'],
  series: [{
          name: 'Old Patients',
          data: [44, 55, 57, 56, 61, 58, 63]
        }, {
          name: 'Total Visits',
          data: [76, 85, 101, 98, 87, 105, 91]
        }, {
          name: 'New Patients',
          data: [35, 41, 36, 26, 45, 48, 52]
        }],
          chart: {
          type: 'bar',
          height: 350
        },
        plotOptions: {
          bar: {
            horizontal: false,
            columnWidth: '55%',
            endingShape: 'rounded'
          },
        },
        dataLabels: {
          enabled: false
        },
        stroke: {
          show: true,
          width: 2,
          colors: ['transparent']
        },
        xaxis: {
          categories: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        },
        yaxis: {
          title: {
            text: '(patients)'
          }
        },
        fill: {
          opacity: 1
        },
        tooltip: {
          y: {
            formatter: function (val) {
              return   + val + " peoples"
            }
          }
        }
        };
  var columnChart = new ApexCharts(columnCtx, columnConfig);
  columnChart.render();
   
   
  
    //Pie Chart
		var pieCtx = document.getElementById("dsh_chart_ex_pie"),
			pieConfig = {
			colors: ['#323584'],
			 series: [86],
			  chart: {
			  height: 390,
			  type: 'radialBar',
			  offsetY: -10
			},
			  plotOptions: {
          radialBar: {
            startAngle: -135,
            endAngle: 135,
            dataLabels: {
              name: {
                fontSize: '16px',
                color: undefined,
                offsetY: 120
              },
              value: {
                offsetY: 76,
                fontSize: '22px',
                color: undefined,
                formatter: function (val) {
                  return val + "%";
                }
              }
            }
          }
        },
        fill: {
          type: 'gradient',
          gradient: { 
              shade: 'dark',
              shadeIntensity: 0.15,
              inverseColors: false,
              opacityFrom: 1,
              opacityTo: 1,
              stops: [0, 50, 65, 91]
          },
        },
        stroke: {
          dashArray: 4
        },
        labels: ['Reviews Avg'],
        };
		var pieChart = new ApexCharts(pieCtx, pieConfig);
		pieChart.render();
  
});
