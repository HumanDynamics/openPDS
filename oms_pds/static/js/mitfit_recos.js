window.MITFITEventModel = Backbone.Model.extend({                

    event_name: "Event Name",
    min_activity_level: 0,
    max_activity_level: 1,
    location_value: "42.358280, -71.096107",
    timestamp: "Timestamp",
    description: "Description",
    url_value: "URL"
});

window.MITFITEventList = Backbone.Collection.extend({
    model: MITFITEventModel,
    url: "../../static/data/mitfit_events.json",

    initialize: function(){
        //console.log("Initialize events");
    },

    parse : function(response){
        //console.log(response.objects);
        return response.objects;  
   }    
});

window.AnswerListMap = Backbone.View.extend({
    el: "#answerListMapContainer",
    
    initialize: function (activityAnswerKey, containerId, autoResize) {
        _.bindAll(this, "render", "renderRecos");

        this.render();

	//console.log(activityAnswerKey);
	this.activityAnswerLists = new AnswerListCollection([],{ "key": activityAnswerKey });
	this.activityAnswerLists.bind("reset", this.renderRecos);
	this.activityAnswerLists.fetch();

        this.mitfit_events = new MITFITEventList();
        this.mitfit_events.fetch();
        this.mitfit_events.bind("reset", this.renderRecos);
    },
    
    render: function () {
	var myLatlng = new google.maps.LatLng(42.359779, -71.093373);
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
   },

    renderRecos: function () {
	var activityEntries = (this.activityAnswerLists && this.activityAnswerLists.length > 0)? this.activityAnswerLists.at(0).get("value"):[];
	//console.log(activityEntries);

	var display_flag = false;
	var locationArray = [];

        for(var i = 0; i < this.mitfit_events.length; i++){
	    events_object = this.mitfit_events.at(i).get("value");
	    for(index in events_object){
		if(activityEntries.length > 0){
			if(activityEntries[0]["average_activity_rate"] >= events_object[index]["min-activity-level"] && activityEntries[0]["max_high_activity_rate"] <= events_object[index]["max-activity-level"]){
			    var time_string = new Date(events_object[index]["timestamp"]*1000);
			    var location_coords = events_object[index]["location"].split(",");
		  	    var lat = parseFloat(location_coords[0].trim());
		  	    var lng = parseFloat(location_coords[1].trim());
			    var marker = new google.maps.Marker({
                	        position: new google.maps.LatLng(lat,lng),
                	    	map: this.map
            		    });

			    var locationPoint = [];
			    locationPoint.push(lat);
			    locationPoint.push(lng);
			
			    locationArray.push(locationPoint);
			    display_flag = true;
			    //this.element.append("Event: " + events_object[index]["event-name"] + ", Location: " + events_object[index]["location"] + ", Time: " + events_object[index]["timestamp"] + ", Description: " + events_object[index]["description"] + ", URL: " + events_object[index]["url"]);
			}
		}	
	    }
	
        }


	// this is important, because if you set the data set too early, the latlng/pixel projection doesn't work

/*	var beachMarker = new google.maps.Marker({
     	    position: new google.maps.LatLng(42.359779, -71.093373),
      	    map: this.map,
  	});
*/

	//console.log(locationArray);
        google.maps.event.addListener(this.map, "idle", function(){


	    console.log("map loaded");
	    console.log(locationArray);
	    for(locationIndex in locationArray){
		console.log(locationIndex);
		console.log(locationArray[locationIndex][0]);

		var marker = new google.maps.Marker({
                    position: new google.maps.LatLng(locationArray[locationIndex][0], locationArray[locationIndex][1]),
                    map: this.map
            	});
		var infowindow = new google.maps.InfoWindow({
      		    content: "test"
  		});

		google.maps.event.addListener(marker, 'click', function() {
    		    infowindow.open(this.map,marker);
  		});
	    }

                            //marker.info = new google.maps.InfoWindow({
                            //  content: '<b>Test:</b> text'
                            //});

        });

/*
	google.maps.event.addListener(this.map, 'click', function() {
	    marker.info.open(this.map, marker);
	});
*/
    },

});

