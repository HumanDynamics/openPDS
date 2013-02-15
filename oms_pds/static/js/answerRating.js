window.AnswerRatingTextView = Backbone.View.extend({
    tagName: "div", 
    
    initialize: function (options) {
        _.bindAll(this, "render");
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
    }

});
