var endpoint = "http://dcaps-staging.media.mit.edu:8080/api/reality_analysis_service/get_reality_analysis_data?document_key=radialData&bearer_token=8e2f9e3129";
  d3.json(endpoint, function(json){

//  var data = json.radialData.data;
  var data = [.2,0,-.5];

  var meta = json.radialData.meta;
  var capitalMeta = [];
  for (i = 0; i < meta.length; i++){
      capitalMeta.push(capitaliseFirstLetter(meta[i]));
  }

  var width = window.innerWidth - 5,
      height = window.innerHeight - (window.innerHeight * .35),
    outerRadius = height / 2 - 10,
    innerRadius = 120;

  var width = 960,
      height = 500;

  var outerRadius = height / 2 - 10;

  var radius = d3.scale.linear()
      .domain([-1, 1])
      .range([0, outerRadius]);

  var angle = d3.scale.linear()
      .domain([0, data.length])
      .range([0, 2 * Math.PI]);

  var line = d3.svg.line.radial()
      .interpolate("cardinal-closed")
      .radius(radius)
      .angle(function(d, i) { return angle(i); });


  var pink = d3.rgb(238,98,226);

  var svg = d3.select("#radial_chart").append("svg")
      .datum(data)
      .attr("width", width)
      .attr("height", height)
    .append("g")
      .attr("transform", "translate(" + width / 2 + "," + ((height / 2) + 20) + ")");

      capitalMeta = ["Social","Activity","Focus"];
       meta = ["social","activity","focus"];
        unhealthyArray = ["social","Blahdf","blsah"];

    // create Axis
    svg.selectAll(".axis")
        .data(d3.range(angle.domain()[1]))
      .enter().append("g")
        .attr("class", "axis")
        .attr("transform", function(d) { return "rotate(" + angle(d) * 180 / Math.PI + ")"; })
      .call(d3.svg.axis()
        .scale(radius.copy().range([-5, -outerRadius]))
        .ticks(5)
        .tickSize(10,2,2)
        .orient("left"))
      .append("text")
        .attr("y", 
          function (d) {
            if (window.innerWidth < 455){
              return -(window.innerHeight * .32);
            }
            else{
              return -(window.innerHeight * .32);
            }
          })
        .attr("dy", ".71em")
        .attr("text-anchor", "middle")
        .text(function(d, i) { return capitalMeta[i]; })
        .attr("style","font-size:16px;")
        .style("fill", function(d,i) {
          if ($.inArray(meta[i], unhealthyArray) != -1) {
             return "red";
         } else {
             return "black";
          }
      });

  svg.append("path")
      .attr("class", "line")
      .style("stroke-width",7)
      .style("stroke",pink)
      .style("fill",pink)
      .style("opacity",.6)
      .attr("d", line);
});
