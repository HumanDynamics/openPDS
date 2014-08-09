window.AnswerListMap = Backbone.View.extend({
    el: "#answerListMapContainer",
    
    initialize: function (locationAnswerKey, mapContainerId) {
        _.bindAll(this, "render", "renderPlaces");

        if (mapContainerId) {
            this.mapContainerId = mapContainerId;
            this.el = "#" + mapContainerId;
        } else {
            this.mapContainerId = "answerListMapContainer";
        }

        this.render();
        this.locationAnswerLists = new AnswerListCollection([],{ "key": locationAnswerKey });
        this.locationAnswerLists.bind("reset", this.renderPlaces);
        this.locationAnswerLists.fetch();
	var heatmap;
    },
    
    render: function () {
	var myLatlng = new google.maps.LatLng(42.361794,-71.090804);
	var myOptions = {
	  zoom: 13,
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

    renderPlaces: function () {
        var hot_spots = (this.locationAnswerLists && this.locationAnswerLists.length > 0)? this.locationAnswerLists.at(0).get("value"):[];
        var max = 0;
        for (hot_spot_index in hot_spots){
	    console.log(hot_spots[hot_spot_index]);
            if(hot_spots[hot_spot_index]["frequency"] > max){
                max = hot_spots[hot_spot_index]["frequency"];
            }
        }
	
	var hot_spots_data = {
		max: max,
		data: hot_spots
	};
	
	console.log(max);

        // this is important, because if you set the data set too early, the latlng/pixel projection doesn't work
        google.maps.event.addListenerOnce(this.map, "idle", function(){
                heatmap.setDataSet(hot_spots_data);
        });

    },

});
