window.AnswerListMap = Backbone.View.extend({
    el: "#statsAnswerListContainer",
    
    initialize: function (statsAnswerKey, locationAnswerKey, statsContainerId, autoResize) {
        _.bindAll(this, "render", "renderStats");

        if (statsContainerId) {
            this.statsContainerId = statsContainerId;
            this.el = "#" + statsContainerId;
        } else {
            this.stastContainerId = "answerListStatsContainer";
        }
	this.statsElement = $(this.el);

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
	console.log(max);
	
	if(statEntries[0] != undefined){
            this.statsElement.replaceWith("You are in the following percentile: " + statEntries[0]["rank"]["percentile"] + ", with a rank of  " + statEntries[0]["rank"]["own"] + " out of " + statEntries[0]["rank"]["total"] + "<br/>");
	}

    },

});
