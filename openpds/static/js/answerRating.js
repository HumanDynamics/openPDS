window.AnswerRatingTextView = Backbone.View.extend({
    tagName: "div", 
    
    initialize: function (options) {
        this.bindAll();
        this.ratingListCollection = new AnswerListCollection([], { key: options.key });
        this.ratingListCollection.bind("reset", this.render);
        this.ratingListCollection.fetch();
    }, 
    
    render: function () {
        var entriesModel = this.ratingListCollection.at(0);
        entriesModel || (entriesModel = new AnswerList({ key: this.options.key, value:[]}));
        var me = this;
        $(this.el).append($("<input type='text' />").change(function () { 
            entriesModel.get("value").push({time: (new Date).getTime() / 1000, value: $(this).val() });
            entriesModel.save();
        }) );
    },

    bindAll: function () {
        _.bindAll(this, "render");
    }
});

window.AnswerRatingStarView = AnswerRatingTextView.extend({
    el: "<div>",
    selectedRating: 0,

    bindAll: function () {
        _.bindAll(this, "render", "appendStar", "saveRating");
    },
    
    render: function () {
        var el = $(this.el);
        el.empty();
        var entriesModel = this.ratingListCollection.at(0);
        entriesModel || (entriesModel = new AnswerList({ key: this.options.key, value: [] }));
        var me = this;
        var len = entriesModel.get("value").length;
        this.averageRating = (len > 0)? entriesModel.get("value").reduce(function (sum, num) { return sum + num.value; }, 0) / len : 0;
	    this.averageRating = Math.max(0, Math.min(5, this.averageRating));        
        var yellow = (this.selectedRating > 0)? this.selectedRating : 0; 
 
        for (i = 1; i <= yellow; i++) {
            this.appendStar(entriesModel, i, "/static/img/star_3.png");
        }
        
        for (i = Math.floor(yellow + 1); i <= 5; i++) {
            this.appendStar(entriesModel, i, "/static/img/star_1.png");
        }

        return el;
    },
    
    appendStar: function (entriesModel, value, imgSrc) {
        var me = this;
        $(this.el).append($("<img src='"+imgSrc+"' />").click(function () { me.saveRating(entriesModel, value); }));
    },
    
    saveRating: function (entriesModel, value) {
        // NOTE: we're relying on the entries being sorted in descending-time order.
        var mostRecentVoteTime = (entriesModel.get("value").length > 0)? entriesModel.get("value")[0].time : 0;
        var now = (new Date).getTime() / 1000;
        this.selectedRating = value;

        // We're limiting to one vote per day.
        // Data just doesn't change quickly enough for more frequent recordings to matter.
        // Note that in the case of a recent entry, we're not overwriting the time.
        // This is to allow votes at 24 hour intervals, regardless of how many times the user updates their vote.
        if (now > mostRecentVoteTime + 3600 * 24) {
            entriesModel.get("value").unshift({ time: now, value: value });
        } else {
            entriesModel.get("value")[0].value = value;
        }

        entriesModel.save();
        this.render();
    }
});
