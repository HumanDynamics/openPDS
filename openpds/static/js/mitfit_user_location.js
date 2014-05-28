window.AnswerListMap = Backbone.View.extend({
    el: "#answerListMapContainer",
    
    initialize: function (locationAnswerKey, activityAnswerKey, mapContainerId, autoResize, entity) {
        _.bindAll(this, "render", "renderPlaces");

        if (mapContainerId) {
            this.mapContainerId = mapContainerId;
            this.el = "#" + mapContainerId;
        } else {
            this.mapContainerId = "answerListMapContainer";
        }

	this.entity = entity;
        this.autoResize = autoResize;
        this.render();
        this.locationAnswerLists = new AnswerListCollection([],{ "key": locationAnswerKey });
        this.activityAnswerLists = new AnswerListCollection([],{ "key": activityAnswerKey });
        this.locationAnswerLists.bind("reset", this.renderPlaces);
        this.activityAnswerLists.bind("reset", this.renderPlaces);
        this.locationAnswerLists.fetch();
        this.activityAnswerLists.fetch();
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
	var locationPoints = [];
	if(this.entity == "user"){
            var locationEntries = (this.locationAnswerLists && this.locationAnswerLists.length > 0)? this.locationAnswerLists.at(0).get("value"):[];
            var activityEntries = (this.activityAnswerLists && this.activityAnswerLists.length > 0)? this.activityAnswerLists.at(0).get("value"):[];

            var highActivityLocations = [];

	    var max = 0;
            for (i in locationEntries){
                var locationEntry = locationEntries[i];
                var centroid = locationEntry["centroid"];

                if(activityEntries[i] != undefined && centroid[0] != undefined){
                    var high = activityEntries[i]["high"];
                    var low = activityEntries[i]["low"];
		    var total = activityEntries[i]["total"];
			if(max < high){
			    max = high;
			}
			if(high > 0){
                            repeatLocation = false;
                            for (highActivityLocation in highActivityLocations){
                                if (centroid[0][0] == highActivityLocation[0] && centroid[0][1] == highActivityLocation[1]){
                                    repeatLocation = true;
                                    break;
                                }
                            }
                            if(repeatLocation == false){
                                highActivityLocations.push(centroid[0]);
			        locationPoints.push({lat: centroid[0][0], lng: centroid[0][1], count: high});
                            }

                        }
                }
            }
	} else if(this.entity == "average"){
	    var activityEntries = (this.activityAnswerLists && this.activityAnswerLists.length > 0)? this.activityAnswerLists.at(0).get("value"):[];
            locationPoints = (this.locationAnswerLists && this.locationAnswerLists.length > 0)? this.locationAnswerLists.at(0).get("value"):[];

            var max = 0;
            for (locationIndex in locationPoints){
                if(locationPoints[locationIndex]["count"] > max){
                    max = locationPoints[locationIndex]["count"]
                }
            }
	}
	

	var testData = {
		max: max,
		data: locationPoints
	};

        // this is important, because if you set the data set too early, the latlng/pixel projection doesn't work
        google.maps.event.addListenerOnce(this.map, "idle", function(){
                heatmap.setDataSet(testData);
        });

    },

});
