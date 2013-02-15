window.AnswerRatingTextView = Backbone.View.Extend({
    tagName: "div", 
    
    initialize: function (options) {
        _.bindAll(this, "render");
        this.ratingListCollection = new AnswerListCollection([], { key: options.key });
        this.ratingListCollection.bind("reset", this.render);
        this.ratingListCollection.fetch();
    }, 
    
    render: function () {
        var entriesModel = this.ratingListCollection.at(0);
        var me = this;
        $(this.el).append($("<input type='text' />").change(function () { 
            entriesModel.get("value").push({time: (new Date).getTime() * 1000,  value: $(this).text() });
            entriesModel.save();
        }) );
    }

});