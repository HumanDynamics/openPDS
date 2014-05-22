window.AnswerListMap = Backbone.View.extend({
    el: "#statsAnswerListContainer",
    
    initialize: function (statsAnswerKey, locationAnswerKey, mapContainerId, autoResize) {
        _.bindAll(this, "render", "renderStats");

        if (mapContainerId) {
            this.mapContainerId = mapContainerId;
            this.el = "#" + mapContainerId;
        } else {
            this.mapContainerId = "answerListMapContainer";
        }

        this.autoResize = autoResize;
        this.render();
        this.statsAnswerLists = new AnswerListCollection([],{ "key": statsAnswerKey });
        this.locationAnswerLists = new AnswerListCollection([],{ "key": locationAnswerKey });
        this.statsAnswerLists.bind("reset", this.renderStats);
        this.locationAnswerLists.bind("reset", this.renderStats);
        this.statsAnswerLists.fetch();
        this.locationAnswerLists.fetch();
    },
    
    render: function () {
        var myLatlng = new google.maps.LatLng(42.361794,-71.090804);
        var myOptions = {
          zoom: 15,
          center: myLatlng,
          mapTypeId: google.maps.MapTypeId.ROADMAP,
          disableDefaultUI: false,
          scrollwheel: true,
          draggable: true,
          navigationControl: true,
          mapTypeControl: false,
          scaleControl: true,
          disableDoubleClickZoom: false
        };
        this.map = new google.maps.Map(document.getElementById("answerListMapContainer"), myOptions);

        heatmap = new HeatmapOverlay(this.map, {"radius":15, "visible":true, "opacity":60});
   },

    renderStats: function () {
        var statEntries = (this.statsAnswerLists && this.statsAnswerLists.length > 0)? this.statsAnswerLists.at(0).get("value"):[];
	var locationEntries = (this.locationAnswerLists && this.locationAnswerLists.length > 0)? this.locationAnswerLists.at(0).get("value"):[];

	//console.log(locationEntries);
	var max = 0;
	for (locationIndex in locationEntries){
	    if(locationEntries[locationIndex]["count"] > max){
		max = locationEntries[locationIndex]["count"]
	    }
	}
	
        var testData = {
                max: max,
                data: locationEntries
        };
	console.log(testData);

        // this is important, because if you set the data set too early, the latlng/pixel projection doesn't work
        google.maps.event.addListenerOnce(this.map, "idle", function(){
                heatmap.setDataSet(testData);
        });

    },

});
