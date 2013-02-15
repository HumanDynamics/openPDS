$(function () {

	window.AnswerByHourGraph = Backbone.View.extend({
		el: "#answerByHourGraphContainer",
		
		initialize: function () {
			_.bindAll(this, "render");
			
			this.activityByHourList = new AnswerListCollection();
			this.activityByHourList.bind("reset", this.render);
			this.activityByHourList.fetch();
		},
		
		render: function () {
			
			// It might not be necessary to remove the graph first. D3 seems to have some capability to change the data and have the graph update
			if (this.graph) {
				this.graph.remove();
			}
			var padding = [0,20,40,0];
			var w = $(this.el).width() - 50, h = 150;
			var pink = d3.rgb(238,98,226);
			var lightblue = d3.rgb(122,205,247);
			
			// For now, activity in an hour is calculated as the percentage of intervals that have some activity in them during that hour
			// We then multiply by 10 to get scores consistent with our social health radial scores
			var entries = this.activityByHourList.at(0).get("value").map(ANSWERLIST_VALUE_SELECTOR);
			var timestamps = this.activityByHourList.at(0).get("value").map(function (a) { return a.start * 1000; });
			// We're performing some simple smoothing on the data here to avoid the drastic peaks and valleys typical of activity data
			//entries = entries.map(function (a, i) { return 0.5 * a + (0.25 * entries[Math.max(0, i - 1)]) + (0.25 * entries[Math.min(entries.length - 1, i + 1)]); });

			// Add zero entries to the beginning and end of entries, with duplicate beginning and end timestamps associated with them
			// This closes up the data in case we want to do an area graph
			entries.push(0);
			entries.unshift(0);
			timestamps.push(timestamps[timestamps.length-1]);
			timestamps.unshift(timestamps[0]);
	
			var endDate = new Date();//entries[entries.length - 1].date);
			endDate.setTime(timestamps[timestamps.length - 1]);
			
			var startDate = new Date();
			startDate.setTime(timestamps[0]);
			//endDate = new Date(endDate.getUTCFullYear(), endDate.getUTCMonth(), endDate.getUTCDate() + 1);
			
			//this.x = d3.scale.linear().domain([0, entries.length]).range([0,w]);
			//this.x = d3.scale.ordinal().domain(d3.time.days(startDate, endDate)).rangeRoundBands([0,w], 0.1);
			this.x = d3.time.scale().domain([startDate, endDate]).rangeRound([0,w]);
			this.y = d3.scale.linear().range([0,h]);
			// In the event of all-zero data, use 1 as the max activity to avoid an incorrect graph
			// (a domain of [0,0] mapping to a range of [0, h], for instance, results in obvious problems)
			var maxActivity = Math.max(d3.max(entries), 1);
			
			this.y.domain([maxActivity, 0]);
			
			// Orienting the x axis as left so we can rotate it later for vertical labels
			//var xAxis = d3.svg.axis().scale(this.x).orient("left").ticks(entries.length);

			var xAxis = d3.svg.axis().scale(this.x).orient("left").ticks(d3.time.hours, 12);//.tickFormat(d3.time.format.utc("%b %e"));
			var yAxis = d3.svg.axis().scale(this.y).orient("left").ticks(10);			

			var me = this;
			var line = d3.svg.line()
				.x(function (d, i) { 
					var thisDate = new Date();
					thisDate.setTime(timestamps[i]);
					return me.x(thisDate);
				})
				.y(function (d) { 
					return me.y(d);
				})
				.interpolate("basis");

			this.graph = d3.select(this.el).append("svg").attr("class", "chart");
			
			// Append the x axis
			this.graph.append("g").attr("class", "axis").attr("transform", "translate(" + padding[2] + "," + (h + padding[1]) + ")rotate(-90 )").call(xAxis);
			
			// Append the y axis
			this.graph.append("g").attr("class", "axis").attr("transform", "translate(" + padding[2] + "," + padding[1] + ")").call(yAxis);

			this.graph.append("svg:path").attr("transform", "translate(" + padding[2] + "," + padding[1] + ")").attr("d", line(entries)).attr("fill", pink);
		}
	});
});
