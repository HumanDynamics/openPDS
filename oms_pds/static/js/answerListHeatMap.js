window.AnswerListHeatMap = Backbone.View.extend({
    el: "#answerListHeatMapContainer",
                                            
    initialize: function () {
                                            
        _.bindAll(this, "render");
		this.initButtons();
        this.timeSelector = function (a) { return a.start * 1000; };
		this.locationSelector = function (a) { return { "lat" : a.latitude, "lng" : a.longitude }; };
        
        // this.answerLists = new AnswerListCollection([],{ "key": answerKey });
        this.answerLists = new AnswerListCollection();
        this.answerLists.bind("reset", this.render);
		
	  	var gradient = [
			'rgba(0, 255, 255, 0)',
			'rgba(0, 255, 255, 1)',
			'rgba(0, 191, 255, 1)',
			'rgba(0, 127, 255, 1)',
			'rgba(0, 63, 255, 1)',
			'rgba(0, 0, 255, 1)',
			'rgba(0, 0, 223, 1)',
			'rgba(0, 0, 191, 1)',
			'rgba(0, 0, 159, 1)',
			'rgba(0, 0, 127, 1)',
			'rgba(63, 0, 91, 1)',
			'rgba(127, 0, 63, 1)',
			'rgba(191, 0, 31, 1)',
			'rgba(255, 0, 0, 1)'
		]
                                            
		var cambridge = new google.maps.LatLng(42.3736, -71.1106);
		var mapOptions = {
			center: cambridge,
			zoom: 12
		};
		// WARNING
		var map = new google.maps.Map(document.getElementById("answerListHeatMapContainer"), mapOptions);

		// try empty init
		var heatmap = new google.maps.visualization.HeatmapLayer({
			data: []
		});
		heatmap.setMap(map);
		heatmap.set('gradient', gradient);
		heatmap.set('radius', 20);
		
		this.heatmap = heatmap;
    },
	
    render: function () {
		var values = this.activityByHourList.at(0).get("value").map(this.valueSelector);
		var locations = this.activityByHourList.at(0).get("value").map(this.locationSelector);
		var timestamps = this.activityByHourList.at(0).get("value").map(this.timeSelector);
		
		var heatmapData = [];
		for (x =0; x < entries.length; x++) {
			var location = locations[x];
			var lat = location.lat;
			var lng = location.lng;
			var val = values[x];
			var point = {location: new google.maps.LatLng(lat,lng), weight: val};
			heatmapData.push(point);
		};
		
		console.log(heatmapData);
		this.heatmap.setData(heatmapData);
    },
    
	show: function (answerKey, valueSelector) {
		this.valueSelector = valueSelector;
		this.answerLists.options = { "key" : answerKey };
		this.answerLists.fetch({ 'reset' : true });
	},
	
	showFocus: function () {
		var answerKey = "RecentFocusByHour";
		var valueSelector = function (a) { return a.focus; };
		this.show(answerKey, valueSelector);
	},
	
	showActivity: function () {
		var answerKey = "RecentActivityByHour";
		var valueSelector = function (a) { return (a.total > 0)? 10 * ((a.low + a.high) / a.total) : 0; };
		this.show(answerKey, valueSelector);
	},
	
	showSocial: function () {
		var answerKey = "RecentSocialByHour";
		var valueSelector = function (a) { return a.social; };
		this.show(answerKey, valueSelector);
	},
	
	initButtons: function () {
		var activity = $('<div>');
		activity.addClass('button2');
		activity.addClass('activity');
		$('#buttons').append(activity);
		activity.click(function(){
			this.showActivity();
		});
		
		var social = $('<div>');
		social.addClass('button2');
		social.addClass('social');
		$('#buttons').append(social);
		social.click(function(){
			this.showSocial();
		});
		
		var focus = $('<div>');
		focus.addClass('button2');
		focus.addClass('focus');
		$('#buttons').append(focus);
		social.click(function(){
			this.showFocus();
		})
	},
	
    updateSize: function () {
        var navbar= $("div[data-role='navbar']:visible"),
        content = $("div[data-role='content']:visible:visible"),
        footer = $("div[data-role='footer']:visible"),
        viewHeight = $(window).height(),
        contentHeight = viewHeight - navbar.outerHeight() - footer.outerHeight();
    
        if (content.outerHeight() !== contentHeight) {
            content.height(contentHeight);
        }
    },
});

