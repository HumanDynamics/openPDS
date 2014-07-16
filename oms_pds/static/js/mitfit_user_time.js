window.AnswerListMap = Backbone.View.extend({
    el: "#answerListMapContainer",
    
    initialize: function (averageActivityAnswerKey, activityAnswerKey, center, timesContainerId, autoResize) {
        _.bindAll(this, "render", "renderPlaces");

        if (timesContainerId) {
            this.timesContainerId = timesContainerId;
            this.timesEl = "#" + timesContainerId;
        } else {
            this.timesContainerId = "answerListTimesContainer";
            this.timesEl = "#" + timesContainerId;
        }
        this.timesElement = $(this.timesEl);
//        this.timesElement.append("The times you are most active:<br/>");

        this.autoResize = autoResize;
        this.center = center;
        this.render();
        this.averageActivityAnswerLists = new AnswerListCollection([],{ "key": averageActivityAnswerKey });
        this.activityAnswerLists = new AnswerListCollection([],{ "key": activityAnswerKey });
        this.averageActivityAnswerLists.bind("reset", this.renderPlaces);
        this.activityAnswerLists.bind("reset", this.renderPlaces);
        this.averageActivityAnswerLists.fetch();
        this.activityAnswerLists.fetch();
//	google.load("visualization", "1", {packages:["corechart"]});
//google.setOnLoadCallback(this.drawChart);
    },
    
    render: function () {
	//google.load("visualization", "1", {packages:["corechart"]});
//	google.setOnLoadCallback(this.renderPlaces);
   },

    renderPlaces: function () {
//        var locationEntries = (this.locationAnswerLists && this.locationAnswerLists.length > 0)? this.locationAnswerLists.at(0).get("value"):[];
	var averageActivityEntries = (this.averageActivityAnswerLists && this.averageActivityAnswerLists.length > 0)? this.averageActivityAnswerLists.at(0).get("value"):[];
	console.log(averageActivityEntries);

        var activityEntries = (this.activityAnswerLists && this.activityAnswerLists.length > 0)? this.activityAnswerLists.at(0).get("value"):[];
        var highActivityLocations = [];
        //var highActivityTimes = [];
	var highActivityTimes = new Array(24);
	for(var i=0; i<24; i++){
	    highActivityTimes[i] = 0;
	}

	//var locationPoints = [];
	var max = 0;
//        for (i in locationEntries){
	for(i in activityEntries){
	    var activityEntry = activityEntries[i];
//            var locationEntry = locationEntries[i];
//            var centroid = locationEntry["centroid"];

//            var startTime = locationEntry["start"];
//            var endTime = locationEntry["end"];
	    var startTime = activityEntry["start"];
	    var endTime = activityEntry["end"];

                var high = activityEntries[i]["high"];
                var low = activityEntries[i]["low"];
		var total = activityEntries[i]["total"];
//                if ( high + low > 0 ){
//                    var normalizedActivity = Math.round((high + low)*500/(total)); //500 for testing. Need to look at various datasets to figure out formula.
//		    if(max < normalizedActivity){
//			max = normalizedActivity;
///		    }
		    if(max < high){
			max = high;
		    }
//                    if (normalizedActivity > 1){
		    if(high > 0){

/*                        repeatLocation = false;
                        for (highActivityLocation in highActivityLocations){
                            if (centroid[0][0] == highActivityLocation[0] && centroid[0][1] == highActivityLocation[1]){
                                repeatLocation = true;
                                break;
                            }
                        }
                        if(repeatLocation == false){
                            highActivityLocations.push(centroid[0]);
			    locationPoints.push({lat: centroid[0][0], lng: centroid[0][1], count: normalizedActivity});
                        }
*/

                        var startDate = new Date(startTime*1000);
                        var startHours = startDate.getHours();
                        var endDate = new Date(endTime*1000);
                        var endHours = endDate.getHours();

			highActivityTimes[startHours] += 1;
                    }
//                } //high+low
        }
	//console.log(highActivityTimes);
	//console.log(averageActivityEntries);


        var newHighActivityTimes = new Array(8);
        for(var i=0; i<8; i++){
            newHighActivityTimes[i] = highActivityTimes[2*i + i] + highActivityTimes[2*i + (i+1)] + highActivityTimes[2*i + (i+2)];
        }

        var newAverageActivityEntries = new Array(8);
        for(var i=0; i<8; i++){
            newAverageActivityEntries[i] = averageActivityEntries[2*i + i] + averageActivityEntries[2*i + (i+1)] + averageActivityEntries[2*i + (i+2)];
        }

	var dataForVisualization = [];
	var headers = [];
	headers.push('Hour');
	headers.push('Frequency');
	dataForVisualization.push(headers);
	for(highActivityTime in highActivityTimes){
	    var data = [];
	    var time = '';
	    if(highActivityTimes[highActivityTime]["start"] == 12){
		time = 'Noon';
	    } else if(highActivityTimes[highActivityTime]["start"] == 0){
                time = 'Midnight';
            } else if(highActivityTimes[highActivityTime]["start"] < 12){
                time = highActivityTimes[highActivityTime]["start"] + 'am';
            } else{
	    	time = highActivityTimes[highActivityTime]["start"] + 'pm';
	    }
	    data.push(time);
	    data.push(highActivityTimes[highActivityTime] + highActivityTimes[highActivityTime + 1] + highActivityTimes[highActivityTime + 2]);    
	    dataForVisualization.push(data);

	    highActivityTime += 3;
	}
	//console.log(dataForVisualization);

        /*var results = google.visualization.arrayToDataTable(dataForVisualization);

        var options = {
legend: {position: 'none'}
        };

        var chart = new google.visualization.BarChart(document.getElementById('chart_div'));
        chart.draw(results, options);
	*/

        //$('#chart_div').highcharts({
	chart = new Highcharts.Chart({
            chart: {
                type: 'column',
		renderTo: 'chart_div'
            },
            title: {
                text: ''
            },
            xAxis: {
                categories: ['Midnight', '3am', '6am', '9am',
			    'Noon', '3pm', '6pm', 
			    '9pm'],
                title: {
                    text: null
                }
            },
            yAxis: {
                min: 0,
                title: {
                    text: 'Frequency',
                    align: 'high'
                },
                labels: {
                    overflow: 'justify'
                }
            },
            plotOptions: {
                bar: {
                    dataLabels: {
                        enabled: false
                    }
                }
            },
            series: [{
		name: 'Me',
		color: '#EE62E2',
                data: newHighActivityTimes
            },
		{
                name: 'Everyone',
		color: '#7ACDF7',
                data: newAverageActivityEntries
	    }]
        });

    },

    formatTime: function (time) {
	var timeString = "";
        if(time == 12){
     	    timeString = "Noon";
        } else if (time == 24){
	    timeString = "Midnight";
        } else if(time > 12 && time < 24){
	    timeValue = time - 12;
	    timeString = timeValue + " PM";
        } else {
	    timeString = time + " AM";
        }
	return timeString;
    },

    /*drawChart: function () {
        var data = google.visualization.arrayToDataTable([
          ['Year', 'Sales', 'Expenses'],
          ['2004',  1000,      400],
          ['2005',  1170,      460],
          ['2006',  660,       1120],
          ['2007',  1030,      540]
        ]);

        var options = {
          title: 'Company Performance',
          hAxis: {title: 'Year', titleTextStyle: {color: 'red'}}
        };

        var chart = new google.visualization.ColumnChart(document.getElementById('chart_div'));
        chart.draw(data, options);
      },*/

});
