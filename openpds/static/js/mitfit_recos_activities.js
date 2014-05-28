window.MITFITEventModel = Backbone.Model.extend({                

    event_name: "Event Name",
    min_activity_level: 0,
    max_activity_level: 1,
    //location_value: "42.358280, -71.096107",
    timestamp: "Timestamp",
    description: "Description"
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
   },

    renderRecos: function () {
	var activityEntries = (this.activityAnswerLists && this.activityAnswerLists.length > 0)? this.activityAnswerLists.at(0).get("value"):[];
	//console.log(activityEntries);

	var events = [];

        for(var i = 0; i < this.mitfit_events.length; i++){
	    var event_item = [];
	    events_object = this.mitfit_events.at(i).get("value");
	    //console.log(events_object);
	    for(index in events_object){
		if(activityEntries.length > 0){
			//console.log("comparing");
			console.log("average: " + activityEntries[0]["average_activity_rate"]);
			console.log("min: " + activityEntries[0]["min_low_activity_rate"]);
			console.log("max: " + activityEntries[0]["max_high_activity_rate"]);
			if(activityEntries[0]["average_activity_rate"] >= events_object[index]["min-activity-level"] && activityEntries[0]["max_high_activity_rate"] <= events_object[index]["max-activity-level"]){
			//if(activityEntries[0]["min_low_activity_rate"] >= events_object[index]["min-activity-level"] && activityEntries[0]["max_high_activity_rate"] <= events_object[index]["max-activity-level"]){
			    var time_string = new Date(events_object[index]["timestamp"]*1000);
			    console.log(formattedDate(time_string));
			    //this.element.append("Event: " + events_object[index]["event-name"] + ", Location: " + events_object[index]["location"] + ", Time: " + events_object[index]["timestamp"] + ", Description: " + events_object[index]["description"] + ", URL: " + events_object[index]["url"]);
			    event_item.push(events_object[index]["event-name"]);
			    //event_item.push(events_object[index]["location"]);
			    //event_item.push(events_object[index]["timestamp"]);
			    event_item.push(formattedDate(time_string));
			    //event_item.push(events_object[index]["description"]);

			    events.push(event_item);
			    //console.log(event_item);
			}
		}	
	    }
	
        }

        var html = '<table>';
        for(var i=0; i< events.length; i++){
            html += '<tr><td>';
	    for(var j=0; j<events[i].length; j++){
		html += events[i][j] + '<br/>';
	    }
	    html += '<a href="#" onclick="return false;">Register</a>';
	    html += '</td></tr>';
        }
        html += '</table>';

        $("#answerListMapContainer").append($(html));   

	//console.log(events);

//	$('#answerListMapContainer')
//		.TidyTable({
//			columnTitles : ['Event','Time'],
//			columnValues : events
//		});

	
    },

});

//source: http://stackoverflow.com/questions/6348431/best-way-to-remove-edt-from-a-date-returned-via-javascript-with-tolocalestring
function padZ(num, n) {
    n = n || 1; // Default assume 10^1
    return num < Math.pow(10, n) ? "0" + num : num;
}

function formattedDate(d) {
    var day = d.getDate();
    var month = d.getMonth() + 1; // Note the `+ 1` -- months start at zero.
    var year = d.getFullYear();
    var hour = d.getHours();
    var min = d.getMinutes();
    return month+"/"+day+"/"+year+" "+hour+":"+padZ(min);
}
