
window.handleTabChange = function (dimension, tabNum) {
	if (typeof android !== "undefined" && android.handleTabChange) {
		return android.handleTabChange(dimension, tabNum);
	}
	
	return true;
};

window.SocialHealthRadialView = Backbone.View.extend({
	el: "#triangle",
	
	initialize: function () {
		_.bindAll(this, "render");
		this.answerLists = new AnswerListCollection();
		this.answerLists.bind("reset", this.render);
		this.answerLists.fetch();
	},
	
	render: function () {
		if (this.graph) {
			this.graph.remove();
		}
		
		var data = this.answerLists.models[0].attributes["value"];
		// Note: we're subtracting an extra 48 from height to allow for the voting stars below it
		var viewHeight = window.innerHeight - 48;
		var width = window.innerWidth - 5,
		height = viewHeight - 5,
		maxRadius = Math.min(height, width) / 2 - 10;
		
		var z = d3.scale.category20();
		var whiteColor = d3.rgb(255,255,255);
		var redColor = d3.rgb(200,100,50);
		var newColor = d3.rgb(100,100,100);
		var pink = d3.rgb(238,98,226);
		var lightblue = d3.rgb(122,205,247);
		
		// Warning: the code below assumes that both average and user-specific sets are returned. If the user is not sharing, 
		// this will not be the case, and will need to be handled eventually.
		
		var averageData = _.filter(data, function (d) { return d.layer.indexOf("average") != -1; });
		var userData = _.filter(data, function (d) { return d.layer == "User";});

		// Handle the fact that our data is in different layers (ie; "User", "AverageLow", "AverageHigh")		
		// nest - essentially a "group by": gets us a mapping from a layer to the associated objects with that layer 
		var nest = d3.nest()
			.key(function(d) { return d.layer; });
		
		// stack essentially just computes the inner radius for consecutive layers such as the average low and high layers we have
		var stack = d3.layout.stack()
			.offset("zero")//.offset(function(d) { return d.y0; })
			.values(function(layer) { return layer.values; })
			.x(function(d, i) { return d.key; })
			.y(function(d) { return d.value; });
		
		var layers = (averageData != null && averageData.length > 0)? stack(nest.entries(averageData)):[];
		
		// Now that we got the stacking out of the way, we know the inner and outer radius for the average layer
		// To simplify things (and optimize a bit), let's throw out the averageLow and replace it with the user data
		layers[0] = {key: "User", values: userData };
		//layers = layers.splice(1,1);

		// Since all layers have the same dimensions, using the first one to pull the dimension names is fine
		var dimensions = _.pluck(layers[0].values, "key");
		var angle = d3.scale.ordinal().domain(dimensions).range([0,120,240])
		var radius = d3.scale.linear().domain([0,10]).range([0, maxRadius]);
		
		var line = d3.svg.line.radial()
			.interpolate("cardinal-closed")
			.angle(function(d,i) { return angle(d.key) * (Math.PI / 180.0); })
			.radius(function(d) { return radius(d.value); });

		// Setting up the radial area graph used by both the user and group values
		var area = d3.svg.area.radial()
			.interpolate("cardinal-closed")
			.angle(function(d, i) { return angle(d.key) * (Math.PI / 180.0); })
			.innerRadius(function(d) { return radius((d.y0)? d.y0: 0); })
			.outerRadius(function(d) { return radius(d.value); });

		var heightPadding = 20;
		var widthPadding = 2;
		var chartCenter = [ ((width / 2) + widthPadding), ((height / 2) + heightPadding)];
		// Adjusted height is essentially the center plus the height of the graph below the center (lines at 30 degree angles = 0.5 height)
		var adjustedHeight = chartCenter[1] * 1.5 + heightPadding;

		var chartSvg = d3.select("#radial_chart").append("svg")
			.attr("width", width)
			.attr("height", adjustedHeight);
		
		this.graph = chartSvg;

		// Draw the legend first - putting it up top and off to the side allows us to make the chart iteself - important on smallers screens
		
		var arrayOfTypes = ["User","Average"];
		var legendOffset = 35;
		var legendMarginLeft = 20;
		
		// Plot the bullet circles...
		var legend = chartSvg.append("g").attr("id", "legend");
			
		legend.selectAll("circle")
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
		legend.selectAll("a.legend_link")
			.data(arrayOfTypes) // Instruct to bind dataSet to text elements
			.enter().append("svg:a") // Append legend elements
			.append("text")
			.attr("text-anchor", "left")
			.attr("x", legendMarginLeft+15)
			.attr("y", function(d, i) { return legendOffset + i*24 - 10; })
			.attr("dx", 5)
			.attr("dy", "1em") // Controls padding to place text above bars
			.text(function(d, i) { return arrayOfTypes[i];})
			.style("color","white");
		
		// Center the chart itself on the page
		chartSvg = chartSvg.append("g")
			.attr("transform", "translate("+chartCenter[0]+","+chartCenter[1]+")");
	
		// Draw the layers
		chartSvg.selectAll(".layer")
			.data(layers)
			.enter().append("path")
			.attr("class", "layer")
			.attr("d", function(d) { return area(d.values); })
			.style("fill",
		        function(d, i) { return (d.key == "User")? pink:lightblue; })
			.style("opacity", 0.6);
			
		// create Axis		
		chartSvg.selectAll(".axis")
			.data(dimensions)
			.enter().append("g")
			.attr("class", "axis")
			.attr("transform", function(d, i) { return "rotate(" + angle(d) + ")"; })
			.on("click", function (d,i) { return handleTabChange(d,i); })
			.call(d3.svg.axis()
				.scale(radius.copy().range([-10, -maxRadius]))
				.ticks(5)
				.orient("left"))
				.append("text")
				.attr("y", -maxRadius - 10)
				.attr("text-anchor", "middle")
				.text(function(d) { return d; })
				.attr("style","font-size:16px;")
				.style("fill", function(d,i) {
					return "black"; // Insert means of determining unhealthy value here
				});
	
	}
});
