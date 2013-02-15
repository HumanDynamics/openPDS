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

window.AnswerRatingStarView = AnswerRatingTextView.extend({
   tagName: "div",
   
   render: function () {
       var entriesModel = this.ratingListCollection.at(0);
       entriesModel || (entriesModel = new AnswerListColleciton ({ key: this.options.key, value: [] }));
       var me = this;
       this.selectedRating = 0;
       this.averageRating = Math.min(5, Math.max(0, entriesModel.value.reduce(function (sum, num) { return sum + num;}, 0) / entriesModel.value.length));
       
       for (i = 1; i <= this.averageRating; i++) {
           this.appendStar(entriesModel, i, "/static/img/star_3.png");
       }
       
       for (i = Math.min(5, Math.floor(this.averageRating + 1)); i <= 5; i++) {
           this.appendStar(entriesModel, i, "/static/img/star_3.png");
       }
       
   },
   
   appendStar: function (entriesModel, value, imgSrc) {
       var me = this;
       $(this.el).append($("<img src='"+imgSrc+"' />").click(function () { me.saveRating(entriesModel, value); }));
   },
   
   saveRating: function (entriesModel, value) {
       entriesModel.get("value").push({time: (new Date).getTime() / 1000, value: value });
       entriesModel.save();
   }
});