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
  ;

  chart.xAxis     //Chart x-axis settings
      .axisLabel('Congress')
      .tickFormat(d3.format(',r'));

  chart.yAxis     //Chart y-axis settings
      .axisLabel('Bills Produced')
      .tickFormat(d3.format(',r'));

  /* Done setting the chart up? Time to render it!*/
  var myData = getData()   //You need data...
  console.log(myData)

  d3.select('svg#chart')    //Select the <svg> element you want to render the chart in.   
      .datum(myData)         //Populate the <svg> element with chart data...
      .call(chart);          //Finally, render the chart!

  //Update the chart when window resizes.
  nv.utils.windowResize(function() { chart.update() });

  console.log(chart.hasData())
  return chart;
});

function getData() {

  console.log( "getting data ")
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


/**************************************
 * Simple test data generator
 */
function sinAndCos() {
  var sin = [],sin2 = [],
      cos = [];

  //Data is represented as an array of {x,y} pairs.
  for (var i = 0; i < 100; i++) {
    sin.push({x: i, y: Math.sin(i/10)});
    sin2.push({x: i, y: Math.sin(i/10) *0.25 + 0.5});
    cos.push({x: i, y: .5 * Math.cos(i/10)});
  }

  //Line chart data should be sent as an array of series objects.
  return [
    {
      values: sin,      //values - represents the array of {x,y} data points
      key: 'Sine Wave', //key  - the name of the series.
      color: '#ff7f0e'  //color - optional: choose your own line color.
    },
    {
      values: cos,
      key: 'Cosine Wave',
      color: '#2ca02c'
    },
    {
      values: sin2,
      key: 'Another sine wave',
      color: '#7777ff',
      area: true      //area - set to true if you want this line to turn into a filled area chart.
    }
  ];
}




})

