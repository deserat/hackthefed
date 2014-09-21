$(document).ready( function() {

  /*These lines are all chart setup.  Pick and choose which chart features you want to utilize. */
  nv.addGraph(function() {
    var chart = nv.models.lineChart()
                  .margin({left: 100})  //Adjust chart margins to give the x-axis some breathing room.
                  .useInteractiveGuideline(false)  //We want nice looking tooltips and a guideline!
                  .transitionDuration(350)  //how fast do you want the lines to transition?
                  .showLegend(true)       //Show the legend, allowing users to turn on/off line series.
                  .showYAxis(true)        //Show the y-axis
                  .showXAxis(true)        //Show the x-axis

    chart.xAxis     //Chart x-axis settings
        .axisLabel('Congress')
        .tickFormat(d3.format(',r'))

    chart.yAxis     //Chart y-axis settings
        .axisLabel('Bills Produced')
        .tickFormat(d3.format(',r'));

    // Get Data
    var myData = getData()   

    // Make the Chart
    d3.select('svg#chart')    
        .datum(myData)         
        .call(chart);          

    //Update the chart when window resizes.
    nv.utils.windowResize(function() { chart.update() });

    return chart;
  });

  function getData() {

    hr = []
    s = []
    hjres = []
    hres = []
    sres = []
    sjres = []


    $.each( data, function( index, d ) {
      
        hr.push({ y : getProperty(d, 'hr' ), x : d.name } )
        s.push({ y : getProperty(d, 's' ), x : d.name } )
        hjres.push({ y : getProperty(d, 'hjres' ), x : d.name } )
        hres.push({ y : getProperty(d, 'hres' ), x : d.name } )
        sres.push({ y : getProperty(d, 'sres' ), x : d.name } )
        sjres.push({ y : getProperty(d, 'sjres' ), x : d.name } )
      
    });

    return [
      {
        values: hr,      //values - represents the array of {x,y} data points
        key: 'House Bill', //key  - the name of the series.
      },
      {
        values: s,
        key: 'Senate Bill',
      },
      {
        values: hjres,
        key: 'House Joint',
      },
      {
        values: hres,      
        key: 'House Resolution', 
      },
      {
        values: sres,
        key: 'Senate Resolution',
      },
      {
        values: sjres,
        key: 'Senate Joint',
      }
    ];
  }
})

