$(function () {

	window.AuditEntry = Backbone.Model.extend({
		
		initialize: function () {
			_.bindAll(this, "elementGroupId");
		},
		
		elementGroupId: function () {
			return "AuditEntryGroup" + this.attributes.timestamp_date.replace(/-/g, "");
		}
	});
	
	window.AuditEntryCollection = Backbone.Collection.extend({
		model: AuditEntry,
		urlRoot: AUDIT_API_URL,
		
		updateFilterMapping: function (key, value) {
			var oldValue = this.filterMapping[key];
			
			if (value && value !== "") {
				this.filterMapping[key] = value;
				this.filterMapping["offset"] = 0;
			} else if (this.filterMapping[key]) {
				delete this.filterMapping[key];
				this.filterMapping["offset"] = 0;
			}
			
			return oldValue != value;	
		},
		
		setFromDate: function (date) {			
			return this.updateFilterMapping("timestamp__gte", date);
		},
		
		setToDate: function (dateString) {
			// This isn't as simple as setting the start date - we need to search up to and including the
			// end of the end date. We achieve this by incrementing the day by one, and doing a non-inclusive
			// filter on that date.
			if (dateString && dateString !== "") {
				var date = new Date(dateString);
				date.setDate(date.getUTCDate() + 1);			
				var toDate = date.getFullYear() + "-" + (date.getMonth() + 1) + "-" + date.getDate();
				
				return this.updateFilterMapping("timestamp__lt", toDate);
			}
			
			return false;
		},
		
		setScript: function (script) {
			return this.updateFilterMapping("script__contains", script);
		},
		
		setRequester: function (requester) {
			return this.updateFilterMapping("requester__uuid__contains", requester);
		},
		
		filterMapping: {
			"order_by": "-timestamp"
		},
		
		fetch: function (options) {
			options || (options = {});
			options.data || (options.data = {});
			options.data = _.extend(options.data, this.filterMapping);
			
			return Backbone.Collection.prototype.fetch.call(this,options);
		},
		
		fetchMore: function (options) {
			if (this.meta) {
				this.filterMapping["offset"] = Math.min(this.meta.total_count, this.meta.offset + this.meta.limit);
				options || (options = {});
				options["add"] = true;
				this.fetch(options);
			}
			
			return this.hasMoreEntries();
		},
		
		hasMoreEntries: function () {
			return this.meta && this.meta.total_count > this.meta.offset + this.meta.limit;
		}
	});
	
	window.AuditEntryView = Backbone.View.extend({
	    el: "#auditEntriesContainer",

		initialize: function () {
			this.model.on('change', this.render, this);        
			this.el = "#" + this.model.elementGroupId();
		},
		
		render: function() {
			$(this.el).append(ich.auditEntryTemplate(this.model.toJSON()));
			return this;
		}
	});

	window.AuditEntryCount = Backbone.Model.extend({});

	window.AuditEntryCountCollection = Backbone.Collection.extend({
		model: AuditEntryCount,
		urlRoot: AUDIT_COUNT_API_URL,
		
		filterMapping: {},
		
		updateFilterMapping: function (key, value) {
			var oldValue = this.filterMapping[key];
			
			if (value && value !== "") {
				this.filterMapping[key] = value;
			} else if (this.filterMapping[key]) {
				delete this.filterMapping[key];
			}
			
			return oldValue != value;	
		},
		
		setFromDate: function (fromDate) {
			return this.updateFilterMapping("date__gte", fromDate);
		},
		
		setToDate: function (toDate) {
			return this.updateFilterMapping("date__lte", toDate);
		},
		
		fetch: function (options) {
			options || (options = {});
			options.data || (options.data = {});
			if (this.filterMapping) {
				options.data = _.extend(options.data, this.filterMapping);
			}
			
			return Backbone.Collection.prototype.fetch.call(this,options);
		}
	});
	
	window.AuditEntryCountGraph = Backbone.View.extend({
		el: "#auditEntryCountGraphContainer",
		
		initialize: function () {
			_.bindAll(this, "render");
			
			this.auditEntryCounts = new AuditEntryCountCollection();
			this.auditEntryCounts.bind("reset", this.render);
			// Let's not fetch the entries on init... wait until refresh is explicitly called
			//this.auditEntryCounts.fetch();
		},
		
		render: function () {
			
			// It might not be necessary to remove the graph first. D3 seems to have some capability to change the data and have the graph update
			if (this.graph) {
				this.graph.remove();
			}
			var padding = [0,20,30,0];
			var w = 450, h = 150;
			
			var entries = this.auditEntryCounts.map(function (model) { return { date: model.attributes['date'], count: model.attributes['count']}});
			
			var startDate = new Date(this.fromDate);
			var endDate = new Date(this.toDate);//entries[entries.length - 1].date);
			
			startDate = new Date(startDate.getUTCFullYear(), startDate.getUTCMonth(), startDate.getUTCDate());
			endDate = new Date(endDate.getUTCFullYear(), endDate.getUTCMonth(), endDate.getUTCDate() + 1);
			
			this.x = d3.scale.ordinal().domain(d3.time.days(startDate, endDate)).rangeRoundBands([0,w], 0.1);
			this.y = d3.scale.linear().range([0,h]);
			var maxEntries = d3.max(entries, function (d) { return d.count; });
			
			this.y.domain([maxEntries, 0]);
			
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
					return me.x(new Date(d.date + "T00:00:00.0000-05:00")) - 0.5;
				})
				.attr("y", function (d) { 
					return me.y(d.count) - 0.5;
				})
				.attr("width", me.x.rangeBand())
				.attr("height", function (d) { return h - me.y(d.count); });
		},
		
		setFromDate: function (fromDate) {
			this.fromDate = fromDate;
			return this.auditEntryCounts.setFromDate(fromDate);
		},
		
		setToDate: function (toDate) {
			this.toDate = toDate;
			return this.auditEntryCounts.setToDate(toDate);
		},
		
		refresh: function () {
			return this.auditEntryCounts.fetch();
		}
	});
	
	window.AuditApp = Backbone.View.extend({
		el: "#auditEntriesContainer",
		
		events: {
			"click #fetchMoreLink" : "fetchMoreAuditEntries"
		},
		
		initialize: function () {
			_.bindAll(this, "addOne", "addAll", "removeOne", "toggleMoreLink", "fetchMoreAuditEntries", "fetchAuditEntries");
			
			this.auditEntries = new AuditEntryCollection();
			this.auditEntries.bind("add", this.addOne);
			this.auditEntries.bind("reset", this.addAll);
			this.auditEntries.bind("remove", this.removeOne);
			
			var me = this;
			
			this.auditEntryGraph = new AuditEntryCountGraph();
			
			// NOTE: we're adding filtering events via jquery below, rather than as typical Backbone view events
			// This is because the inputs are located outside of the scope of this view (in the sidebar), so 
			// this view does not have access to the elements.
			
			$("#fromDate").datepicker({
				defaultDate: "-1w",
				changeMonth: true,
				numberOfMonths: 1,
				dateFormat: "yy-mm-dd",
				autoSize: true,
				onClose: function (selectedDate) {
					$("#toDate").datepicker("option", "minDate", selectedDate);
					if (me.auditEntries.setFromDate(selectedDate)) {
						me.fetchAuditEntries();
					}
					if (me.auditEntryGraph.setFromDate(selectedDate)) {
						me.auditEntryGraph.refresh();
					}
				}
			});
			
			$("#toDate").datepicker({
				changeMonth: true,
				numberOfMonths: 1,
				dateFormat: "yy-mm-dd",
				autoSize: true,
				onClose: function (selectedDate) {
					$("#fromDate").datepicker("option", "maxDate", selectedDate);
					if (me.auditEntries.setToDate(selectedDate)) { 
						me.fetchAuditEntries();
					}
					if (me.auditEntryGraph.setToDate(selectedDate)) {
						me.auditEntryGraph.refresh();
					}
				}
			});
			
			var today = new Date();
			today.setYear(today.getUTCFullYear());
			today.setMonth(today.getUTCMonth());
			today.setDate(today.getUTCDate());
			var lastWeek = new Date();
			lastWeek.setDate(lastWeek.getUTCDate() - 14);
			
			$("#fromDate").datepicker("setDate", lastWeek);
			$("#toDate").datepicker("setDate", today);
			
			this.auditEntryGraph.setFromDate(lastWeek.getUTCFullYear() + "-" + (lastWeek.getUTCMonth() + 1) + "-" + lastWeek.getUTCDate());
			this.auditEntryGraph.setToDate(today.getUTCFullYear() + "-" + (today.getUTCMonth() + 1) + "-" + today.getUTCDate());
			this.auditEntryGraph.refresh()
			
			$("#script").change(function () { if (me.auditEntries.setScript($(this).val())) { me.fetchAuditEntries(); }});
			$("#requester").change(function () { if (me.auditEntries.setRequester($(this).val())) { me.fetchAuditEntries(); }});
			
			this.fetchAuditEntries();
		},
		
		addOne: function (auditEntry) {
			var view = new AuditEntryView({model : auditEntry});
			var groupEl = $("#" + auditEntry.elementGroupId());
			
			if (groupEl.length == 0) {
				groupEl = $("<div><h2>" + auditEntry.attributes.timestamp_date + "</h2></div>");
				
				// Todo: replace html building below with a template
				var entryTable = $("<table id='" + auditEntry.elementGroupId() + "'>");
				entryTable.append("<tr><th>Time</th><th>Script/Scopes</th><th>Token/Requester/System Entity</th></tr>");
				groupEl.append(entryTable);
				this.$("#auditEntriesList").append(groupEl);
			}
			
			// We've already appended a DOM element within the render method, no need to append here
			view.render();
		},
		
		addAll: function () {
			this.$("#auditEntriesList").empty();
			this.auditEntries.each(this.addOne);
		},
		
		removeOne: function (auditEntry) {
			auditEntry.destroy();
		},
		
		toggleMoreLink: function () {
			if (this.auditEntries.hasMoreEntries()) { 
				this.$("#fetchMoreLink").show();
			} else {
				this.$("#fetchMoreLink").hide();
			}
		},		
		
		fetchAuditEntries: function () {
			this.auditEntries.fetch({success: this.toggleMoreLink });
		},
		
		fetchMoreAuditEntries: function () {
			this.auditEntries.fetchMore({ success: this.toggleMoreLink });
		}
	});
	
	window.auditApp = new AuditApp();
});