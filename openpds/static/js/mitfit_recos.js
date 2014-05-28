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
	var days_times = [];

	for(var i=0; i<activityEntries.length; i++){
		//console.log(activityEntries[i]);
		var start_date = new Date(activityEntries[i]["start"]*1000);
		var start_day = start_date.getDay(); //0-6, Sunday = 0
		var start_hour = start_date.getHours(); //0-23
		var count = activityEntries[i]["high"]
		for(var j=0; j<days_times.length; j++) {
			var days_times_obj = days_times[j];
			var present_flag = false;
			if(start_day == days_times_obj.day && start_hour == days_times_obj.hour){
				days_times_obj.count += count;
				present_flag =true;
				break;
			}
		}
		if(!present_flag){
			days_times.push({"day": start_day, "hour": start_hour, "count": count}); 
		}
	}

        for(var i=0; i<this.mitfit_events.length; i++){
                event_object = this.mitfit_events.at(i).get("value");
		var event_date = new Date(event_object.timestamp*1000);
                var event_day = event_date.getDay(); //0-6, Sunday = 0
                var event_hour = event_date.getHours(); //0-23

		var count = 0;
		for(var j=0; j<days_times.length; j++){
			if(event_day == days_times[j].day && event_hour == days_times[j].hour){
				count = days_times[j].count;
			}
		}
		events.push({"name": event_object.name, "timestamp": event_object.timestamp, "description": event_object.description, "count": count});		
        }
	console.log(events);
	sorted_events = events.sort(function(a,b) { return parseInt(a.count) - parseInt(b.count) } ).reverse();
	console.log(sorted_events);


	var html_string = "";
	for(var i=0; i<sorted_events.length; i++){
		html_string += "<b>Name: </b>" + sorted_events[i].name + "<br/>" + 
				"Time: " + new Date(sorted_events[i].timestamp*1000).toString().replace(/GMT.+/,"") + "<br/>" +
				"Description: " + sorted_events[i].description + "<br/><br/>";
	}
	

	$('#answerListMapContainer').html(html_string);
/*	$('#answerListMapContainer')
		.TidyTable({
			columnTitles : ['Event Name','Time'],
			columnValues : events
		});
*/
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
