$(function () {

window.AnswerList = Backbone.Model.extend({});

window.AnswerListCollection = Backbone.Collection.extend({
	model: AnswerList, 
	urlRoot: ANSWERLIST_API_URL
});

window.SocialHealthTriangleView = Backbone.View.extend({
	el: "#triangle",
	
	initialize: function () {
		answerLists = new AnswerListCollection();
		answerLists.bind("reset", this.render);
		answerLists.fetch();
	},
	
	render: function () {
		var stop = {};
		var data = answerLists.models[0].attributes["value"];

		var width = window.innerWidth - 5,
		height = window.innerHeight - (window.innerHeight * .35),
		outerRadius = height / 2 - 10,
		innerRadius = 120;

		var angle = d3.scale.linear()
		.range([0, 2 * Math.PI]);

		var radius = d3.scale.linear()
		.range([0, outerRadius]);

		var z = d3.scale.category20();
		var whiteColor = d3.rgb(255,255,255);
		var redColor = d3.rgb(200,100,50);
		var newColor = d3.rgb(100,100,100);
		var pink = d3.rgb(238,98,226);
		var lightblue = d3.rgb(122,205,247);

		var stack = d3.layout.stack()
			.offset("zero")//.offset(function(d) { return d.y0; })
			.values(function(d) { return d.values; })
			.x(function(d, i) { return i; })
			.y(function(d) { return d.value; });

		var replaceY0 = 0;

		var nest = d3.nest()
			.key(function(d) { return d.layer; });

		var line = d3.svg.line.radial()
			.interpolate("cardinal-closed")
			.angle(function(d,i) { return angle(i); })
			.radius(function(d) { return radius(replaceY0 + d.y); });


		var lowestValues = [];

		// parse response for lowest values
		for (i = 0; i < data.length; i++){
			if (data[i].layer == "averageLow"){
				lowestValues.push(data[i].value);
			}
		}

		var area = d3.svg.area.radial()
			.interpolate("cardinal-closed")
			.angle(function(d, i) { return angle(i); })
			//.innerRadius(function(d) { return radius(replaceY0); })
			.innerRadius(function(d, i) {
				if (d.layer == "User"){ // Hardcoded check right now, might change later...data tag must have USER in it...
					//  return radius(d.y);
					return 0;
				}
				else{
					return radius(lowestValues[i]);
				}
			})
			.outerRadius(function(d) { return radius(replaceY0 + d.y); });

		var heightPadding = 20;
		var widthPadding = 2;

		var svg = d3.select("#radial_chart").append("svg")
			.attr("width", width)
			.attr("height", height)
			.append("g")
			.attr("transform", "translate(" + ((width / 2) + widthPadding) + "," + ((height / 2) + heightPadding) + ")");


		var layers = stack(nest.entries(data));

		// Hardcoded swap for User and Average High
		var swapper = layers[2];
		layers[2] = layers[1];
		layers[1] = swapper;

		//var unhealthyArray = isHealthy(layers);

		//console.log("unhealthyArray: ",unhealthyArray);
		console.log("LAYERS : ",layers);


		// Extend the domain slightly to match the range of [0, 2π].
		angle.domain([0, layers.length]);
		//radius.domain([0, d3.max(data, function(d) {  return d.y + replaceY0; })]);
		// I think the numbers are out of 10, so it makes sense to make the radius domain [0, 10]
		radius.domain([0, 10]);

		// create Axis
		svg.selectAll(".axis")
		.data(d3.range(angle.domain()[1]))
		.enter().append("g")
		.attr("class", "axis")
		.attr("transform", function(d) { return "rotate(" + angle(d) * 180 / Math.PI + ")"; })
		.call(d3.svg.axis()
				.scale(radius.copy().range([-5, -outerRadius]))
				.ticks(5)
				.orient("left"))
				.append("text")
				.attr("y", 
						function (d) {
					if (window.innerWidth < 455){
						return -(window.innerHeight * .335);
					}
					else{
						return -(window.innerHeight * .335);
					}
				})
				.attr("dy", ".11em")
				.attr("text-anchor", "middle")
				.text(function(d, i) { return "label" + i; }) // insert means of getting at axis titles here
				.attr("style","font-size:16px;")
				.style("fill", function(d,i) {
					return "black"; // Insert means of determining unhealthy value here
				});

		svg.selectAll(".layer")
			.data(layers)
			.enter().append("path")
			.attr("class", "layer")
			.attr("d", function(d) { return area(d.values); })
			.style("fill",
				function(d, i) {
					if (i === 0){
						return pink;
					}
					else if (i == 1){
						return lightblue;
					}
					else
						return pink; 
				})
			.style("opacity",.6)
			.style("stroke",function(d, i) {
				if (i == 0)
					return whiteColor;
				else if (i == 2)
					return pink;
				else if (i == 1)
					return whiteColor;
			})
			.style("stroke-width", 0);


		// Create the svg drawing canvas...
		var canvas = d3.select("#radial_chart")
			.append("svg:svg")
			.attr("width", 300)//canvasWidth)
			.attr("height", 75)//canvasHeight);
			.attr("id","legend");

		legendOffset = 35;
		legendMarginLeft = 60;

		var arrayOfTypes = ["User","Average High-Low"];

		// Plot the bullet circles...
		canvas.selectAll("circle")
			.data(arrayOfTypes).enter().append("svg:circle") // Append circle elements
			.attr("cx", legendMarginLeft)// barsWidthTotal + legendBulletOffset)
			.attr("cy", function(d, i) { return legendOffset + i*25; } )
			.attr("stroke-width", ".5")
			.style("fill", function(d, i) { 
				if (i == 0)
					return pink;
				else
					return lightblue 
			}) // Bar fill color
			.attr("r", 10);

		// Create hyper linked text at right that acts as label key...
		canvas.selectAll("a.legend_link")
			.data(arrayOfTypes) // Instruct to bind dataSet to text elements
			.enter().append("svg:a") // Append legend elements
			.append("text")
			.attr("text-anchor", "left")
			.attr("x", legendMarginLeft+15)
			.attr("y", function(d, i) { return legendOffset + i*24 - 10; })
			.attr("dx", 5)
			.attr("dy", "1em") // Controls padding to place text above bars
			.text(function(d, i) { return arrayOfTypes[i];})
			.style("color","white")
		
	}
});

});