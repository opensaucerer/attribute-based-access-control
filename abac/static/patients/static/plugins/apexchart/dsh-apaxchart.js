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
 series: [{ 
          name: 'HeartRate',
          data: [31, 40, 28, 51, 42, 109, 100]
        }, {
          name: 'PulseRate',
          data: [11, 32, 45, 32, 34, 52, 41]
        }],
          chart: {
          height: 250,
          type: 'area',
		  zoom: {
            enabled: false
          },
        },
        dataLabels: {
          enabled: false
        },
        stroke: {
          curve: 'smooth'
        },
        xaxis: {
          type: 'datetime',
          categories: ["2018-09-19T00:00:00.000Z", "2018-09-19T01:30:00.000Z", "2018-09-19T02:30:00.000Z", "2018-09-19T03:30:00.000Z", "2018-09-19T04:30:00.000Z", "2018-09-19T05:30:00.000Z", "2018-09-19T06:30:00.000Z"]
        },
		axisTicks: {
                    show: false,
                },
                axisBorder: {
                    show: false, 
                },
        tooltip: {
          x: {
            show: false
          },
        },
        };
  var columnChart = new ApexCharts(columnCtx, columnConfig);
  columnChart.render();
});
