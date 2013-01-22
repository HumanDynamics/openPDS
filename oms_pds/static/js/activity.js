$(function () {
	window.ActivityByHour = Backbone.Model.extend({});
	
	window.ActivityByHourCollection = Backbone.Collection.extend({
		model: ActivityByHour,
		urlRoot: ANSWERLIST_API_URL,
		
		fetch: function (options) {
			options || (options = {});
			options.data || (options.data = {});
			filterMapping = { "key": "ActivityByHour20130122" }
			options.data = _.extend(options.data, filterMapping);
			
			return Backbone.Collection.prototype.fetch.call(this,options);
		}
	});
	
	window.ActivityByHourGraph = Backbone.View.extend({
		el: "#activityByHourGraphContainer",
		
		initialize: function () {
			_.bindAll(this, "render");
			
			this.activityByHourList = new ActivityByHourCollection();
			this.activityByHourList.bind("reset", this.render);
		},
		
		render: function () {
			
			// It might not be necessary to remove the graph first. D3 seems to have some capability to change the data and have the graph update
			if (this.graph) {
				this.graph.remove();
			}
			var padding = [0,20,30,0];
			var w = $(this.el).width() - 50, h = 150;
			
			var entries = this.activityByHourList.at(0).get("value").map(function (a) { return (a.total > 0)? (a.low + a.high) / a.total : 0});
			
			//var startDate = new Date(this.fromDate);
			//var endDate = new Date(this.toDate);//entries[entries.length - 1].date);
			
			//startDate = new Date(startDate.getUTCFullYear(), startDate.getUTCMonth(), startDate.getUTCDate());
			//endDate = new Date(endDate.getUTCFullYear(), endDate.getUTCMonth(), endDate.getUTCDate() + 1);
			
			this.x = d3.scale.linear().domain([0, entries.length]).range([0,w]);
			this.y = d3.scale.linear().range([0,h]);
			var maxActivity = d3.max(entries);
			
			this.y.domain([maxActivity, 0]);
			
			// Orienting the x axis as left so we can rotate it later for vertical labels
			var xAxis = d3.svg.axis().scale(this.x).orient("left").ticks(5).tickFormat(d3.time.format.utc("%b %e"));
			var yAxis = d3.svg.axis().scale(this.y).orient("left").ticks(10);			
			
			this.graph = d3.select(this.el).append("svg").attr("class", "chart")
			
			// Append the x axis
			this.graph.append("g").attr("class", "axis").attr("transform", "translate(" + padding[2] + "," + (h + padding[1]) + ")rotate(-90 )").call(xAxis);
			
			// Append the y axis
			this.graph.append("g").attr("class", "axis").attr("transform", "translate(" + padding[2] + "," + padding[1] + ")").call(yAxis);

			// Note: a bit of a hack below. D3 dates are in the current timezone at midnight.			
			var me = this;
			
			this.graph.selectAll("rect").data(entries).enter()
				.append("rect")
				.attr("transform", "translate(" + padding[2] + "," + padding[1] + ")")
				.attr("x", function (d, i) { 
					return me.x(i) - 0.5;
				})
				.attr("y", function (d) { 
					return me.y(d) - 0.5;
				})
				.attr("width", 20)
				.attr("height", function (d) { return h - me.y(d); });
		}
	});
});