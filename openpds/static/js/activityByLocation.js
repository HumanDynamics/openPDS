window.AnswerListMap = Backbone.View.extend({
    el: "#answerListMapContainer",
    
    initialize: function (locationAnswerKey, activityAnswerKey, center, mapContainerId, timesContainerId, autoResize) {
        _.bindAll(this, "render", "renderPlaces");        

        if (mapContainerId) {
            this.mapContainerId = mapContainerId;
            this.el = "#" + mapContainerId;
        } else {
            this.mapContainerId = "answerListMapContainer";
        }

        if (timesContainerId) {
            this.timesContainerId = timesContainerId;
            this.timesEl = "#" + timesContainerId;
        } else {
            this.timesContainerId = "answerListTimesContainer";
	    this.timesEl = "#" + timesContainerId;
        }
	this.timesElement = $(this.timesEl);
	this.timesElement.append("The times you are most active:<br/>");

        this.autoResize = autoResize;
        this.center = center;
        this.render();
        this.locationAnswerLists = new AnswerListCollection([],{ "key": locationAnswerKey });
	this.activityAnswerLists = new AnswerListCollection([],{ "key": activityAnswerKey });
        this.locationAnswerLists.bind("reset", this.renderPlaces);
        this.activityAnswerLists.bind("reset", this.renderPlaces);
        this.locationAnswerLists.fetch();
	this.activityAnswerLists.fetch();
    },
    
    render: function () {
	this.overlay = new OpenLayers.Layer.Vector('Overlay', {
            styleMap: new OpenLayers.StyleMap({
                externalGraphic: 'http://www.openlayers.org/dev/img/marker.png',
                graphicWidth: 20, graphicHeight: 24, graphicYOffset: -24,
            })
        });


        this.map = new OpenLayers.Map({
            div: this.mapContainerId, projection: "EPSG:3857",
            zoom: 15
        });

	this.map.addLayers([new OpenLayers.Layer.OSM(), this.overlay]);
    },

    renderPlaces: function () {
        var locationEntries = (this.locationAnswerLists && this.locationAnswerLists.length > 0)? this.locationAnswerLists.at(0).get("value"):[];
        var activityEntries = (this.activityAnswerLists && this.activityAnswerLists.length > 0)? this.activityAnswerLists.at(0).get("value"):[];
	var highActivityLocations = []
	var highActivityStartTimes = []
	for (i in locationEntries){
            var locationEntry = locationEntries[i];
            var centroid = locationEntry["centroid"];
		
            var startTime = locationEntry["start"];
            var endTime = locationEntry["end"];
		
	    if(activityEntries[i] != undefined && centroid[0] != undefined){
                var high = activityEntries[i]["high"];
		var low = activityEntries[i]["low"];
		if ( high + low > 0 ){
		    var normalizedActivity = (high - low)/(high + low);
	            if (normalizedActivity > 0.8){
		        repeatLocation = false;
		        for (highActivityLocation in highActivityLocations){
			    console.log(centroid[0]);
			    console.log(highActivityLocation);
		            if (centroid[0][0] = highActivityLocation[0] && centroid[0][1] == highActivityLocation[1]){
			        repeatLocation = true;
				break;
			    }
			}
                        if(repeatLocation == false){
			    highActivityLocations.push(centroid[0]);
                            console.log(centroid);
                            this.addPoint(centroid[0]);
                        }

	                var startDate = new Date(startTime*1000);
                        var startHours = startDate.getHours();
                        var endDate = new Date(endTime*1000);
                        var endHours = endDate.getHours();

                        repeatTime = false;
                        for (highActivityStartTime in highActivityStartTimes){
                            if (startHours = highActivityStartTime){
                                repeatTime = true;
                                break;
                            }
                        }
			if(repeatTime == false){
				this.timesElement.append("From " + startHours + " to " + endHours + "<br/>");
			}
		    }
		}
	    }
	}
	if (this.center) {
            this.setCenter(this.center, 18);
        }
        if (this.autoResize) {
            this.updateSize();
        }
    },
    
    addPoint: function (point) {
	console.log(point);
	var pointGeometry = new OpenLayers.Geometry.Point(point[1], point[0]).transform('EPSG:4326', 'EPSG:3857');
        this.overlay.addFeatures([new OpenLayers.Feature.Vector(pointGeometry, {tooltip: 'OpenLayers'})]);

	this.map.setCenter(pointGeometry.getBounds().getCenterLonLat());
    },
   
    setCenter: function (latLong, zoom, plot) {
        this.center = latLong;
        var center = new OpenLayers.LonLat(this.center[1], this.center[0]);
        center.transform(this.map.displayProjection, this.map.getProjectionObject());
        this.map.setCenter(center, 18);
        if (plot) {
            this.addPoint(latLong);
        }
    },
 
    zoomIn: function () {
        if (this.map) {
            this.map.zoomIn();
        }
    },
    
    zoomOut: function () {
        if (this.map) {
            this.map.zoomOut();
        }
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
    
        if (this.map && this.map instanceof OpenLayers.Map) {
            this.map.updateSize();
        }
    }
    
});
